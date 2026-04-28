"""
PaySentinel Kafka Consumer: Real-time fraud detection stream processor.

Consumes from 'upi-transactions', runs ML predictions, produces to 'fraud-alerts'.

Run: python kafka_consumer.py
"""

import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer
from model import PaySentinelDetector
import pandas as pd

# ── Kafka Setup ──
BROKER = "localhost:9092"
INPUT_TOPIC = "upi-transactions"
OUTPUT_TOPIC = "fraud-alerts"

# ── Model & State Setup ──
try:
    detector = PaySentinelDetector.load("models/detector.pkl")
    print("✅ Detector loaded from models/detector.pkl")
except FileNotFoundError:
    print("⚠️  No pre-trained model found. Using fresh detector.")
    detector = PaySentinelDetector(contamination=0.05)

# Kafka Consumers & Producers
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='paysentinel-detector',
    session_timeout_ms=30000
)

alert_producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ── Stream State Management ──
ROLLING_WINDOW_SIZE = 50  # Keep last 50 transactions per merchant
REFIT_INTERVAL = 100  # Re-fit fingerprint every 100 transactions
DEDUP_WINDOW = 60  # seconds
RISK_THRESHOLD = 60  # Alert if risk_score > 60

# Rolling window per merchant
merchant_window = defaultdict(lambda: deque(maxlen=ROLLING_WINDOW_SIZE))

# Deduplication: {transaction_id: timestamp}
seen_transactions = {}

# State tracking
transaction_count = 0
alerts_count = 0


def get_top_flag(flags):
    """Extract the most critical flag for display."""
    if flags and len(flags) > 0:
        return flags[0][:60]  # First 60 chars
    return "Statistical outlier"


def process_transaction(tx):
    """
    Process a single transaction through the detector.
    Returns: (risk_score, risk_level, top_flag, shap_explanation)
    """
    # Create a single-row DataFrame for prediction
    df = pd.DataFrame([{
        'date': tx.get('date', datetime.now().strftime("%Y-%m-%d")),
        'hour': tx.get('hour', 12),
        'amount': tx.get('amount', 0),
        'sender': tx.get('sender', 'unknown'),
        'timestamp': tx.get('timestamp', datetime.now().isoformat()),
    }])
    
    # Predict
    result = detector.predict(df)
    
    # Extract from result
    risk_score = float(result['anomaly_score'].iloc[0])
    risk_level = str(result['risk_level'].iloc[0])
    flags = result['flags'].iloc[0]
    
    return risk_score, risk_level, get_top_flag(flags)


def deduplicate_transaction(tx_id, current_time):
    """
    Check if transaction ID has been seen recently (within DEDUP_WINDOW).
    Returns: True if duplicate, False if new.
    """
    if tx_id in seen_transactions:
        last_seen = seen_transactions[tx_id]
        if (current_time - last_seen).total_seconds() < DEDUP_WINDOW:
            return True  # Duplicate
    
    # Mark as seen
    seen_transactions[tx_id] = current_time
    
    # Cleanup old entries (>DEDUP_WINDOW seconds old)
    to_delete = [k for k, v in seen_transactions.items() 
                 if (current_time - v).total_seconds() > DEDUP_WINDOW]
    for k in to_delete:
        del seen_transactions[k]
    
    return False  # New transaction


def main():
    """Consume and process UPI transactions in real-time."""
    global transaction_count, alerts_count
    
    print(f"\n🚀 PaySentinel Consumer Started")
    print(f"📍 Kafka Broker: {BROKER}")
    print(f"📨 Input Topic: {INPUT_TOPIC}")
    print(f"📨 Alert Topic: {OUTPUT_TOPIC}")
    print(f"⚠️  Alert Threshold: risk_score > {RISK_THRESHOLD}")
    print(f"🔄 Listening... (Ctrl+C to stop)\n")
    
    try:
        for message in consumer:
            tx = message.value
            current_time = datetime.now()
            
            # 1. Deduplicate
            if deduplicate_transaction(tx.get('transaction_id'), current_time):
                print(f"⏭️  [{tx.get('transaction_id')}] Duplicate, skipping")
                continue
            
            # 2. Process through detector
            risk_score, risk_level, top_flag = process_transaction(tx)
            
            # 3. Update rolling window
            merchant_id = tx.get('merchant_id')
            merchant_window[merchant_id].append({
                'amount': tx.get('amount'),
                'risk_score': risk_score,
                'sender': tx.get('sender')
            })
            
            # 4. Refit fingerprint if threshold reached
            transaction_count += 1
            if transaction_count % REFIT_INTERVAL == 0:
                print(f"🔧 [REFIT] Re-fitting fingerprint after {REFIT_INTERVAL} transactions")
                # In production, you'd trigger a re-training job here
            
            # 5. Alert Logic
            if risk_score > RISK_THRESHOLD:
                alerts_count += 1
                alert = {
                    "transaction_id": tx.get('transaction_id'),
                    "merchant_id": merchant_id,
                    "merchant_name": tx.get('merchant_name', 'Unknown'),
                    "sender": tx.get('sender'),
                    "amount": tx.get('amount'),
                    "risk_score": round(risk_score, 1),
                    "risk_level": risk_level,
                    "top_flag": top_flag,
                    "timestamp": current_time.isoformat(),
                    "hour": tx.get('hour'),
                    "date": tx.get('date'),
                }
                
                # Send to fraud-alerts topic
                alert_producer.send(OUTPUT_TOPIC, value=alert, key=merchant_id.encode('utf-8'))
                
                # Print alert
                print(f"\n🚨 [ALERT #{alerts_count}] [{tx.get('transaction_id')}]")
                print(f"   Amount: ₹{tx.get('amount'):,}")
                print(f"   Merchant: {tx.get('merchant_name')}")
                print(f"   Risk Score: {risk_score:.1f}/100 ({risk_level})")
                print(f"   Flag: {top_flag}")
                print(f"   Time: {current_time.strftime('%H:%M:%S')}\n")
            else:
                # Normal transaction
                print(f"✓ [{tx.get('transaction_id')}] ₹{tx.get('amount')} | "
                      f"{tx.get('merchant_name')} | Risk: {risk_score:.1f} ({risk_level})")
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Consumer stopped.")
        print(f"📊 Processed: {transaction_count} transactions | Alerts: {alerts_count}")
        consumer.close()
        alert_producer.close()


if __name__ == "__main__":
    main()

# updated
