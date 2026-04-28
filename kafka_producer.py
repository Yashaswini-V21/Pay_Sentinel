"""
PaySentinel Kafka Producer: Simulates live UPI transaction stream.

Produces realistic UPI transactions to 'upi-transactions' topic:
- 95% normal transactions (low fraud probability)
- 5% suspicious transactions (high fraud probability patterns)
- One transaction every 0.5–2 seconds

Run: python kafka_producer.py
"""

import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from uuid import uuid4

# ── Kafka Setup ──
BROKER = "localhost:9092"
TOPIC = "upi-transactions"

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ── Merchant & Sender Database (Simulated) ──
MERCHANTS = [
    {"id": "MER_001", "name": "Tech Store Delhi", "city": "Delhi"},
    {"id": "MER_002", "name": "Cafe Mumbai", "city": "Mumbai"},
    {"id": "MER_003", "name": "Medical Clinic Bangalore", "city": "Bangalore"},
    {"id": "MER_004", "name": "Grocery Shop Chennai", "city": "Chennai"},
    {"id": "MER_005", "name": "Fashion Boutique Pune", "city": "Pune"},
]

SENDERS = [
    "sender_001@okhdfcbank",
    "sender_002@okaxis",
    "sender_003@okicici",
    "sender_004@ybl",
    "sender_005@paytm",
    "sender_006@oksbi",
    "anomaly_bot_001@okaxis",  # Suspicious pattern
    "anomaly_bot_002@unknown",  # Suspicious pattern
]

NORMAL_AMOUNTS = [100, 250, 500, 1000, 2000, 3000, 5000]
SUSPICIOUS_AMOUNTS = [10000, 15000, 20000, 50000, 100000]  # Structuring attempts


def generate_normal_transaction():
    """Generate a normal UPI transaction (95% probability)."""
    merchant = random.choice(MERCHANTS)
    sender = random.choice(SENDERS[:6])  # Use only known senders
    
    hour = random.randint(9, 21)  # Business hours
    amount = random.choice(NORMAL_AMOUNTS)
    
    return {
        "transaction_id": str(uuid4())[:8],
        "merchant_id": merchant["id"],
        "merchant_name": merchant["name"],
        "sender": sender,
        "amount": amount,
        "hour": hour,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "description": "Normal Payment",
        "is_simulated": True
    }


def generate_suspicious_transaction():
    """Generate a suspicious UPI transaction (5% probability)."""
    merchant = random.choice(MERCHANTS)
    
    # Pick one of multiple suspicious patterns
    pattern = random.choice([
        "velocity_attack",     # Multiple transactions from same sender
        "structuring",         # Very large amounts
        "after_hours",         # Late night transaction
        "new_sender",          # Unknown sender
        "round_amount"         # Unusual round amount
    ])
    
    if pattern == "velocity_attack":
        sender = random.choice(SENDERS[6:])  # Use bot senders
        hour = random.randint(9, 21)
        amount = random.choice([250, 500])  # Small amounts, rapid-fire
        
    elif pattern == "structuring":
        sender = random.choice(SENDERS[6:])
        hour = random.randint(9, 21)
        amount = random.choice(SUSPICIOUS_AMOUNTS)
        
    elif pattern == "after_hours":
        sender = random.choice(SENDERS[:6])
        hour = random.choice([2, 3, 4, 23])  # 2-4 AM or 11 PM
        amount = random.choice(NORMAL_AMOUNTS)
        
    elif pattern == "new_sender":
        sender = f"unknown_sender_{random.randint(1000, 9999)}@unknown"
        hour = random.randint(9, 21)
        amount = random.choice(NORMAL_AMOUNTS)
        
    else:  # round_amount
        sender = random.choice(SENDERS[:6])
        hour = random.randint(9, 21)
        amount = random.choice([10000, 50000, 100000])
    
    return {
        "transaction_id": str(uuid4())[:8],
        "merchant_id": merchant["id"],
        "merchant_name": merchant["name"],
        "sender": sender,
        "amount": amount,
        "hour": hour,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "description": f"Suspicious: {pattern}",
        "is_simulated": True
    }


def send_transaction(transaction):
    """Send a single transaction to Kafka."""
    producer.send(
        TOPIC,
        value=transaction,
        key=transaction["merchant_id"].encode('utf-8')
    )
    print(f"📤 [{transaction['transaction_id']}] ₹{transaction['amount']} | {transaction['merchant_name']} | Risk: {transaction['description']}")


def main():
    """Continuously produce UPI transactions."""
    print(f"\n🚀 PaySentinel Producer Started")
    print(f"📍 Kafka Broker: {BROKER}")
    print(f"📨 Topic: {TOPIC}")
    print(f"🔄 Sending transactions... (Ctrl+C to stop)\n")
    
    try:
        while True:
            # 95% normal, 5% suspicious
            if random.random() < 0.95:
                tx = generate_normal_transaction()
            else:
                tx = generate_suspicious_transaction()
            
            send_transaction(tx)
            
            # Random delay between 0.5 and 2 seconds
            time.sleep(random.uniform(0.5, 2))
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Producer stopped.")
        producer.close()


if __name__ == "__main__":
    main()

# updated
