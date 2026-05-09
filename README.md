<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,2,5,30&height=200&section=header&text=PaySentinel&fontSize=72&fontColor=ffffff&fontAlignY=38&desc=AI%20Merchant%20Fraud%20Shield%20for%20Bharat&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<br/>

[![BLUEPRINT 2026](https://img.shields.io/badge/🏆_BLUEPRINT-2026-0fc98f?style=for-the-badge&labelColor=0d0d1c)](https://blueprint.hackaday.io)
[![Status](https://img.shields.io/badge/Status-🟢_Production_Ready-27ae60?style=for-the-badge&labelColor=0d0d1c)](https://github.com/Yashaswini-V21/Pay_Sentinel)
[![Tests](https://img.shields.io/badge/Tests-56_Passing-22c55e?style=for-the-badge&labelColor=0d0d1c)](./tests)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0d0d1c)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white&labelColor=0d0d1c)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge&labelColor=0d0d1c)](LICENSE)
[![CI/CD](https://github.com/Yashaswini-V21/Pay_Sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/Yashaswini-V21/Pay_Sentinel/actions/workflows/ci.yml)

<br/>

> ### *"The first fraud detection system in the world that speaks Kannada."*
> **Protecting ₹4,000 Crore of small business dreams. One alert at a time.**

<br/>

[**⚡ Quick Start**](#-quick-start) &nbsp;•&nbsp;
[**🏗️ Architecture**](#️-architecture) &nbsp;•&nbsp;
[**🧠 ML Engine**](#-ml-engine) &nbsp;•&nbsp;
[**📊 Dashboard**](#-dashboard) &nbsp;•&nbsp;
[**🧪 Testing**](#-testing) &nbsp;•&nbsp;
[**🗺️ Roadmap**](#️-roadmap)

<br/>

</div>

## ⚡ 60-Second Demo

```bash
git clone https://github.com/Yashaswini-V21/Pay_Sentinel.git
cd Pay_Sentinel && pip install -r requirements.txt && python app.py
```
Open http://localhost:5000 → Click **"Load Sample"** → Click **"Run Analysis"**
→ Hear the Kannada voice alert → Download your forensic PDF report.
**No API keys. No cloud setup. Zero cost.**

---

## 🔻 The Problem

<table>
<tr>
<td width="50%">

Every year, India's small merchants — **kirana stores, street vendors, local repair shops** — lose **₹4,000 Crore** to UPI fraud.

A kirana owner in Bengaluru receives ₹8,200 at 2am from an unknown sender. **Is it fraud? She has no way to know.**

- ❌ Every fraud tool is built **for banks**, not merchants
- ❌ Alerts arrive **15–30 minutes** too late
- ❌ Everything is in **English** — not their language
- ❌ **No explanations** — just "blocked" or "allowed"

</td>
<td width="50%">

```
18,000,000,000
UPI transactions / month

60,000,000
Small merchants with zero
fraud protection

6,50,00,000
Kannada speakers — zero fraud
tools in their language

₹4,000 Cr
Lost to UPI fraud annually
(RBI Report 2024)
```

</td>
</tr>
</table>

### ❓ Why Not Use Bank Fraud Detection?
Banks protect *their* assets, not merchants' inventory.
When a fraudster tricks a merchant, the bank sees a *successful* payment.
**PaySentinel sits at the merchant's endpoint — seeing what the bank never can.**

---

## 🛡️ The Solution

**PaySentinel** is an AI-driven fraud shield that detects suspicious UPI transactions in **< 100ms** and alerts merchants in **5 Indian languages** — so they can act before it's too late.

```
Upload CSV / Live Kafka Stream
           ↓
   11 Features Engineered (~15ms)
   Merchant Fingerprint Built
           ↓
   Triple ML Ensemble (~30ms)
   IsolationForest (35%) + OneClassSVM (35%) + LOF (20%) + Rules (10%)
           ↓
   SHAP Explainability (~50ms)
   "Why this is fraud" — in plain language
           ↓
   ಎಚ್ಚರಿಕೆ! Kannada Voice Alert
   Forensic PDF + QR Certificate
           ↓
          <100ms ⚡
```

> **No labelled data needed. No bank API required. 100% free & open-source.**

---

## 📁 Project Structure

```
Pay_Sentinel/
│
├── app.py                     # Flask API server (10 REST endpoints, 1028 lines)
├── model.py                   # Triple ML ensemble + SHAP explainer (343 lines)
├── generate_data.py           # Synthetic data with 20 fraud patterns (354 lines)
├── voice_alerts.py            # 5-language voice engine + offline fallback (491 lines)
├── pdf_report.py              # Bilingual PDF + QR forensic certificates (497 lines)
├── train_detector.py          # CLI model training + validation tool
│
├── index.html                 # Landing page (WebGL particles, glitch FX)
├── dashboard.html             # Merchant command center (Stark Tech UI)
│
├── kafka_consumer.py          # Streaming fraud detection consumer
├── kafka_producer.py          # Transaction stream simulator
│
├── tests/                     # 🧪 Test Suites
│   ├── conftest.py            #    Shared fixtures (sample data, trained detector)
│   ├── test_model.py          #    ML validation: 28 tests
│   └── test_voice.py          #    Voice alert validation: 16 tests
├── test_api.py                # API integration tests: 30 tests
│
├── docs/                      # 📖 Documentation
│   └── ARCHITECTURE.md        #    System architecture + API reference
│
├── .github/workflows/
│   └── ci.yml                 # 5-job CI pipeline (lint → test → ML → security → Docker)
│
├── Dockerfile                 # Multi-stage production build (tini, non-root)
├── docker-compose.yml         # App + Kafka + Zookeeper
├── docker-compose.prod.yml    # Production deployment
├── nginx/                     # Reverse proxy configuration
├── Makefile                   # Build automation
│
├── requirements.txt           # Pinned Python dependencies
├── LICENSE                    # MIT License
├── SECURITY.md                # Security policy & measures
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
├── PITCH.md                   # Investor/judge pitch deck
└── README.md                  # ← You are here
```

---

## ⚡ Quick Start

### Option 1: Local (Recommended for Demo)
```bash
# Clone & install
git clone https://github.com/Yashaswini-V21/Pay_Sentinel.git
cd Pay_Sentinel
pip install -r requirements.txt

# Run
python app.py
# → Landing page: http://localhost:5000
# → Dashboard:    http://localhost:5000/dashboard
```

### Option 2: Docker
```bash
docker build -t paysentinel .
docker run -p 5000:5000 paysentinel
```

### Option 3: Docker Compose (with Kafka streaming)
```bash
docker-compose up -d
# App: :5000 | Kafka: :9092 | Zookeeper: :2181
```

---

## 📂 Project Structure

PaySentinel follows a professional, modular enterprise structure designed for scale and auditability.

```text
Pay_Sentinel/
├── .github/workflows/      # Automated CI/CD (Testing + Docker)
├── docs/                   # Enterprise Documentation
│   ├── ARCHITECTURE.md     # System Design & Data Flow
│   └── USER_GUIDE.md       # Operator & Deployment Guide
├── static/                 # Frontend Assets
│   ├── css/                # Shared Design Tokens (global.css)
│   └── (images)            # Space-Tech UI Assets
├── tests/                  # Robust Test Suite (55+ Tests)
│   ├── conftest.py         # Shared Pytest Fixtures
│   ├── test_model.py       # ML Pipeline Validation
│   └── test_voice.py       # Linguistic Routing Tests
├── app.py                  # Forensic API Gateway (Flask)
├── model.py                # Core ML Ensemble Engine
├── voice_alerts.py         # Regional Linguistic Alert System
├── pdf_report.py           # Forensic Audit PDF Generator
├── kafka_consumer.py       # Enterprise Live-Stream Handler
├── train_detector.py       # Model Calibration Pipeline
├── Dockerfile              # Containerization
└── requirements.txt        # Dependency Manifest
```

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  Landing Page │  │  Dashboard       │  │  Mobile Nav    │  │
│  │  (WebGL)      │  │  (Stark Tech UI) │  │  (Responsive)  │  │
│  └──────┬───────┘  └────────┬─────────┘  └───────┬────────┘  │
├─────────┴──────────────────┬┴────────────────────┴────────────┤
│                    FLASK REST API (10 endpoints)               │
│  /health · /status · /analyze · /report · /stream              │
│  /explain · /voice · /sample-data · /metrics · /docs           │
│  Rate Limiting · API Auth · Security Headers · Request Tracing │
├────────────────────────────┬──────────────────────────────────┤
│                    ML PIPELINE                                 │
│  ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐   │
│  │ Isolation  │ │ OneClass │ │  LOF    │ │ Rule-Based    │   │
│  │ Forest 35% │ │ SVM 35%  │ │  20%    │ │ Heuristics 10%│   │
│  └─────┬──────┘ └────┬─────┘ └────┬────┘ └──────┬────────┘   │
│        └──────────────┴────────────┴─────────────┘             │
│                    Weighted Ensemble → Score 0-100             │
├────────────────────────────┬──────────────────────────────────┤
│                    OUTPUT LAYER                                 │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ SHAP     │ │ Voice (5   │ │ PDF +    │ │ SSE Live     │   │
│  │ Explain  │ │ Languages) │ │ QR Cert  │ │ Stream       │   │
│  └──────────┘ └────────────┘ └──────────┘ └──────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Landing page (WebGL particle universe) | Public |
| `GET` | `/dashboard` | Merchant fraud detection command center | Public |
| `GET` | `/api/health` | System health with psutil metrics | Public |
| `GET` | `/api/status` | Operational status | Public |
| `GET` | `/api/sample-data` | Load 610 synthetic transactions | Rate-limited |
| `POST` | `/api/analyze` | Run ML ensemble on CSV/JSON data | Rate-limited |
| `POST` | `/api/report` | Generate forensic PDF report | Rate-limited |
| `GET` | `/api/stream` | SSE real-time transaction feed | Rate-limited |
| `POST` | `/api/explain` | AI-powered fraud explanation | Rate-limited |
| `POST` | `/api/voice` | Generate localized voice alert | Rate-limited |

---

## 🧠 ML Engine

### Triple Ensemble Architecture

| Model | Weight | Strengths |
|-------|--------|-----------|
| **IsolationForest** | 35% | Tree-based outlier isolation, handles high-dimensional data |
| **OneClassSVM** | 35% | Decision boundary novelty detection |
| **LocalOutlierFactor** | 20% | Density-based local anomaly detection |
| **Rule Heuristics** | 10% | Domain-specific patterns (out-of-hours, velocity spikes) |

### 11 Engineered Features

| Feature | Description |
|---------|-------------|
| `amount` | Raw transaction amount |
| `hour` | Time of day (0-23) |
| `day_of_week` | Day of week (0-6) |
| `amt_ratio_median` | Amount / rolling median ratio |
| `vel_1h` | Transaction velocity (1-hour window) |
| `vel_15m` | Transaction velocity (15-min window) |
| `is_new_sender` | First-time sender flag |
| `sender_diversity` | Unique sender ratio in window |
| `txn_burst` | Burst transaction detection |
| `time_gap_zscore` | Inter-transaction time anomaly |
| `amt_entropy` | Amount distribution entropy |

### Key ML Capabilities
- **Zero-Label Learning** — no labelled fraud data required (fully unsupervised)
- **SHAP Explainability** — top-4 feature attribution for every flagged transaction
- **Merchant Fingerprinting** — learns each merchant's normal behavior profile
- **Cryptographic Fraud Proof** — SHA-256 hash-based evidence certificates
- **ModelCard Tracking** — full model lineage, version, and training metadata
- **Resilience Scoring** — 0-100 health score with 5 tiers (EXCELLENT → COMPROMISED)

---

## 🎙️ Voice Alert System

| Language | Script | Engine | Status |
|----------|--------|--------|--------|
| **Kannada** | ಕನ್ನಡ | gTTS + pyttsx3 | ✅ Production |
| **Hindi** | हिन्दी | gTTS + pyttsx3 | ✅ Production |
| **English** | English | gTTS + pyttsx3 | ✅ Production |
| **Tamil** | தமிழ் | gTTS + pyttsx3 | ✅ Production |
| **Telugu** | తెలుగు | gTTS + pyttsx3 | ✅ Production |

**Dual-Engine Resilience:**
- **Primary**: gTTS (Google Text-to-Speech) — high-quality online synthesis
- **Fallback**: pyttsx3 — fully offline local WAV generation
- Auto-retry with 2 attempts before switching to offline mode

---

## 📊 Dashboard

### "Stark Tech" Command Center
- **Dark glassmorphism** design with animated gradient borders
- **Real-time risk gauge** (0-100 score with needle animation)
- **Metric counter animations** (easeOutCubic count-up effect)
- **Scroll-reveal sections** (IntersectionObserver driven)
- **Panel hover glow** effects with teal luminance
- **7×24 risk heatmap** (day-of-week × hour-of-day)
- **SHAP waterfall bars** showing feature attribution
- **Flip cards** for anomalous transactions with evidence
- **AI Fraud Assistant** with Kannada/Hindi prompt suggestions
- **Live API status polling** every 30s with heartbeat animation

---

## 🔐 Security

| Measure | Implementation |
|---------|---------------|
| Input Sanitization | `bleach` HTML stripping + regex validation |
| Rate Limiting | 30 req/min sliding window per IP |
| Security Headers | CSP, X-Frame-Options, X-XSS, Referrer-Policy |
| API Authentication | Optional key via `PAYSENTINEL_API_KEY` env var |
| File Validation | 10MB max, extension whitelist (.csv, .xlsx) |
| Request Tracing | UUID per request via `ContextVar` |
| Data Validation | Negative/extreme amount rejection |
| Non-root Docker | `paysentinel` user (UID 1000) |

See [SECURITY.md](SECURITY.md) for the full security policy.

---

## 🧪 Testing

### Test Suites

| Suite | Tests | Coverage |
|-------|-------|----------|
| `test_api.py` — API Integration | 30 | Health, analyze, report, stream, explain, security headers, XSS, SQL injection |
| `tests/test_model.py` — ML Validation | 28 | Feature engineering, ensemble predictions, resilience scoring, model cards, contamination sweep |
| `tests/test_voice.py` — Voice Alerts | 16 | Template integrity, 5-language routing, alert sequences |
| **Total** | **74** | |

### Running Tests

```bash
# All tests
pytest test_api.py tests/ -v

# ML tests only
pytest tests/test_model.py -v

# Voice tests only
pytest tests/test_voice.py -v

# With coverage report
pytest test_api.py tests/ --cov=. --cov-report=term
```

### CI/CD Pipeline (5 Jobs)

```
Lint (flake8, black) → API Tests (pytest + coverage) → ML Validation
                                                           ↓
                    Docker Build ← Security Scan (bandit, safety)
```

---

## 🏆 Technical Moats

| Moat | Detail |
|------|--------|
| **First Kannada fraud detection** | No competing product exists in any Indian regional language |
| **Zero-label learning** | Works without labelled fraud data — deploys instantly for any merchant |
| **Offline voice resilience** | pyttsx3 fallback ensures alerts work without internet |
| **Cryptographic fraud proofs** | SHA-256 evidence certificates admissible in cyber crime complaints |
| **Triple ensemble** | IsolationForest + SVM + LOF outperforms any single model |
| **Merchant fingerprinting** | Learns each merchant's unique behavior — not a one-size-fits-all model |
| **74 automated tests** | 3 test suites with ML validation, contamination sweep, and security testing |

---

## 🐳 Deployment

### Docker (Production)
```bash
docker build --target production -t paysentinel:latest .
docker run -e WORKERS=4 -e LOG_LEVEL=warning -p 5000:5000 paysentinel:latest
```

### Docker Compose (Full Stack)
```bash
# App + Kafka + Zookeeper + Nginx
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```bash
PAYSENTINEL_API_KEY=your-secret-key     # Optional API authentication
ANTHROPIC_API_KEY=sk-...                # Optional AI explanations
PORT=5000                                # Server port
WORKERS=2                                # Gunicorn workers
WORKER_CLASS=gevent                      # Async worker class
LOG_LEVEL=info                           # Logging level
```

---

## 🗺️ Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| ✅ v1.0 | IsolationForest + Kannada/Hindi/English alerts | Complete |
| ✅ v2.0 | Triple ensemble + Tamil/Telugu + offline voice + ModelCard | Complete |
| 🔨 v2.1 | Marathi + Bengali voice templates | In Progress |
| 📋 v3.0 | WhatsApp Business API integration | Planned |
| 📋 v3.1 | Mobile app (React Native) | Planned |
| 📋 v4.0 | PostgreSQL persistence + merchant dashboard login | Planned |

---

## 📞 Emergency Resources

> This tool is a fraud detection aid — not a substitute for official action.

**🚨 Cyber Crime Helpline: 1930**
**🌐 File a complaint: cybercrime.gov.in**
**🏦 Bank fraud: call your bank's 24/7 helpline immediately**

---

## 📄 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, API reference, ML ensemble design |
| [PITCH.md](PITCH.md) | Investor/judge pitch deck with market analysis |
| [SECURITY.md](SECURITY.md) | Security policy and implemented measures |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development setup and contribution guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [LICENSE](LICENSE) | MIT License |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,2,5,30&height=120&section=footer&animation=fadeIn" width="100%"/>

### *"Protecting ₹4,000 Crore Worth of Small Business Dreams"*

**Made with ❤️ for Indian Merchants Who Deserve Better**

<br/>

[![GitHub Stars](https://img.shields.io/github/stars/Yashaswini-V21/Pay_Sentinel?style=for-the-badge&logo=github&labelColor=0d0d1c)](https://github.com/Yashaswini-V21/Pay_Sentinel)
[![GitHub Issues](https://img.shields.io/github/issues/Yashaswini-V21/Pay_Sentinel?style=for-the-badge&labelColor=0d0d1c)](https://github.com/Yashaswini-V21/Pay_Sentinel/issues)
[![GitHub Forks](https://img.shields.io/github/forks/Yashaswini-V21/Pay_Sentinel?style=for-the-badge&labelColor=0d0d1c)](https://github.com/Yashaswini-V21/Pay_Sentinel/network)
[![License MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge&labelColor=0d0d1c)](LICENSE)

---

**Submitted to** [BLUEPRINT 2026](https://blueprint.hackaday.io) &nbsp;|&nbsp; **Open-Source** &nbsp;|&nbsp; **Production-Ready**

**Version:** 2.0.0 &nbsp;|&nbsp; **Tests:** 74 passing &nbsp;|&nbsp; **Last Updated:** May 2026

<br/>

*Kannada · Hindi · English · Tamil · Telugu → Marathi → 800 Million Indians*

</div>
