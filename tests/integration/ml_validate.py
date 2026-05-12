import os
import sys
import pandas as pd

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "src"))

from generate_data import generate_merchant_transactions
from model import PaySentinelDetector

def validate():
    print("Generating synthetic data for validation...")
    df = generate_merchant_transactions('Test Merchant', days=30)
    
    print(f"Training detector with 5% contamination on {len(df)} rows...")
    detector = PaySentinelDetector(contamination=0.05)
    detector.fit(df)
    
    print("Running predictions...")
    results = detector.predict(df)
    
    anomaly_count = int(results['is_anomaly'].sum())
    print(f"Detected {anomaly_count} anomalies.")
    
    # We expect at least some anomalies in synthetic data with 5% contamination
    assert anomaly_count > 0, "ML Validation failed: No anomalies detected in synthetic data!"
    print("ML Pipeline Validation PASSED.")

if __name__ == "__main__":
    try:
        validate()
    except Exception as e:
        print(f"ML Validation ERROR: {e}")
        sys.exit(1)
