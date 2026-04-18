# PaySentinel 🛡️

> AI-powered UPI fraud detection for small merchants.
> Explains every suspicious transaction in **Kannada** and **English**.

[![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=flat)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Language](https://img.shields.io/badge/ಕನ್ನಡ-Kannada-orange?style=flat)](README.md)

---

## The Problem

A kirana store owner in Bengaluru receives ₹8,200 from an unknown
sender at 2am. Is it fraud? She has no way to know.

Every fraud tool is built for banks. PaySentinel is built for her.

---

## Features

| | Feature | What It Does |
|---|---|---|
| 🤖 | Isolation Forest | Unsupervised ML — no fraud labels needed |
| 👤 | Merchant Fingerprint | Learns YOUR normal hours and amounts |
| 🧠 | SHAP Explainability | Plain-language reason for every flag |
| 🔊 | Kannada Voice Alert | ಎಚ್ಚರಿಕೆ! — world-first fraud alert in Kannada |
| 📱 | WhatsApp UI | Familiar red/green alert bubbles |
| 📈 | Anomaly Timeline | 30-day chart with fraud markers |
| 📄 | PDF Report | Kannada advisory + helpline 1930 |

---

## Quick Start

```bash
git clone https://github.com/yourusername/pay-sentinel.git
cd pay-sentinel
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

---

## Project Structure

```text
pay-sentinel/
│
├── generate_data.py   # Creates 60-day synthetic merchant transactions
├── model.py           # Isolation Forest + SHAP + Merchant Fingerprint
├── voice_alerts.py    # Kannada + English gTTS voice alerts
├── pdf_report.py      # PDF with Kannada advisory section
├── app.py             # Streamlit 5-tab dashboard (main entry)
│
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/              # Auto-created by generate_data.py (gitignored)
│   └── sample_transactions.csv
│
└── models/            # Saved model after training (gitignored)
	└── detector.pk
```

---

## Tech Stack 

| Layer | Tool / Library | Purpose | Cost |
|---|---|---|---|
| Anomaly ML | scikit-learn IsolationForest | Core fraud detection — no labels needed | 
| Explainability | SHAP KernelExplainer | Why was this transaction flagged |
| Kannada voice | gTTS `lang='kn'` | Speaks Kannada alerts aloud |
| English voice | gTTS `lang='en'` | Speaks English alerts aloud |
| Dashboard UI | Streamlit | 5-tab interactive app 
| Charts | Plotly | Timeline, bar, heatmap charts 
| PDF report | fpdf2 | Kannada audit report generation 
| Data | Pandas + NumPy | Feature engineering + wrangling 
| Model save | joblib | Save trained model to disk |
| Deployment | Streamlit Cloud | Free public URL for Devpost 
| Repo | GitHub | Code hosting + submission link 

\* gTTS is free to use, but requires internet access for text-to-speech generation.

---

## Why Kannada?

6.5 crore Kannada speakers. Zero fraud tools in their language.
Roadmap: Tamil · Telugu · Malayalam · Hindi · Marathi → 800M Indians.

**Cyber Crime Helpline: 1930 | cybercrime.gov.in**

---
Built for HackPulse 2026 | MIT License
