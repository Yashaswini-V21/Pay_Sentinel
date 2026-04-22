# ============================================================================
# PaySentinel — app.py  (Complete Streamlit Dashboard)
# AI-Powered UPI Merchant Fraud Detection | English + Kannada
# ============================================================================

# ── PART 1 — IMPORTS ────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector
from voice_alerts import alert_html, summary_html
from pdf_report import make_pdf

# ── PART 2 — PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="PaySentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PART 3 — CUSTOM DARK CSS ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── App background ── */
    .stApp {
        background-color: #07070f;
        color: #f0f0fa;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0d0d1c !important;
        border-right: 1px solid rgba(255, 255, 255, 0.055);
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: #0d0d1c;
        border: 1px solid rgba(255, 255, 255, 0.055);
        border-radius: 8px;
        padding: 1rem;
    }
    [data-testid="stMetricLabel"] {
        color: #8888a8 !important;
        font-size: 12px !important;
    }

    /* ── Chat-style bubbles ── */
    .fraud-bubble {
        background: #1a0505;
        border-left: 4px solid #e24b4a;
        border-radius: 0 8px 8px 0;
        padding: 11px 14px;
        margin: 5px 0;
    }
    .safe-bubble {
        background: #041208;
        border-left: 4px solid #0fc98f;
        border-radius: 0 8px 8px 0;
        padding: 11px 14px;
        margin: 5px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── PART 4 — SESSION STATE (initialise only if key does NOT already exist) ──
if "detector" not in st.session_state:
    st.session_state["detector"] = None
if "results" not in st.session_state:
    st.session_state["results"] = None
if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = None
if "merchant_name" not in st.session_state:
    st.session_state["merchant_name"] = "My UPI Store"

# ── PART 5 — MAIN HEADER ───────────────────────────────────────────────────
merchant = st.session_state["merchant_name"]
st.markdown(f"## 🛡️ PaySentinel — {merchant}")

# ── PART 6 — SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    # ── Title ──
    st.markdown("# 🛡️ PaySentinel")
    st.markdown("*AI Merchant Fraud Shield*")
    st.divider()

    # ── Merchant name input ──
    merchant_name = st.text_input(
        "🏪 Merchant Name", value=st.session_state["merchant_name"]
    )
    st.session_state["merchant_name"] = merchant_name

    # ── Language selector ──
    lang_select = st.selectbox("🔊 Alert Language", ["English", "Kannada (ಕನ್ನಡ)"])
    lang_key = "Kannada" if "Kannada" in lang_select else "English"

    # ── Detection sensitivity slider ──
    sensitivity = st.select_slider(
        "🎯 Detection Sensitivity",
        options=["2%", "5%", "8%", "12%", "15%"],
        value="5%",
    )
    contamination = float(sensitivity.replace("%", "")) / 100
    st.caption(f"Detecting top {sensitivity} unusual transactions")

    st.divider()

    # ── About section ──
    st.markdown("**About**")
    st.markdown(
        """
- 🤖 Isolation Forest ML
- 🧠 SHAP Explainability
- 🔊 Kannada + English voice
- 📄 PDF audit report
- ✅ 100% Free
"""
    )

    # ── Bottom note ──
    st.markdown("---")
    st.caption("ಕನ್ನಡ + English | HackPulse 2026")

# ── PART 7 — TABS ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📤 Upload & Analyse",
        "🚨 Fraud Alerts",
        "📈 Timeline",
        "🧠 Explain",
        "📄 PDF Report",
    ]
)

with tab1:
    # ── SECTION A — Data loading (two columns) ──
    col_upload, col_sample = st.columns(2)

    with col_upload:
        uploaded = st.file_uploader(
            "Upload UPI CSV",
            type=["csv"],
            help="Columns needed: date, hour, amount, sender (optional)",
        )

    with col_sample:
        st.markdown("")
        if st.button("🎲 Use Sample Data"):
            with st.spinner("Generating sample data..."):
                df = generate_merchant_transactions(
                    merchant_name=st.session_state["merchant_name"]
                )
                st.session_state["df_raw"] = df
            st.success(f"✅ Loaded {len(df):,} sample transactions!")

    if uploaded is not None:
        df_up = pd.read_csv(uploaded)
        st.session_state["df_raw"] = df_up
        st.success(f"✅ Loaded {len(df_up):,} transactions from {uploaded.name}")

    # ── SECTION B — Sample CSV download ──
    if st.session_state["df_raw"] is not None and uploaded is None:
        st.download_button(
            "⬇️ Download Sample CSV",
            st.session_state["df_raw"].to_csv(index=False),
            "sample_upi_transactions.csv",
            "text/csv",
        )

    # ── SECTION C — Run Detection button ──
    if st.session_state["df_raw"] is not None:
        st.markdown("---")
        if st.button("🔍 Run Anomaly Detection", type="primary"):
            with st.spinner("Training on your merchant data..."):
                progress = st.progress(0)
                time.sleep(0.2)
                progress.progress(20)
                detector = PaySentinelDetector(contamination=contamination)
                detector.fit(st.session_state["df_raw"])
                progress.progress(60)
                results = detector.predict(st.session_state["df_raw"])
                progress.progress(100)
                time.sleep(0.2)
                progress.empty()
                st.session_state["detector"] = detector
                st.session_state["results"] = results
            st.success("✅ Analysis complete! Check the Fraud Alerts tab →")

    # ── SECTION D — Summary metrics ──
    if st.session_state["results"] is not None:
        results = st.session_state["results"]
        anomalies = results[results["is_anomaly"] == 1]
        n_total = len(results)
        n_fraud = len(anomalies)
        risk_amt = (
            anomalies["amount"].sum() if "amount" in anomalies.columns else 0
        )

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Transactions", f"{n_total:,}")
        m2.metric(
            "🚨 Suspicious Found",
            f"{n_fraud}",
            delta=f"{n_fraud / n_total * 100:.1f}% of total",
            delta_color="inverse",
        )
        m3.metric("💰 At-Risk Amount", f"₹{risk_amt:,.0f}")
        m4.metric("✅ Safe", f"{n_total - n_fraud:,}")

        st.markdown("---")
        st.markdown("**All Transactions**")
        display_cols = [
            c
            for c in [
                "transaction_id",
                "date",
                "hour",
                "amount",
                "sender",
                "description",
                "is_anomaly",
                "anomaly_score",
                "risk_level",
            ]
            if c in results.columns
        ]
        st.dataframe(
            results[display_cols], use_container_width=True, height=360
        )

with tab2:
    # ── GUARD CHECK ──
    if st.session_state["results"] is None:
        st.info("👆 Run detection in the Upload tab first.")
    else:
        results = st.session_state["results"]
        anomalies = results[results["is_anomaly"] == 1].sort_values(
            "anomaly_score", ascending=False
        )

        # ── STEP 1 — Summary audio (autoplay on page load) ──
        st.markdown(
            summary_html(len(anomalies), lang_key), unsafe_allow_html=True
        )

        # ── STEP 2 — Header ──
        if len(anomalies) == 0:
            st.success(
                "✅ No suspicious transactions found! "
                "Your merchant activity looks normal."
            )
        else:
            st.markdown(
                f"### 🚨 {len(anomalies)} Suspicious Transactions Found"
            )

            # ── STEP 3 — WhatsApp-style bubble for each anomaly (top 10) ──
            for i, (_, row) in enumerate(anomalies.head(10).iterrows()):
                risk = str(row.get("risk_level", "HIGH"))
                amount = row.get("amount", 0)
                hour = int(row.get("hour", 0))
                date = str(row.get("date", ""))[:10]
                sender = str(row.get("sender", "Unknown"))[:35]
                score = row.get("anomaly_score", 0)
                flags = row.get("flags", [])
                if not isinstance(flags, list):
                    flags = []

                # bubble colour by risk level
                bg = "#1a0505" if risk in ("CRITICAL", "HIGH") else "#1a1405"
                bl = "#e24b4a" if risk in ("CRITICAL", "HIGH") else "#f0a828"
                sc = "#ff6060" if risk in ("CRITICAL", "HIGH") else "#f0a828"
                ico = "🚨" if risk in ("CRITICAL", "HIGH") else "⚠️"
                flags_html = "<br>".join([f"⚠ {f}" for f in flags[:3]])

                st.markdown(
                    f"""
                    <div style="background:{bg}; border-left:4px solid {bl};
                                border-radius:0 8px 8px 0; padding:11px 14px;
                                margin:5px 0;">
                      <span style="font-size:1.3rem; font-weight:700;
                                   color:{sc};">{ico} ₹{amount:,.0f}</span>
                      <div style="color:#aaa; font-size:0.85rem; margin:4px 0;">
                        📅 {date}  |  🕐 {hour}:00  |  👤 {sender}
                      </div>
                      <div style="color:#ccc; font-size:0.85rem; margin:6px 0;">
                        {flags_html}
                      </div>
                      <div style="margin-top:6px;">
                        <span style="background:{bl}; color:#fff; padding:2px 10px;
                                     border-radius:999px; font-size:0.78rem;
                                     font-weight:700;">{risk}</span>
                        <span style="color:#888; font-size:0.8rem;
                                     margin-left:8px;">{score:.1f}</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── STEP 4 — Voice buttons (first 5 only) ──
                if i < 5:
                    c_en, c_kn = st.columns(2)
                    with c_en:
                        if st.button(f"🔊 English", key=f"en_{i}"):
                            html = alert_html(
                                amount, hour, risk, "English", autoplay=True
                            )
                            st.markdown(html, unsafe_allow_html=True)
                    with c_kn:
                        if st.button(f"🔊 ಕನ್ನಡ", key=f"kn_{i}"):
                            html = alert_html(
                                amount, hour, risk, "Kannada", autoplay=True
                            )
                            st.markdown(html, unsafe_allow_html=True)

                if i < len(anomalies.head(10)) - 1:
                    st.markdown(
                        "<hr style='border-color:rgba(255,255,255,0.06);'>",
                        unsafe_allow_html=True,
                    )

with tab3:
    # ── GUARD CHECK ──
    if st.session_state["results"] is None:
        st.info("👆 Run detection in the Upload tab first.")
    else:
        r = st.session_state["results"].copy()
        r["date"] = pd.to_datetime(r["date"], errors="coerce")
        normal = r[r["is_anomaly"] == 0]
        fraud = r[r["is_anomaly"] == 1]

        # ── CHART 1 — Anomaly timeline ──
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=normal["date"],
                y=normal["amount"],
                mode="markers",
                name="✅ Normal",
                marker=dict(color="#0fc98f", size=6, opacity=0.6),
                hovertemplate=(
                    "Normal<br>Date: %{x}<br>Amount: ₹%{y:,.0f}"
                ),
            )
        )
        if len(fraud) > 0:
            fig.add_trace(
                go.Scatter(
                    x=fraud["date"],
                    y=fraud["amount"],
                    mode="markers+text",
                    name="🚨 Suspicious",
                    marker=dict(
                        color="#e24b4a",
                        size=16,
                        symbol="star",
                        line=dict(color="#ff9999", width=1),
                    ),
                    text=["⚠"] * len(fraud),
                    textposition="top center",
                    hovertemplate=(
                        "🚨 SUSPICIOUS<br>Date: %{x}<br>Amount: ₹%{y:,.0f}"
                    ),
                )
            )
        fig.update_layout(
            title="Transaction Timeline — 60 Days",
            paper_bgcolor="#07070f",
            plot_bgcolor="#0d0d1c",
            font=dict(color="#f0f0fa"),
            xaxis=dict(title="Date", gridcolor="#1e1e45", color="#8888a8"),
            yaxis=dict(
                title="Amount (₹)", gridcolor="#1e1e45", color="#8888a8"
            ),
            legend=dict(bgcolor="#0d0d1c", bordercolor="#1e1e45"),
            height=400,
            hovermode="closest",
            margin=dict(t=50, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── CHART 2 — Daily transaction volume ──
        daily = (
            r.groupby(r["date"].dt.date)
            .agg(total=("amount", "count"), fraud_count=("is_anomaly", "sum"))
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=daily["date"],
                y=daily["total"],
                name="All Transactions",
                marker_color="rgba(112,96,238,0.4)",
            )
        )
        fig2.add_trace(
            go.Bar(
                x=daily["date"],
                y=daily["fraud_count"],
                name="🚨 Suspicious",
                marker_color="#e24b4a",
            )
        )
        fig2.update_layout(
            barmode="overlay",
            title="Daily Transaction Volume",
            paper_bgcolor="#07070f",
            plot_bgcolor="#0d0d1c",
            font=dict(color="#f0f0fa"),
            xaxis=dict(gridcolor="#1e1e45"),
            yaxis=dict(gridcolor="#1e1e45"),
            legend=dict(bgcolor="#0d0d1c"),
            height=280,
            margin=dict(t=40, b=30),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ── CHART 3 — Hourly fraud heatmap ──
        if len(fraud) > 0:
            fraud_h = fraud.copy()
            fraud_h["day_name"] = fraud_h["date"].dt.day_name()
            heat = (
                fraud_h.groupby(["day_name", "hour"])
                .size()
                .reset_index(name="count")
            )
            fig3 = px.density_heatmap(
                heat,
                x="hour",
                y="day_name",
                z="count",
                color_continuous_scale="Reds",
                title="Fraud Heatmap — Hour × Day of Week",
            )
            fig3.update_layout(
                paper_bgcolor="#07070f",
                plot_bgcolor="#0d0d1c",
                font=dict(color="#f0f0fa"),
                height=280,
                margin=dict(t=40, b=30),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No fraud detected — heatmap unavailable.")

with tab4:
    # ── GUARD CHECK ──
    if (
        st.session_state["results"] is None
        or st.session_state["detector"] is None
    ):
        st.info("👆 Run detection in the Upload tab first.")
    else:
        results = st.session_state["results"]
        detector = st.session_state["detector"]
        df_raw = st.session_state["df_raw"]
        fp = detector.fp

        st.markdown("**Select a suspicious transaction to explain:**")
        anomalies = results[results["is_anomaly"] == 1]

        if len(anomalies) == 0:
            st.success("✅ No suspicious transactions to explain.")
        else:
            # Build dropdown options
            options = [
                f"#{i} — ₹{row['amount']:,.0f} at "
                f"{int(row.get('hour', 0))}:00 "
                f"| Score: {row.get('anomaly_score', 0):.1f} "
                f"| {str(row.get('risk_level', ''))}"
                for i, (_, row) in enumerate(anomalies.head(10).iterrows())
            ]
            selected = st.selectbox("Transaction:", options)
            sel_pos = options.index(selected)
            sel_idx = anomalies.index[sel_pos]
            row = results.loc[sel_idx]

            # ── STEP 1 — Two columns: details + flags ──
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("**Transaction Details**")
                for col in [
                    "date",
                    "hour",
                    "amount",
                    "sender",
                    "description",
                    "anomaly_score",
                    "risk_level",
                ]:
                    if col in row.index:
                        st.markdown(f"- **{col}:** {row[col]}")
            with c_right:
                st.markdown("**Why flagged?**")
                flags = row.get("flags", [])
                if isinstance(flags, list) and flags:
                    for flag in flags:
                        st.markdown(f"⚠️ {flag}")
                else:
                    st.markdown("⚠️ Statistical outlier detected by ML")

            # ── STEP 2 — SHAP bar chart ──
            st.markdown("---")
            st.markdown("**SHAP Feature Importance**")
            with st.spinner("Computing SHAP values..."):
                try:
                    orig_pos = (
                        list(df_raw.index).index(sel_idx)
                        if sel_idx in df_raw.index
                        else 0
                    )
                    explanation = detector.explain(
                        df_raw, min(orig_pos, len(df_raw) - 1)
                    )
                    features = [
                        e["feature"].replace("_", " ").title()
                        for e in explanation
                    ]
                    impacts = [e["impact"] for e in explanation]
                    colors = [
                        "#e24b4a"
                        if e["direction"] == "increases"
                        else "#0fc98f"
                        for e in explanation
                    ]
                    fig_shap = go.Figure(
                        go.Bar(
                            x=impacts,
                            y=features,
                            orientation="h",
                            marker_color=colors,
                            text=[f"{v:.4f}" for v in impacts],
                            textposition="outside",
                        )
                    )
                    fig_shap.update_layout(
                        title="Feature Contributions to Anomaly Score",
                        paper_bgcolor="#07070f",
                        plot_bgcolor="#0d0d1c",
                        font=dict(color="#f0f0fa"),
                        xaxis=dict(
                            title="SHAP Impact", gridcolor="#1e1e45"
                        ),
                        yaxis=dict(gridcolor="#1e1e45"),
                        height=300,
                        margin=dict(t=40, b=20, l=180),
                    )
                    st.plotly_chart(fig_shap, use_container_width=True)
                    st.caption(
                        "🔴 Red = increases fraud risk   "
                        "🟢 Green = decreases fraud risk"
                    )
                except Exception as e:
                    st.warning(f"SHAP could not compute: {e}")

            # ── STEP 3 — Plain language explanation ──
            st.markdown("---")
            st.markdown("**Plain Language Explanation**")
            amt = row.get("amount", 0)
            hour = int(row.get("hour", 0))
            explanation_text = (
                f"This transaction of **₹{amt:,.0f}** at **{hour}:00** "
                f"was flagged because it deviates from your normal pattern. "
                f"Your store normally operates between "
                f"**{fp.get('hour_min', 8):.0f}:00** and "
                f"**{fp.get('hour_max', 21):.0f}:00**, and typical amounts "
                f"are up to **₹{fp.get('amt_p95', 1500):,.0f}**."
            )
            st.info(explanation_text)

            # ── STEP 4 — Merchant fingerprint ──
            st.markdown("---")
            st.markdown("**Your Merchant Behaviour Fingerprint**")
            f1, f2, f3 = st.columns(3)
            f1.metric(
                "Normal Operating Hours",
                f"{fp.get('hour_min', 8):.0f}:00 – "
                f"{fp.get('hour_max', 21):.0f}:00",
            )
            f2.metric(
                "Typical Max Amount",
                f"₹{fp.get('amt_p95', 1500):,.0f}",
            )
            f3.metric(
                "Peak Business Hour",
                f"{fp.get('peak_hour', 12)}:00",
            )

with tab5:
    # ── GUARD CHECK ──
    if (
        st.session_state["results"] is None
        or st.session_state["detector"] is None
    ):
        st.info("👆 Run detection in the Upload tab first.")
    else:
        results = st.session_state["results"]
        detector = st.session_state["detector"]
        merchant = st.session_state["merchant_name"]
        anomalies = results[results["is_anomaly"] == 1]
        risk_amt = (
            anomalies["amount"].sum()
            if "amount" in anomalies.columns
            else 0
        )

        # ── STEP 1 — Report preview info (two columns) ──
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**This report includes:**")
            st.markdown(
                f"- 📊 **{len(results):,}** total transactions analysed"
            )
            st.markdown(
                f"- 🚨 **{len(anomalies)}** suspicious transactions"
            )
            st.markdown(f"- 💰 **₹{risk_amt:,.0f}** at-risk amount")
            st.markdown("- 🌐 English + ಕನ್ನಡ sections")
            st.markdown("- 📞 Cyber Crime Helpline: **1930**")

        with col_b:
            st.markdown("**Kannada section preview:**")
            st.markdown(
                """
                <div style="background:#0d0d1c; border:1px solid
                    rgba(255,255,255,0.08); border-radius:8px;
                    padding:12px; margin-top:4px;">
                <b>ಕನ್ನಡ ಸಲಹೆ (Kannada Advisory):</b><br>
                ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ: ತಕ್ಷಣ ಬ್ಯಾಂಕ್‌ಗೆ ತಿಳಿಸಿ<br>
                ಸೈಬರ್ ಕ್ರೈಮ್ ಸಹಾಯವಾಣಿ: <b>1930</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── STEP 2 — Generate button ──
        st.markdown("---")
        if st.button("📄 Generate PDF Report", type="primary"):
            with st.spinner("Generating report..."):
                try:
                    pdf_bytes = make_pdf(merchant, results, detector.fp)
                    st.success("✅ Report generated!")
                    fname = (
                        f"paysentinel_{merchant.replace(' ', '_')}.pdf"
                    )
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=fname,
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")

        # ── STEP 3 — Info note ──
        st.caption(
            "The PDF includes a Kannada advisory section and "
            "Cyber Crime Helpline 1930. Safe to share with your bank."
        )
