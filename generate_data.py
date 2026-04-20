"""
PaySentinel: Synthetic UPI Transaction Data Generator
Generates realistic kirana store transactions with injected fraud patterns.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os


def generate_merchant_transactions(merchant_name="Kirana Store", days=60, seed=42):
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
    
    Returns:
    --------
    pd.DataFrame
        Transaction data with columns: date, hour, amount, sender, description, 
        is_fraud_gt, transaction_id
    
    Fraud Injections (10 total):
    - 3 late-night large amounts (0-4 AM, Rs.6700-15000)
    - 2 structuring attacks (same sender, just under Rs.5000)
    - 1 massive single transaction (Rs.45000)
    - 2 midnight transfers (23-0 hours)
    - 2 very early morning (1-4 AM)
    """
    
    # Set seed for reproducibility
    np.random.seed(seed)
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
        num_transactions = np.random.randint(5, 16)
        
        for _ in range(num_transactions):
            hour = np.random.randint(8, 22)  # 8 AM to 9 PM
            amount = np.random.uniform(20, 1500)  # Rs. 20 to Rs. 1500
            sender = random.choice(normal_senders)
            description = random.choice(descriptions)
            
            transactions.append({
                "date": date_str,
                "hour": hour,
                "amount": round(amount, 2),
                "sender": sender,
                "description": description,
                "is_fraud_gt": 0,
                "transaction_id": f"TXN{transaction_id_counter:05d}"
            })
            transaction_id_counter += 1
    
    # ============================================================================
    # FRAUD INJECTION: Exactly 10 fraud patterns
    # ============================================================================
    
    fraud_transactions = []
    
    # 1. THREE late-night large amounts (0-4 AM, Rs.6700-15000)
    for i in range(3):
        current_date = start_date + timedelta(days=np.random.randint(0, days))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = np.random.randint(0, 5)  # 0-4 AM
        amount = np.random.uniform(6700, 15000)
        sender = f"unknown{i}@ybl"  # Unknown senders
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(amount, 2),
            "sender": sender,
            "description": "Large Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 2. TWO structuring attacks (same sender, just under Rs.5000, 2 PM)
    structuring_sender = "structural@okaxis"
    for i in range(2):
        current_date = start_date + timedelta(days=np.random.randint(0, days))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = 14  # 2 PM
        amount = np.random.uniform(4800, 4999)  # Just under 5000
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(amount, 2),
            "sender": structuring_sender,
            "description": "Structuring Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 3. ONE massive single transaction (Rs.45000, 11 AM)
    current_date = start_date + timedelta(days=np.random.randint(0, days))
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
    
    # 4. TWO midnight transfers (23-0 hours)
    midnight_senders = ["latenight@ybl", "midnight@oksbi"]
    for i in range(2):
        current_date = start_date + timedelta(days=np.random.randint(0, days))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = random.choice([23, 0])  # 11 PM or midnight
        amount = np.random.uniform(3000, 8000)
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(amount, 2),
            "sender": midnight_senders[i],
            "description": "Midnight Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # 5. TWO very early morning (1-4 AM)
    early_morning_senders = ["temp@okaxis", "early@ybl"]
    for i in range(2):
        current_date = start_date + timedelta(days=np.random.randint(0, days))
        date_str = current_date.strftime("%Y-%m-%d")
        hour = np.random.randint(1, 5)  # 1-4 AM
        amount = np.random.uniform(2000, 7000)
        
        fraud_transactions.append({
            "date": date_str,
            "hour": hour,
            "amount": round(amount, 2),
            "sender": early_morning_senders[i],
            "description": "Early Morning Transfer",
            "is_fraud_gt": 1,
            "transaction_id": f"TXN{transaction_id_counter:05d}"
        })
        transaction_id_counter += 1
    
    # ============================================================================
    # Combine all transactions and shuffle
    # ============================================================================
    
    all_transactions = transactions + fraud_transactions
    df = pd.DataFrame(all_transactions)
    
    # Shuffle rows randomly
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    # ============================================================================
    # Save to CSV
    # ============================================================================
    
    os.makedirs("data", exist_ok=True)
    csv_path = "data/sample_transactions.csv"
    df.to_csv(csv_path, index=False)
    
    # Print summary
    fraud_count = (df["is_fraud_gt"] == 1).sum()
    print(f"✅ {len(df)} transactions generated ({fraud_count} fraud injected)")
    print(f"   Saved to: {csv_path}")
    
    return df


if __name__ == "__main__":
    # Generate transactions
    df = generate_merchant_transactions(merchant_name="PaySentinel Kirana Store", days=60, seed=42)
    
    # Quick verification
    print("\n--- Dataset Summary ---")
    print(f"Total rows: {len(df)}")
    print(f"Fraud rows: {(df['is_fraud_gt'] == 1).sum()}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"\nFirst 5 rows:\n{df.head()}")
