import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── RISK GAUGE ──────────────────────────────────────────────────────────────
def risk_gauge(score, title="Risk Score"):
    """Premium Plotly Gauge with Stark Tech aesthetic."""
    color = "#0fc98f" if score < 30 else "#f0a828" if score < 60 else "#e24b4a"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 18, 'color': '#8888a8', 'family': 'Space Grotesk'}},
        number={'font': {'color': color, 'size': 50, 'family': 'JetBrains Mono'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#444"},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(15, 201, 143, 0.1)'},
                {'range': [30, 60], 'color': 'rgba(240, 168, 40, 0.1)'},
                {'range': [60, 100], 'color': 'rgba(226, 75, 74, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=20, l=30, r=30),
        height=280,
    )
    return fig

# ── TRANSACTION BUBBLE ──────────────────────────────────────────────────────
def transaction_bubble(row, index=0, is_new=False):
    """HTML component for transaction alerts."""
    risk_level = str(row.get("risk_level", "LOW")).upper()
    badge_class = f"badge-{risk_level.lower()}"
    card_class = "fraud-card" if row.get("is_anomaly") == 1 else "safe-card"
    if is_new and row.get("is_anomaly") == 1:
        card_class += " new-alert"
    
    amount = row.get("amount", 0)
    hour = int(row.get("hour", 0))
    sender = row.get("sender", "Unknown")
    score = row.get("anomaly_score", 0)
    
    flags_html = ""
    flags = row.get("flags", [])
    if isinstance(flags, list):
        for f in flags[:2]:
            flags_html += f'<div style="font-size:0.75rem; color:#aaa; margin-top:4px;">⚠️ {f}</div>'

    return f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div class="amount">₹{amount:,.0f}</div>
                <div class="meta">{hour}:00 | {sender}</div>
            </div>
            <div style="text-align:right;">
                <div class="badge {badge_class}">{risk_level}</div>
                <div style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#888; margin-top:8px;">SCORE: {score}</div>
            </div>
        </div>
        {flags_html}
    </div>
    """

# ── MERCHANT PROFILE CARD ───────────────────────────────────────────────────
def merchant_profile_card(name, fp, total, fraud, risk_amt):
    """Premium merchant behaviour summary card."""
    return f"""
    <div class="merchant-profile">
        <div class="subtitle">Merchant Profile</div>
        <div class="name">{name}</div>
        <div class="stat-row">
            <div class="stat">
                <div class="stat-label">Total Transactions</div>
                <div class="stat-value">{total:,}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Operating Hours</div>
                <div class="stat-value">{int(fp.get('hour_min',8))}:00 - {int(fp.get('hour_max',21))}:00</div>
            </div>
            <div class="stat">
                <div class="stat-label">Typical Max</div>
                <div class="stat-value">₹{fp.get('amt_p95',0):,.0f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Peak Hour</div>
                <div class="stat-value">{fp.get('peak_hour', 12)}:00</div>
            </div>
        </div>
    </div>
    """

# ── ANIMATED TIMELINE ───────────────────────────────────────────────────────
def animated_timeline(df):
    """Plotly timeline with fraud markers."""
    df_plot = df.copy()
    df_plot['is_fraud_label'] = df_plot['is_anomaly'].map({1: 'Suspicious', 0: 'Normal'})
    
    fig = px.scatter(
        df_plot,
        x="date",
        y="amount",
        color="is_fraud_label",
        size="anomaly_score",
        hover_data=["hour", "sender", "anomaly_score"],
        color_discrete_map={'Suspicious': '#e24b4a', 'Normal': '#0fc98f'},
        template="plotly_dark",
        title="Transaction Timeline"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    )
    return fig

# ── DAILY VOLUME CHART ─────────────────────────────────────────────────────
def daily_volume_chart(df):
    """Bar chart of daily transactions with fraud highlight."""
    daily = df.groupby('date').agg(
        total=('amount', 'count'),
        fraud=('is_anomaly', 'sum')
    ).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily['date'], y=daily['total'],
        name='Normal', marker_color='rgba(112, 96, 238, 0.3)',
        bordercolor='rgba(112, 96, 238, 0.5)', borderwidth=1
    ))
    fig.add_trace(go.Bar(
        x=daily['date'], y=daily['fraud'],
        name='Suspicious', marker_color='#e24b4a'
    ))
    
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_dark",
        height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", y=1.1)
    )
    return fig

# ── FRAUD HEATMAP ───────────────────────────────────────────────────────────
def fraud_heatmap(df):
    """Density heatmap of fraud occurrences."""
    df_fraud = df[df['is_anomaly'] == 1]
    if len(df_fraud) == 0: return None
    
    fig = px.density_heatmap(
        df_fraud,
        x="day_of_week",
        y="hour",
        z="anomaly_score",
        nbinsx=7, nbinsy=24,
        color_continuous_scale=[[0, 'rgba(0,0,0,0)'], [1, '#e24b4a']],
        template="plotly_dark"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        height=400
    )
    return fig

# ── SHAP BAR CHART ──────────────────────────────────────────────────────────
def shap_bar_chart(explanation):
    """Visualizes SHAP contribution values."""
    df_shap = pd.DataFrame(explanation)
    df_shap = df_shap.sort_values("impact", ascending=True)
    
    colors = ['#0fc98f' if d == 'decreases' else '#e24b4a' for d in df_shap['direction']]
    
    fig = go.Figure(go.Bar(
        x=df_shap['impact'],
        y=df_shap['feature'],
        orientation='h',
        marker_color=colors,
        text=df_shap['feature'],
        textposition='auto',
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Contribution to Anomaly Score", showgrid=False),
        yaxis=dict(showticklabels=False),
        height=300,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    return fig

# ── SKELETON LOADER ────────────────────────────────────────────────────────
def skeleton_loader(kind="card"):
    """HTML skeleton loader for async transitions."""
    if kind == "chart":
        return '<div class="skeleton skeleton-chart"></div>'
    elif kind == "card":
        return '<div class="skeleton skeleton-card"></div>'
    return '<div class="skeleton skeleton-text"></div>'

# ── SECTION HEADER ──────────────────────────────────────────────────────────
def section_header(title, subtitle=""):
    """Styled header for sections."""
    sub_html = f'<div style="font-size:0.75rem; color:#8888a8; font-weight:400; margin-left:14px; letter-spacing:0.5px;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-header">
        <span class="accent"></span>
        <span style="letter-spacing:-0.5px;">{title}</span>
        {sub_html}
    </div>
    """

# updated
