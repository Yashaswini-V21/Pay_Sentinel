# PaySentinel - Project Structure

## Directory Organization

```
Pay_Sentinel/
├── backend/                          # Backend Python source code
│   └── src/
│       ├── app.py                   # Flask API gateway (main entry point)
│       ├── model.py                 # ML ensemble detector
│       ├── generate_data.py         # Synthetic data generator
│       ├── kafka_producer.py        # Kafka transaction producer
│       ├── kafka_consumer.py        # Real-time transaction consumer
│       ├── train_detector.py        # Model training script
│       ├── pdf_report.py            # Fraud certificate PDF generator
│       ├── voice_alerts.py          # Voice alert system (gTTS + pyttsx3)
│       └── __init__.py              # Package marker
│
├── frontend/                         # Web UI assets
│   ├── templates/                   # HTML templates (Jinja2)
│   │   ├── index.html              # Landing page
│   │   └── dashboard.html          # Merchant dashboard
│   └── static/                      # Static assets (served directly)
│       ├── css/
│       │   └── global.css          # Glassmorphic UI styles
│       ├── images/                  # Product images & backgrounds
│       │   ├── hero_shield.png     # Favicon
│       │   ├── space_bg.png        # Hero background
│       │   ├── splash_screen_bg.png
│       │   ├── roadmap.png
│       │   └── 1-6.jpg            # Screenshot tiles
│       └── openapi.json            # OpenAPI spec
│
├── tests/                            # Test suite (99 tests, organized)
│   ├── unit/                        # Unit tests (~70 tests)
│   │   ├── test_api.py             # Flask endpoint tests
│   │   ├── test_model.py           # ML model tests
│   │   └── test_voice.py           # Voice alert tests
│   ├── integration/                # Integration tests (~20 tests)
│   │   └── ml_validate.py          # End-to-end ML pipeline tests
│   ├── conftest.py                 # Shared pytest fixtures
│   └── __init__.py                 # Package marker
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md             # System design & diagrams
│   ├── DEPLOYMENT.md               # Hosting & deployment guide
│   ├── USER_GUIDE.md               # User manual & API reference
│   └── hackathon/
│       ├── PITCH.md                # Hackathon elevator pitch
│       └── JUDGE_EVALUATION_*.md   # Evaluation rubrics
│
├── data/                            # Data artifacts
│   ├── sample_transactions.csv     # Sample merchant data
│   └── alerts/                      # Generated alerts (CSV)
│
├── models/                          # Trained ML model cache
│   └── detector_*.meta             # Serialized model metadata
│
├── logs/                            # Application logs
│   └── paysentinel.log             # Rotating log file
│
├── nginx/                           # Web server config
│   └── nginx.conf                  # Reverse proxy configuration
│
├── Dockerfile                       # Multi-stage production image
├── docker-compose.yml              # Dev environment (Flask + Kafka)
├── docker-compose.prod.yml         # Prod environment (Gunicorn + Nginx)
├── Makefile                        # Build/test/deploy commands
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview & setup
├── SECURITY.md                     # Security policies
├── CONTRIBUTING.md                # Contribution guidelines
├── CHANGELOG.md                    # Version history
└── LICENSE                         # MIT License

```

## Key Configuration Files

| File | Purpose |
|------|---------|
| `backend/src/app.py` | Flask app with hardened auth, caching, logging |
| `tests/conftest.py` | Pytest fixtures for all tests |
| `Dockerfile` | Multi-stage build: builder → production (slim) |
| `docker-compose.yml` | Kafka + Zookeeper + Flask + Redis (dev) |
| `Makefile` | Commands: `make dev`, `make test`, `make prod` |
| `requirements.txt` | All Python dependencies (42 packages) |

## Python Import Paths

### From Repository Root
```python
from backend.src.app import app
from backend.src.model import PaySentinelDetector
from backend.src.generate_data import generate_merchant_transactions
```

### From Tests
```python
# conftest.py automatically adds backend/src to sys.path
from app import app
from model import PaySentinelDetector
from generate_data import generate_merchant_transactions
```

## Running the Project

### Local Development
```bash
cd backend/src
python app.py
# Or use Makefile:
make dev
```

### Running Tests
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# All tests
pytest tests/ -v

# With Makefile:
make test
make test-integration
```

### Docker Deployment
```bash
# Build image
make build

# Run dev environment (Kafka + Flask)
docker-compose up -d

# Run prod environment (Nginx + Gunicorn)
docker-compose -f docker-compose.prod.yml up -d
```

## Frontend Asset Serving

Flask serves static files from `frontend/static/`:
- CSS: `/static/css/global.css`
- Images: `/static/images/*.{png,jpg}`
- API Spec: `/static/openapi.json`

HTML templates from `frontend/templates/`:
- `/` → `index.html` (landing)
- `/dashboard` → `dashboard.html` (merchant UI)
- `/favicon.ico` → `hero_shield.png` (branding)

## Environment Variables

### Optional (Development)
```bash
FLASK_DEBUG=true          # Enable dev server reload
FLASK_ENV=development
```

### Recommended (Production)
```bash
PAYSENTINEL_API_KEY=your-key              # Enforce auth
PAYSENTINEL_MODEL_CACHE_KEY=your-key      # Sign model cache
PAYSENTINEL_ALLOWED_ORIGIN=https://domain # CORS origin
FLASK_DEBUG=false                          # Production mode
```

## Model Cache Management

Models are cached with HMAC signatures for integrity:
- Location: `models/detector_*.meta`
- Signing key: `PAYSENTINEL_MODEL_CACHE_KEY` (env var)
- Signature verified on load in `backend/src/app.py`

## Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`):
- ✅ Linting (flake8)
- ✅ 99 unit/integration tests
- ✅ ML pipeline validation
- ✅ Security checks (Bandit, safety)
- ✅ Docker build verification

## Status

- **99/99 tests passing** ✅
- **Enterprise hardening applied** ✅
- **Multi-stage Docker build** ✅
- **Kafka streaming ready** ✅
- **Production-grade logging** ✅

