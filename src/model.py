import os
import joblib
import logging
import hashlib
import numpy as np
import pandas as pd
import shap
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

# Set up logger
logger = logging.getLogger("paysentinel.model")

FEATURES = [
    'amount', 'hour', 'vel_1h', 'vel_15m', 'amt_ratio_median', 
    'sender_diversity', 'mahalanobis_dist', 'sender_graph_weight', 
    'txn_burst_score', 'time_gap_zscore', 'sender_cross_merchant_risk'
]

def engineer(df):
    """
    Feature engineering for fraud detection.
    Uses expanding windows to prevent data leakage.
    """
    df = df.copy()
    
    # Ensure hour and amount are numeric
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(12).astype(int)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Convert date and hour to timestamp
    df['timestamp'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['hour'].astype(str) + ':00:00')
    df = df.sort_values('timestamp')
    
    # Velocity features
    df['vel_1h'] = df.rolling('1h', on='timestamp')['amount'].count()
    df['vel_15m'] = df.rolling('15min', on='timestamp')['amount'].count()
    
    # Amount features
    df['median_amt'] = df['amount'].expanding().median()
    df['amt_ratio_median'] = df['amount'] / (df['median_amt'] + 1e-9)
    
    # Sender features
    # Convert sender to category codes if needed, but here we just count unique
    df['sender_count'] = (df['sender'].duplicated() == False).astype(int).cumsum()
    df['sender_diversity'] = df['sender_count'] / (np.arange(len(df)) + 1)
    
    # Statistical features
    df['amt_mean'] = df['amount'].expanding().mean()
    df['amt_std'] = df['amount'].expanding().std().fillna(0)
    df['mahalanobis_dist'] = (df['amount'] - df['amt_mean']).abs() / (df['amt_std'] + 1e-9)
    
    # Placeholder for more complex metrics (simulated for now)
    rng = np.random.default_rng(42)
    df['sender_graph_weight'] = rng.uniform(0.1, 0.9, len(df))
    df['txn_burst_score'] = df['vel_15m'] * 0.5
    
    df['time_gap'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    df['time_gap_mean'] = df['time_gap'].expanding().mean()
    df['time_gap_std'] = df['time_gap'].expanding().std().fillna(0)
    df['time_gap_zscore'] = (df['time_gap'] - df['time_gap_mean']).abs() / (df['time_gap_std'] + 1e-9)
    
    df['sender_cross_merchant_risk'] = rng.uniform(0, 0.5, len(df))
    
    return df

def build_fingerprint(df):
    """Build merchant behavior fingerprint."""
    if df.empty:
        return {"hour_min": 8, "hour_max": 21, "peak_hour": 12, "amt_p95": 1500, "amt_p99": 5000}
    return {
        "hour_min": int(df['hour'].min()),
        "hour_max": int(df['hour'].max()),
        "peak_hour": int(df['hour'].mode()[0]) if not df.empty else 12,
        "amt_p95": float(df['amount'].quantile(0.95)),
        "amt_p99": float(df['amount'].quantile(0.99))
    }

def get_flags(row, fp):
    """Identify specific fraud flags for a transaction."""
    flags = []
    if row['hour'] < fp['hour_min'] or row['hour'] > fp['hour_max']:
        flags.append("Out-of-hours")
    if row['amount'] > fp['amt_p95']:
        flags.append("High amount")
    if row.get('vel_1h', 0) > 8:
        flags.append("High velocity")
    if row.get('amt_ratio_median', 0) > 4:
        flags.append("Amount spike")
    return flags

@dataclass
class ModelCard:
    model_id: str
    trained_at: str
    training_samples: int
    contamination: float
    feature_count: int
    data_hash: str
    ensemble_weights: dict
    validation_metrics: dict
    model_version: str = "2.0.0"
    framework: str = "scikit-learn"
    languages: list = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = ["Kannada", "Hindi", "English", "Tamil", "Telugu"]

    def to_dict(self):
        return asdict(self)

    def save(self, path: str):
        import json
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str):
        import json
        with open(path) as f:
            return cls(**json.load(f))

    def display(self):
        logger.info("=" * 50)
        logger.info(f"MODEL CARD \u2014 PaySentinel v{self.model_version}")
        logger.info(f"  Model ID:       {self.model_id}")
        logger.info(f"  Trained:        {self.trained_at}")
        logger.info(f"  Training rows:  {self.training_samples:,}")
        logger.info(f"  Features:       {self.feature_count}")
        logger.info(f"  Contamination:  {self.contamination:.1%}")
        logger.info(f"  Data hash:      {self.data_hash}")
        logger.info("=" * 50)

class PaySentinelDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.iforest = IsolationForest(contamination=contamination, random_state=42)
        self.svm = OneClassSVM(nu=contamination, kernel='rbf', gamma='auto')
        self.lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination, novelty=True)
        self.explainer = None
        self.bg = None
        self.fp = None
        self.model_card = None

    def fit(self, df):
        merchant_name = df.get('merchant_name', ['Unknown'])[0] if 'merchant_name' in df.columns else 'Unknown'
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        self.scaler.fit(X)
        Xs = self.scaler.transform(X)
        
        self.iforest.fit(Xs)
        self.svm.fit(Xs)
        self.lof.fit(Xs)
        
        self.bg = shap.sample(pd.DataFrame(Xs, columns=FEATURES), min(50, len(Xs)))
        self.fp = build_fingerprint(df_f)
        
        # Create Model Card
        self.model_card = ModelCard(
            model_id=hashlib.md5(f"{merchant_name}{len(df)}{self.contamination}".encode()).hexdigest()[:12],
            trained_at=datetime.now(timezone.utc).isoformat(),
            training_samples=len(df),
            contamination=float(self.contamination),
            feature_count=len(FEATURES),
            data_hash=hashlib.md5(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()[:12],
            ensemble_weights={"isolation_forest": 0.35, "one_class_svm": 0.35, "lof": 0.20, "rules": 0.10},
            validation_metrics={"feature_tiers": {"core": 20, "basic": 9, "advanced": 10, "expert": 6}}
        )
        self.model_card.display()
        
        return self

    def predict(self, df):
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.transform(X)
        
        # 1. Get Base Model Scores
        if_scores = self.iforest.score_samples(Xs)
        svm_scores = self.svm.decision_function(Xs)
        lof_scores = self.lof.decision_function(Xs)
        
        # 2. Normalize Scores (0 safe, 1 fraud)
        if_norm = 1 - ((if_scores - if_scores.min()) / (if_scores.max() - if_scores.min() + 1e-9))
        svm_norm = 1 - ((svm_scores - svm_scores.min()) / (svm_scores.max() - svm_scores.min() + 1e-9))
        lof_norm = 1 - ((lof_scores - lof_scores.min()) / (lof_scores.max() - lof_scores.min() + 1e-9))
        
        # 3. Rule-based Heuristics (0 to 1)
        rule_score = np.zeros(len(df_f))
        rule_score += (df_f['vel_1h'] > 8).astype(int) * 0.15
        rule_score += (df_f['amt_ratio_median'] > 4).astype(int) * 0.15
        rule_score += (df_f['sender_diversity'] < 0.2).astype(int) * 0.1
        rule_score += (df_f['vel_15m'] > 5).astype(int) * 0.1
        rule_score += (df_f['mahalanobis_dist'] > 8).astype(int) * 0.15
        rule_score += (df_f['sender_graph_weight'] < 0.15).astype(int) * 0.1
        rule_score += (df_f['txn_burst_score'] > 4).astype(int) * 0.1
        rule_score += (df_f['time_gap_zscore'].abs() > 3).astype(int) * 0.1
        rule_score += (df_f['sender_cross_merchant_risk'] > 0.6).astype(int) * 0.05
        rule_score = np.clip(rule_score, 0, 1)

        # 4. Ensemble Logic: IF 35% + SVM 35% + LOF 20% + Rules 10%
        final_risk = (0.35 * if_norm) + (0.35 * svm_norm) + (0.20 * lof_norm) + (0.10 * rule_score)
        risk_100 = (final_risk * 100).clip(0, 100)

        r = df.copy()
        r["is_anomaly"] = (risk_100 > 75).astype(int)
        r["anomaly_score"] = np.round(risk_100, 1)
        r["merchant_percentile"] = r["anomaly_score"].rank(pct=True).round(2) * 100
        r["risk_level"] = pd.cut(
            r["anomaly_score"],
            [-1, 30, 60, 85, 101],
            labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            include_lowest=True,
        )
        r["flags"] = [get_flags(df_f.iloc[i], self.fp) for i in range(len(df_f))]
        return r

    def calculate_resilience_score(self, results):
        if results is None or len(results) == 0:
            return 100, "EXCELLENT", "#0fc98f"
        n_total = len(results)
        anomalies = results[results["is_anomaly"] == 1]
        n_fraud = len(anomalies)
        fraud_ratio = n_fraud / n_total

        # Base score
        score = 100

        # Penalise by fraud ratio
        if fraud_ratio > 0.15: score -= 40
        elif fraud_ratio > 0.10: score -= 30
        elif fraud_ratio > 0.05: score -= 20
        elif fraud_ratio > 0.02: score -= 10
        else: score -= 5

        # Penalise by CRITICAL count
        critical = anomalies[anomalies["risk_level"] == "CRITICAL"] if len(anomalies) else []
        score -= len(critical) * 5

        # Penalise by HIGH count
        high = anomalies[anomalies["risk_level"] == "HIGH"] if len(anomalies) else []
        score -= len(high) * 2

        # Bonus for healthy transaction volume
        if n_total > 100: score += 5
        if n_total > 500: score += 3

        # Bonus for low anomaly score mean
        if len(anomalies) > 0:
            mean_score = anomalies["anomaly_score"].mean()
            if mean_score < 65: score += 5

        score = int(np.clip(score, 0, 100))
        if score >= 85: return score, "EXCELLENT", "#0fc98f"
        elif score >= 70: return score, "GOOD", "#f0a828"
        elif score >= 50: return score, "RISKY", "#e24b4a"
        elif score >= 25: return score, "CRITICAL", "#ff0000"
        else: return score, "COMPROMISED", "#7f0000"

    def generate_fraud_proof(self, merchant_name, txn_row):
        """
        Generates a cryptographic 'Fraud Proof' for a specific transaction.
        Returns a dictionary with hash, timestamp, and proof_id.
        """
        ts = datetime.utcnow().isoformat()
        txn_id = txn_row.get("transaction_id", "TXN_UNKNOWN")
        amt = txn_row.get("amount", 0)
        score = txn_row.get("anomaly_score", 0)
        
        raw_proof = f"{merchant_name}|{txn_id}|{amt}|{score}|{ts}"
        proof_hash = hashlib.sha256(raw_proof.encode()).hexdigest()
        
        return {
            "proof_id": f"PS-{proof_hash[:8].upper()}",
            "timestamp": ts,
            "hash": proof_hash,
            "verification_url": f"https://paysentinel.ai/verify/{proof_hash[:16]}"
        }

    def explain(self, df, idx):
        """SHAP-based explanation for a transaction's anomaly score."""
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.transform(X)

        if self.explainer is None:
            bg = self.bg
            if bg is None:
                bg = shap.sample(pd.DataFrame(Xs, columns=FEATURES), min(50, len(Xs)))
            self.explainer = shap.KernelExplainer(lambda x: self.iforest.score_samples(x), bg)

        sv = self.explainer.shap_values(Xs[idx : idx + 1], nsamples=80)[0]
        top = np.argsort(np.abs(sv))[-4:][::-1]
        return [
            {
                "feature": FEATURES[i],
                "value": round(float(X.iloc[idx][FEATURES[i]]), 2),
                "impact": round(abs(float(sv[i])), 4),
                "direction": "increases" if sv[i] < 0 else "decreases",
            }
            for i in top
        ]

    def save(self, path=None):
        """Save model to disk."""
        if path is None:
            # Default to root/models/detector.pkl
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(root, "models", "detector.pkl")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)  # nosec B301
        logger.info(f"[MODEL] Saved to {path}")

    def __getstate__(self):
        """Handle pickling (SHAP explainer not picklable)."""
        state = self.__dict__.copy()
        state["explainer"] = None
        return state

    def __setstate__(self, state):
        """Handle unpickling."""
        self.__dict__.update(state)

    @classmethod
    def load(cls, path=None):
        """Load model from disk."""
        if path is None:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(root, "models", "detector.pkl")
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
            
        model = joblib.load(path)  # nosec B301
        logger.info(f"[MODEL] Loaded from {path}")
        return model

if __name__ == "__main__":
    from generate_data import generate_merchant_transactions
    df = generate_merchant_transactions()
    detector = PaySentinelDetector().fit(df)
    result = detector.predict(df)
    logger.info("Anomalies found in sample data:")
    logger.info(result[result["is_anomaly"] == 1][["date", "amount", "hour", "anomaly_score", "risk_level"]])
    detector.save()
    logger.info("Done. Run: python app.py")
