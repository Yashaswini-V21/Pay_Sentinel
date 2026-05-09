"""
PaySentinel: Train and Save Detector for Streaming Pipeline

Usage:
  python train_detector.py
  python train_detector.py --merchant "My Store" --contamination 0.05
  python train_detector.py --data data/my_transactions.csv --days 90
  python train_detector.py --validate --show-metrics
"""

import argparse
import sys
import pandas as pd
import os
from model import PaySentinelDetector, engineer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("paysentinel.trainer")


def parse_args():
    parser = argparse.ArgumentParser(
        description="PaySentinel Detector Training Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--merchant", default="PaySentinel Kirana Store",
        help="Merchant name for the model (default: 'PaySentinel Kirana Store')")
    parser.add_argument("--contamination", type=float, default=0.05,
        help="Expected fraud rate 0.01-0.25 (default: 0.05 = 5%%)")
    parser.add_argument("--data", default="data/sample_transactions.csv",
        help="Path to training CSV (default: data/sample_transactions.csv)")
    parser.add_argument("--days", type=int, default=60,
        help="Days of synthetic data if CSV not found (default: 60)")
    parser.add_argument("--output", default="models/detector.pkl",
        help="Output model path (default: models/detector.pkl)")
    parser.add_argument("--validate", action="store_true",
        help="Run validation metrics after training")
    parser.add_argument("--show-metrics", action="store_true",
        help="Show detailed performance metrics")
    return parser.parse_args()


def load_or_generate_data(args):
    if os.path.exists(args.data):
        logger.info(f"Loading data from: {args.data}")
        return pd.read_csv(args.data)
    else:
        logger.info(f"No CSV found at {args.data}. Generating {args.days} days of synthetic data...")
        from generate_data import generate_merchant_transactions
        return generate_merchant_transactions(
            merchant_name=args.merchant, days=args.days, save_csv=True)


def validate_model(detector, df, args):
    logger.info("Running validation...")
    results = detector.predict(df)
    anomalies = results[results["is_anomaly"] == 1]

    logger.info(f"  Total transactions: {len(df):,}")
    logger.info(f"  Anomalies detected: {len(anomalies):,} ({len(anomalies)/len(df)*100:.1f}%)")

    if "is_fraud_gt" in df.columns:
        gt_fraud = (df["is_fraud_gt"] == 1).sum()
        true_pos = ((results["is_anomaly"] == 1) & (df["is_fraud_gt"] == 1)).sum()
        false_neg = ((results["is_anomaly"] == 0) & (df["is_fraud_gt"] == 1)).sum()
        recall = true_pos / max(gt_fraud, 1)
        logger.info(f"  Ground truth fraud: {gt_fraud}")
        logger.info(f"  True positives: {true_pos}")
        logger.info(f"  False negatives: {false_neg}")
        logger.info(f"  Recall: {recall:.2%}")
        if recall < 0.5:
            logger.warning(f"  ⚠️  Low recall ({recall:.2%}) — consider lowering contamination")

    score, label, _ = detector.calculate_resilience_score(results)
    logger.info(f"  Resilience Score: {score}/100 ({label})")


def main():
    args = parse_args()

    if not 0.01 <= args.contamination <= 0.25:
        logger.error("contamination must be between 0.01 and 0.25")
        sys.exit(1)

    df = load_or_generate_data(args)
    logger.info(f"Loaded {len(df):,} transactions")

    logger.info(f"Training detector: merchant='{args.merchant}', contamination={args.contamination}")
    detector = PaySentinelDetector(contamination=args.contamination)
    detector.fit(df)

    if args.validate or args.show_metrics:
        validate_model(detector, df, args)

    detector.save(args.output)
    logger.info(f"✅ Model saved to: {args.output}")
    logger.info(f"   Run: python kafka_consumer.py to start streaming")


if __name__ == "__main__":
    main()
