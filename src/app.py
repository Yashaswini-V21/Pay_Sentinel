from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import pickle
import time
from collections import defaultdict
from datetime import datetime, timezone
import psutil
from pathlib import Path
from functools import wraps
import re
import uuid
from contextvars import ContextVar
import bleach
import threading
import signal
import sys
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flasgger import Swagger, swag_from

import random
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_file, send_from_directory, Response, stream_with_context, g
from werkzeug.exceptions import RequestEntityTooLarge

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector
from pdf_report import make_pdf
from voice_alerts import alert_html as _voice_alert_html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODEL_CACHE_DIR = Path(PROJECT_ROOT) / "models"
LOG_DIR = Path(PROJECT_ROOT) / "logs"

# Create directories if they don't exist
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Distributed Tracing ---
_request_id: ContextVar[str] = ContextVar('request_id', default='-')

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id.get('-')
        return True

# Configure logging
logger = logging.getLogger("paysentinel")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] [req=%(request_id)s] - %(message)s"
)

file_handler = logging.FileHandler(LOG_DIR / "paysentinel.log")
file_handler.setLevel(logging.DEBUG)
file_handler.addFilter(RequestIdFilter())
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(RequestIdFilter())
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def _graceful_shutdown(signum, frame):
    logger.info(f"[SHUTDOWN] Signal {signum} received. Shutting down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGTERM, _graceful_shutdown)
signal.signal(signal.SIGINT, _graceful_shutdown)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app._start_time = time.time()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# ── Swagger Configuration ──
swagger_config = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/api/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "PaySentinel API",
        "description": "AI-powered UPI fraud detection for Indian merchants. "
                       "World's first Kannada voice fraud alert system.",
        "version": "2.0.0",
        "contact": {"email": "hello@paysentinel.ai"},
        "license": {"name": "MIT"},
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    },
    "tags": [
        {"name": "analysis", "description": "Fraud detection endpoints"},
        {"name": "reporting", "description": "PDF report generation"},
        {"name": "streaming", "description": "Live transaction stream"},
        {"name": "utility", "description": "Health, metrics, sample data"},
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# ── Security Audit Log ──
sec_logger = logging.getLogger("paysentinel.security")
sec_handler = logging.FileHandler(LOG_DIR / "security.log")
sec_handler.setFormatter(logging.Formatter("%(asctime)s SECURITY %(message)s"))
sec_logger.addHandler(sec_handler)

def log_sec(event, req, details='', severity='INFO'):
    ip_hash = hashlib.sha256(req.remote_addr.encode()).hexdigest()[:12]
    sec_logger.info(f"[{severity}] {event} ip={ip_hash} path={req.path} {details}")

@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
        "https://cdnjs.cloudflare.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
        "https://fonts.gstatic.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; media-src 'self' blob: data:; "
        "object-src 'none'; frame-ancestors 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(self), geolocation=()'
    response.headers.pop('Server', None)
    return response

# ── Input Sanitization ──
_ALLOWED_MERCHANT = re.compile(r'[^a-zA-Z0-9\s\-_\'\u0C00-\u0C7F\u0900-\u097F]')

def sanitize_merchant_name(name: str) -> str:
    if not name or not isinstance(name, str): return 'My UPI Store'
    name = bleach.clean(name, tags=[], strip=True)
    name = _ALLOWED_MERCHANT.sub('', name).strip()[:80]
    return name or 'My UPI Store'

def sanitize_language(lang: str) -> str:
    return lang if lang in {'English', 'Kannada', 'Hindi'} else 'English'

def deep_validate_csv(df) -> tuple[bool, str]:
    if df.empty: return False, "CSV file is empty"
    if len(df) > 50000: return False, "CSV too large — max 50,000 rows"
    if len(df.columns) > 50: return False, "Too many columns — max 50"
    if 'amount' not in df.columns: return False, "CSV must include an 'amount' column"
    amounts = pd.to_numeric(df['amount'], errors='coerce')
    if amounts.isna().all(): return False, "Amount column has no valid numbers"
    if (amounts < 0).any(): return False, "Amount column contains negative values"
    if (amounts > 1e8).any(): return False, "Amount exceeds ₹10 crore maximum"
    for col in ['sender', 'description']:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(
                lambda x: bleach.clean(x, tags=[], strip=True)[:200])
    return True, ""

# Rate limiting: track requests per IP
REQUEST_LIMIT_WINDOW = 60  # seconds
REQUEST_LIMIT_COUNT = 30  # requests per window
request_tracker = defaultdict(list)

def _cleanup_rate_limiter():
    while True:
        time.sleep(300)  # every 5 minutes
        now = time.time()
        stale_ips = [ip for ip, times in request_tracker.items()
                     if not any(now - t < REQUEST_LIMIT_WINDOW for t in times)]
        for ip in stale_ips:
            del request_tracker[ip]
        if stale_ips:
            logger.debug(f"[CLEANUP] Removed {len(stale_ips)} stale rate limit entries")

cleanup_thread = threading.Thread(target=_cleanup_rate_limiter, daemon=True)
cleanup_thread.start()

@app.before_request
def assign_request_id():
    """Assign a unique ID to each request for tracing."""
    req_id = request.headers.get('X-Request-Id') or str(uuid.uuid4())[:8]
    _request_id.set(req_id)
    g.request_id = req_id

@app.after_request
def add_request_id_header(response):
    """Add request ID to response headers."""
    response.headers['X-Request-Id'] = getattr(g, 'request_id', '-')
    return response

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter('paysentinel_requests_total',
    'Total API requests', ['endpoint', 'method', 'status'])
REQUEST_LATENCY = Histogram('paysentinel_request_duration_seconds',
    'API request latency', ['endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5])
ANOMALY_COUNT = Counter('paysentinel_anomalies_detected_total',
    'Total anomalies detected', ['risk_level'])
ANALYSIS_ROWS = Histogram('paysentinel_analysis_rows',
    'Rows per analysis', buckets=[1, 10, 50, 100, 500, 1000, 5000])
ACTIVE_MODELS = Gauge('paysentinel_cached_models',
    'Number of models in cache')

def track_metrics(f):
    """Decorator to track request latency and throughput."""
    @wraps(f)
    def tracked(*args, **kwargs):
        start = time.time()
        status = 200
        try:
            response = f(*args, **kwargs)
            if isinstance(response, tuple) and len(response) > 1:
                status = response[1]
            elif hasattr(response, 'status_code'):
                status = response.status_code
            return response
        except Exception:
            status = 500
            raise
        finally:
            REQUEST_LATENCY.labels(endpoint=request.path).observe(time.time() - start)
            REQUEST_COUNT.labels(endpoint=request.path, method=request.method, status=str(status)).inc()
    return tracked


def _rate_limit(f):
    """Decorator to enforce rate limiting per client IP."""
    @wraps(f)
    def rate_limited(*args, **kwargs):
        if app.testing:
            return f(*args, **kwargs)
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old entries outside the window
        request_tracker[client_ip] = [
            req_time for req_time in request_tracker[client_ip]
            if now - req_time < REQUEST_LIMIT_WINDOW
        ]
        
        # Check if limit exceeded
        if len(request_tracker[client_ip]) >= REQUEST_LIMIT_COUNT:
            ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
            logger.warning(f"Rate limit exceeded for ip_hash={ip_hash}")
            log_sec('RATE_LIMIT_HIT', request, severity='WARNING')
            return jsonify({"status": "error", "message": "Rate limit exceeded. Max 30 requests per minute."}), 429
        
        request_tracker[client_ip].append(now)
        return f(*args, **kwargs)
    return rate_limited


def _require_api_key(f):
    """Optional API key auth. If environment variable PAYSENTINEL_API_KEY is set,
    requests must provide the same key in `X-API-Key` header or `api_key` payload.
    If env var is not set, this decorator is a no-op for backward compatibility.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        required = os.environ.get("PAYSENTINEL_API_KEY")
        if not required:
            return f(*args, **kwargs)

        provided = None
        # Prefer header, fallback to JSON/form payload
        try:
            provided = request.headers.get("X-API-Key")
        except Exception:
            provided = None
        if not provided:
            payload = _request_payload()
            provided = payload.get("api_key") if isinstance(payload, dict) else None

        if provided != required:
            logger.warning(f"Unauthorized request from {request.remote_addr}")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return wrapped


def _json_error(message: str, status_code: int):
    return jsonify({"status": "error", "message": message}), status_code


@app.errorhandler(RequestEntityTooLarge)
def handle_payload_too_large(error):
    return _json_error("Upload exceeds the 10MB limit.", 413)


@app.errorhandler(429)
def handle_too_many_requests(error):
    return _json_error("Rate limit exceeded. Max 30 requests per minute.", 429)


@app.errorhandler(401)
def handle_unauthorized(error):
    return _json_error("Unauthorized", 401)


def _get_cache_key(merchant_name: str, contamination: float) -> str:
    """Generate a cache key for model persistence."""
    key_str = f"{merchant_name}_{contamination:.4f}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cached_detector(merchant_name: str, contamination: float) -> PaySentinelDetector | None:
    """Load detector from cache if available and fresh."""
    cache_key = _get_cache_key(merchant_name, contamination)
    cache_file = MODEL_CACHE_DIR / f"detector_{cache_key}.pkl"
    cache_meta = MODEL_CACHE_DIR / f"detector_{cache_key}.meta"
    
    if not cache_file.exists() or not cache_meta.exists():
        return None
    
    try:
        # Check cache TTL (1 hour)
        with open(cache_meta, "r") as f:
            meta = json.load(f)
            if time.time() - meta["timestamp"] > 3600:  # 1 hour TTL
                logger.info(f"Cache expired for {merchant_name}, contamination={contamination}")
                return None
        
        with open(cache_file, "rb") as f:
            detector = pickle.load(f)  # nosec B301
            logger.info(f"Loaded detector from cache: {merchant_name}, contamination={contamination}")
            return detector
    except Exception as e:
        logger.warning(f"Failed to load detector from cache: {e}")
        return None


def _save_detector_cache(detector: PaySentinelDetector, merchant_name: str, contamination: float) -> None:
    """Save detector to cache."""
    cache_key = _get_cache_key(merchant_name, contamination)
    cache_file = MODEL_CACHE_DIR / f"detector_{cache_key}.pkl"
    cache_meta = MODEL_CACHE_DIR / f"detector_{cache_key}.meta"
    
    try:
        if app.testing:
            logger.debug(f"Skipping detector cache save during tests: {merchant_name}, contamination={contamination}")
            return
        with open(cache_file, "wb") as f:
            pickle.dump(detector, f)  # nosec B301
        with open(cache_meta, "w") as f:
            json.dump({"timestamp": time.time(), "merchant": merchant_name, "contamination": contamination}, f)
        logger.info(f"Saved detector to cache: {merchant_name}, contamination={contamination}")
    except Exception as e:
        logger.warning(f"Skipping detector cache save: {e}")


def _validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """Validate file upload: size and MIME type."""
    if not uploaded_file:
        return False, "No file provided"
    
    if not uploaded_file.filename:
        return False, "File has no name"
    
    # Check file size (max 10MB)
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit"
    
    # Check MIME type
    allowed_mimes = {"text/csv", "application/csv", "text/plain"}
    if uploaded_file.content_type not in allowed_mimes and not uploaded_file.filename.endswith(".csv"):
        log_sec('BAD_FILE_UPLOAD', request, details=f'file={uploaded_file.filename} reason=Invalid type', severity='WARNING')
        return False, "Invalid file type. Only CSV files are accepted."
    
    return True, ""


def _parse_sensitivity(value: str | None) -> float:
    try:
        raw = str(value or "5%").strip().replace("%", "")
        return max(0.01, min(float(raw) / 100.0, 0.25))
    except Exception:
        return 0.05


def _normalize_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    if "timestamp" in data.columns:
        timestamps = pd.to_datetime(data["timestamp"], errors="coerce")
        if "date" not in data.columns:
            data["date"] = timestamps.dt.strftime("%Y-%m-%d")
        if "hour" not in data.columns:
            data["hour"] = timestamps.dt.hour.fillna(12).astype(int)

    if "date" not in data.columns:
        data["date"] = datetime.now().strftime("%Y-%m-%d")
    if "hour" not in data.columns:
        data["hour"] = 12
    if "amount" not in data.columns:
        raise ValueError("CSV must include an 'amount' column.")
    if "sender" not in data.columns:
        data["sender"] = "unknown@upi"
    if "description" not in data.columns:
        data["description"] = "Transaction"

    data["date"] = pd.to_datetime(data["date"], errors="coerce").fillna(
        pd.Timestamp.now()
    ).dt.strftime("%Y-%m-%d")
    data["hour"] = pd.to_numeric(data["hour"], errors="coerce").fillna(12).astype(int)
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)

    if "transaction_id" not in data.columns:
        data["transaction_id"] = [f"TXN-{i:05d}" for i in range(len(data))]
    if "timestamp" not in data.columns:
        data["timestamp"] = (
            pd.to_datetime(data["date"], errors="coerce")
            + pd.to_timedelta(data["hour"], unit="h")
        ).dt.strftime("%Y-%m-%dT%H:%M:%S")

    return data.reset_index(drop=True)


def _request_payload() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict(flat=True)


def _request_value(name: str, default: str) -> str:
    payload = _request_payload()
    value = payload.get(name, default)
    if value in (None, ""):
        return default
    return str(value)


def _read_dataframe_from_request() -> tuple[pd.DataFrame, str]:
    payload = _request_payload()

    if request.is_json:
        if "rows" in payload:
            rows = payload.get("rows") or []
            frame = pd.DataFrame(rows)
            if frame.empty:
                return frame, "sample"
            return _normalize_input_dataframe(frame), "sample"

    uploaded = request.files.get("file")
    if uploaded and uploaded.filename:
        # Validate file upload
        is_valid, error_msg = _validate_file_upload(uploaded)
        if not is_valid:
            raise ValueError(f"File validation failed: {error_msg}")
        try:
            df = pd.read_csv(uploaded)
            valid, err = deep_validate_csv(df)
            if not valid:
                log_sec('DEEP_VAL_FAILED', request, details=f'reason={err}', severity='WARNING')
                raise ValueError(err)
            logger.info(f"Uploaded file: {uploaded.filename}, rows: {len(df)}")
            return _normalize_input_dataframe(df), uploaded.filename
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

    merchant_name = _request_value("merchant_name", "My UPI Store")
    return _normalize_input_dataframe(
        generate_merchant_transactions(merchant_name=merchant_name)
    ), "sample"


def _json_records(df: pd.DataFrame, limit: int | None = None) -> list[dict]:
    frame = df.copy()
    if limit is not None:
        frame = frame.head(limit)
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records", date_format="iso"))


def _build_timeline(results: pd.DataFrame) -> list[dict]:
    if "date" not in results.columns:
        return []
    timeline = (
        results.assign(date=pd.to_datetime(results["date"], errors="coerce"))
        .dropna(subset=["date"])
        .assign(date=lambda frame: frame["date"].dt.strftime("%Y-%m-%d"))
        .groupby("date", as_index=False)
        .agg(total=("amount", "size"), suspicious=("is_anomaly", "sum"), amount=("amount", "sum"))
        .sort_values("date")
    )
    return timeline.to_dict(orient="records")


def _build_heatmap(results: pd.DataFrame) -> list[list[int]]:
    grid = [[0 for _ in range(24)] for _ in range(7)]
    if "date" not in results.columns or "hour" not in results.columns:
        return grid

    dates = pd.to_datetime(results["date"], errors="coerce")
    hours = pd.to_numeric(results["hour"], errors="coerce").fillna(0).astype(int)
    for idx, date_value in enumerate(dates):
        if pd.isna(date_value):
            continue
        day = int(date_value.dayofweek)
        hour = int(hours.iloc[idx]) if idx < len(hours) else 0
        hour = max(0, min(23, hour))
        grid[day][hour] += int(results.iloc[idx].get("is_anomaly", 0))
    return grid


def _risk_summary(detector: PaySentinelDetector, results: pd.DataFrame) -> dict:
    anomalies = results[results["is_anomaly"] == 1]
    score, label, color = detector.calculate_resilience_score(results)
    return {
        "total": int(len(results)),
        "suspicious": int(len(anomalies)),
        "safe": int(len(results) - len(anomalies)),
        "at_risk_amount": float(anomalies["amount"].sum()) if len(anomalies) else 0.0,
        "suspicious_ratio": round((len(anomalies) / len(results) * 100) if len(results) else 0, 1),
        "resilience_score": int(score),
        "resilience_label": label,
        "resilience_color": color,
    }


def _alert_texts(row: pd.Series, count: int, language: str) -> dict:
    amount = float(row.get("amount", 0))
    hour = int(row.get("hour", 0))
    risk = str(row.get("risk_level", "HIGH"))
    amount_text = f"₹{amount:,.0f}"

    if language.lower() in {"kannada", "ಕನ್ನಡ", "kn"}:
        summary = f"{count} ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ ಪತ್ತೆ. ವರದಿಯನ್ನು ಪರಿಶೀಲಿಸಿ."
        alert = f"ಎಚ್ಚರಿಕೆ! {amount_text} ಮೊತ್ತದ {risk.lower()} ಅಪಾಯದ ವ್ಯವಹಾರ {hour}:00ಕ್ಕೆ ಪತ್ತೆಯಾಗಿದೆ."
    elif language.lower() in {"hindi", "हिन्दी", "hi"}:
        summary = f"{count} संदिग्ध लेनदेन पाए गए। कृपया समीक्षा करें।"
        alert = f"चेतावनी! {amount_text} का {risk.lower()} जोखिम लेनदेन {hour}:00 बजे पाया गया।"
    else:
        summary = f"{count} suspicious transactions detected. Please review the report."
        alert = f"Warning. A {risk.lower()} risk transaction of {amount_text} was detected at {hour}:00."

    return {"summary": summary, "alert": alert}


def _run_analysis(df: pd.DataFrame, merchant_name: str, sensitivity: str, language: str) -> dict:
    if df is None or df.empty:
        raise ValueError("No transaction rows were provided. Upload a CSV or load sample data first.")

    contamination = _parse_sensitivity(sensitivity)
    
    # Try to load cached detector first
    detector = _get_cached_detector(merchant_name, contamination)
    
    # If no cached detector, create and cache a new one
    if detector is None:
        logger.info(f"Training new detector for {merchant_name}, contamination={contamination}")
        detector = PaySentinelDetector(contamination=contamination)
        detector.fit(df)
        _save_detector_cache(detector, merchant_name, contamination)
    else:
        logger.info(f"Using cached detector for {merchant_name}, contamination={contamination}")
    
    results = detector.predict(df)

    summary = _risk_summary(detector, results)
    anomalies = results[results["is_anomaly"] == 1].sort_values("anomaly_score", ascending=False)
    top_row = anomalies.iloc[0] if len(anomalies) else results.iloc[0]
    explanation = []
    if len(results) > 0:
        try:
            explanation_index = int(anomalies.index[0]) if len(anomalies) else 0
            explanation = detector.explain(df, min(explanation_index, len(df) - 1))
        except Exception:
            explanation = []

    display_columns = [
        column
        for column in [
            "transaction_id",
            "date",
            "hour",
            "amount",
            "sender",
            "description",
            "is_anomaly",
            "anomaly_score",
            "risk_level",
        ]
        if column in results.columns
    ]

    payload = {
        "merchant_name": merchant_name,
        "language": language,
        "contamination": contamination,
        "summary": summary,
        "fingerprint": detector.fp,
        "top_transaction": _json_records(pd.DataFrame([top_row]), limit=1)[0],
        "alert_text": _alert_texts(top_row, summary["suspicious"], language),
        "anomalies": _json_records(anomalies, limit=12),
        "results_preview": _json_records(results[display_columns], limit=50) if display_columns else [],
        "timeline": _build_timeline(results),
        "heatmap": _build_heatmap(results),
        "explanation": explanation,
        "risk_table_columns": display_columns,
        "report_rows": len(results),
    }

    if hasattr(detector, 'model_card') and detector.model_card:
        payload["model_card"] = detector.model_card.to_dict()

    return payload, detector, results


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/dashboard")
@app.get("/dashboard.html")
def dashboard():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.get("/api/metrics")
@track_metrics
def metrics():
    """
    Expose Prometheus metrics for production monitoring.
    ---
    tags: [utility]
    responses:
      200:
        description: Standard Prometheus text format
    """
    ACTIVE_MODELS.set(len(list(MODEL_CACHE_DIR.glob("*.pkl"))))
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.get('/api/health')
def health():
    """Detailed health check for load balancers and monitoring."""
    process = psutil.Process()
    memory = process.memory_info()
    cache_files = list(MODEL_CACHE_DIR.glob('*.pkl'))

    status = {
        "status": "ok",
        "app": "PaySentinel",
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - app._start_time),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Only add detailed info for non-production or internal calls
    if request.headers.get('X-Internal-Check') == 'true':
        status.update({
            "memory_mb": round(memory.rss / 1024 / 1024, 1),
            "cpu_percent": round(process.cpu_percent(interval=0.1), 1),
            "cached_models": len(cache_files),
            "rate_limit_ips_tracked": len(request_tracker),
            "log_file_size_kb": round(
                (LOG_DIR / "paysentinel.log").stat().st_size / 1024, 1
            ) if (LOG_DIR / "paysentinel.log").exists() else 0,
        })

    return jsonify(status)


@app.get('/api/status')
def status_page():
    """Public status endpoint — safe to expose."""
    cache_files = list(MODEL_CACHE_DIR.glob('*.pkl'))
    return jsonify({
        "status": "operational",
        "services": {
            "api": "up",
            "ml_engine": "up",
            "model_cache": f"{len(cache_files)} models cached",
            "voice_alerts": "up",
        },
        "metrics": {
            "uptime_seconds": round(time.time() - app._start_time),
            "version": "2.0.0",
        },
        "languages_supported": ["Kannada", "Hindi", "English", "Tamil", "Telugu"],
        "fraud_patterns": 20,
        "feature_count": 45,
    })


@app.get("/api/sample-data")
@track_metrics
@_rate_limit
@_require_api_key
def sample_data():
    """
    Generate synthetic merchant transaction data for testing.
    ---
    tags: [utility]
    security: [ApiKey: []]
    parameters:
      - name: merchant_name
        in: query
        type: string
        default: "My UPI Store"
    responses:
      200:
        description: Synthetic transaction dataset
    """
    try:
        merchant_name = request.args.get("merchant_name", "My UPI Store")
        logger.info(f"[SAMPLE-DATA] merchant={merchant_name}, ip={request.remote_addr}")
        
        df = _normalize_input_dataframe(generate_merchant_transactions(merchant_name=merchant_name))
        
        logger.debug(f"[SAMPLE-DATA] Generated {len(df)} sample transactions")
        
        return jsonify(
            {
                "merchant_name": merchant_name,
                "rows": len(df),
                "columns": list(df.columns),
                "data": _json_records(df, limit=12),
            }
        )
    except Exception as exc:
        logger.error(f"[SAMPLE-DATA] ERROR - {str(exc)}", exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.post("/api/analyze")
@track_metrics
@_rate_limit
@_require_api_key
def analyze():
    """
    Run fraud detection analysis on UPI transactions.
    ---
    tags: [analysis]
    security: [ApiKey: []]
    consumes: [application/json, multipart/form-data]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            merchant_name: {type: string, example: "Manjunath Kirana Store"}
            language: {type: string, enum: [English, Kannada, Hindi], default: English}
            sensitivity: {type: string, example: "5%"}
            rows: {type: array, items: {type: object}}
    responses:
      200:
        description: Analysis results with fraud alerts
      400:
        description: Invalid input
      429:
        description: Rate limit exceeded
    """
    try:
        merchant_name = sanitize_merchant_name(_request_value("merchant_name", "My UPI Store"))
        language = sanitize_language(_request_value("language", "English"))
        sensitivity = _request_value("sensitivity", "5%")
        
        logger.info(f"[ANALYZE] START - merchant={merchant_name}, sensitivity={sensitivity}, language={language}, ip={request.remote_addr}")
        
        df, source = _read_dataframe_from_request()
        logger.debug(f"[ANALYZE] Data loaded - source={source}, rows={len(df)}")
        
        payload, detector, results = _run_analysis(df, merchant_name, sensitivity, language)
        payload["source"] = source
        
        # Record metrics
        ANALYSIS_ROWS.observe(len(df))
        if results is not None:
            for rl in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                count = (results['risk_level'] == rl).sum()
                if count > 0:
                    ANOMALY_COUNT.labels(risk_level=rl).inc(count)
        
        payload["request_id"] = g.request_id
        logger.info(f"[ANALYZE] SUCCESS - merchant={merchant_name}, rows={len(df)}, ip={request.remote_addr}")
        return jsonify(payload)
    except Exception as exc:
        logger.error(f"[ANALYZE] ERROR - {str(exc)}, ip={request.remote_addr}", exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.post("/api/report")
@track_metrics
@_rate_limit
@_require_api_key
def report():
    """
    Generate a Forensic PDF Fraud Certificate.
    ---
    tags: [reporting]
    security: [ApiKey: []]
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            merchant_name: {type: string}
            rows: {type: array, items: {type: object}}
    responses:
      200:
        description: PDF file stream
        content:
          application/pdf:
            schema: {type: string, format: binary}
    """
    try:
        merchant_name = sanitize_merchant_name(_request_value("merchant_name", "My UPI Store"))
        language = sanitize_language(_request_value("language", "English"))
        sensitivity = _request_value("sensitivity", "5%")
        
        logger.info(f"[REPORT] START - merchant={merchant_name}, sensitivity={sensitivity}, language={language}, ip={request.remote_addr}")
        
        df, _ = _read_dataframe_from_request()
        logger.debug(f"[REPORT] Data loaded - rows={len(df)}")
        
        payload, detector, results = _run_analysis(df, merchant_name, sensitivity, language)
        pdf_bytes = make_pdf(merchant_name, results, detector.fp)
        filename = f"paysentinel_{merchant_name.replace(' ', '_')}.pdf"
        
        logger.info(f"[REPORT] SUCCESS - merchant={merchant_name}, rows={len(df)}, pdf_size={len(pdf_bytes)} bytes, ip={request.remote_addr}")
        
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
    except Exception as exc:
        logger.error(f"[REPORT] ERROR - {str(exc)}, ip={request.remote_addr}", exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 400




@app.get("/api/stream")
@track_metrics
@_rate_limit
def stream():
    """
    Live UPI transaction simulation via Server-Sent Events (SSE).
    ---
    tags: [streaming]
    parameters:
      - name: merchant
        in: query
        type: string
        default: "My UPI Store"
    responses:
      200:
        description: Infinite text/event-stream of transaction JSON
    """
    merchant = request.args.get('merchant', 'My UPI Store')
    
    def generate():
        senders_normal = [
            'priya@okaxis','suresh@oksbi','kavitha@ybl','rajesh@okicici',
            'anita@okaxis','vikram@oksbi','divya@ybl','amit@okaxis'
        ]
        senders_fraud = ['unknown99@ybl','temp_acc@okaxis','structural@okicici',
                         'bot_3829@upi','anon_tx@ybl']
        descriptions_normal = ['Groceries','Vegetables','Milk','Rice','Snacks','Payment']
        counter = 5000

        while True:
            is_fraud = random.random() < 0.06
            hour = random.choice([0,1,2,3,23] if is_fraud else list(range(8,22)))
            amount = (random.uniform(6000,18000) if is_fraud
                      else random.uniform(20, 1800))
            sender = random.choice(senders_fraud if is_fraud else senders_normal)
            txn = {
                'transaction_id': f'TXN-LIVE-{counter:05d}',
                'amount': round(amount, 2),
                'hour': hour,
                'sender': sender,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Suspicious Transfer' if is_fraud else random.choice(descriptions_normal),
                'timestamp': datetime.now().isoformat(),
                'merchant': merchant
            }
            counter += 1
            yield f"data: {json.dumps(txn)}\n\n"
            time.sleep(random.uniform(0.8, 2.5))

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Access-Control-Allow-Origin': '*',
            'Connection': 'keep-alive'
        }
    )


@app.post("/api/explain")
@_rate_limit
def explain_fraud():
    """Plain-language fraud explanation using rule-based engine.
    Optionally powered by Anthropic API if ANTHROPIC_API_KEY is set."""
    try:
        payload = _request_payload()
        language = str(payload.get('language', 'English'))
        if language not in ('English', 'Kannada', 'Hindi'): language = 'English'
        question = str(payload.get('question', ''))[:300].strip()
        ctx = payload.get('context', {}) or {}
        
        amount = float(ctx.get('amount', 0))
        score = float(ctx.get('score', 0))
        risk = str(ctx.get('risk_level', 'UNKNOWN'))
        hour = int(ctx.get('hour', 0))
        sender = str(ctx.get('sender', 'Unknown'))[:60]
        flags = ctx.get('flags', []) or []
        fp = ctx.get('fp', {}) or {}

        # Build rule-based explanation (always available)
        flag_text = '. '.join(flags[:2]) if flags else 'Statistical outlier detected.'
        time_note = f"Transaction arrived at {hour}:00" + (
            " — outside your normal hours." if hour < int(fp.get('hour_min',8))
            or hour > int(fp.get('hour_max',21)) else ".")

        explanations = {
            'English': (
                f"This ₹{amount:,.0f} transaction scored {score:.0f}/100 risk. "
                f"{flag_text} {time_note} "
                f"{'Recommend: Contact your bank immediately.' if score > 75 else 'Monitor this transaction.'}"
            ),
            'Kannada': (
                f"₹{amount:,.0f} ಮೊತ್ತದ ವ್ಯವಹಾರ {score:.0f}/100 ಅಪಾಯ ಅಂಕ ಪಡೆದಿದೆ. "
                f"{'ತಕ್ಷಣ ನಿಮ್ಮ ಬ್ಯಾಂಕ್ಗೆ ಸಂಪರ್ಕಿಸಿ.' if score > 75 else 'ಈ ವ್ಯವಹಾರವನ್ನು ಗಮನಿಸಿ.'}"
            ),
            'Hindi': (
                f"₹{amount:,.0f} का यह लेनदेन {score:.0f}/100 जोखिम स्कोर है। "
                f"{flag_text} "
                f"{'तुरंत अपने बैंक से संपर्क करें।' if score > 75 else 'इस लेनदेन पर नज़र रखें।'}"
            )
        }

        result = {'explanation': explanations.get(language, explanations['English']),
                  'source': 'rule-based', 'risk_score': score}

        # If Anthropic key available, upgrade to Claude
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key and question:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                lang_instr = {
                    'Kannada': 'Reply ONLY in Kannada script. Simple language for a 45-year-old shopkeeper.',
                    'Hindi': 'Reply ONLY in Hindi. Simple language for a 45-year-old shopkeeper.',
                    'English': 'Reply in simple English. No technical jargon. Target: small shop owner.'
                }.get(language, 'Reply in simple English.')
                
                msg = client.messages.create(
                    model='claude-3-sonnet-20240229',
                    max_tokens=150,
                    system=f"""You are PaySentinel fraud assistant for Indian merchants.
{lang_instr}
Transaction: ₹{amount:,.0f}, Score: {score:.0f}/100, Level: {risk}, Hour: {hour}:00
Sender: {sender}. Flags: {'. '.join(flags[:2])}
Rules: under 60 words, no technical terms, end with action Yes/No/Maybe""",
                    messages=[{'role':'user','content': question or 'Explain this transaction'}]
                )
                result['explanation'] = msg.content[0].text
                result['source'] = 'claude'
            except Exception as ai_err:
                logger.warning(f"[EXPLAIN] Claude failed, using rule-based: {ai_err}")

        logger.info(f"[EXPLAIN] source={result['source']}, lang={language}, score={score}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"[EXPLAIN] ERROR: {e}", exc_info=True)
        return jsonify({'error': str(e), 'explanation': 'Explanation unavailable.'}), 400


@app.post('/api/voice')
@_rate_limit
def voice_endpoint():
    """Generate localized voice alert HTML for a specific transaction."""
    try:
        payload = _request_payload()
        amount = float(payload.get('amount', 0))
        hour = int(payload.get('hour', 0))
        risk = str(payload.get('risk', 'HIGH'))
        language = sanitize_language(str(payload.get('language', 'English')))
        
        # Generate the voice alert HTML with embedded audio
        html = _voice_alert_html(amount, hour, risk=risk, language=language, autoplay=False)
        
        logger.info(f"[VOICE] Generated {language} alert for ₹{amount}")
        return jsonify({'html': html, 'language': language})
    except Exception as e:
        logger.error(f"[VOICE] ERROR: {e}")
        return jsonify({'error': str(e)}), 400


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)  # nosec B201

