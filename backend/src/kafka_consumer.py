"""
PaySentinel Kafka Consumer: Real-time fraud detection stream processor.

Consumes from 'upi-transactions', runs ML predictions, produces to 'fraud-alerts'.

Run: python kafka_consumer.py
"""

import json
import os
import signal
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector

# ── Kafka Setup ──
BROKER = "localhost:9092"
INPUT_TOPIC = "upi-transactions"
OUTPUT_TOPIC = "fraud-alerts"
DLQ_TOPIC = "fraud-dead-letter"

# ── Model & State Setup ──
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_ROOT, "models", "detector.pkl")

try:
    detector = PaySentinelDetector.load(_MODEL_PATH)
    print(f"✅ Detector loaded from {_MODEL_PATH}")
except Exception as e:
    print(f"⚠️  Could not load pre-trained model: {e}. Bootstrapping detector from synthetic data.")
    detector = PaySentinelDetector(contamination=0.05)
    bootstrap_df = generate_merchant_transactions(merchant_name="Bootstrap Merchant", days=14)
    detector.fit(bootstrap_df)
    print("✅ Detector bootstrapped and fitted for streaming")

def _create_kafka_clients():
    """Safely initialize Kafka consumer and producers with error handling."""
    try:
        consumer = KafkaConsumer(
            INPUT_TOPIC,
            bootstrap_servers=BROKER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='paysentinel-detector',
            session_timeout_ms=30000,
            request_timeout_ms=5000  # Fail fast if broker is down
        )
        alert_p = KafkaProducer(
            bootstrap_servers=BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=5000
        )
        dlq_p = KafkaProducer(
            bootstrap_servers=BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=5000
        )
        print(f"✅ Connected to Kafka at {BROKER}")
        return consumer, alert_p, dlq_p
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        print(f"   Make sure Kafka is running: docker-compose up -d")
        return None, None, None

consumer, alert_producer, dlq_producer = _create_kafka_clients()

# ── Health Check Server ──
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            status = {
                'status': 'ok',
                'processed': transaction_count,
                'alerts': alerts_count,
                'uptime_s': int(time.time() - start_time)
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
    def log_message(self, *args): pass

def start_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    server.serve_forever()

threading.Thread(target=start_health_server, daemon=True).start()

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
start_time = time.time()

# ── Graceful Shutdown ──
def shutdown_handler(signum, frame):
    elapsed = time.time() - start_time
    print(f"\n\n{'='*60}")
    print(f"🛑 PAYSENTINEL CONSUMER SHUTTING DOWN")
    print(f"{'='*60}")
    print(f"Runtime:     {elapsed:.0f}s")
    print(f"Processed:   {transaction_count} transactions")
    print(f"Alerts:      {alerts_count} ({alerts_count/max(transaction_count,1)*100:.1f}%)")
    print(f"Throughput:  {transaction_count/max(elapsed,1):.1f} txn/s")
    print(f"{'='*60}\n")
    consumer.close()
    alert_producer.close()
    dlq_producer.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


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
    if not tx_id:
        return False

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
    if consumer is None or alert_producer is None:
        print("❌ Cannot start: Kafka clients not initialized. Check your broker connection.")
        return

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
            
            # 2. Process through detector with error handling
            try:
                risk_score, risk_level, top_flag = process_transaction(tx)
            except Exception as e:
                print(f"❌ [{tx.get('transaction_id')}] Processing failed: {e}")
                dlq_producer.send(DLQ_TOPIC, value={
                    'original_tx': tx,
                    'error': str(e),
                    'timestamp': current_time.isoformat()
                })
                continue
            
            # 3. Update rolling window
            merchant_id = tx.get('merchant_id') or 'unknown_merchant'
            merchant_window[merchant_id].append({
                'amount': tx.get('amount'),
                'risk_score': risk_score,
                'sender': tx.get('sender')
            })
            
            # 4. Refit fingerprint & Metrics
            transaction_count += 1
            if transaction_count % 50 == 0:
                # Sliding window metrics
                sample_merchant = list(merchant_window.keys())[0] if merchant_window else None
                if sample_merchant:
                    recent = list(merchant_window[sample_merchant])[-50:]
                    avg_risk = sum(r['risk_score'] for r in recent) / len(recent)
                    fraud_rate = sum(1 for r in recent if r['risk_score'] > RISK_THRESHOLD) / len(recent) * 100
                    print(f"\n📊 [METRICS] tx={transaction_count} | alerts={alerts_count} | "
                          f"avg_risk={avg_risk:.1f} | fraud_rate={fraud_rate:.1f}% | "
                          f"uptime={int(time.time()-start_time)}s\n")

            if transaction_count % REFIT_INTERVAL == 0:
                print(f"🔧 [REFIT] Re-fitting fingerprint after {REFIT_INTERVAL} transactions")
            
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
    
    except Exception as e:
        print(f"💥 Consumer Crashed: {e}")
        shutdown_handler(None, None)


if __name__ == "__main__":
    main()

