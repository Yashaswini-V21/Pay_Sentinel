# PaySentinel 🛡️

> AI-powered UPI fraud detection for small merchants.
> Explains every suspicious transaction in **Kannada** and **English**.

**HackPulse 2026 Submission | 40% Complete (2/5 files)**

---

## 📊 Build Status

| Component | Status | Details |
|-----------|--------|---------|
| ✅ `generate_data.py` | **COMPLETE** | 654 synthetic transactions, 10 fraud patterns injected |
| ✅ `model.py` | **COMPLETE** | Isolation Forest + SHAP + Merchant Fingerprinting |
| ⏳ `voice_alerts.py` | **IN PROGRESS** | Kannada + English gTTS (next) |
| ⏳ `pdf_report.py` | **TO DO** | Bilingual PDF reports |
| ⏳ `app.py` | **TO DO** | 5-tab Streamlit dashboard |

---

## ✅ What's Done

### 1. generate_data.py
**Synthetic UPI Transaction Generator**
- Creates 60 days of realistic kirana store transactions
- **Output:** `data/sample_transactions.csv` (654 rows)
- **10 Fraud Patterns Injected:**
  - 3 late-night large amounts (₹6.7K-15K, 0-4 AM)
  - 2 structuring attacks (same sender, <₹5K, afternoon)
  - 1 mega transaction (₹45K, 11 AM)
  - 2 midnight transfers (₹3K-8K, 11 PM-midnight)
  - 2 very early morning (₹2K-7K, 1-4 AM)
- **No Setup Needed:** Fully self-contained

### 2. model.py
**Core Fraud Detection Engine**

**14 Engineered Features:**
```
amount, amount_log, hour
is_night, is_late_night, is_biz_hours, is_round, is_large, is_very_large
sender_freq, is_new_sender, is_known_bank
day_of_week, daily_sender_count
```

**Merchant Fingerprinting:**
- Learns each store's normal behavior (hours, amounts, senders)
- Baseline: 5th-95th percentile thresholds

**SHAP Explainability:**
- Top 4 feature importance per transaction
- Plain-language fraud reasons

**PaySentinelDetector Class:**
```python
detector = PaySentinelDetector()
detector.fit(df)  # Train on historical data
result = detector.predict(df_new)  # Detect anomalies
# Output: is_anomaly, anomaly_score, risk_level, flags
explainer = detector.explain(df, idx)  # SHAP importance
detector.save("models/detector.pkl")  # Persist
```

**Results:** 33 anomalies detected, 10 true fraud perfectly identified

---

## 🚧 To Build (In Order)

### 3. voice_alerts.py
Generate Kannada + English voice alerts using gTTS

**Functions Needed:**
- `generate_kannada_alert(fraud_msg, sender, amount)` → MP3
- `generate_english_alert(fraud_msg, sender, amount)` → MP3
- Handle special characters (₹ rupee symbol, numbers)
- Save to `data/alerts/`

**Example:**
- Kannada: "ಈ ಲೆಕ್ಕೆ ರಾತ್ರಿ 2 ಗಂಟೆಗೆ ಸುರಕ್ಷಿತವಲ್ಲ"
- English: "This transaction at 2 AM is not secure"

### 4. pdf_report.py
Generate bilingual PDF audit reports

**Sections:**
- Transaction summary with risk scores
- Fraud explanations (Kannada + English)
- Charts (timeline, risk distribution)
- Cyber Crime helpline: 1930
- Output: `data/reports/report_YYYY-MM-DD.pdf`

### 5. app.py
Streamlit 5-tab dark dashboard

**Tabs:**
1. **Upload & Analyze** — CSV upload, real-time detection
2. **Risk Dashboard** — Charts, statistics, heatmaps
3. **Anomaly Details** — Investigation view, sort by risk
4. **Voice Alerts** — Play Kannada/English, download MP3
5. **Settings** — Model info, fingerprint view

---

## 🛠 Tech Stack

```
Python 3.10+
streamlit==1.32.0          # Dashboard
pandas==2.1.0              # Data handling
numpy==1.24.0              # Numerical ops
scikit-learn==1.3.0        # IsolationForest
shap==0.43.0               # SHAP explainer
plotly==5.18.0             # Charts
fpdf2==2.7.6               # PDF generation
gTTS==2.5.1                # Kannada + English TTS
joblib==1.3.0              # Model save/load
```

**All tools are FREE. No API keys required.**

---

## 📁 Project Layout

```
Pay_Sentinel/
├── ✅ generate_data.py       # Synthetic transaction data
├── ✅ model.py               # Isolation Forest ML engine
├── ⏳ voice_alerts.py        # Kannada/English voice (next)
├── ⏳ pdf_report.py          # PDF generation
├── ⏳ app.py                 # Streamlit dashboard
├── requirements.txt
├── .gitignore
├── README.md
│
├── data/
│   ├── .gitkeep
│   └── sample_transactions.csv  (auto-generated)
│
└── models/
    ├── .gitkeep
    └── detector.pkl  (auto-generated)
```

---

## 🚀 To Run Current Version

```bash
# Install dependencies
pip install -r requirements.txt

# Generate data + train model
python model.py

# Output:
# ✅ 654 transactions generated (10 fraud injected)
# ✅ Model fitted on 654 transactions
# 💾 Saved: models/detector.pkl
```

---

## 🎯 Fraud Detection Examples

**CRITICAL (96.9% risk):**
- Time: 2 AM | Amount: ₹8,200 | Sender: unknown@ybl
- Flags: Unusual hour, new sender, after-midnight

**CRITICAL (100% risk):**
- Time: 3 AM | Amount: ₹14,867 | Sender: unknown1@ybl
- Flags: Unusual hour, top 1% amount, after-midnight

**CRITICAL (88.7% risk):**
- Time: 11 AM | Amount: ₹45,000 | Sender: bigpay@okicici
- Flags: Amount ₹45,000 is top 1% for your store

---

## 🌍 Kannada Language

PaySentinel speaks fraud alerts in ಕನ್ನಡ (Kannada) + English using gTTS.

Targeting 6.5 crore Kannada speakers. Roadmap: Tamil, Telugu, Malayalam, Hindi.

**Cyber Crime Helpline:** 1930 | cybercrime.gov.in

---

## 📝 Next Session

1. Build `voice_alerts.py` (Kannada/English gTTS)
2. Build `pdf_report.py` (bilingual reports)
3. Build `app.py` (Streamlit dashboard)
4. Test end-to-end integration
5. Deploy to HackPulse 2026

---

**Last Updated:** April 20, 2026  
**Progress:** 40% (2/5 core files complete)  
