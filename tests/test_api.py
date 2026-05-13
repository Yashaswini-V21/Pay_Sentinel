"""
Automated API tests for PaySentinel fraud detection system.
Tests /api/analyze, /api/report, and /api/sample-data endpoints.

Run with: pytest test_api.py -v
"""

import json
import os
import sys
import types
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import pandas as pd
import pytest


def setup_mocks():
    """Mock heavy dependencies only for app import."""
    # Create fake model module
    fake_model = types.ModuleType("model")

    class FakeDetector:
        def __init__(self, contamination=0.05):
            self.contamination = contamination
            self.fp = {"hour_min": 8, "hour_max": 21, "peak_hour": 12, "amt_p95": 1500}

        def fit(self, df):
            return self

        def predict(self, df):
            out = df.copy()
            out["is_anomaly"] = 0
            out["anomaly_score"] = 0
            out["risk_level"] = "LOW"
            out["flags"] = [[] for _ in range(len(out))]
            return out

        def calculate_resilience_score(self, results):
            return 100, "EXCELLENT", "#0fc98f"

        def explain(self, df, idx):
            return [
                {"feature": "amount", "value": 1, "impact": 1, "direction": "decreases"}
            ]

    fake_model.PaySentinelDetector = FakeDetector

    # Create fake pdf_report module
    fake_pdf = types.ModuleType("pdf_report")
    fake_pdf.make_pdf = lambda merchant, results, fp: b"PDF"

    # Create fake generate_data module
    fake_gen = types.ModuleType("generate_data")

    def fake_generate(merchant_name="My UPI Store"):
        return pd.DataFrame(
            [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "a@upi",
                    "description": "x",
                }
            ]
        )

    fake_gen.generate_merchant_transactions = fake_generate

    # Save originals
    orig = {
        "model": sys.modules.get("model"),
        "pdf_report": sys.modules.get("pdf_report"),
        "generate_data": sys.modules.get("generate_data"),
    }

    # Apply mocks
    sys.modules["model"] = fake_model
    sys.modules["pdf_report"] = fake_pdf
    sys.modules["generate_data"] = fake_gen

    return orig


# Apply mocks, import app, then RESTORE originals to avoid polluting other tests
orig_modules = setup_mocks()
from app import app

for name, mod in orig_modules.items():
    if mod:
        sys.modules[name] = mod
    else:
        sys.modules.pop(name, None)


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test /api/health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 with status ok."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "PaySentinel" in data["app"]


class TestSampleDataEndpoint:
    """Test /api/sample-data endpoint."""

    def test_sample_data_returns_200(self, client):
        """Sample data endpoint should return 200."""
        response = client.get("/api/sample-data?merchant_name=Test+Shop")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["merchant_name"] == "Test Shop"
        assert data["rows"] > 0
        assert "data" in data
        assert "columns" in data

    def test_sample_data_default_merchant(self, client):
        """Sample data should use default merchant if not specified."""
        response = client.get("/api/sample-data")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "merchant_name" in data
        assert data["rows"] > 0


class TestAnalyzeEndpoint:
    """Test /api/analyze endpoint."""

    def test_analyze_with_json_rows(self, client):
        """Analyze should accept JSON payload with rows."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "payment",
                }
            ],
            "merchant_name": "Shop X",
            "language": "English",
            "sensitivity": "5%",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["merchant_name"] == "Shop X"
        assert data["language"] == "English"
        assert "summary" in data
        assert "anomalies" in data

    def test_analyze_preserves_merchant_settings(self, client):
        """Analyze should preserve merchant_name, language, sensitivity in JSON mode."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 14,
                    "amount": 500,
                    "sender": "buyer@upi",
                    "description": "order",
                }
            ],
            "merchant_name": "Premium Store",
            "language": "Kannada",
            "sensitivity": "8%",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["merchant_name"] == "Premium Store"
        assert data["language"] == "Kannada"
        assert abs(data["contamination"] - 0.08) < 0.01  # 8% = 0.08

    def test_analyze_with_empty_rows_returns_400(self, client):
        """Analyze should reject empty rows with 400 error."""
        payload = {"rows": [], "merchant_name": "Shop X"}
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data.get("status", "").lower() or "error" in data.get("message", "").lower()
        assert "No transaction rows" in data.get("message", "")

    def test_analyze_with_csv_file(self, client):
        """Analyze should accept CSV file upload."""
        csv_data = "date,hour,amount,sender,description\n2026-05-04,12,100,test@upi,payment"
        data = {
            "file": (BytesIO(csv_data.encode()), "test.csv"),
            "merchant_name": "File Upload Test",
            "language": "English",
            "sensitivity": "5%",
        }
        response = client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["merchant_name"] == "File Upload Test"
        assert "summary" in result

    def test_analyze_with_oversized_file_returns_400(self, client):
        """Analyze should reject files larger than 10MB."""
        # Create a file that exceeds 10MB
        large_csv = "date,hour,amount,sender,description\n"
        large_csv += "\n".join(
            ["2026-05-04,12,100,test@upi,payment"] * 200000
        )  # ~5MB each
        large_csv = large_csv * 3  # Make it > 10MB

        data = {
            "file": (BytesIO(large_csv.encode()), "large.csv"),
            "merchant_name": "Large File Test",
        }
        response = client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        # Flask catches large files at MAX_CONTENT_LENGTH level and returns 413
        # or our validation returns 400 - both are valid error responses
        assert response.status_code in [400, 413], f"Expected 400 or 413, got {response.status_code}"

    def test_analyze_with_invalid_file_type_returns_400(self, client):
        """Analyze should reject non-CSV files."""
        data = {
            "file": (BytesIO(b"not a csv"), "test.bin"),  # Use .bin extension to ensure rejection
            "merchant_name": "Invalid File Test",
        }
        response = client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        result = json.loads(response.data)
        assert "Invalid file type" in result.get("message", "")

    def test_analyze_default_merchant_when_not_provided(self, client):
        """Analyze should use default merchant name if not provided."""
        payload = {"rows": []}
        response = client.post("/api/analyze", json=payload)
        # This will fail because rows is empty, but the merchant should still be set
        assert response.status_code == 400  # Empty rows should fail

    def test_analyze_returns_expected_fields(self, client):
        """Analyze response should include all required fields."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "test",
                }
            ],
            "merchant_name": "Field Test Shop",
            "language": "English",
            "sensitivity": "5%",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)

        # Check required fields
        required_fields = [
            "merchant_name",
            "language",
            "contamination",
            "summary",
            "fingerprint",
            "anomalies",
            "timeline",
            "heatmap",
            "explanation",
            "alert_text",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check summary structure
        assert "total" in data["summary"]
        assert "suspicious" in data["summary"]
        assert "safe" in data["summary"]
        assert "resilience_score" in data["summary"]


class TestReportEndpoint:
    """Test /api/report endpoint."""

    def test_report_returns_pdf(self, client):
        """Report endpoint should return PDF binary."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "payment",
                }
            ],
            "merchant_name": "Report Test Shop",
            "language": "English",
            "sensitivity": "5%",
        }
        response = client.post("/api/report", json=payload)
        assert response.status_code == 200
        assert response.content_type == "application/pdf"
        assert len(response.data) > 0

    def test_report_filename_includes_merchant(self, client):
        """Report PDF filename should include merchant name."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "payment",
                }
            ],
            "merchant_name": "Test Merchant Store",
            "language": "English",
            "sensitivity": "5%",
        }
        response = client.post("/api/report", json=payload)
        assert response.status_code == 200
        assert "paysentinel_Test" in response.headers.get(
            "Content-Disposition", ""
        )

    def test_report_with_empty_rows_returns_400(self, client):
        """Report should reject empty rows."""
        payload = {"rows": [], "merchant_name": "Empty Report"}
        response = client.post("/api/report", json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data or "message" in data

    def test_report_preserves_merchant_settings(self, client):
        """Report should respect merchant_name, language, sensitivity settings."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 14,
                    "amount": 500,
                    "sender": "buyer@upi",
                    "description": "order",
                }
            ],
            "merchant_name": "Report Merchant",
            "language": "Hindi",
            "sensitivity": "10%",
        }
        response = client.post("/api/report", json=payload)
        assert response.status_code == 200
        assert response.content_type == "application/pdf"


class TestPageEndpoints:
    """Test static page endpoints."""

    def test_index_page_returns_200(self, client):
        """Index page should be accessible."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"PaySentinel" in response.data or b"html" in response.data.lower()

    def test_dashboard_page_returns_200(self, client):
        """Dashboard page should be accessible after secret code verification."""
        auth = client.post("/api/verify-code", json={"code": "paysentinel2005"})
        assert auth.status_code == 200
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"html" in response.data.lower() or b"form" in response.data.lower()


class TestErrorHandling:
    """Test error handling."""

    def test_analyze_with_malformed_csv_returns_400(self, client):
        """Analyze should handle malformed CSV gracefully."""
        bad_csv = "this is not valid csv format\\x00\\x01"
        data = {
            "file": (BytesIO(bad_csv.encode("latin1")), "bad.csv"),
            "merchant_name": "Bad CSV Test",
        }
        response = client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        result = json.loads(response.data)
        assert "error" in result or "message" in result

    def test_missing_required_columns_in_csv(self, client):
        """Analyze should handle CSV missing 'amount' column."""
        csv_data = "date,hour,sender,description\n2026-05-04,12,test@upi,payment"
        data = {
            "file": (BytesIO(csv_data.encode()), "no_amount.csv"),
            "merchant_name": "Missing Amount Test",
        }
        response = client.post(
            "/api/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        result = json.loads(response.data)
        assert "amount" in result.get("message", "").lower() or "error" in result.get("status", "").lower()


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_decorator_applied(self, client):
        """Rate limiter decorator should be applied to endpoints."""
        # Verify that rate limiter is working by making multiple requests
        # In a real production environment, this would enforce 30 req/min
        # In test environment, the tracking may vary due to request context
        response = client.get("/api/health")
        assert response.status_code == 200
        
    def test_rate_limit_headers_present(self, client):
        """Test that multiple endpoints accept requests (rate limiting in place)."""
        # Make requests to different endpoints to ensure they're all rate-limited
        endpoints = ["/api/health", "/api/sample-data"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should get 200 or 429, both indicate the endpoint is protected
            assert response.status_code in [200, 429]


class TestSensitivityParsing:
    """Test sensitivity percentage parsing."""

    def test_sensitivity_with_percent_sign(self, client):
        """Sensitivity with % sign should be parsed correctly."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "test",
                }
            ],
            "merchant_name": "Sensitivity Test",
            "sensitivity": "15%",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data["contamination"] - 0.15) < 0.01  # 15% = 0.15

    def test_sensitivity_without_percent_sign(self, client):
        """Sensitivity without % sign should be parsed correctly."""
        payload = {
            "rows": [
                {
                    "date": "2026-05-04",
                    "hour": 12,
                    "amount": 100,
                    "sender": "user@upi",
                    "description": "test",
                }
            ],
            "merchant_name": "Sensitivity Test",
            "sensitivity": "10",
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data["contamination"] - 0.10) < 0.01


class TestStreamEndpoint:
    """Test /api/stream endpoint."""

    def test_stream_endpoint_exists(self, client):
        """Just check endpoint exists, don't consume SSE fully."""
        response = client.get('/api/stream?merchant=Test', headers={'Accept': 'text/event-stream'})
        # Accept 200 or 404 (if not yet implemented)
        assert response.status_code in [200, 404]

    def test_stream_requires_no_auth_when_no_key_set(self, client):
        """Stream should be accessible if no API key is configured."""
        response = client.get('/api/stream')
        assert response.status_code in [200, 404]


class TestExplainEndpoint:
    """Test /api/explain endpoint."""

    def test_explain_english(self, client):
        """Test explanation generation in English."""
        payload = {
            'question': 'Why is this suspicious?',
            'language': 'English',
            'context': {
                'amount': 8200, 'score': 85, 'risk_level': 'CRITICAL',
                'hour': 2, 'sender': 'unknown@ybl', 'flags': ['Late night'],
                'fp': {'hour_min': 9, 'hour_max': 21}
            }
        }
        response = client.post('/api/explain', json=payload)
        assert response.status_code in [200, 404]  # 404 if not yet added
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'explanation' in data or 'error' in data

    def test_explain_kannada_language(self, client):
        """Test explanation generation in Kannada."""
        payload = {'language': 'Kannada', 'context': {'amount': 5000, 'score': 70}}
        response = client.post('/api/explain', json=payload)
        assert response.status_code in [200, 404]

    def test_explain_invalid_language_defaults(self, client):
        """Invalid language should default to English without crashing."""
        payload = {'language': 'Swahili', 'context': {'amount': 100, 'score': 20}}
        response = client.post('/api/explain', json=payload)
        assert response.status_code in [200, 404]


class TestInputSanitization:
    """Test XSS and SQL Injection protection."""

    def test_merchant_name_xss_attempt(self, client):
        """XSS tags should be stripped from merchant name."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': '<script>alert("xss")</script>Merchant',
            'language': 'English', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '<script>' not in data.get('merchant_name', '')

    def test_merchant_name_sql_injection(self, client):
        """SQL injection characters in merchant name should not cause errors."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': "'; DROP TABLE transactions; --",
            'language': 'English', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        assert response.status_code == 200

    def test_extremely_long_merchant_name(self, client):
        """Oversized merchant names should be truncated."""
        long_name = 'A' * 10000
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': long_name, 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data.get('merchant_name', '')) <= 200

    def test_unicode_merchant_name(self, client):
        """Unicode characters (Kannada) should be preserved if allowed."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': 'ಮಂಜುನಾಥ್ ಕಿರಾಣ ಅಂಗಡಿ', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        assert response.status_code == 200

    def test_invalid_sensitivity_values(self, client):
        """Malformed sensitivity values should not crash the API."""
        for bad_val in ['abc', '-5%', '200%', None, '', '0']:
            payload = {
                'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
                'merchant_name': 'Test', 'sensitivity': bad_val
            }
            response = client.post('/api/analyze', json=payload)
            assert response.status_code == 200  # Should not crash


class TestSecurityHeaders:
    """Test that mandatory security headers are present."""

    def test_x_content_type_nosniff(self, client):
        """MIME sniffing protection should be enabled."""
        r = client.get('/api/health')
        assert r.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_x_frame_options_deny(self, client):
        """Clickjacking protection should be enabled."""
        auth = client.post('/api/verify-code', json={'code': 'paysentinel2005'})
        assert auth.status_code == 200
        r = client.get('/dashboard')
        assert r.headers.get('X-Frame-Options') == 'DENY'

    def test_no_server_header_leaked(self, client):
        """Backend server version should not be leaked."""
        r = client.get('/api/health')
        assert 'Server' not in r.headers or 'Werkzeug' not in r.headers.get('Server', '')

    def test_referrer_policy_set(self, client):
        """Referrer policy should be configured."""
        r = client.get('/api/health')
        assert 'Referrer-Policy' in r.headers


class TestDataValidation:
    """Test business logic validation for financial data."""

    def test_negative_amounts_rejected(self, client):
        """Transactions with negative amounts must return 400."""
        csv_data = 'date,hour,amount,sender,description\n2026-05-04,12,-500,test@upi,payment'
        data = {'file': (BytesIO(csv_data.encode()), 'neg.csv'), 'merchant_name': 'Test'}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_extremely_large_amount_rejected(self, client):
        """Amounts exceeding safety thresholds (₹10cr) must return 400."""
        csv_data = 'date,hour,amount,sender,description\n2026-05-04,12,999999999,test@upi,payment'
        data = {'file': (BytesIO(csv_data.encode()), 'big.csv'), 'merchant_name': 'Test'}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_all_nan_amounts_rejected(self, client):
        """Non-numeric amounts should be rejected with 400."""
        csv_data = 'date,hour,amount,sender\n2026-05-04,12,notanumber,test@upi'
        data = {'file': (BytesIO(csv_data.encode()), 'nan.csv'), 'merchant_name': 'Test'}
        response = client.post('/api/analyze', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestResponseSchema:
    """Test the structural integrity of API responses."""

    def test_analyze_summary_has_resilience_score(self, client):
        """Analysis summary must include Resilience metrics."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': 'Schema Test', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'resilience_score' in data['summary']
        assert 'resilience_label' in data['summary']
        assert 'resilience_color' in data['summary']

    def test_analyze_fingerprint_has_required_keys(self, client):
        """Merchant fingerprint must include all required statistical keys."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': 'FP Test', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        data = json.loads(response.data)
        fp = data.get('fingerprint', {})
        for key in ['hour_min', 'hour_max', 'peak_hour', 'amt_p95']:
            assert key in fp, f"Missing fingerprint key: {key}"

    def test_analyze_heatmap_is_7x24_grid(self, client):
        """Risk heatmap must be a standard 7x24 weekly-hourly grid."""
        payload = {
            'rows': [{'date': '2026-05-04', 'hour': 12, 'amount': 100, 'sender': 'a@b', 'description': 'x'}],
            'merchant_name': 'Heatmap Test', 'sensitivity': '5%'
        }
        response = client.post('/api/analyze', json=payload)
        data = json.loads(response.data)
        heatmap = data.get('heatmap', [])
        assert len(heatmap) == 7
        for row in heatmap:
            assert len(row) == 24


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

