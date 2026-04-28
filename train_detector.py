"""
PaySentinel: Train and Save Detector for Streaming Pipeline

This script trains the hybrid detector on sample data and saves it
to models/detector.pkl for use in the Kafka consumer.

Run: python train_detector.py
"""

import pandas as pd
import os
from model import PaySentinelDetector, engineer

def main():
    print("\n" + "="*60)
    print("🚀 PaySentinel Detector Training & Export")
    print("="*60 + "\n")
    
    # 1. Load or generate training data
    data_path = "data/sample_transactions.csv"
    
    if not os.path.exists(data_path):
        print("⚠️  No training data found. Run generate_data.py first.")
        print("   $ python generate_data.py")
        return
    
    print(f"📂 Loading training data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} transactions\n")
    
    # 2. Initialize detector
    print("🔨 Initializing hybrid detector (IF + SVM)...")
    detector = PaySentinelDetector(contamination=0.05)
    
    # 3. Train
    print("🎓 Training on historical data...")
    detector.fit(df)
    
    # 4. Validate on sample
    print("\n📊 Validation on sample transactions:")
    sample = df.head(5)
    results = detector.predict(sample)
    
    print(results[['amount', 'anomaly_score', 'risk_level']].to_string())
    
    # 5. Save
    print("\n💾 Saving detector...")
    detector.save("models/detector.pkl")
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print("="*60)
    print(f"\n📦 Detector saved to: models/detector.pkl")
    print(f"\n🚀 You can now start the streaming pipeline:")
    print(f"   Terminal 1: python kafka_producer.py")
    print(f"   Terminal 2: python kafka_consumer.py")
    print(f"   Terminal 3: streamlit run app.py\n")


if __name__ == "__main__":
    main()

# updated
