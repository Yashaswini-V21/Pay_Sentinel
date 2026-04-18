from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector
from pdf_report import make_pdf
from voice_alerts import alert_html, summary_html

st.set_page_config(page_title="PaySentinel", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
    .stApp {
        background: radial-gradient(circle at 12% 20%, #0f172a 0%, #0b1220 35%, #05080f 100%);
        color: #edf2f7;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .stat-big {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .wa-wrap {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .wa-left, .wa-right {
        padding: 10px 12px;
        border-radius: 12px;
        max-width: 88%;
        font-size: 0.93rem;
        line-height: 1.3;
    }
    .wa-left {
        background: #1f2937;
        border: 1px solid #374151;
        align-self: flex-start;
    }
    .wa-right {
        background: #14532d;
        border: 1px solid #166534;
        align-self: flex-end;
    }
    .risk-chip {
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data():
    path = Path("data/sample_transactions.csv")
    if not path.exists():
        return generate_merchant_transactions()
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def load_detector(df):
    model_path = Path("models/detector.pkl")
    if model_path.exists():
        return PaySentinelDetector.load(str(model_path))
    detector = PaySentinelDetector().fit(df)
    detector.save(str(model_path))
    return detector


def ensure_datetime(df):
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out


def risk_color(risk):
    colors = {
        "CRITICAL": ("#7f1d1d", "#fecaca"),
        "HIGH": ("#7c2d12", "#fed7aa"),
        "MEDIUM": ("#78350f", "#fde68a"),
        "LOW": ("#064e3b", "#a7f3d0"),
    }
    bg, fg = colors.get(str(risk), ("#1f2937", "#e5e7eb"))
    return f"<span class='risk-chip' style='background:{bg};color:{fg}'>{risk}</span>"


def sidebar_controls(df):
    st.sidebar.title("Controls")
    merchant = st.sidebar.text_input("Merchant Name", value="Raju Kirana")
    min_amt, max_amt = float(df["amount"].min()), float(df["amount"].max())
    amt_range = st.sidebar.slider("Amount Range", min_amt, max_amt, (min_amt, max_amt))
    language = st.sidebar.radio("Voice Language", ["English", "Kannada"], horizontal=True)
    regenerate = st.sidebar.button("Regenerate 60-day Data")
    return merchant, amt_range, language, regenerate


raw_df = ensure_datetime(load_data())
merchant_name, amount_range, chosen_language, regenerate_data = sidebar_controls(raw_df)

if regenerate_data:
    raw_df = ensure_datetime(generate_merchant_transactions(merchant=merchant_name, days=60))
    st.cache_resource.clear()

detector = load_detector(raw_df)
results = detector.predict(raw_df)
results["date"] = pd.to_datetime(results["date"], errors="coerce")
filtered = results[(results["amount"] >= amount_range[0]) & (results["amount"] <= amount_range[1])]
flagged = filtered[filtered["is_anomaly"] == 1].copy()

st.title("PaySentinel 🛡️")
st.caption("AI-powered UPI fraud detection for small merchants")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Live Feed",
        "Explainability",
        "Voice Alerts",
        "PDF Report",
    ]
)

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", f"{len(filtered):,}")
    c2.metric("Suspicious", f"{len(flagged):,}")
    c3.metric("At Risk (Rs.)", f"{flagged['amount'].sum():,.0f}")
    c4.metric("Peak Hour", f"{detector.fp.get('peak_hour', 0)}:00")

    trend = (
        filtered.groupby(filtered["date"].dt.date, dropna=False)
        .agg(total=("amount", "count"), suspicious=("is_anomaly", "sum"))
        .reset_index()
    )
    fig = px.line(
        trend,
        x="date",
        y=["total", "suspicious"],
        markers=True,
        title="30-60 Day Activity Timeline",
        color_discrete_sequence=["#38bdf8", "#fb7185"],
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    if len(flagged):
        top = flagged.sort_values("anomaly_score", ascending=False).head(10)
        bar = px.bar(
            top,
            x="transaction_id",
            y="anomaly_score",
            color="risk_level",
            title="Top Suspicious Transactions",
            color_discrete_map={
                "CRITICAL": "#ef4444",
                "HIGH": "#f97316",
                "MEDIUM": "#facc15",
                "LOW": "#22c55e",
            },
        )
        bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(bar, use_container_width=True)

with tab2:
    st.subheader("WhatsApp-style Fraud Feed")
    st.markdown("<div class='wa-wrap'>", unsafe_allow_html=True)
    show_rows = filtered.sort_values("anomaly_score", ascending=False).head(25)
    for _, row in show_rows.iterrows():
        bubble_class = "wa-left" if row["is_anomaly"] == 1 else "wa-right"
        txt = (
            f"{row.get('transaction_id', '')} | Rs.{row['amount']:,.0f} | "
            f"{int(row['hour'])}:00 | {row.get('sender', '')}"
        )
        st.markdown(
            f"<div class='{bubble_class}'>{txt}<br>{risk_color(row.get('risk_level', 'LOW'))}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    preview = filtered[["transaction_id", "date", "hour", "amount", "sender", "anomaly_score", "risk_level", "is_anomaly"]].copy()
    st.dataframe(preview.sort_values("anomaly_score", ascending=False), use_container_width=True, height=360)

with tab3:
    st.subheader("Why was this flagged?")
    anomalies = filtered[filtered["is_anomaly"] == 1].sort_values("anomaly_score", ascending=False)
    if anomalies.empty:
        st.info("No suspicious transactions in current filter range.")
    else:
        choices = anomalies.index.tolist()
        selected_idx = st.selectbox(
            "Select suspicious transaction",
            choices,
            format_func=lambda i: f"{filtered.loc[i, 'transaction_id']} | Rs.{filtered.loc[i, 'amount']:,.0f} | score {filtered.loc[i, 'anomaly_score']}",
        )
        ex = detector.explain(filtered.reset_index(drop=True), filtered.index.get_loc(selected_idx))

        for item in ex:
            st.markdown(
                f"<div class='glass-card'><b>{item['feature']}</b><br>"
                f"Value: {item['value']}<br>"
                f"Impact: {item['impact']} ({item['direction']} anomaly confidence)</div>",
                unsafe_allow_html=True,
            )

        tx = filtered.loc[selected_idx]
        flags = tx.get("flags", [])
        if isinstance(flags, str):
            st.write(flags)
        else:
            st.write("Rule-based reasons:")
            for f in flags:
                st.write(f"- {f}")

with tab4:
    st.subheader("Kannada + English Voice Alerts")
    if flagged.empty:
        st.success("No suspicious transactions to announce.")
    else:
        top_alert = flagged.sort_values("anomaly_score", ascending=False).iloc[0]
        st.write(
            f"Top alert: {top_alert['transaction_id']} | Rs.{top_alert['amount']:,.0f} | Risk {top_alert['risk_level']}"
        )
        autoplay = st.checkbox("Autoplay top alert", value=True)
        st.markdown(
            alert_html(
                amount=float(top_alert["amount"]),
                hour=int(top_alert["hour"]),
                risk=str(top_alert["risk_level"]),
                language=chosen_language,
                autoplay=autoplay,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(summary_html(len(flagged), chosen_language), unsafe_allow_html=True)

with tab5:
    st.subheader("Download Kannada Audit PDF")
    st.write("Includes bilingual advisory and cybercrime helpline 1930.")
    pdf_bytes = make_pdf(merchant_name, filtered, detector.fp)
    st.download_button(
        "Download Report",
        data=pdf_bytes,
        file_name="pay_sentinel_report.pdf",
        mime="application/pdf",
    )

st.caption("Cyber Crime Helpline: 1930 | cybercrime.gov.in")
