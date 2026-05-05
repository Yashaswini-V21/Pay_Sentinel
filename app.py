from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import pickle
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from functools import wraps

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_file, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector
from pdf_report import make_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_CACHE_DIR = Path(BASE_DIR) / "models"
LOG_DIR = Path(BASE_DIR) / "logs"

# Create directories if they don't exist
MODEL_CACHE_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger("paysentinel")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"
)

file_handler = logging.FileHandler(LOG_DIR / "paysentinel.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Rate limiting: track requests per IP
REQUEST_LIMIT_WINDOW = 60  # seconds
REQUEST_LIMIT_COUNT = 30  # requests per window
request_tracker = defaultdict(list)


def _rate_limit(f):
    """Decorator to enforce rate limiting per client IP."""
    @wraps(f)
    def rate_limited(*args, **kwargs):
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old entries outside the window
        request_tracker[client_ip] = [
            req_time for req_time in request_tracker[client_ip]
            if now - req_time < REQUEST_LIMIT_WINDOW
        ]
        
        # Check if limit exceeded
        if len(request_tracker[client_ip]) >= REQUEST_LIMIT_COUNT:
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
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
            detector = pickle.load(f)
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
            pickle.dump(detector, f)
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
    return payload, detector, results


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/dashboard")
@app.get("/dashboard.html")
def dashboard():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "app": "PaySentinel HTML dashboard"})


@app.get("/api/sample-data")
@_rate_limit
@_require_api_key
def sample_data():
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
@_rate_limit
@_require_api_key
def analyze():
    start_time = time.time()
    try:
        merchant_name = _request_value("merchant_name", "My UPI Store")
        language = _request_value("language", "English")
        sensitivity = _request_value("sensitivity", "5%")
        
        logger.info(f"[ANALYZE] START - merchant={merchant_name}, sensitivity={sensitivity}, language={language}, ip={request.remote_addr}")
        
        df, source = _read_dataframe_from_request()
        logger.debug(f"[ANALYZE] Data loaded - source={source}, rows={len(df)}")
        
        payload, _, _ = _run_analysis(df, merchant_name, sensitivity, language)
        payload["source"] = source
        
        elapsed = time.time() - start_time
        logger.info(f"[ANALYZE] SUCCESS - merchant={merchant_name}, rows={len(df)}, time={elapsed:.2f}s, ip={request.remote_addr}")
        
        return jsonify(payload)
    except Exception as exc:
        elapsed = time.time() - start_time
        logger.error(f"[ANALYZE] ERROR - {str(exc)}, time={elapsed:.2f}s, ip={request.remote_addr}", exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.post("/api/report")
@_rate_limit
@_require_api_key
def report():
    start_time = time.time()
    try:
        merchant_name = _request_value("merchant_name", "My UPI Store")
        language = _request_value("language", "English")
        sensitivity = _request_value("sensitivity", "5%")
        
        logger.info(f"[REPORT] START - merchant={merchant_name}, sensitivity={sensitivity}, language={language}, ip={request.remote_addr}")
        
        df, _ = _read_dataframe_from_request()
        logger.debug(f"[REPORT] Data loaded - rows={len(df)}")
        
        payload, detector, results = _run_analysis(df, merchant_name, sensitivity, language)
        pdf_bytes = make_pdf(merchant_name, results, detector.fp)
        filename = f"paysentinel_{merchant_name.replace(' ', '_')}.pdf"
        
        elapsed = time.time() - start_time
        logger.info(f"[REPORT] SUCCESS - merchant={merchant_name}, rows={len(df)}, pdf_size={len(pdf_bytes)} bytes, time={elapsed:.2f}s, ip={request.remote_addr}")
        
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
    except Exception as exc:
        elapsed = time.time() - start_time
        logger.error(f"[REPORT] ERROR - {str(exc)}, time={elapsed:.2f}s, ip={request.remote_addr}", exc_info=True)
        return jsonify({"status": "error", "message": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
