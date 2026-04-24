# ============================================================================
# PaySentinel — app.py  (Premium Fintech Dashboard)
# AI-Powered UPI Merchant Fraud Detection | English + Kannada
# "Stark Tech" Aesthetic — Award-winning Fintech UI
# ============================================================================

# ── IMPORTS ─────────────────────────────────────────────────────────────────
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
from premium_css import inject_css
from premium_components import (
    risk_gauge,
    transaction_bubble,
    merchant_profile_card,
    animated_timeline,
    daily_volume_chart,
    fraud_heatmap,
    shap_bar_chart,
    skeleton_loader,
    section_header,
)

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaySentinel — AI Fraud Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── INJECT PREMIUM CSS ─────────────────────────────────────────────────────
st.markdown(inject_css(), unsafe_allow_html=True)

# ── SESSION STATE ───────────────────────────────────────────────────────────
for key, default in [("detector", None), ("results", None),
                     ("df_raw", None), ("merchant_name", "My UPI Store")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── PREMIUM HEADER ──────────────────────────────────────────────────────────
merchant = st.session_state["merchant_name"]
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">
      <div style="font-size:2rem;">🛡️</div>
      <div>
        <div style="font-size:1.7rem; font-weight:800;
                    background:linear-gradient(135deg,#e24b4a,#ff8a80);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:-0.5px; font-family:'Space Grotesk',sans-serif;">
          PaySentinel
        </div>
        <div style="font-size:0.76rem; color:#8888a8; font-weight:400;
                    letter-spacing:0.5px;">
          AI-Powered Fraud Shield for {merchant}
        </div>
      </div>
      <div style="flex:1;"></div>
      <div style="display:flex; align-items:center; gap:6px;
                  background:rgba(15,201,143,0.1); padding:4px 12px;
                  border-radius:999px; border:1px solid rgba(15,201,143,0.2);">
        <span class="live-dot"></span>
        <span style="font-size:0.72rem; color:#0fc98f; font-weight:600;
                     letter-spacing:0.5px;">MONITORING</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🛡️ PaySentinel")
    st.markdown(
        '<span style="color:#8888a8; font-size:0.82rem;">AI Merchant Fraud Shield</span>',
        unsafe_allow_html=True,
    )
    st.divider()

    merchant_name = st.text_input(
        "🏪 Merchant Name", value=st.session_state["merchant_name"]
    )
    st.session_state["merchant_name"] = merchant_name

    lang_select = st.selectbox(
        "🔊 Alert Language", ["English", "Kannada (ಕನ್ನಡ)"]
    )
    lang_key = "Kannada" if "Kannada" in lang_select else "English"

    sensitivity = st.select_slider(
        "🎯 Detection Sensitivity",
        options=["2%", "5%", "8%", "12%", "15%"],
        value="5%",
    )
    contamination = float(sensitivity.replace("%", "")) / 100
    st.caption(f"Detecting top {sensitivity} unusual transactions")

    st.divider()

    st.markdown(
        """
        <div style="background:rgba(112,96,238,0.08); border:1px solid rgba(112,96,238,0.15);
                    border-radius:12px; padding:14px; margin:8px 0;">
          <div style="font-size:0.75rem; font-weight:600; color:#7060ee;
                      text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">
            Tech Stack
          </div>
          <div style="font-size:0.78rem; color:#aaa; line-height:1.8;">
            🤖 Isolation Forest + SVM Hybrid<br>
            🧠 SHAP Explainability<br>
            🔊 Kannada + English Voice<br>
            📄 Bilingual PDF Reports<br>
            ⚡ &lt;100ms Kafka Pipeline
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; font-size:0.7rem; color:#555577;">'
        'ಕನ್ನಡ + English &nbsp;|&nbsp; Blueprint 2026</div>',
        unsafe_allow_html=True,
    )

# ── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📤 Upload & Analyse",
        "🚨 Fraud Alerts",
        "📈 Timeline & Heatmap",
        "🧠 Explain (SHAP)",
        "📄 PDF Report",
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — UPLOAD & ANALYSE
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(
        section_header("Upload & Analyse", "Load transaction data and run ML detection"),
        unsafe_allow_html=True,
    )

    col_upload, col_sample = st.columns(2)

    with col_upload:
        uploaded = st.file_uploader(
            "Upload UPI CSV",
            type=["csv"],
            help="Columns needed: date, hour, amount, sender (optional)",
        )

    with col_sample:
        st.markdown("")
        if st.button("🎲 Generate Sample Data", use_container_width=True):
            with st.spinner("Generating sample data..."):
                df = generate_merchant_transactions(
                    merchant_name=st.session_state["merchant_name"]
                )
                st.session_state["df_raw"] = df
            st.success(f"✅ Loaded {len(df):,} sample transactions!")

    if uploaded is not None:
        df_up = pd.read_csv(uploaded)
        st.session_state["df_raw"] = df_up
        st.success(
            f"✅ Loaded {len(df_up):,} transactions from {uploaded.name}"
        )

    if st.session_state["df_raw"] is not None and uploaded is None:
        st.download_button(
            "⬇️ Download Sample CSV",
            st.session_state["df_raw"].to_csv(index=False),
            "sample_upi_transactions.csv",
            "text/csv",
        )

    # ── Run Detection ──
    if st.session_state["df_raw"] is not None:
        st.markdown("---")
        if st.button("🔍 Run Anomaly Detection", type="primary",
                     use_container_width=True):
            progress = st.progress(0)
            status = st.empty()

            # Show skeleton while processing
            placeholder = st.empty()
            placeholder.markdown(
                skeleton_loader("chart") + skeleton_loader("card"),
                unsafe_allow_html=True,
            )

            steps = [
                (15, "⚙️ Loading data..."),
                (35, "🔧 Engineering 20 features..."),
                (50, "👤 Building merchant fingerprint..."),
            ]
            for pct, msg in steps:
                status.text(msg)
                time.sleep(0.2)
                progress.progress(pct)

            detector = PaySentinelDetector(contamination=contamination)
            detector.fit(st.session_state["df_raw"])
            progress.progress(65)

            status.text("🔍 Running hybrid anomaly detection...")
            results = detector.predict(st.session_state["df_raw"])
            progress.progress(85)

            status.text("🧠 Setting up SHAP explainer...")
            time.sleep(0.2)
            progress.progress(100)

            progress.empty()
            status.empty()
            placeholder.empty()
            st.session_state["detector"] = detector
            st.session_state["results"] = results

            st.success("✅ Analysis complete! Navigate to other tabs →")

    # ── Summary Metrics + Merchant Profile ──
    if st.session_state["results"] is not None:
        results = st.session_state["results"]
        anomalies = results[results["is_anomaly"] == 1]
        n_total = len(results)
        n_fraud = len(anomalies)
        risk_amt = (
            anomalies["amount"].sum() if "amount" in anomalies.columns else 0
        )

        st.markdown("---")

        # Premium Metric Cards
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

        # Merchant Profile Card
        st.markdown("---")
        detector = st.session_state["detector"]
        st.markdown(
            merchant_profile_card(
                st.session_state["merchant_name"],
                detector.fp,
                n_total,
                n_fraud,
                risk_amt,
            ),
            unsafe_allow_html=True,
        )

        # Data table
        st.markdown("---")
        st.markdown(
            section_header("Transaction Data", "All processed transactions"),
            unsafe_allow_html=True,
        )
        display_cols = [
            c
            for c in [
                "transaction_id", "date", "hour", "amount", "sender",
                "description", "is_anomaly", "anomaly_score", "risk_level",
            ]
            if c in results.columns
        ]
        st.dataframe(
            results[display_cols], use_container_width=True, height=360
        )

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FRAUD ALERTS (Live Feed + Risk Gauges)
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    if st.session_state["results"] is None:
        st.markdown(
            section_header("Fraud Alerts", "Run detection first"),
            unsafe_allow_html=True,
        )
        st.info("👆 Run detection in the Upload tab first.")
        st.markdown(skeleton_loader("card") * 3, unsafe_allow_html=True)
    else:
        results = st.session_state["results"]
        anomalies = results[results["is_anomaly"] == 1].sort_values(
            "anomaly_score", ascending=False
        )

        # Summary audio
        st.markdown(
            summary_html(len(anomalies), lang_key), unsafe_allow_html=True
        )

        st.markdown(
            section_header(
                "Live Transaction Feed",
                f'<span class="live-dot"></span> {len(anomalies)} alerts detected',
            ),
            unsafe_allow_html=True,
        )

        if len(anomalies) == 0:
            st.success(
                "✅ No suspicious transactions found! "
                "Your merchant activity looks normal."
            )
        else:
            # ── Risk Gauge for top threat ──
            top_score = float(anomalies.iloc[0].get("anomaly_score", 0))
            col_gauge, col_summary = st.columns([1, 1])

            with col_gauge:
                fig_gauge = risk_gauge(top_score, "Highest Threat Score")
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col_summary:
                n_crit = len(anomalies[anomalies['risk_level'] == 'CRITICAL'])
                n_high = len(anomalies[anomalies['risk_level'] == 'HIGH'])
                n_med = len(anomalies[anomalies['risk_level'] == 'MEDIUM'])
                st.markdown(
                    f"""
                    <div class="threat-summary">
                      <div style="font-size:0.7rem; color:#8888a8; text-transform:uppercase;
                                  letter-spacing:1px; margin-bottom:12px;">Threat Summary</div>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:2.4rem;
                                  font-weight:800; color:#e24b4a; margin-bottom:8px;">
                        {len(anomalies)} alerts
                      </div>
                      <div style="color:#aaa; font-size:0.85rem; line-height:2;">
                        🔴 Critical: {n_crit} &nbsp;
                        🟠 High: {n_high} &nbsp;
                        🟡 Medium: {n_med}<br>
                        💰 Total at risk: ₹{anomalies['amount'].sum():,.0f}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ── Transaction Feed ──
            for i, (_, row) in enumerate(anomalies.head(12).iterrows()):
                is_new = i < 3  # First 3 get blink animation
                st.markdown(
                    transaction_bubble(row, index=i, is_new=is_new),
                    unsafe_allow_html=True,
                )

                # Voice buttons for first 5
                if i < 5:
                    c_en, c_kn, c_gauge = st.columns([1, 1, 1])
                    with c_en:
                        if st.button(f"🔊 English", key=f"en_{i}"):
                            html = alert_html(
                                row.get("amount", 0),
                                int(row.get("hour", 0)),
                                str(row.get("risk_level", "HIGH")),
                                "English",
                                autoplay=True,
                            )
                            st.markdown(html, unsafe_allow_html=True)
                    with c_kn:
                        if st.button(f"🔊 ಕನ್ನಡ", key=f"kn_{i}"):
                            html = alert_html(
                                row.get("amount", 0),
                                int(row.get("hour", 0)),
                                str(row.get("risk_level", "HIGH")),
                                "Kannada",
                                autoplay=True,
                            )
                            st.markdown(html, unsafe_allow_html=True)
                    with c_gauge:
                        score = float(row.get("anomaly_score", 0))
                        mini_fig = risk_gauge(score, f"Score")
                        mini_fig.update_layout(height=180,
                                               margin=dict(t=30, b=0, l=20, r=20))
                        st.plotly_chart(mini_fig, use_container_width=True,
                                        key=f"gauge_{i}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — TIMELINE & HEATMAP
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    if st.session_state["results"] is None:
        st.markdown(
            section_header("Timeline & Heatmap", "Run detection first"),
            unsafe_allow_html=True,
        )
        st.info("👆 Run detection in the Upload tab first.")
        st.markdown(skeleton_loader("chart"), unsafe_allow_html=True)
    else:
        results = st.session_state["results"]

        st.markdown(
            section_header("Animated Fraud Timeline",
                           "Press ▶ Play to watch transactions unfold over 60 days"),
            unsafe_allow_html=True,
        )

        # Chart 1 — Animated Timeline with play button
        fig_timeline = animated_timeline(results)
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Chart 2 — Daily Volume
        st.markdown(
            section_header("Daily Volume",
                           "Transaction count per day with fraud overlay"),
            unsafe_allow_html=True,
        )
        fig_vol = daily_volume_chart(results)
        st.plotly_chart(fig_vol, use_container_width=True)

        # Chart 3 — Heatmap
        st.markdown(
            section_header("Fraud Risk Heatmap",
                           "Hour × Day concentration of suspicious activity"),
            unsafe_allow_html=True,
        )
        fig_heat = fraud_heatmap(results)
        if fig_heat is not None:
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption(
                "🔴 Darker red = higher fraud concentration at that hour + day"
            )
        else:
            st.info("No fraud detected — heatmap unavailable.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPLAIN (SHAP)
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    if (
        st.session_state["results"] is None
        or st.session_state["detector"] is None
    ):
        st.markdown(
            section_header("SHAP Explainability", "Run detection first"),
            unsafe_allow_html=True,
        )
        st.info("👆 Run detection in the Upload tab first.")
        st.markdown(skeleton_loader("chart"), unsafe_allow_html=True)
    else:
        results = st.session_state["results"]
        detector = st.session_state["detector"]
        df_raw = st.session_state["df_raw"]
        fp = detector.fp

        st.markdown(
            section_header("SHAP Explainability",
                           "Understand why each transaction was flagged"),
            unsafe_allow_html=True,
        )

        anomalies = results[results["is_anomaly"] == 1]

        if len(anomalies) == 0:
            st.success("✅ No suspicious transactions to explain.")
        else:
            # Build dropdown
            options = [
                f"#{i} — ₹{row['amount']:,.0f} at "
                f"{int(row.get('hour', 0))}:00 "
                f"| Score: {row.get('anomaly_score', 0):.1f} "
                f"| {str(row.get('risk_level', ''))}"
                for i, (_, row) in enumerate(anomalies.head(10).iterrows())
            ]
            selected = st.selectbox("Select a suspicious transaction:", options)
            sel_pos = options.index(selected)
            sel_idx = anomalies.index[sel_pos]
            row = results.loc[sel_idx]

            # ── Two columns: Details + Risk Gauge ──
            c_left, c_right = st.columns([3, 2])

            with c_left:
                st.markdown(
                    section_header("Transaction Details"),
                    unsafe_allow_html=True,
                )
                for col in [
                    "date", "hour", "amount", "sender", "description",
                    "anomaly_score", "risk_level",
                ]:
                    if col in row.index:
                        val = row[col]
                        if col == "amount":
                            val = f"₹{val:,.0f}"
                        st.markdown(f"- **{col.replace('_',' ').title()}:** {val}")

                st.markdown(
                    section_header("Why Flagged?"), unsafe_allow_html=True
                )
                flags = row.get("flags", [])
                if isinstance(flags, list) and flags:
                    for flag in flags:
                        st.markdown(f"⚠️ {flag}")
                else:
                    st.markdown("⚠️ Statistical outlier detected by ML")

            with c_right:
                score = float(row.get("anomaly_score", 0))
                fig_g = risk_gauge(score, "Risk Score")
                st.plotly_chart(fig_g, use_container_width=True)

            # ── SHAP bar chart ──
            st.markdown("---")
            st.markdown(
                section_header("SHAP Feature Importance",
                               "How each feature contributed to the score"),
                unsafe_allow_html=True,
            )
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
                    fig_shap = shap_bar_chart(explanation)
                    st.plotly_chart(fig_shap, use_container_width=True)
                    st.caption(
                        "🔴 Red = increases fraud risk   "
                        "🟢 Green = decreases fraud risk"
                    )
                except Exception as e:
                    st.warning(f"SHAP could not compute: {e}")

            # ── Plain Language Explanation ──
            st.markdown("---")
            st.markdown(
                section_header("Plain Language Explanation"),
                unsafe_allow_html=True,
            )
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

            # ── Merchant Fingerprint ──
            st.markdown("---")
            st.markdown(
                section_header("Merchant Behaviour Fingerprint",
                               "Baseline learned from your history"),
                unsafe_allow_html=True,
            )
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

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — PDF REPORT
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    if (
        st.session_state["results"] is None
        or st.session_state["detector"] is None
    ):
        st.markdown(
            section_header("PDF Report", "Run detection first"),
            unsafe_allow_html=True,
        )
        st.info("👆 Run detection in the Upload tab first.")
    else:
        results = st.session_state["results"]
        detector = st.session_state["detector"]
        merchant = st.session_state["merchant_name"]
        anomalies = results[results["is_anomaly"] == 1]
        risk_amt = (
            anomalies["amount"].sum() if "amount" in anomalies.columns else 0
        )

        st.markdown(
            section_header("Generate Audit Report",
                           "Bilingual PDF for bank submission"),
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                f"""
                <div class="info-card info-card-purple">
                  <div class="info-card-label" style="color:#7060ee;">
                    Report Contents
                  </div>
                  <div style="color:#ccc; font-size:0.85rem; line-height:2;">
                    📊 <strong>{len(results):,}</strong> total transactions analysed<br>
                    🚨 <strong>{len(anomalies)}</strong> suspicious transactions<br>
                    💰 <strong>₹{risk_amt:,.0f}</strong> at-risk amount<br>
                    🌐 English + ಕನ್ನಡ sections<br>
                    📞 Cyber Crime Helpline: <strong>1930</strong>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                """
                <div class="info-card info-card-orange">
                  <div class="info-card-label" style="color:#f0a828;">
                    Kannada Advisory Preview
                  </div>
                  <div style="color:#ccc; font-size:0.85rem; line-height:2;">
                    ಕನ್ನಡ ಸಲಹೆ (Kannada Advisory):<br>
                    ಸಂಶಯಾಸ್ಪದ ವ್ಯವಹಾರ: ತಕ್ಷಣ ಬ್ಯಾಂಕ್‌ಗೆ ತಿಳಿಸಿ<br>
                    ಸೈಬರ್ ಕ್ರೈಮ್ ಸಹಾಯವಾಣಿ: 1930
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        if st.button("📄 Generate PDF Report", type="primary",
                     use_container_width=True):
            with st.spinner("Generating report..."):
                try:
                    pdf_bytes = make_pdf(merchant, results, detector.fp)
                    st.success("✅ Report generated!")
                    fname = f"paysentinel_{merchant.replace(' ', '_')}.pdf"
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=fname,
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")

        st.caption(
            "The PDF includes a Kannada advisory section and Cyber Crime "
            "Helpline 1930. Safe to share with your bank."
        )
