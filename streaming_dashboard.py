"""
PaySentinel Streaming Dashboard: Live Kafka alert feed for Streamlit.

This component connects to the 'fraud-alerts' Kafka topic and displays
real-time fraud notifications with animated indicators.

Integration with app.py:
    import streamlit_live_alerts from streaming_dashboard
    st_live_alerts.display_live_feed()
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import threading
import time
from collections import deque

# ── Configuration ──
KAFKA_BROKER = "localhost:9092"
ALERTS_TOPIC = "fraud-alerts"
MAX_ALERTS_DISPLAY = 15
REFRESH_INTERVAL = 2  # seconds

# Global state for live alerts
if 'live_alerts' not in st.session_state:
    st.session_state['live_alerts'] = deque(maxlen=MAX_ALERTS_DISPLAY)

if 'kafka_consumer_active' not in st.session_state:
    st.session_state['kafka_consumer_active'] = False

if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = datetime.now()


def start_kafka_listener():
    """Start Kafka consumer in background thread."""
    def consume_alerts():
        try:
            consumer = KafkaConsumer(
                ALERTS_TOPIC,
                bootstrap_servers=KAFKA_BROKER,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                group_id='streamlit-dashboard',
                session_timeout_ms=30000,
            )
            
            for message in consumer:
                alert = message.value
                alert['received_at'] = datetime.now().isoformat()
                st.session_state['live_alerts'].appendleft(alert)  # Add to front
                st.session_state['last_refresh'] = datetime.now()
        
        except Exception as e:
            print(f"❌ Kafka Consumer Error: {e}")
    
    # Start consumer in daemon thread
    thread = threading.Thread(target=consume_alerts, daemon=True)
    thread.start()
    st.session_state['kafka_consumer_active'] = True


def display_live_feed():
    """Main component: Display live fraud alert feed."""
    
    # ── Header with Live Indicator ──
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🔴 **LIVE Fraud Alerts**")
    
    with col2:
        # Blinking indicator
        if st.session_state['kafka_consumer_active']:
            st.markdown("🔴 **LIVE**", help="Connected to Kafka fraud-alerts topic")
        else:
            if st.button("🟢 Connect to Kafka", use_container_width=True):
                start_kafka_listener()
                st.rerun()
    
    with col3:
        last_update = st.session_state['last_refresh'].strftime("%H:%M:%S")
        st.caption(f"🕐 Last: {last_update}")
    
    st.markdown("---")
    
    # ── No Alerts Yet ──
    if len(st.session_state['live_alerts']) == 0:
        st.info("👂 Listening for fraud alerts... None detected yet.")
        return
    
    # ── Display Alerts ──
    st.markdown(f"**{len(st.session_state['live_alerts'])} Recent Alerts**")
    
    for i, alert in enumerate(st.session_state['live_alerts']):
        # Color code by risk level
        risk_level = alert.get('risk_level', 'MEDIUM')
        if risk_level == 'CRITICAL':
            risk_color = "🔴"
            color_box = "🔴"
        elif risk_level == 'HIGH':
            risk_color = "🟠"
            color_box = "🟠"
        else:
            risk_color = "🟡"
            color_box = "🟡"
        
        # Expandable alert card
        with st.expander(
            f"{color_box} {risk_color} ₹{alert.get('amount', 0):,} | {alert.get('merchant_name', 'Unknown')} | Score: {alert.get('risk_score', 0)}"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Amount", f"₹{alert.get('amount', 0):,}")
                st.metric("Risk Score", f"{alert.get('risk_score', 0):.1f}/100")
            
            with col2:
                st.metric("Merchant", alert.get('merchant_name', 'N/A'))
                st.metric("Risk Level", risk_level)
            
            with col3:
                st.metric("Sender", alert.get('sender', 'N/A')[:20])
                st.metric("Transaction ID", alert.get('transaction_id', 'N/A')[:8])
            
            st.markdown("---")
            
            # Flag explanation
            st.markdown(f"**🚩 Alert Reason:**")
            st.write(alert.get('top_flag', 'Statistical anomaly detected'))
            
            # Additional details
            st.markdown(f"**Time:** {alert.get('timestamp', 'N/A')}")


def display_statistics():
    """Show summary statistics of live alerts."""
    if len(st.session_state['live_alerts']) == 0:
        return
    
    alerts_df = pd.DataFrame(list(st.session_state['live_alerts']))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", len(alerts_df))
    
    with col2:
        critical = len(alerts_df[alerts_df['risk_level'] == 'CRITICAL'])
        st.metric("CRITICAL", critical)
    
    with col3:
        avg_risk = alerts_df['risk_score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.1f}")
    
    with col4:
        total_amount = alerts_df['amount'].sum()
        st.metric("Total Amount at Risk", f"₹{total_amount:,}")


# ── Convenience function for integration ──
def stream_live_alerts():
    """
    Integration function for app.py.
    
    Usage in app.py:
        from streaming_dashboard import stream_live_alerts
        
        if st.button("📊 Show Live Alerts"):
            stream_live_alerts()
    """
    st.set_page_config(page_title="PaySentinel Live Stream", layout="wide")
    
    st.title("🚨 PaySentinel Live Fraud Detection")
    
    # Statistics row
    display_statistics()
    
    st.markdown("---")
    
    # Live feed
    display_live_feed()
    
    # Auto-refresh placeholder
    placeholder = st.empty()
    
    def auto_refresh():
        while True:
            time.sleep(REFRESH_INTERVAL)
            placeholder.empty()
            with placeholder.container():
                st.markdown(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*")
    
    # Uncomment for auto-refresh in production
    # thread = threading.Thread(target=auto_refresh, daemon=True)
    # thread.start()

# updated
