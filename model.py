import os
import warnings

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

FEATURES = [
    "amount",
    "amount_log",
    "hour",
    "is_night",
    "is_late_night",
    "is_biz_hours",
    "is_round",
    "is_large",
    "is_very_large",
    "sender_freq",
    "is_new_sender",
    "is_known_bank",
    "day_of_week",
    "daily_sender_count",
]


def engineer(df):
    """
    Feature engineering for anomaly detection.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Transaction data with columns: date, hour, amount, sender, description, etc.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with 14 engineered features added
    
    Features Created (14 total):
    1. amount - numeric conversion
    2. amount_log - log-transformed amount
    3. hour - numeric conversion
    4. is_night - binary flag for night hours (< 6 AM OR > 10 PM)
    5. is_late_night - binary flag for very late night (< 4 AM)
    6. is_biz_hours - binary flag for business hours (9 AM - 9 PM)
    7. is_round - binary flag for round amounts (divisible by 100)
    8. is_large - binary flag for large transactions (> Rs.5000)
    9. is_very_large - binary flag for very large transactions (> Rs.15000)
    10. sender_freq - frequency of sender in dataset
    11. is_new_sender - binary flag for new/first-time sender
    12. is_known_bank - binary flag for known bank UPI providers
    13. day_of_week - day of week (0-6)
    14. daily_sender_count - count of sender transactions per day
    """
    
    d = df.copy()
    
    # ========================================================================
    # NUMERIC FEATURES
    # ========================================================================
    
    # Convert amount to numeric and fill nulls
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce").fillna(0)
    
    # Log-transformed amount (log1p to handle zeros)
    d["amount_log"] = np.log1p(d["amount"])
    
    # Convert hour to numeric and fill nulls with 12 (noon)
    d["hour"] = pd.to_numeric(d["hour"], errors="coerce").fillna(12).astype(int)
    
    # ========================================================================
    # TIME-BASED FEATURES
    # ========================================================================
    
    # Night hours: < 6 AM OR > 10 PM
    d["is_night"] = ((d["hour"] < 6) | (d["hour"] > 22)).astype(int)
    
    # Very late night: < 4 AM
    d["is_late_night"] = (d["hour"] < 4).astype(int)
    
    # Business hours: 9 AM to 9 PM
    d["is_biz_hours"] = ((d["hour"] >= 9) & (d["hour"] <= 21)).astype(int)
    
    # Round amount (divisible by 100)
    d["is_round"] = (d["amount"] % 100 == 0).astype(int)
    
    # Large transaction (> Rs.5000)
    d["is_large"] = (d["amount"] > 5000).astype(int)
    
    # Very large transaction (> Rs.15000)
    d["is_very_large"] = (d["amount"] > 15000).astype(int)
    
    # ========================================================================
    # SENDER-BASED FEATURES
    # ========================================================================
    
    if "sender" in d.columns:
        # Sender frequency in dataset
        sc = d["sender"].value_counts()
        d["sender_freq"] = d["sender"].map(sc)
        
        # New sender (first time, freq == 1)
        d["is_new_sender"] = (d["sender_freq"] == 1).astype(int)
        
        # Known bank UPI providers
        known_banks = ["oksbi", "okaxis", "okicici", "ybl", "paytm", "okhdfcbank"]
        d["is_known_bank"] = d["sender"].apply(
            lambda x: int(any(b in str(x).lower() for b in known_banks))
        )
    else:
        # If sender column missing, set features to 0
        d["sender_freq"] = 0
        d["is_new_sender"] = 0
        d["is_known_bank"] = 0
    
    # ========================================================================
    # DATE-BASED FEATURES
    # ========================================================================
    
    if "date" in d.columns:
        # Convert to datetime
        d["_date_parsed"] = pd.to_datetime(d["date"], errors="coerce")
        
        # Day of week (0=Monday, 6=Sunday)
        d["day_of_week"] = d["_date_parsed"].dt.dayofweek
        
        # Daily sender count: how many times this sender sent TODAY
        if "sender" in d.columns:
            d["daily_sender_count"] = (
                d.groupby([d["_date_parsed"].dt.date, "sender"])["amount"].transform("count")
            )
        else:
            d["daily_sender_count"] = 0
        
        # Drop temporary column
        d = d.drop(columns=["_date_parsed"])
    else:
        # If date column missing, set features to 0
        d["day_of_week"] = 0
        d["daily_sender_count"] = 0
    
    return d


# Legacy function name for backward compatibility
def features(df):
    """Wrapper for engineer() for backward compatibility."""
    return engineer(df)


def build_fingerprint(df):
    """
    Build a merchant transaction profile for baseline behavior.
    Learns what is NORMAL for this specific merchant from their history.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Feature-engineered transaction data (should have FEATURES)
    
    Returns:
    --------
    dict
        Merchant baseline profile with keys:
        - hour_min: 5th percentile of hours (int)
        - hour_max: 95th percentile of hours (int)
        - amt_p95: 95th percentile of amounts (float)
        - amt_p99: 99th percentile of amounts (float)
        - peak_hour: most common hour (int)
        - known_senders: top 15 senders by frequency (list)
    """
    return {
        "hour_min": int(df["hour"].quantile(0.05)),
        "hour_max": int(df["hour"].quantile(0.95)),
        "amt_p95": df["amount"].quantile(0.95),
        "amt_p99": df["amount"].quantile(0.99),
        "peak_hour": int(df["hour"].mode()[0]) if len(df["hour"].mode()) > 0 else 12,
        "known_senders": df["sender"].value_counts().head(15).index.tolist()
        if "sender" in df.columns
        else [],
    }


# Backward compatibility alias
def fingerprint(df):
    """Alias for build_fingerprint() for backward compatibility."""
    return build_fingerprint(df)


def get_flags(row, fp):
    """
    Generate human-readable fraud indicators from a transaction.
    Checks a single transaction row against the merchant fingerprint and returns 
    plain-language reasons it's suspicious.
    
    Parameters:
    -----------
    row : pd.Series
        A single engineered transaction
    fp : dict
        Merchant fingerprint/profile (from build_fingerprint)
    
    Returns:
    --------
    list
        List of explanatory text flags
    """
    flags = []
    
    # Check: Unusual hour (outside 5th-95th percentile range)
    if row["hour"] < fp["hour_min"] or row["hour"] > fp["hour_max"]:
        flags.append(
            f"Unusual hour ({int(row['hour'])}:00) — you normally trade {int(fp['hour_min'])}–{int(fp['hour_max'])}:00"
        )
    
    # Check: Top 1% amount
    if row["amount"] > fp["amt_p99"]:
        flags.append(f"Amount ₹{row['amount']:,.0f} is top 1% for your store")
    # Check: Unusually high but not top 1%
    elif row["amount"] > fp["amt_p95"]:
        flags.append(f"Amount ₹{row['amount']:,.0f} unusually high (your normal max ≈ ₹{fp['amt_p95']:,.0f})")
    
    # Check: First-time or rare sender
    sender = str(row.get("sender", "")).strip()
    known_senders = fp.get("known_senders", [])
    if sender and sender not in known_senders:
        flags.append(f"First-time or rare sender: {sender}")
    
    # Check: After-midnight transaction
    if row.get("is_late_night", 0) == 1:
        flags.append("After-midnight transaction")
    
    # Check: Same sender multiple times today (structuring pattern)
    if row.get("daily_sender_count", 0) >= 3:
        flags.append("Same sender 3+ times today — possible structuring")
    
    # Default: if no specific flags, return generic statistical outlier
    return flags or ["Statistical outlier detected by ML"]


class PaySentinelDetector:
    """
    Isolation Forest-based fraud detection model for UPI transactions.
    Includes SHAP explainability and merchant fingerprinting.
    """
    
    def __init__(self, contamination=0.05):
        """
        Initialize the detector.
        
        Parameters:
        -----------
        contamination : float
            Expected proportion of anomalies (default: 0.05)
        """
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.explainer = None
        self.bg = None
        self.fp = {}
        self.fitted = False

    def fit(self, df):
        """
        Train the detector on transaction data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training transaction data
        
        Returns:
        --------
        self
        """
        df_f = engineer(df)
        self.fp = build_fingerprint(df_f)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs)
        self.bg = shap.sample(pd.DataFrame(Xs, columns=FEATURES), 50)
        self.explainer = shap.KernelExplainer(
            lambda x: self.model.score_samples(x), self.bg
        )
        self.fitted = True
        print(f"✅ Model fitted on {len(df)} transactions")
        return self

    def predict(self, df):
        """
        Predict anomalies and risk scores.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Transaction data to predict on
        
        Returns:
        --------
        pd.DataFrame
            Original data with added columns: is_anomaly, anomaly_score, risk_level, flags
        """
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.transform(X)
        preds = self.model.predict(Xs)
        scores = self.model.score_samples(Xs)

        mn, mx = scores.min(), scores.max()
        risk = 100 * (1 - (scores - mn) / (mx - mn + 1e-9))

        r = df.copy()
        r["is_anomaly"] = (preds == -1).astype(int)
        r["anomaly_score"] = np.round(risk, 1)
        r["risk_level"] = pd.cut(
            r["anomaly_score"],
            [0, 30, 60, 80, 100],
            labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            include_lowest=True,
        )
        r["flags"] = [get_flags(df_f.iloc[i], self.fp) for i in range(len(df_f))]
        return r

    def explain(self, df, idx):
        """
        Get SHAP-based explanation for a transaction's anomaly score.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Full transaction dataset
        idx : int
            Row index of transaction to explain
        
        Returns:
        --------
        list
            Top 4 contributing features with impact scores
        """
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.transform(X)

        if self.explainer is None:
            bg = self.bg
            if bg is None:
                bg = shap.sample(
                    pd.DataFrame(Xs, columns=FEATURES), min(50, len(Xs))
                )
            self.explainer = shap.KernelExplainer(
                lambda x: self.model.score_samples(x), bg
            )

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

    def save(self, path="models/detector.pkl"):
        """Save model to disk."""
        os.makedirs("models", exist_ok=True)
        joblib.dump(self, path)
        print(f"💾 Saved: {path}")

    def __getstate__(self):
        """Handle pickling (SHAP explainer not picklable)."""
        state = self.__dict__.copy()
        state["explainer"] = None
        return state

    def __setstate__(self, state):
        """Handle unpickling."""
        self.__dict__.update(state)

    @classmethod
    def load(cls, path="models/detector.pkl"):
        """Load model from disk."""
        model = joblib.load(path)
        print(f"✅ Detector loaded from {path}")
        return model


if __name__ == "__main__":
    from generate_data import generate_merchant_transactions

    df = generate_merchant_transactions()
    detector = PaySentinelDetector().fit(df)
    result = detector.predict(df)
    print(result[result["is_anomaly"] == 1][["date", "amount", "hour", "anomaly_score", "risk_level"]])
    detector.save()
    print("Done. Run: streamlit run app.py")
