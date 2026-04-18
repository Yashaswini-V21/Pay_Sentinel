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
    "sender_freq",
    "is_new_sender",
    "is_known_bank",
    "day_of_week",
    "daily_sender_count",
    "daily_sender_amt",
]


def features(df):
    d = df.copy()
    d["hour"] = pd.to_numeric(d["hour"], errors="coerce").fillna(12)
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce").fillna(0)
    d["amount_log"] = np.log1p(d["amount"])
    d["is_night"] = ((d["hour"] < 6) | (d["hour"] > 22)).astype(int)
    d["is_late_night"] = (d["hour"] < 4).astype(int)
    d["is_biz_hours"] = ((d["hour"] >= 9) & (d["hour"] <= 21)).astype(int)
    d["is_round"] = (d["amount"] % 100 == 0).astype(int)
    d["is_large"] = (d["amount"] > 5000).astype(int)

    banks = ["oksbi", "okaxis", "okicici", "ybl", "paytm"]
    if "sender" in d.columns:
        sc = d["sender"].value_counts()
        d["sender_freq"] = d["sender"].map(sc)
        d["is_new_sender"] = (d["sender_freq"] == 1).astype(int)
        d["is_known_bank"] = d["sender"].apply(
            lambda x: int(any(b in str(x) for b in banks))
        )
    else:
        d["sender_freq"] = d["is_new_sender"] = d["is_known_bank"] = 0

    if "date" in d.columns:
        d["date"] = pd.to_datetime(d["date"], errors="coerce")
        d["day_of_week"] = d["date"].dt.dayofweek
        d["daily_sender_count"] = (
            d.groupby([d["date"].dt.date, "sender"])["amount"].transform("count")
            if "sender" in d.columns
            else 1
        )
        d["daily_sender_amt"] = (
            d.groupby([d["date"].dt.date, "sender"])["amount"].transform("sum")
            if "sender" in d.columns
            else d["amount"]
        )
    else:
        d["day_of_week"] = d["daily_sender_count"] = d["daily_sender_amt"] = 0
    return d


def fingerprint(df):
    return {
        "hour_min": df["hour"].quantile(0.05),
        "hour_max": df["hour"].quantile(0.95),
        "amt_p95": df["amount"].quantile(0.95),
        "amt_p99": df["amount"].quantile(0.99),
        "peak_hour": int(df["hour"].mode()[0]),
        "known_senders": df["sender"].value_counts().head(15).index.tolist()
        if "sender" in df.columns
        else [],
    }


def get_flags(row, fp):
    flags = []
    if row["hour"] < fp["hour_min"] or row["hour"] > fp["hour_max"]:
        flags.append(
            f"Unusual hour ({int(row['hour'])}:00) - you normally trade {int(fp['hour_min'])}-{int(fp['hour_max'])}:00"
        )
    if row["amount"] > fp["amt_p99"]:
        flags.append(f"Amount Rs.{row['amount']:,.0f} is top 1% for your store")
    elif row["amount"] > fp["amt_p95"]:
        flags.append(f"Amount Rs.{row['amount']:,.0f} unusually high for you")

    sender = str(row.get("sender", ""))
    if sender and sender not in fp["known_senders"]:
        flags.append(f"First-time / rare sender: {sender}")
    if row.get("is_late_night", 0):
        flags.append("After-midnight transaction")
    if row.get("daily_sender_count", 1) >= 3:
        flags.append("Same sender 3+ times today - possible structuring")
    return flags or ["Statistical outlier detected by ML"]


class PaySentinelDetector:
    def __init__(self, contamination=0.05):
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
        df_f = features(df)
        self.fp = fingerprint(df_f)
        X = df_f[FEATURES].fillna(0)
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs)
        self.bg = shap.sample(pd.DataFrame(Xs, columns=FEATURES), 50)
        self.explainer = shap.KernelExplainer(
            lambda x: self.model.score_samples(x), self.bg
        )
        self.fitted = True
        return self

    def predict(self, df):
        df_f = features(df)
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
        df_f = features(df)
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

        sv = self.explainer.shap_values(Xs[idx : idx + 1], nsamples=100)[0]
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
        os.makedirs("models", exist_ok=True)
        joblib.dump(self, path)

    def __getstate__(self):
        state = self.__dict__.copy()
        # KernelExplainer holds a local lambda wrapper that is not picklable.
        state["explainer"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @classmethod
    def load(cls, path="models/detector.pkl"):
        return joblib.load(path)


if __name__ == "__main__":
    from generate_data import generate_merchant_transactions

    df = generate_merchant_transactions()
    detector = PaySentinelDetector().fit(df)
    result = detector.predict(df)
    print(result[result["is_anomaly"] == 1][["date", "amount", "hour", "anomaly_score", "risk_level"]])
    detector.save()
    print("Done. Run: streamlit run app.py")
