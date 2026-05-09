from __future__ import annotations
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import logging

"""
PaySentinel: Synthetic UPI Transaction Data Generator
Generates realistic kirana store transactions with injected fraud patterns.
"""

logger = logging.getLogger("paysentinel.data")
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)

try:
    from model import INDIA_HOLIDAYS
except ImportError:
    INDIA_HOLIDAYS = pd.to_datetime(["2026-01-26", "2026-03-14", "2026-04-14", "2026-08-15"])


def generate_merchant_transactions(merchant_name="Kirana Store", days=60, seed=42, save_csv=False):
    """
    Generate synthetic UPI transaction data for a merchant.
    
    Parameters:
    -----------
    merchant_name : str
        Name of the merchant (default: "Kirana Store")
    days : int
        Number of days of historical data (default: 60)
    seed : int
        Random seed for reproducibility (default: 42)
    save_csv : bool
        Whether to save the result to data/sample_transactions.csv
    
    Returns:
    --------
    pd.DataFrame
        Transaction data with columns: date, hour, amount, sender, description, 
        is_fraud_gt, transaction_id
    """
    
    # Set isolated RNG for thread safety and reproducibility
    rng = np.random.default_rng(seed)
    random.seed(seed)
    
    # Configuration
    transactions = []
    transaction_id_counter = 1
    
    # UPI sender profiles for normal transactions
    normal_senders = [
        "priya@okaxis", "suresh@oksbi", "kavitha@ybl", "rajesh@okicici",
        "anita@okaxis", "vikram@oksbi", "divya@ybl", "amit@okaxis",
        "neha@oksbi", "rohan@ybl", "pooja@okicici", "arjun@okaxis"
    ]
    
    # Product descriptions (for kirana store)
    descriptions = ["Groceries", "Vegetables", "Milk", "Rice", "Snacks", "Bread", "Eggs", "Oil"]
    
    # Generate normal transactions (5-15 per day, 8 AM to 9 PM)
    start_date = datetime.now() - timedelta(days=days)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Random number of transactions per day (5-15)
        num_transactions = rng.integers(5, 16)
        
        for _ in range(num_transactions):
            hour = rng.integers(8, 22)  # 8 AM to 9 PM
            amount = rng.uniform(20, 1500)  # Rs. 20 to Rs. 1500
            sender = random.choice(normal_senders)
            description = random.choice(descriptions)
            
            transactions.append({
                "date": date_str,
                "hour": hour,
                "amount": round(float(amount), 2),
                "sender": sender,
                "description": description,
                "is_fraud_gt": 0,
                "transaction_id": f"TXN{transaction_id_counter:05d}"
            })
            transaction_id_counter += 1
    
    # ============================================================================
    # FRAUD INJECTION: Exactly 20 fraud patterns
    # ============================================================================
    
    fraud_transactions = []
    
    # 1-3. THREE late-night large amounts (0-4 AM, Rs.6700-15000)
    for i in range(3):
        current_date = start_date + timedelta(days=int(rng.integers(0, days)))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = rng.integers(0, 5)  # 0-4 AM
        amount = rng.uniform(6700, 15000)
        sender = f"unknown{i}@ybl"  # Unknown senders
        
        fraud_transactions.append({
            "date": date_str,
            "hour": int(hour),
            "amount": round(float(amount), 2),
            "sender": sender,
            "description": "Large Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 4-5. TWO structuring attacks (same sender, just under Rs.5000, 2 PM)
    structuring_sender = "structural@okaxis"
    for i in range(2):
        current_date = start_date + timedelta(days=int(rng.integers(0, days)))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = 14  # 2 PM
        amount = rng.uniform(4800, 4999)  # Just under 5000
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(float(amount), 2),
            "sender": structuring_sender,
            "description": "Structuring Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 6. ONE massive single transaction (Rs.45000, 11 AM)
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    date_str = current_date.strftime("%Y-%m-%d")
    fraud_transactions.append({
        "date": date_str,
        "hour": 11,
        "amount": 45000.0,
        "sender": "bigpay@okicici",
        "description": "Huge Transfer",
        "is_fraud_gt": 1,
        "transaction_id": f"TXN{transaction_id_counter:05d}"
    })
    transaction_id_counter += 1
    
    # 7-8. TWO midnight transfers (23-0 hours)
    midnight_senders = ["latenight@ybl", "midnight@oksbi"]
    for i in range(2):
        current_date = start_date + timedelta(days=int(rng.integers(0, days)))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = random.choice([23, 0])  # 11 PM or midnight
        amount = rng.uniform(3000, 8000)
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(float(amount), 2),
            "sender": midnight_senders[i],
            "description": "Midnight Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 9-10. TWO very early morning (1-4 AM)
    early_morning_senders = ["temp@okaxis", "early@ybl"]
    for i in range(2):
        current_date = start_date + timedelta(days=int(rng.integers(0, days)))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = rng.integers(1, 5)  # 1-4 AM
        amount = rng.uniform(2000, 7000)
        
        fraud_transactions.append({
            "date": date_str,
            "hour": int(hour),
            "amount": round(float(amount), 2),
            "sender": early_morning_senders[i],
            "description": "Early Morning Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1

    # 11. Benford's Law violation (starts with 7,8,9)
    ben_amt = random.choice([700, 800, 900, 7000, 8000, 9000, 7500, 8200, 9100])
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    fraud_transactions.append({
        "date": current_date.strftime("%Y-%m-%d"),
        "hour": random.randint(8, 20),
        "amount": float(ben_amt),
        "sender": "benford_anomaly@upi",
        "description": "Benford Violation",
        "is_fraud_gt": 1,
        "transaction_id": f"TXN{transaction_id_counter:05d}"
    })
    transaction_id_counter += 1

    # 12. Probe-Test-Cashout sequence
    ptc_sender = "ptc_attacker@ybl"
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    ptc_date = current_date.strftime("%Y-%m-%d")
    fraud_transactions.extend([
        {"date": ptc_date, "hour": 14, "amount": 50.0, "sender": ptc_sender, "description": "Probe", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"},
        {"date": ptc_date, "hour": 14, "amount": 500.0, "sender": ptc_sender, "description": "Test", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+1:05d}"},
        {"date": ptc_date, "hour": 15, "amount": 8000.0, "sender": ptc_sender, "description": "Cashout", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+2:05d}"}
    ])
    transaction_id_counter += 3

    # 13. Velocity burst (5 txns in 1 hour)
    vel_sender = "velocity_bot@okaxis"
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    vel_date = current_date.strftime("%Y-%m-%d")
    for _ in range(5):
        fraud_transactions.append({
            "date": vel_date, "hour": 10, "amount": round(float(rng.uniform(200, 400)), 2),
            "sender": vel_sender, "description": "Velocity Burst", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1

    # 14. Weekend large transfer
    weekend_date = None
    for d_off in range(days):
        chk_date = start_date + timedelta(days=d_off)
        if chk_date.weekday() in [5, 6]:
            weekend_date = chk_date
            if random.random() > 0.5: break
    if weekend_date:
        fraud_transactions.append({
            "date": weekend_date.strftime("%Y-%m-%d"), "hour": random.randint(10, 18),
            "amount": round(float(random.uniform(5500, 12000)), 2), "sender": "weekend_fraud@oksbi",
            "description": "Weekend Transfer", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1

    # 15. Holiday proximity spike
    holiday_date = random.choice(list(INDIA_HOLIDAYS))
    spike_date = holiday_date + timedelta(days=random.choice([-1, 0, 1]))
    fraud_transactions.append({
        "date": spike_date.strftime("%Y-%m-%d"), "hour": random.randint(9, 20),
        "amount": round(float(random.uniform(4000, 9000)), 2), "sender": "holiday_spike@ybl",
        "description": "Holiday Transfer", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"
    })
    transaction_id_counter += 1

    # 16. Dormant sender reactivation
    dormant_sender = "dormant_user@okicici"
    # Early normal txns
    for i in range(3):
        early_date = start_date + timedelta(days=i)
        transactions.append({
            "date": early_date.strftime("%Y-%m-%d"), "hour": 12, "amount": 100.0,
            "sender": dormant_sender, "description": "Groceries", "is_fraud_gt": 0, "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    # Late fraud txn
    late_date = start_date + timedelta(days=int(rng.integers(40, 59)))
    fraud_transactions.append({
        "date": late_date.strftime("%Y-%m-%d"), "hour": 15, "amount": round(float(random.uniform(3000, 7000)), 2),
        "sender": dormant_sender, "description": "Dormant Reactivation", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"
    })
    transaction_id_counter += 1

    # 17. Exact threshold structuring
    thresh_sender = "threshold_struct@paytm"
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    t_date = current_date.strftime("%Y-%m-%d")
    fraud_transactions.extend([
        {"date": t_date, "hour": 16, "amount": 9800.0, "sender": thresh_sender, "description": "Threshold Structuring", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"},
        {"date": t_date, "hour": 16, "amount": 9900.0, "sender": thresh_sender, "description": "Threshold Structuring", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+1:05d}"}
    ])
    transaction_id_counter += 2

    # 18. Bot handle
    bot_sender = f"tx{rng.integers(10000000, 99999999)}@upi"
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    fraud_transactions.append({
        "date": current_date.strftime("%Y-%m-%d"), "hour": random.randint(8, 20),
        "amount": round(float(rng.uniform(2000, 6000)), 2), "sender": bot_sender,
        "description": "Bot Handle", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"
    })
    transaction_id_counter += 1

    # 19. Cross-midnight split
    split_sender = "midnight_split@ybl"
    d_off = int(rng.integers(0, days-2))
    day1 = start_date + timedelta(days=d_off)
    day2 = day1 + timedelta(days=1)
    fraud_transactions.extend([
        {"date": day1.strftime("%Y-%m-%d"), "hour": 23, "amount": 4900.0, "sender": split_sender, "description": "Midnight Split", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"},
        {"date": day2.strftime("%Y-%m-%d"), "hour": 0, "amount": 4950.0, "sender": split_sender, "description": "Midnight Split", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+1:05d}"}
    ])
    transaction_id_counter += 2

    # 20. First-digit pattern
    fd_sender = "first9_pattern@okaxis"
    current_date = start_date + timedelta(days=int(rng.integers(0, days)))
    fd_date = current_date.strftime("%Y-%m-%d")
    fraud_transactions.extend([
        {"date": fd_date, "hour": 11, "amount": 9000.0, "sender": fd_sender, "description": "First-Digit Pattern", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter:05d}"},
        {"date": fd_date, "hour": 14, "amount": 9500.0, "sender": fd_sender, "description": "First-Digit Pattern", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+1:05d}"},
        {"date": fd_date, "hour": 17, "amount": 9200.0, "sender": fd_sender, "description": "First-Digit Pattern", "is_fraud_gt": 1, "transaction_id": f"TXN{transaction_id_counter+2:05d}"}
    ])
    transaction_id_counter += 3
    
    # ============================================================================
    # Combine all transactions and shuffle
    # ============================================================================
    
    all_transactions = transactions + fraud_transactions
    df = pd.DataFrame(all_transactions)
    
    # Shuffle rows randomly using isolated RNG
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    # ============================================================================
    # Save to CSV (Optional)
    # ============================================================================
    
    if save_csv:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "sample_transactions.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved generated dataset to: {csv_path}")
    
    # Audit summary
    fraud_count = (df["is_fraud_gt"] == 1).sum()
    logger.info(f"Generated {len(df)} transactions ({fraud_count} fraud injected — 20 patterns)")
    
    return df


if __name__ == "__main__":
    # Generate transactions and save to CSV when run as script
    df = generate_merchant_transactions(
        merchant_name="PaySentinel Kirana Store", 
        days=60, 
        seed=42, 
        save_csv=True
    )
    
    # Quick verification
    print("\n--- Dataset Summary ---")
    print(f"Total rows: {len(df)}")
    print(f"Fraud rows: {(df['is_fraud_gt'] == 1).sum()}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"\nFirst 5 rows:\n{df.head()}")
