# Changelog

All notable changes to PaySentinel are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] — 2026-05-09

### Added
- Triple ML ensemble (IsolationForest + OneClassSVM + LOF) with weighted scoring
- ModelCard dataclass for model lineage tracking
- SHAP KernelExplainer for top-4 feature attribution
- pyttsx3 offline voice fallback when gTTS/internet unavailable
- Tamil and Telugu voice alert templates
- `/api/health` with real-time psutil system metrics
- `/api/status` public operational status endpoint
- Dashboard premium animation system (entrance, hover, scroll-reveal, counter)
- Intersection Observer scroll-reveal for dashboard sections
- CLI arguments for `train_detector.py` (--merchant, --contamination, --validate)
- Comprehensive ML validation test suite (`tests/test_model.py`)
- Voice alert test suite (`tests/test_voice.py`)
- SECURITY.md, CONTRIBUTING.md, CHANGELOG.md
- MIT LICENSE file

### Changed
- Upgraded from single IsolationForest to triple-model ensemble
- Dashboard status pill now polls `/api/status` every 30s
- README completely rewritten with architecture diagrams
- PITCH.md updated with Technical Moats section and validated metrics
- Hardened voice alert retry logic (2 attempts before offline fallback)

### Fixed
- Kannada label typo in voice_alerts.py cached-audio path
- argparse help string percent sign escaping in train_detector.py

## [1.0.0] — 2026-05-03

### Added
- Initial Flask + HTML5 architecture
- IsolationForest anomaly detection
- Kannada + English + Hindi voice alerts via gTTS
- Forensic PDF reports with QR code certificates
- Apache Kafka streaming pipeline
- CI/CD pipeline via GitHub Actions
- Docker multi-stage build with tini
- 23+ API test cases with pytest
