# PaySentinel — System Architecture

## High-Level Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     PaySentinel Platform                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  Landing  │    │  Dashboard   │    │  Mobile Responsive    │  │
│  │  Page     │    │  Command     │    │  Navigation           │  │
│  │  (WebGL)  │    │  Center      │    │                       │  │
│  └─────┬────┘    └──────┬───────┘    └───────────┬───────────┘  │
│        │                │                         │              │
│  ══════╪════════════════╪═════════════════════════╪══════════    │
│        │         Flask REST API Layer             │              │
│  ══════╪════════════════╪═════════════════════════╪══════════    │
│        │                │                         │              │
│  ┌─────┴────┐    ┌──────┴───────┐    ┌───────────┴───────────┐  │
│  │ /api/    │    │ /api/        │    │ /api/                 │  │
│  │ health   │    │ analyze      │    │ voice, explain,       │  │
│  │ status   │    │ report       │    │ stream, sample-data   │  │
│  └──────────┘    └──────┬───────┘    └───────────────────────┘  │
│                         │                                        │
│  ════════════════ ML Pipeline ═══════════════════════════════    │
│                         │                                        │
│  ┌──────────────────────┴────────────────────────────────────┐  │
│  │              Feature Engineering (11 features)             │  │
│  │  velocity · amount_ratio · mahalanobis · sender_diversity  │  │
│  │  txn_burst · time_gap_zscore · cross_merchant_risk         │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────┐ ┌─────────┴──┐ ┌──────────┐ ┌─────────────────┐  │
│  │Isolation │ │ OneClass   │ │  Local   │ │ Rule-Based      │  │
│  │Forest    │ │ SVM        │ │ Outlier  │ │ Heuristics      │  │
│  │  (35%)   │ │  (35%)     │ │  (20%)   │ │  (10%)          │  │
│  └────┬─────┘ └─────┬──────┘ └────┬─────┘ └───────┬─────────┘  │
│       └──────────────┴─────────────┴───────────────┘             │
│                         │                                        │
│              Weighted Ensemble Score (0-100)                     │
│                         │                                        │
│  ┌──────────┐    ┌──────┴───────┐    ┌───────────────────────┐  │
│  │  SHAP    │    │  Voice       │    │  PDF Report           │  │
│  │  Explain │    │  Alert       │    │  + QR Certificates    │  │
│  │          │    │  (5 langs)   │    │                       │  │
│  └──────────┘    └──────────────┘    └───────────────────────┘  │
│                                                                  │
│  ════════════════ Streaming (Optional) ══════════════════════    │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  Kafka   │    │  Kafka       │    │  SSE Live             │  │
│  │ Producer │───▶│  Consumer    │───▶│  Dashboard Feed       │  │
│  └──────────┘    └──────────────┘    └───────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Landing page (WebGL) | Public |
| GET | `/dashboard` | Merchant command center | Public |
| GET | `/api/health` | System health + psutil metrics | Public |
| GET | `/api/status` | Operational status | Public |
| GET | `/api/sample-data` | Load 610 synthetic transactions | Public |
| POST | `/api/analyze` | Run ML ensemble on CSV/JSON | Rate-limited |
| POST | `/api/report` | Generate forensic PDF | Rate-limited |
| GET | `/api/stream` | SSE live transaction feed | Rate-limited |
| POST | `/api/explain` | AI fraud explanation | Rate-limited |
| POST | `/api/voice` | Generate voice alert HTML | Rate-limited |

## ML Ensemble Weights

| Model | Weight | Purpose |
|-------|--------|---------|
| IsolationForest | 35% | Tree-based outlier detection |
| OneClassSVM | 35% | Boundary-based novelty detection |
| LocalOutlierFactor | 20% | Density-based local anomalies |
| Rule-based Heuristics | 10% | Domain-specific fraud patterns |

## Voice Alert Pipeline

```
Transaction Flagged → Select Language Template
                        ├─ Kannada (kn)
                        ├─ Hindi (hi)
                        ├─ Tamil (ta)
                        ├─ Telugu (te)
                        └─ English (en)
                    → Try gTTS (online, 2 retries)
                        ├─ Success → MP3 → Base64 → HTML <audio>
                        └─ Fail → pyttsx3 offline → WAV → Base64 → HTML <audio>
```

## Deployment

```
Production: Dockerfile → Gunicorn (gevent) → Nginx reverse proxy
Streaming:  docker-compose.yml → App + Kafka + Zookeeper
CI/CD:      GitHub Actions → Lint → Test → ML Validate → Security → Docker Build
```
