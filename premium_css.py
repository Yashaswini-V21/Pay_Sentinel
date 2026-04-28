# ============================================================================
# PaySentinel — premium_css.py
# "Stark Tech" Design System — Award-winning fintech aesthetic
# ============================================================================

STARK_CSS = """
<style>
/* ── Google Fonts (Geist Mono for numbers, Inter for labels) ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-primary: #07070f;
    --bg-secondary: #0d0d1c;
    --bg-card: rgba(13,13,28,0.85);
    --bg-glass: rgba(13,13,28,0.6);
    --bg-elevated: rgba(18,18,38,0.9);
    --border-subtle: rgba(255,255,255,0.055);
    --border-glow: rgba(226,75,74,0.3);
    --border-hover: rgba(112,96,238,0.35);
    --text-primary: #f0f0fa;
    --text-muted: #8888a8;
    --text-dim: #555577;
    --accent-red: #e24b4a;
    --accent-green: #0fc98f;
    --accent-orange: #f0a828;
    --accent-purple: #7060ee;
    --accent-blue: #3b82f6;
    --accent-cyan: #22d3ee;
    --glow-red: 0 0 20px rgba(226,75,74,0.25);
    --glow-green: 0 0 20px rgba(15,201,143,0.2);
    --glow-purple: 0 0 20px rgba(112,96,238,0.2);
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'Courier New', monospace;
    --font-display: 'Space Grotesk', var(--font-sans);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --transition-smooth: all 0.35s cubic-bezier(0.4,0,0.2,1);
}

/* ── App Background with Grid Texture ── */
.stApp {
    background-color: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(112,96,238,0.08), transparent),
        linear-gradient(rgba(112,96,238,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(112,96,238,0.025) 1px, transparent 1px);
    background-size: 100% 100%, 44px 44px, 44px 44px;
    color: var(--text-primary);
    font-family: var(--font-sans) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #0d0d1c 50%, #090918 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] .stMarkdown h1 {
    background: linear-gradient(135deg, var(--accent-red), #ff8a80);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

/* ── Tab Styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    padding: 4px;
    border: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
    transition: var(--transition-smooth) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(226,75,74,0.12) !important;
    color: var(--accent-red) !important;
    font-weight: 600 !important;
    border-bottom: none !important;
    box-shadow: 0 0 12px rgba(226,75,74,0.1);
}

/* ── Premium Metric Cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.2rem 1.4rem !important;
    transition: var(--transition-smooth) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-hover) !important;
    box-shadow: var(--glow-purple);
    transform: translateY(-3px);
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-red));
    opacity: 0;
    transition: opacity 0.3s ease;
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    color: var(--text-primary) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-family: var(--font-sans) !important;
    letter-spacing: 0.3px !important;
    transition: var(--transition-smooth) !important;
    border: 1px solid var(--border-subtle) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-red), #c9302c) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(226,75,74,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 25px rgba(226,75,74,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-subtle) !important;
    overflow: hidden;
}

/* ── Progress Bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-red), var(--accent-purple)) !important;
    border-radius: 99px !important;
}

/* ── Dividers ── */
hr { border-color: var(--border-subtle) !important; }

/* ═══════ ANIMATION KEYFRAMES ═══════ */

@keyframes blink-alert {
    0%, 100% { box-shadow: 0 0 0 rgba(226,75,74,0); }
    25% { box-shadow: 0 0 24px rgba(226,75,74,0.55), inset 0 0 12px rgba(226,75,74,0.1); }
    50% { box-shadow: 0 0 6px rgba(226,75,74,0.15); }
    75% { box-shadow: 0 0 24px rgba(226,75,74,0.55), inset 0 0 12px rgba(226,75,74,0.1); }
}
@keyframes slide-in {
    from { opacity: 0; transform: translateX(-24px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fade-up {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes glow-pulse {
    0%, 100% { opacity: 0.4; box-shadow: 0 0 8px rgba(226,75,74,0.15); }
    50% { opacity: 1; box-shadow: 0 0 20px rgba(226,75,74,0.35); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes pulse-dot {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.6); opacity: 0.4; }
}
@keyframes scanline {
    0% { top: -5%; }
    100% { top: 105%; }
}
@keyframes border-glow {
    0%, 100% { border-color: rgba(112,96,238,0.15); }
    50% { border-color: rgba(112,96,238,0.4); }
}

/* ═══════ PREMIUM COMPONENT CLASSES ═══════ */

/* ── Fraud Alert Bubble ── */
.fraud-card {
    background: linear-gradient(135deg, rgba(26,5,5,0.75) 0%, rgba(35,8,8,0.6) 100%);
    backdrop-filter: blur(10px);
    border-left: 4px solid var(--accent-red);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 18px 22px;
    margin: 10px 0;
    transition: var(--transition-smooth);
    animation: slide-in 0.5s ease forwards;
    position: relative;
    overflow: hidden;
}
.fraud-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, rgba(226,75,74,0.03), transparent 40%);
    pointer-events: none;
}
.fraud-card.new-alert {
    animation: slide-in 0.5s ease forwards, blink-alert 1.5s ease 2;
}
.fraud-card:hover {
    background: linear-gradient(135deg, rgba(35,8,8,0.9) 0%, rgba(45,10,10,0.7) 100%);
    border-left-width: 6px;
    transform: translateX(6px);
    box-shadow: 0 4px 20px rgba(226,75,74,0.12);
}
.fraud-card .amount {
    font-family: var(--font-mono);
    font-size: 1.5rem;
    font-weight: 700;
    color: #ff6060;
}
.fraud-card .meta {
    color: var(--text-muted);
    font-size: 0.82rem;
    margin: 6px 0;
    font-weight: 400;
}
.fraud-card .flags { color: #ccc; font-size: 0.82rem; margin: 8px 0; }
.fraud-card .badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-critical {
    background: linear-gradient(135deg, #e24b4a, #ff3333);
    color: #fff;
    box-shadow: 0 0 10px rgba(226,75,74,0.4);
}
.badge-high { background: #c9302c; color: #fff; }
.badge-medium { background: var(--accent-orange); color: #111; }
.badge-low { background: var(--accent-green); color: #111; }

/* ── Safe Transaction Bubble ── */
.safe-card {
    background: linear-gradient(135deg, rgba(4,18,8,0.7) 0%, rgba(6,24,12,0.5) 100%);
    backdrop-filter: blur(8px);
    border-left: 4px solid var(--accent-green);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 14px 18px;
    margin: 6px 0;
    transition: var(--transition-smooth);
}

/* ── Merchant Profile Card ── */
.merchant-profile {
    background: linear-gradient(145deg, #0f0f24 0%, #131330 50%, #0d0d1c 100%);
    border: 1px solid rgba(112,96,238,0.2);
    border-radius: var(--radius-xl);
    padding: 30px;
    position: relative;
    overflow: hidden;
    animation: fade-up 0.6s ease forwards;
}
.merchant-profile::before {
    content: '';
    position: absolute;
    top: -50%; right: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(112,96,238,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.merchant-profile::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-red), var(--accent-orange));
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}
.merchant-profile .name {
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #fff, #b0b0e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.merchant-profile .subtitle {
    color: var(--text-muted);
    font-size: 0.78rem;
    font-weight: 400;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}
.merchant-profile .stat-row {
    display: flex; gap: 16px; margin-top: 20px; flex-wrap: wrap;
}
.merchant-profile .stat {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.025);
    border-radius: var(--radius-sm);
    padding: 16px;
    border: 1px solid var(--border-subtle);
    transition: var(--transition-smooth);
}
.merchant-profile .stat:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--glow-purple);
}
.merchant-profile .stat-label {
    font-size: 0.66rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}
.merchant-profile .stat-value {
    font-family: var(--font-mono);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 6px;
}

/* ── Skeleton Loading ── */
.skeleton {
    background: linear-gradient(90deg, #0d0d1c 25%, #1a1a35 50%, #0d0d1c 75%);
    background-size: 200% 100%;
    animation: shimmer 1.8s ease-in-out infinite;
    border-radius: var(--radius-sm);
}
.skeleton-text { height: 14px; margin: 8px 0; width: 70%; }
.skeleton-card { height: 120px; margin: 10px 0; }
.skeleton-chart { height: 300px; margin: 12px 0; }

/* ── CRITICAL Glow Line ── */
.critical-glow {
    border: 1px solid rgba(226,75,74,0.4);
    box-shadow: 0 0 18px rgba(226,75,74,0.2), inset 0 0 18px rgba(226,75,74,0.05);
    animation: glow-pulse 2s ease-in-out infinite;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    font-family: var(--font-display);
    color: var(--text-primary);
    margin: 28px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
    display: flex; align-items: center; gap: 10px;
    animation: fade-up 0.4s ease;
}
.section-header .accent {
    width: 4px; height: 22px;
    background: linear-gradient(180deg, var(--accent-red), var(--accent-purple));
    border-radius: 2px;
    display: inline-block;
    box-shadow: 0 0 8px rgba(226,75,74,0.2);
}

/* ── Risk Score Display ── */
.risk-score-lg {
    font-family: var(--font-mono);
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
}
.risk-low { color: var(--accent-green); }
.risk-medium { color: var(--accent-orange); }
.risk-high { color: var(--accent-red); }
.risk-critical { color: #ff3333; text-shadow: 0 0 20px rgba(255,51,51,0.5); }

/* ── Live Feed Dot ── */
.live-dot {
    width: 8px; height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 1.5s ease-in-out infinite;
    margin-right: 6px;
    box-shadow: 0 0 6px rgba(15,201,143,0.4);
}

/* ── Threat Summary Card ── */
.threat-summary {
    background: linear-gradient(135deg, rgba(226,75,74,0.06) 0%, rgba(226,75,74,0.02) 100%);
    border: 1px solid rgba(226,75,74,0.18);
    border-radius: var(--radius-lg);
    padding: 26px;
    position: relative;
    overflow: hidden;
    animation: fade-up 0.5s ease;
}
.threat-summary::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-red), transparent);
}

/* ── Info Cards ── */
.info-card {
    border-radius: var(--radius-lg);
    padding: 22px;
    position: relative;
    overflow: hidden;
    transition: var(--transition-smooth);
    animation: fade-up 0.5s ease;
}
.info-card:hover {
    transform: translateY(-2px);
}
.info-card-purple {
    background: rgba(112,96,238,0.06);
    border: 1px solid rgba(112,96,238,0.15);
}
.info-card-orange {
    background: rgba(240,168,40,0.06);
    border: 1px solid rgba(240,168,40,0.15);
}
.info-card-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    border-radius: var(--radius-md) !important;
    border: 1px dashed rgba(112,96,238,0.3) !important;
}

/* ── Select boxes & inputs ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border-subtle) !important;
    font-family: var(--font-sans) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-family: var(--font-sans) !important;
}

/* ── Hide Streamlit Branding ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
    background: rgba(112,96,238,0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(112,96,238,0.5); }
</style>
"""


def inject_css():
    """Return the full CSS block for st.markdown injection."""
    return STARK_CSS

# updated
