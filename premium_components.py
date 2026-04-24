# ============================================================================
# PaySentinel — premium_components.py
# Reusable premium UI components for Streamlit
# ============================================================================

import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ── Shared Plotly layout defaults ──
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#07070f",
    plot_bgcolor="#0d0d1c",
    font=dict(family="Inter, sans-serif", color="#f0f0fa", size=12),
    xaxis=dict(gridcolor="rgba(30,30,69,0.5)", color="#8888a8", zeroline=False),
    yaxis=dict(gridcolor="rgba(30,30,69,0.5)", color="#8888a8", zeroline=False),
    legend=dict(bgcolor="rgba(13,13,28,0.8)", bordercolor="rgba(255,255,255,0.05)",
                font=dict(size=11)),
    hovermode="closest",
    margin=dict(t=50, b=40, l=60, r=20),
)


# ════════════════════════════════════════════════════════════════════════════
# 1. RISK SCORE GAUGE (Speedometer)
# ════════════════════════════════════════════════════════════════════════════

def risk_gauge(score, title="Risk Score"):
    """
    Plotly gauge chart — speedometer style, 0-100.
    Color zones: green (0-30) → yellow (30-60) → orange (60-80) → red (80-100)
    """
    score = float(score)

    # Dynamic color based on score
    if score < 30:
        needle_color = "#0fc98f"
    elif score < 60:
        needle_color = "#f0a828"
    elif score < 80:
        needle_color = "#ff8c32"
    else:
        needle_color = "#e24b4a"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(
            font=dict(family="JetBrains Mono, monospace", size=52, color=needle_color),
            suffix="",
        ),
        title=dict(text=title, font=dict(size=13, color="#8888a8",
                                          family="Inter, sans-serif")),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=2,
                tickcolor="#333355",
                dtick=10,
                tickfont=dict(size=10, color="#8888a8",
                              family="JetBrains Mono, monospace"),
            ),
            bar=dict(color=needle_color, thickness=0.25),
            bgcolor="rgba(13,13,28,0.5)",
            borderwidth=2,
            bordercolor="rgba(255,255,255,0.06)",
            steps=[
                dict(range=[0, 30], color="rgba(15,201,143,0.18)"),
                dict(range=[30, 60], color="rgba(240,168,40,0.18)"),
                dict(range=[60, 80], color="rgba(255,140,50,0.22)"),
                dict(range=[80, 100], color="rgba(226,75,74,0.28)"),
            ],
            threshold=dict(
                line=dict(color="#ff3333", width=4),
                thickness=0.8,
                value=score,
            ),
        ),
    ))

    fig.update_layout(
        paper_bgcolor="#07070f",
        plot_bgcolor="#07070f",
        font=dict(family="Inter, sans-serif", color="#f0f0fa"),
        height=280,
        margin=dict(t=40, b=10, l=30, r=30),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# 2. LIVE TRANSACTION FEED — HTML Bubble
# ════════════════════════════════════════════════════════════════════════════

def transaction_bubble(row, index=0, is_new=False):
    """
    Returns premium HTML for a single transaction alert card.
    Normal = green border, Suspicious = red border with blink.
    """
    is_fraud = row.get("is_anomaly", 0) == 1
    risk = str(row.get("risk_level", "LOW"))
    amount = row.get("amount", 0)
    hour = int(row.get("hour", 0))
    date = str(row.get("date", ""))[:10]
    sender = str(row.get("sender", "Unknown"))[:30]
    score = row.get("anomaly_score", 0)
    flags = row.get("flags", [])
    if not isinstance(flags, list):
        flags = []

    if is_fraud:
        card_class = "fraud-card new-alert" if is_new else "fraud-card"
        ico = "🚨" if risk in ("CRITICAL", "HIGH") else "⚠️"
        amt_color = "#ff6060" if risk in ("CRITICAL", "HIGH") else "#f0a828"
        badge_class = f"badge-{risk.lower()}"
        border_color = "#e24b4a" if risk in ("CRITICAL", "HIGH") else "#f0a828"
        critical_class = " critical-glow" if risk == "CRITICAL" else ""
    else:
        card_class = "safe-card"
        ico = "✅"
        amt_color = "#0fc98f"
        badge_class = "badge-low"
        border_color = "#0fc98f"
        critical_class = ""

    flags_html = "".join([f'<div style="margin:2px 0;">⚠ {f}</div>' for f in flags[:3]])
    delay = index * 0.12

    # Score bar visual (mini progress indicator)
    score_pct = min(float(score), 100)
    score_bar_color = "#e24b4a" if score_pct > 70 else "#f0a828" if score_pct > 40 else "#0fc98f"

    return f"""
    <div class="{card_class}{critical_class}"
         style="animation-delay:{delay}s; border-left-color:{border_color};">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <span class="amount" style="color:{amt_color};">{ico} ₹{amount:,.0f}</span>
          <div class="meta">📅 {date} &nbsp;|&nbsp; 🕐 {hour}:00 &nbsp;|&nbsp; 👤 {sender}</div>
        </div>
        <div style="text-align:right;">
          <span class="badge {badge_class}">{risk}</span>
          <div style="font-family:'JetBrains Mono',monospace; font-size:0.78rem;
                      color:#888; margin-top:6px;">{score:.1f}</div>
          <div style="width:60px; height:3px; background:rgba(255,255,255,0.06);
                      border-radius:2px; margin-top:4px;">
            <div style="width:{score_pct}%; height:100%; background:{score_bar_color};
                        border-radius:2px; transition:width 0.8s ease;"></div>
          </div>
        </div>
      </div>
      <div class="flags">{flags_html}</div>
    </div>
    """


# ════════════════════════════════════════════════════════════════════════════
# 3. MERCHANT BEHAVIOUR PROFILE CARD
# ════════════════════════════════════════════════════════════════════════════

def merchant_profile_card(merchant_name, fp, n_total, n_fraud, risk_amt):
    """
    Premium merchant profile card styled like a bank statement / credit card.
    """
    hour_min = int(fp.get("hour_min", 8))
    hour_max = int(fp.get("hour_max", 21))
    peak = int(fp.get("peak_hour", 12))
    amt_p95 = fp.get("amt_p95", 1500)
    known = len(fp.get("known_senders", []))

    fraud_pct = (n_fraud / max(n_total, 1)) * 100
    if fraud_pct < 3:
        risk_color = "#0fc98f"
        risk_label = "LOW RISK"
    elif fraud_pct < 8:
        risk_color = "#f0a828"
        risk_label = "MODERATE"
    else:
        risk_color = "#e24b4a"
        risk_label = "HIGH RISK"

    # Generate a simple 7-day risk trend sparkline (simulated)
    trend_bars = ""
    for i in range(7):
        h = max(8, min(40, int(fraud_pct * 3 + np.random.randint(-8, 12))))
        day_label = ["M", "T", "W", "T", "F", "S", "S"][i]
        trend_bars += f'''
        <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
          <div style="width:6px; height:{h}px; background:linear-gradient(180deg,{risk_color},rgba(112,96,238,0.3));
                      border-radius:3px;"></div>
          <span style="font-size:0.55rem; color:#555577;">{day_label}</span>
        </div>'''

    return f"""
    <div class="merchant-profile">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; position:relative; z-index:1;">
        <div>
          <div class="name">🏪 {merchant_name}</div>
          <div class="subtitle">UPI MERCHANT • FRAUD MONITORING ACTIVE</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:0.62rem; color:#8888a8; text-transform:uppercase;
                      letter-spacing:1px; margin-bottom:4px;">Fraud Rate</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:2rem;
                      font-weight:800; color:{risk_color};">{fraud_pct:.1f}%</div>
          <div style="font-size:0.65rem; color:{risk_color}; font-weight:600;
                      letter-spacing:0.8px;">{risk_label}</div>
        </div>
      </div>

      <!-- 7-Day Risk Trend -->
      <div style="margin-top:18px; padding:14px; background:rgba(255,255,255,0.02);
                  border-radius:8px; border:1px solid rgba(255,255,255,0.04);
                  position:relative; z-index:1;">
        <div style="font-size:0.62rem; color:#8888a8; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:10px;">7-Day Risk Trend</div>
        <div style="display:flex; gap:10px; align-items:flex-end; height:50px;">
          {trend_bars}
        </div>
      </div>

      <div class="stat-row" style="position:relative; z-index:1;">
        <div class="stat">
          <div class="stat-label">Operating Hours</div>
          <div class="stat-value">{hour_min}:00 – {hour_max}:00</div>
        </div>
        <div class="stat">
          <div class="stat-label">Peak Hour</div>
          <div class="stat-value">{peak}:00</div>
        </div>
        <div class="stat">
          <div class="stat-label">Normal Max Amt</div>
          <div class="stat-value">₹{amt_p95:,.0f}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Known Senders</div>
          <div class="stat-value">{known}</div>
        </div>
      </div>
      <div style="margin-top:14px; display:flex; gap:14px; flex-wrap:wrap; position:relative; z-index:1;">
        <div class="stat" style="flex:1;">
          <div class="stat-label">Total Transactions</div>
          <div class="stat-value" style="color:#7060ee;">{n_total:,}</div>
        </div>
        <div class="stat" style="flex:1;">
          <div class="stat-label">Flagged</div>
          <div class="stat-value" style="color:#e24b4a;">{n_fraud}</div>
        </div>
        <div class="stat" style="flex:1;">
          <div class="stat-label">At-Risk Amount</div>
          <div class="stat-value" style="color:#f0a828;">₹{risk_amt:,.0f}</div>
        </div>
      </div>
    </div>
    """


# ════════════════════════════════════════════════════════════════════════════
# 4. ANIMATED FRAUD TIMELINE (Plotly animation frames)
# ════════════════════════════════════════════════════════════════════════════

def animated_timeline(results):
    """
    Timeline chart with animation frames — plays through the month
    showing transactions appearing one by one. Fraud = red diamonds.
    """
    r = results.copy()
    r["date"] = pd.to_datetime(r["date"], errors="coerce")
    r = r.dropna(subset=["date"]).sort_values("date")
    normal = r[r["is_anomaly"] == 0]
    fraud = r[r["is_anomaly"] == 1]

    fig = go.Figure()

    # Normal transactions — soft scatter
    fig.add_trace(go.Scatter(
        x=normal["date"], y=normal["amount"],
        mode="markers",
        name="✅ Normal",
        marker=dict(color="rgba(15,201,143,0.5)", size=5,
                    line=dict(width=0.5, color="rgba(15,201,143,0.8)")),
        hovertemplate="Normal<br>Date: %{x}<br>Amount: ₹%{y:,.0f}<extra></extra>",
    ))

    # Fraud transactions with glow markers
    if len(fraud) > 0:
        fig.add_trace(go.Scatter(
            x=fraud["date"], y=fraud["amount"],
            mode="markers+text",
            name="🚨 Suspicious",
            marker=dict(
                color="#e24b4a", size=14, symbol="diamond",
                line=dict(color="rgba(255,153,153,0.6)", width=2),
            ),
            text=["⚠"] * len(fraud),
            textposition="top center",
            textfont=dict(size=10),
            hovertemplate="🚨 SUSPICIOUS<br>Date: %{x}<br>Amount: ₹%{y:,.0f}<extra></extra>",
        ))

        # Add red flash zones around fraud dates
        for _, frow in fraud.iterrows():
            fig.add_vrect(
                x0=frow["date"] - pd.Timedelta(hours=12),
                x1=frow["date"] + pd.Timedelta(hours=12),
                fillcolor="rgba(226,75,74,0.04)",
                line_width=0,
                layer="below",
            )

    # --- Build animation frames (step through by week) ---
    dates_sorted = r["date"].sort_values().unique()
    if len(dates_sorted) > 7:
        n_frames = min(12, len(dates_sorted))
        step = max(1, len(dates_sorted) // n_frames)
        frames = []
        for i in range(1, n_frames + 1):
            cutoff = dates_sorted[min(i * step, len(dates_sorted) - 1)]
            subset = r[r["date"] <= cutoff]
            n_sub = subset[subset["is_anomaly"] == 0]
            f_sub = subset[subset["is_anomaly"] == 1]

            frame_data = [
                go.Scatter(x=n_sub["date"], y=n_sub["amount"],
                           mode="markers", name="✅ Normal",
                           marker=dict(color="rgba(15,201,143,0.5)", size=5,
                                       line=dict(width=0.5, color="rgba(15,201,143,0.8)"))),
            ]
            if len(f_sub) > 0:
                frame_data.append(
                    go.Scatter(x=f_sub["date"], y=f_sub["amount"],
                               mode="markers+text", name="🚨 Suspicious",
                               marker=dict(color="#e24b4a", size=14, symbol="diamond",
                                           line=dict(color="rgba(255,153,153,0.6)", width=2)),
                               text=["⚠"] * len(f_sub), textposition="top center",
                               textfont=dict(size=10))
                )
            frames.append(go.Frame(data=frame_data, name=str(i)))

        fig.frames = frames
        fig.update_layout(
            updatemenus=[dict(
                type="buttons", showactive=False,
                x=0.05, y=1.12, xanchor="left",
                buttons=[
                    dict(label="▶ Play Timeline", method="animate",
                         args=[None, dict(frame=dict(duration=400, redraw=True),
                                          fromcurrent=True,
                                          transition=dict(duration=200))]),
                    dict(label="⏸ Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate")]),
                ],
                font=dict(size=11, color="#f0f0fa"),
                bgcolor="rgba(112,96,238,0.2)",
                bordercolor="rgba(112,96,238,0.3)",
            )],
        )

    fig.update_layout(
        title=dict(text="Transaction Timeline — 60 Days",
                   font=dict(size=15, color="#f0f0fa", family="Space Grotesk, sans-serif")),
        **PLOTLY_LAYOUT,
        height=440,
        xaxis=dict(title="Date", gridcolor="rgba(30,30,69,0.35)", color="#8888a8"),
        yaxis=dict(title="Amount (₹)", gridcolor="rgba(30,30,69,0.35)", color="#8888a8"),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# 5. DAILY VOLUME BAR CHART (Premium)
# ════════════════════════════════════════════════════════════════════════════

def daily_volume_chart(results):
    """Premium daily transaction volume with fraud overlay."""
    r = results.copy()
    r["date"] = pd.to_datetime(r["date"], errors="coerce")
    daily = (r.groupby(r["date"].dt.date)
             .agg(total=("amount", "count"), fraud_count=("is_anomaly", "sum"))
             .reset_index())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["total"],
        name="All Transactions",
        marker_color="rgba(112,96,238,0.3)",
        marker_line=dict(width=0.5, color="rgba(112,96,238,0.5)"),
    ))
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["fraud_count"],
        name="🚨 Suspicious",
        marker_color="rgba(226,75,74,0.8)",
        marker_line=dict(width=0.5, color="rgba(226,75,74,1)"),
    ))
    fig.update_layout(
        barmode="overlay",
        title=dict(text="Daily Transaction Volume",
                   font=dict(size=14, color="#f0f0fa", family="Space Grotesk, sans-serif")),
        **PLOTLY_LAYOUT,
        height=300,
        margin=dict(t=40, b=30, l=50, r=20),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# 6. HOURLY HEATMAP (Premium)
# ════════════════════════════════════════════════════════════════════════════

def fraud_heatmap(results):
    """Premium hourly fraud heatmap."""
    r = results.copy()
    r["date"] = pd.to_datetime(r["date"], errors="coerce")
    fraud = r[r["is_anomaly"] == 1]

    if len(fraud) == 0:
        return None

    fraud_h = fraud.copy()
    fraud_h["day_name"] = fraud_h["date"].dt.day_name()
    fraud_h["hour_int"] = fraud_h["hour"].astype(int)

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                  "Friday", "Saturday", "Sunday"]
    heat = (fraud_h.groupby(["day_name", "hour_int"])
            .size().reset_index(name="count"))

    pivot = heat.pivot_table(index="day_name", columns="hour_int",
                              values="count", fill_value=0)
    pivot = pivot.reindex(days_order, fill_value=0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h}:00" for h in pivot.columns],
        y=pivot.index,
        colorscale=[
            [0, "rgba(13,13,28,1)"],
            [0.25, "rgba(226,75,74,0.15)"],
            [0.5, "rgba(226,75,74,0.4)"],
            [0.75, "rgba(226,75,74,0.65)"],
            [1, "rgba(255,50,50,0.95)"],
        ],
        showscale=True,
        colorbar=dict(
            title="Count",
            titlefont=dict(size=11, color="#8888a8"),
            tickfont=dict(size=10, color="#8888a8"),
        ),
        hovertemplate="Day: %{y}<br>Hour: %{x}<br>Fraud Count: %{z}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Fraud Risk Heatmap — Hour × Day",
                   font=dict(size=14, color="#f0f0fa", family="Space Grotesk, sans-serif")),
        paper_bgcolor="#07070f",
        plot_bgcolor="#0d0d1c",
        font=dict(family="Inter, sans-serif", color="#f0f0fa"),
        height=300,
        margin=dict(t=40, b=30, l=100, r=20),
        xaxis=dict(side="bottom"),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# 7. SHAP BAR CHART (Premium)
# ════════════════════════════════════════════════════════════════════════════

def shap_bar_chart(explanation):
    """Premium SHAP feature importance bar chart."""
    features = [e["feature"].replace("_", " ").title() for e in explanation]
    impacts = [e["impact"] for e in explanation]
    colors = ["#e24b4a" if e["direction"] == "increases" else "#0fc98f"
              for e in explanation]

    fig = go.Figure(go.Bar(
        x=impacts, y=features,
        orientation="h",
        marker_color=colors,
        marker_line=dict(width=0),
        text=[f"{v:.4f}" for v in impacts],
        textposition="outside",
        textfont=dict(family="JetBrains Mono, monospace", size=11,
                      color="#8888a8"),
    ))

    fig.update_layout(
        title=dict(text="Feature Contributions to Anomaly Score",
                   font=dict(size=14, color="#f0f0fa", family="Space Grotesk, sans-serif")),
        paper_bgcolor="#07070f",
        plot_bgcolor="#0d0d1c",
        font=dict(family="Inter, sans-serif", color="#f0f0fa"),
        xaxis=dict(title="SHAP Impact", gridcolor="rgba(30,30,69,0.4)"),
        yaxis=dict(gridcolor="rgba(30,30,69,0.4)"),
        height=300,
        margin=dict(t=40, b=20, l=180, r=60),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# 8. LOADING SKELETON HTML
# ════════════════════════════════════════════════════════════════════════════

def skeleton_loader(variant="card"):
    """Return skeleton loading HTML."""
    if variant == "chart":
        return '<div class="skeleton skeleton-chart"></div>'
    elif variant == "text":
        return """
        <div class="skeleton skeleton-text" style="width:85%;"></div>
        <div class="skeleton skeleton-text" style="width:60%;"></div>
        <div class="skeleton skeleton-text" style="width:72%;"></div>
        """
    else:
        return '<div class="skeleton skeleton-card"></div>'


# ════════════════════════════════════════════════════════════════════════════
# 9. SECTION HEADER HTML
# ════════════════════════════════════════════════════════════════════════════

def section_header(title, subtitle=""):
    """Premium section header with accent bar."""
    sub = f'<div style="color:#8888a8; font-size:0.78rem; font-weight:400; margin-top:2px;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-header">
      <span class="accent"></span>
      <div>
        <span>{title}</span>
        {sub}
      </div>
    </div>
    """
