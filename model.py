import os
import warnings

import joblib
import numpy as np
import pandas as pd
import shap
from scipy.spatial.distance import mahalanobis
from scipy.stats import entropy as shannon_entropy
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Indian public holidays for proximity detection ──
INDIA_HOLIDAYS = pd.to_datetime([
    "2026-01-26", "2026-03-14", "2026-04-14", "2026-05-01",
    "2026-08-15", "2026-10-02", "2026-10-20", "2026-11-01",
])

FEATURES = [
    # ── Core (20) ──
    "amount", "amount_log", "hour", "is_night", "is_late_night", "is_biz_hours",
    "is_round", "is_large", "is_very_large", "sender_freq", "is_new_sender",
    "is_known_bank", "day_of_week", "daily_sender_count", "vel_1h", "vel_6h",
    "amt_dev_median", "amt_ratio_median", "time_gap", "sender_diversity",
    # ── Level 1: Basic (9) ──
    "is_weekend", "hour_sin", "hour_cos", "amount_zscore", "is_exact_thousand",
    "sender_handle_length", "amount_first_digit", "amount_bin", "is_holiday_proximity",
    # ── Level 2: Advanced (10) ──
    "vel_15m", "amt_rolling_std_24h", "amt_pct_change", "sender_recency",
    "hourly_amount_rank", "sender_amt_ratio", "txn_burst_score",
    "cumulative_daily_amount", "night_amount_ratio", "repeat_amount_count",
    # ── Level 3: Expert (6) ──
    "mahalanobis_dist", "sender_graph_weight", "entropy_sender_1d",
    "time_gap_zscore", "sender_cross_merchant_risk", "txn_sequence_anomaly",
]


# ═══════════════════════════════════════════════════════════════
#  LEVEL 3 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _compute_mahalanobis(df, cols):
    """Multivariate distance from the merchant's normal centre."""
    X = df[cols].fillna(0).values
    mean = X.mean(axis=0)
    cov = np.cov(X.T)
    cov_inv = np.linalg.pinv(cov + np.eye(len(cols)) * 1e-6)
    return np.array([mahalanobis(row, mean, cov_inv) for row in X])


def _sender_graph_weight(d):
    """Composite trust score: frequency × recency × consistency."""
    freq = d.groupby("sender")["amount"].transform("count")
    freq_norm = np.log1p(freq) / (np.log1p(freq.max()) + 1e-9)

    last_seen = d.groupby("sender")["_date_parsed"].transform("max")
    max_date = d["_date_parsed"].max()
    recency = 1 - ((max_date - last_seen).dt.days / 60).clip(0, 1)

    amt_cv = d.groupby("sender")["amount"].transform("std") / (
        d.groupby("sender")["amount"].transform("mean") + 1
    )
    consistency = 1 - amt_cv.clip(0, 1)

    return (0.4 * freq_norm + 0.3 * recency + 0.3 * consistency).fillna(0)


def _sender_risk_heuristic(sender):
    """Heuristic risk score based on UPI handle patterns."""
    s = str(sender).lower()
    risk = 0.0
    digit_ratio = sum(c.isdigit() for c in s) / (len(s) + 1)
    risk += digit_ratio * 0.3
    known = ["oksbi", "okaxis", "okicici", "ybl", "paytm", "okhdfcbank"]
    if not any(b in s for b in known):
        risk += 0.3
    if len(s) < 6 or len(s) > 25:
        risk += 0.2
    if any(w in s for w in ["temp", "test", "unknown", "new"]):
        risk += 0.2
    return min(risk, 1.0)


def _sequence_anomaly(d, window=5):
    """Transition-frequency score over recent amount/hour buckets."""
    amt_b = pd.cut(d["amount"], bins=[0, 100, 500, 2000, 10000, np.inf],
                   labels=[0, 1, 2, 3, 4]).astype(float).fillna(2).astype(int)
    hour_b = (d["hour"] // 6).astype(int)
    scores = []
    for i in range(len(d)):
        start = max(0, i - window)
        seq = list(zip(amt_b.iloc[start:i+1], hour_b.iloc[start:i+1]))
        if len(seq) < 3:
            scores.append(0)
            continue
        transitions = sum(1 for j in range(1, len(seq)) if seq[j][0] != seq[j-1][0])
        scores.append(transitions / (len(seq) - 1))
    return scores


# ═══════════════════════════════════════════════════════════════
#  MAIN FEATURE ENGINEERING PIPELINE
# ═══════════════════════════════════════════════════════════════

def engineer(df):
    """
    PaySentinel Feature Engineering Pipeline.
    Produces 45 features across 4 tiers:
      Core (20) → Level 1 Basic (9) → Level 2 Advanced (10) → Level 3 Expert (6)
    """
    d = df.copy()

    # ── 0. Base Setup ──
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce").fillna(0)
    d["amount_log"] = np.log1p(d["amount"])
    d["hour"] = pd.to_numeric(d["hour"], errors="coerce").fillna(12).astype(int)

    if "date" in d.columns:
        d["_ts"] = pd.to_datetime(d["date"]) + pd.to_timedelta(d["hour"], unit='h')
        d["_date_parsed"] = pd.to_datetime(d["date"], errors="coerce")
        d = d.sort_values("_ts")

    # ── 1. Level 1: Basic ──
    d["is_night"] = ((d["hour"] < 6) | (d["hour"] > 22)).astype(int)
    d["is_late_night"] = (d["hour"] < 4).astype(int)
    d["is_biz_hours"] = ((d["hour"] >= 9) & (d["hour"] <= 21)).astype(int)
    d["is_round"] = (d["amount"] % 100 == 0).astype(int)
    d["is_exact_thousand"] = ((d["amount"] % 1000 == 0) & (d["amount"] > 0)).astype(int)
    d["is_large"] = (d["amount"] > 5000).astype(int)
    d["is_very_large"] = (d["amount"] > 15000).astype(int)

    d["day_of_week"] = d["_date_parsed"].dt.dayofweek if "_date_parsed" in d.columns else 0
    d["is_weekend"] = (d["day_of_week"] >= 5).astype(int)

    d["hour_sin"] = np.sin(2 * np.pi * d["hour"] / 24)
    d["hour_cos"] = np.cos(2 * np.pi * d["hour"] / 24)

    d["amount_zscore"] = (d["amount"] - d["amount"].mean()) / (d["amount"].std() + 1e-9)
    d["amount_bin"] = pd.qcut(d["amount"], q=10, labels=False, duplicates="drop").fillna(5)

    # Holiday proximity
    if "_date_parsed" in d.columns:
        d["is_holiday_proximity"] = d["_date_parsed"].apply(
            lambda x: int(min(abs((x - h).days) for h in INDIA_HOLIDAYS) <= 1) if pd.notna(x) else 0
        )
    else:
        d["is_holiday_proximity"] = 0

    if "sender" in d.columns:
        d["sender_handle_length"] = d["sender"].astype(str).str.len()
        d["amount_first_digit"] = d["amount"].apply(
            lambda x: int(str(abs(int(x)))[0]) if x > 0 else 0
        )
        sc = d["sender"].value_counts()
        d["sender_freq"] = d["sender"].map(sc)
        d["is_new_sender"] = (d["sender_freq"] == 1).astype(int)
        known_banks = ["oksbi", "okaxis", "okicici", "ybl", "paytm", "okhdfcbank"]
        d["is_known_bank"] = d["sender"].apply(
            lambda x: int(any(b in str(x).lower() for b in known_banks))
        )
        d["daily_sender_count"] = d.groupby(
            [d["_date_parsed"].dt.date, "sender"]
        )["amount"].transform("count")
    else:
        for c in ["sender_handle_length", "amount_first_digit", "sender_freq",
                   "is_new_sender", "is_known_bank", "daily_sender_count"]:
            d[c] = 0

    # ── 2. Level 2: Advanced (Rolling Windows & Behavior) ──
    if "_ts" in d.columns:
        d = d.set_index("_ts")
        d["vel_1h"] = d["amount"].rolling("1h").count()
        d["vel_6h"] = d["amount"].rolling("6h").count()
        d["vel_15m"] = d["amount"].rolling("15min").count()
        d["amt_rolling_std_24h"] = d["amount"].rolling("24h").std().fillna(0)

        rolling_median = d["amount"].rolling("7d").median()
        d["amt_dev_median"] = (d["amount"] - rolling_median).abs()
        d["amt_ratio_median"] = d["amount"] / (rolling_median + 1)
        d["time_gap"] = d.index.to_series().diff().dt.total_seconds().fillna(0)

        if "sender" in d.columns:
            d["unique_24h"] = d["sender"].rolling("24h").apply(lambda x: len(np.unique(x)))
            d["sender_diversity"] = d["unique_24h"] / (d["vel_6h"] + 1)
            d["sender_recency"] = d.index.to_series().groupby(d["sender"]).diff().dt.days.fillna(999)
        else:
            d["sender_diversity"] = 0
            d["sender_recency"] = 999
        d = d.reset_index()
    else:
        for col in ["vel_1h", "vel_6h", "vel_15m", "amt_rolling_std_24h",
                     "amt_dev_median", "amt_ratio_median", "time_gap",
                     "sender_diversity", "sender_recency"]:
            d[col] = 0

    d["amt_pct_change"] = d["amount"].pct_change().fillna(0).clip(-100, 100)
    d["hourly_amount_rank"] = d.groupby("hour")["amount"].rank(pct=True)

    if "sender" in d.columns:
        sender_avg = d.groupby("sender")["amount"].transform("mean")
        d["sender_amt_ratio"] = d["amount"] / (sender_avg + 1)
    else:
        d["sender_amt_ratio"] = 0

    d["txn_burst_score"] = d["vel_1h"] / (d["vel_1h"].rolling(window=168, min_periods=1).median() + 1)
    d["cumulative_daily_amount"] = d.groupby(d["_date_parsed"].dt.date)["amount"].cumsum()

    day_avg = d.loc[d["is_night"] == 0, "amount"].mean() if len(d[d["is_night"] == 0]) > 0 else 100
    d["night_amount_ratio"] = np.where(d["is_night"] == 1, d["amount"] / (day_avg + 1), 0)
    d["repeat_amount_count"] = d.groupby([d["_date_parsed"].dt.date, "amount"])["amount"].transform("count")

    # ── 3. Level 3: Expert ──
    # 3.1 Mahalanobis distance (multivariate outlier)
    try:
        d["mahalanobis_dist"] = _compute_mahalanobis(d, ["amount_log", "hour", "sender_freq"])
    except Exception:
        d["mahalanobis_dist"] = 0

    # 3.2 Sender-merchant graph weight
    if "sender" in d.columns and "_date_parsed" in d.columns:
        d["sender_graph_weight"] = _sender_graph_weight(d)
    else:
        d["sender_graph_weight"] = 0

    # 3.3 Sender entropy per day
    if "sender" in d.columns and "_date_parsed" in d.columns:
        def _day_entropy(group):
            counts = group.value_counts(normalize=True)
            return shannon_entropy(counts, base=2)
        daily_ent = d.groupby(d["_date_parsed"].dt.date)["sender"].apply(_day_entropy)
        d["entropy_sender_1d"] = d["_date_parsed"].dt.date.map(daily_ent).fillna(0)
    else:
        d["entropy_sender_1d"] = 0

    # 3.4 Time gap z-score
    gap_mean = d["time_gap"].mean()
    gap_std = d["time_gap"].std() + 1e-9
    d["time_gap_zscore"] = ((d["time_gap"] - gap_mean) / gap_std).clip(-10, 10)

    # 3.5 Sender cross-merchant risk heuristic
    if "sender" in d.columns:
        d["sender_cross_merchant_risk"] = d["sender"].apply(_sender_risk_heuristic)
    else:
        d["sender_cross_merchant_risk"] = 0.5

    # 3.6 Transaction sequence anomaly
    d["txn_sequence_anomaly"] = _sequence_anomaly(d)

    # ── Ensure all FEATURES exist ──
    for f in FEATURES:
        if f not in d.columns:
            d[f] = 0

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
    Hybrid Isolation Forest + One-Class SVM detector for UPI transactions.
    Provides normalized risk scores (0-100) and SHAP explainability.
    """
    
    def __init__(self, contamination=0.05):
        """
        Initialize the hybrid detector.
        """
        self.iforest = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.svm = OneClassSVM(
            kernel='rbf',
            gamma='auto',
            nu=contamination
        )
        self.scaler = StandardScaler()
        self.explainer = None
        self.bg = None
        self.fp = {}
        self.fitted = False

    def fit(self, df):
        """
        Train both models on transaction data.
        """
        df_f = engineer(df)
        self.fp = build_fingerprint(df_f)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.fit_transform(X)
        
        # Fit models
        self.iforest.fit(Xs)
        self.svm.fit(Xs)
        
        # Setup SHAP on the primary model (Isolation Forest)
        self.bg = shap.sample(pd.DataFrame(Xs, columns=FEATURES), 50)
        self.explainer = shap.KernelExplainer(
            lambda x: self.iforest.score_samples(x), self.bg
        )
        self.fitted = True
        print(f"✅ Hybrid Model fitted on {len(df)} transactions")
        return self

    def predict(self, df):
        """
        Predict anomalies using hybrid logic.
        Risk Score = 0.4*IF + 0.4*SVM + 0.2*Heuristics
        """
        df_f = engineer(df)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.transform(X)
        
        # 1. Get Base Model Scores
        if_scores = self.iforest.score_samples(Xs)
        svm_scores = self.svm.decision_function(Xs)
        
        # 2. Normalize Scores (0 safe, 1 fraud)
        # IF score_samples: more negative is more anomalous
        if_norm = 1 - ((if_scores - if_scores.min()) / (if_scores.max() - if_scores.min() + 1e-9))
        # SVM decision_function: more negative is more anomalous
        svm_norm = 1 - ((svm_scores - svm_scores.min()) / (svm_scores.max() - svm_scores.min() + 1e-9))
        
        # 3. Rule-based Heuristics (0 to 1) — uses Level 2+3 features
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

        # 4. Ensemble Logic
        final_risk = (0.4 * if_norm) + (0.4 * svm_norm) + (0.2 * rule_score)
        risk_100 = (final_risk * 100).clip(0, 100)

        r = df.copy()
        r["is_anomaly"] = (risk_100 > 75).astype(int)
        r["anomaly_score"] = np.round(risk_100, 1)
        r["risk_level"] = pd.cut(
            r["anomaly_score"],
            [-1, 30, 60, 85, 101],
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
