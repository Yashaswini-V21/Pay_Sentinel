import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_merchant_transactions(merchant="Raju Kirana", days=60, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    os.makedirs("data", exist_ok=True)

    senders = [
        "priya@okaxis",
        "suresh@oksbi",
        "kavitha@ybl",
        "ramesh@okicici",
        "anitha@paytm",
        "vijay@oksbi",
        "meena@okaxis",
        "kumar@ybl",
        "ganesh@paytm",
    ]
    descs = ["Groceries", "Vegetables", "Milk", "Rice", "Snacks", "Bread"]
    rows, base = [], datetime.now() - timedelta(days=days)

    for d in range(days):
        dt = base + timedelta(days=d)
        for _ in range(np.random.randint(5, 16)):
            rows.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "hour": np.random.randint(8, 22),
                    "amount": round(
                        np.random.choice(
                            [
                                np.random.uniform(20, 500),
                                np.random.uniform(500, 1500),
                            ],
                            p=[0.8, 0.2],
                        ),
                        2,
                    ),
                    "sender": random.choice(senders),
                    "description": random.choice(descs),
                    "is_fraud_gt": 0,
                }
            )

    # Inject suspicious transactions.
    frauds = [
        {"hour": 2, "amount": 8200, "sender": "unknown99@okaxis", "is_fraud_gt": 1},
        {"hour": 3, "amount": 15000, "sender": "newuser12@ybl", "is_fraud_gt": 1},
        {"hour": 1, "amount": 9800, "sender": "temp88@paytm", "is_fraud_gt": 1},
        {"hour": 14, "amount": 4999, "sender": "split01@oksbi", "is_fraud_gt": 1},
        {"hour": 14, "amount": 4998, "sender": "split02@oksbi", "is_fraud_gt": 1},
        {"hour": 11, "amount": 45000, "sender": "bigpay@okicici", "is_fraud_gt": 1},
        {"hour": 23, "amount": 7500, "sender": "latenight@ybl", "is_fraud_gt": 1},
        {"hour": 4, "amount": 3200, "sender": "earlybird@paytm", "is_fraud_gt": 1},
        {"hour": 0, "amount": 11000, "sender": "midnight@okaxis", "is_fraud_gt": 1},
        {"hour": 2, "amount": 6700, "sender": "ghost77@oksbi", "is_fraud_gt": 1},
    ]
    for f in frauds:
        fd = base + timedelta(days=random.randint(0, days - 1))
        rows.append({"date": fd.strftime("%Y-%m-%d"), "description": "Transfer", **f})

    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
    df["transaction_id"] = [f"TXN{str(i).zfill(5)}" for i in range(len(df))]
    df.to_csv("data/sample_transactions.csv", index=False)
    print(f"Generated {len(df)} transactions ({df['is_fraud_gt'].sum()} suspicious)")
    return df


if __name__ == "__main__":
    generate_merchant_transactions()
