<div align="center">
  <img src="https://img.icons8.com/color/96/000000/shield.png" width="80" alt="Shield Icon"/>
  <h1>🛡️ PaySentinel</h1>
  <p><b>AI-powered real-time UPI fraud detection for local merchants</b></p>
  <p>
    <img src="https://img.shields.io/badge/BLUEPRINT-2026-0fc98f?style=for-the-badge&logo=hackaday&logoColor=white" alt="Blueprint 2026 Hackathon" />
    <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
    <img src="https://img.shields.io/badge/Language-English%20%7C%20%E0%B2%95%E0%B2%A8%E0%B3%8D%E0%B2%A8%E0%B2%A1-e24b4a?style=for-the-badge" alt="Bilingual" />
  </p>
</div>

---

## 🚀 The Vision
Small business owners and Kirana stores in India are increasingly targeted by UPI spoofing apps and late-night transaction fraud. Existing bank alerts are often delayed, entirely in English, and lack context. 

**PaySentinel** is a highly accessible, ML-driven shield designed to protect local merchants. It learns their exact historical behavior ("merchant fingerprinting"), detects anomalies instantly, and—crucially—delivers **audio fraud alerts in regional languages (Kannada)**.

---

## ✨ Key Features (Judging Criteria Aligned)

### 🧠 1. Explainable AI (XAI)
We don't just say "Fraud" — we prove it.
- **Model:** Isolation Forests (Unsupervised Learning) chosen specifically to handle highly imbalanced fraud datasets without relying on labeled data.
- **Explainability:** Integrated **SHAP values** graph mathematically proves *why* a transaction was flagged (e.g., unusual amount + strange time + new sender).

### 🗣️ 2. Regional Voice Alerts (Human 20%)
Accessibility is our core strength. 
- Using `gTTS`, the app generates real-time audio warnings.
- Currently supports **English** and **Kannada (ಕನ್ನಡ)**. 
- *Targeting 6.5 Crore Kannada speakers.*

### 🎨 3. Premium "Stark Tech" UI (Votes 60%)
- Built entirely in Streamlit but injected with custom cinematic CSS.
- **Dark Mode:** Deep space backgrounds (`#07070f`), WhatsApp-style interactive alert bubbles.
- **Interactive Dashboards:** 60-day visual timelines, daily volume bars, and geographical/hourly heatmaps built with Plotly.

### 📄 4. Audit Reporting
- Instantly generates downloadable bilingual PDF reports for the merchant to hand natively to their bank.
- Highlights the **1930 Cyber Crime Helpline**.

---

## 🛠️ Project Architecture

| Component | Status | Description |
|-----------|--------|-------------|
| 🎲 `generate_data.py` | ✅ **Complete** | Injects 10 complex fraud patterns into synthetic merchant data. |
| 🧠 `model.py` | ✅ **Complete** | The Isolation Forest & SHAP engine. |
| 🔊 `voice_alerts.py` | ✅ **Complete** | Generates the actual Kannada/English base64 audio. |
| 📄 `pdf_report.py` | ✅ **Complete** | PDF rendering using `fpdf2`. |
| 💻 `app.py` | ✅ **Complete** | The core 5-tab Streamlit dashboard linking everything together. |

---

## 🚧 Future Enhancements (In Progress)

This hackathon build is the MVP. To take this to production, the following pipeline upgrades are currently in active development:

1. **🔥 Firebase Integration:**
   - Shifting from local session-state handling to live Firebase Authentication & Firestore.
   - This will allow multi-merchant sign-in and persistent historical fraud logs across devices.

2. **⚡ Apache Kafka Streaming:**
   - Replacing the "CSV Upload" batch process with a live **Kafka data stream**.
   - Simulating real-time incoming UPI webhook pings, allowing the model to predict and ring the voice alert the exact second a transaction hits.

3. **🌍 Multilingual Expansion:**
   - Adding pipeline support for Tamil, Telugu, Malayalam, and Hindi.

---

## 💻 Tech Stack
- **Dashboard:** Streamlit, Custom CSS
- **Machine Learning:** Scikit-Learn (Isolation Forest), SHAP
- **Data Engineering:** Pandas, Numpy
- **Visuals:** Plotly
- **Audio & Docs:** gTTS, fpdf2

---

## 🏁 Quickstart

To run the application locally:
```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Run the application (forcing Streamlit module launch safely)
python -m streamlit run app.py
```
> *Open `http://localhost:8501` to view your dashboard!*

---
<div align="center">
  <i>Built for Blueprint 2026 🚀</i>
</div>
