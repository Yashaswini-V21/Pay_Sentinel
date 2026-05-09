# PaySentinel — User & Operator Guide

## 🚀 Quick Deployment

PaySentinel is designed for zero-friction deployment in a variety of environments.

### 1. Docker (Recommended)
The fastest way to get a production-ready instance:
```bash
docker build -t paysentinel:v2 .
docker run -p 5000:5000 paysentinel:v2
```

### 2. Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the detection server
python app.py
```

## 🧠 Using the Dashboard

### Data Ingestion
- **Forensic CSV**: Upload a CSV containing transaction logs. The system will automatically parse 45+ features.
- **Kafka Stream**: For live deployments, point your Kafka producers to the `/api/ingest` endpoint or use the `kafka_consumer.py`.

### Understanding Risk Scores
- **LOW (Green)**: High confidence in transaction legitimacy.
- **MEDIUM (Yellow)**: Anomalous behavior detected. SHAP evidence will show why (e.g., unusual hour).
- **HIGH (Red)**: Critical threat detected. Isolation Forest and SVM have reached consensus on fraud.

### Regional Voice Alerts
In the **Linguistic Shield** panel, toggle between Kannada, Hindi, and English. The system will announce high-risk transactions instantly.

## 🛡️ Forensic Reports
Every analysis generates a **QR-coded PDF Audit Report**. These reports are designed to be presented to local law enforcement (Cyber Crime Cell) as technical evidence.

---
*PaySentinel — Built for the next billion digital merchants.*
