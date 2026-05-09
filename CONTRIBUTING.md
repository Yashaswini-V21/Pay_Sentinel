# Contributing to PaySentinel

Thank you for your interest in contributing! PaySentinel protects Indian merchants from UPI fraud.

## Quick Start

```bash
git clone https://github.com/Yashaswini-V21/Pay_Sentinel.git
cd Pay_Sentinel
pip install -r requirements.txt
python app.py
```

## Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Run all tests
pytest test_api.py tests/ -v

# Run ML tests only
pytest tests/test_model.py -v

# Run with coverage
pytest test_api.py tests/ --cov=. --cov-report=term
```

## Project Structure

```
Pay_Sentinel/
├── app.py                 # Flask API server (10 endpoints)
├── model.py               # ML ensemble (IF + SVM + LOF)
├── generate_data.py       # Synthetic data with 20 fraud patterns
├── voice_alerts.py        # 5-language voice (gTTS + pyttsx3)
├── pdf_report.py          # Bilingual PDF + QR certificates
├── train_detector.py      # CLI model training tool
├── dashboard.html         # Merchant command center
├── index.html             # Landing page (WebGL)
├── kafka_consumer.py      # Streaming fraud detection
├── kafka_producer.py      # Transaction simulator
├── test_api.py            # API integration tests
├── tests/
│   ├── conftest.py        # Shared fixtures
│   ├── test_model.py      # ML validation (25+ tests)
│   └── test_voice.py      # Voice alert tests
├── docs/
│   └── ARCHITECTURE.md    # System architecture
├── .github/workflows/
│   └── ci.yml             # 5-job CI pipeline
├── Dockerfile             # Multi-stage production build
├── docker-compose.yml     # App + Kafka + Zookeeper
├── nginx/                 # Reverse proxy config
├── SECURITY.md            # Security policy
├── CHANGELOG.md           # Version history
└── PITCH.md               # Investor pitch deck
```

## Code Style
- Python: Follow PEP 8, max line length 120
- HTML/CSS: 2-space indentation
- Commit messages: `[module] Short description` (e.g., `[model] Add LOF to ensemble`)

## Adding a New Language
1. Add template dict in `voice_alerts.py` (follow `KN`/`EN` pattern)
2. Add language routing in `alert_html()` and `summary_html()`
3. Add test cases in `tests/test_voice.py`
4. Update README.md language table
