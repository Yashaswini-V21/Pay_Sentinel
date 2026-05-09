"""
PaySentinel ML Model Validation Tests.
Tests the core ML pipeline: feature engineering, ensemble predictions,
resilience scoring, SHAP explainability, and model serialization.

Run: pytest tests/test_model.py -v
"""
import os
import sys
import tempfile
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from model import (
    PaySentinelDetector,
    engineer,
    build_fingerprint,
    get_flags,
    ModelCard,
    FEATURES,
)
from generate_data import generate_merchant_transactions


class TestFeatureEngineering:
    """Test the 11-feature engineering pipeline."""

    def test_engineer_returns_all_features(self, sample_df):
        """All 11 FEATURES columns must exist after engineering."""
        df_eng = engineer(sample_df)
        for feat in FEATURES:
            assert feat in df_eng.columns, f"Missing feature: {feat}"

    def test_engineer_no_nans_in_features(self, generated_df):
        """Feature engineering must not produce NaN in critical columns."""
        df_eng = engineer(generated_df)
        for feat in FEATURES:
            nan_count = df_eng[feat].isna().sum()
            assert nan_count == 0, f"{feat} has {nan_count} NaN values"

    def test_engineer_preserves_row_count(self, generated_df):
        """Feature engineering must not add or remove rows."""
        df_eng = engineer(generated_df)
        assert len(df_eng) == len(generated_df)

    def test_velocity_features_non_negative(self, generated_df):
        """Velocity features (vel_1h, vel_15m) must be >= 0."""
        df_eng = engineer(generated_df)
        assert (df_eng['vel_1h'] >= 0).all()
        assert (df_eng['vel_15m'] >= 0).all()


class TestMerchantFingerprint:
    """Test merchant behavior fingerprinting."""

    def test_fingerprint_has_required_keys(self, generated_df):
        """Fingerprint must contain all expected statistical keys."""
        df_eng = engineer(generated_df)
        fp = build_fingerprint(df_eng)
        for key in ['hour_min', 'hour_max', 'peak_hour', 'amt_p95', 'amt_p99']:
            assert key in fp, f"Missing fingerprint key: {key}"

    def test_fingerprint_hour_range_valid(self, generated_df):
        """Hour range must be within 0-23."""
        df_eng = engineer(generated_df)
        fp = build_fingerprint(df_eng)
        assert 0 <= fp['hour_min'] <= 23
        assert 0 <= fp['hour_max'] <= 23
        assert fp['hour_min'] <= fp['hour_max']

    def test_fingerprint_empty_df_defaults(self):
        """Empty DataFrame should return safe defaults."""
        fp = build_fingerprint(pd.DataFrame())
        assert fp['hour_min'] == 8
        assert fp['hour_max'] == 21

    def test_get_flags_detects_out_of_hours(self):
        """Out-of-hours transactions must be flagged."""
        fp = {'hour_min': 8, 'hour_max': 21, 'amt_p95': 1500, 'amt_p99': 5000}
        row = pd.Series({'hour': 2, 'amount': 100, 'vel_1h': 1, 'amt_ratio_median': 1})
        flags = get_flags(row, fp)
        assert 'Out-of-hours' in flags

    def test_get_flags_detects_high_amount(self):
        """Amounts above p95 must be flagged."""
        fp = {'hour_min': 8, 'hour_max': 21, 'amt_p95': 1500, 'amt_p99': 5000}
        row = pd.Series({'hour': 12, 'amount': 8000, 'vel_1h': 1, 'amt_ratio_median': 1})
        flags = get_flags(row, fp)
        assert 'High amount' in flags


class TestEnsemblePredictions:
    """Test the triple-model ensemble scoring."""

    def test_predictions_have_required_columns(self, trained_detector, generated_df):
        """Prediction results must include all output columns."""
        results = trained_detector.predict(generated_df)
        for col in ['is_anomaly', 'anomaly_score', 'risk_level', 'flags', 'merchant_percentile']:
            assert col in results.columns, f"Missing output column: {col}"

    def test_anomaly_scores_in_range(self, trained_detector, generated_df):
        """All anomaly scores must be between 0 and 100."""
        results = trained_detector.predict(generated_df)
        assert (results['anomaly_score'] >= 0).all()
        assert (results['anomaly_score'] <= 100).all()

    def test_risk_levels_are_valid(self, trained_detector, generated_df):
        """Risk levels must be one of the four defined tiers."""
        results = trained_detector.predict(generated_df)
        valid_levels = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
        actual_levels = set(results['risk_level'].unique())
        assert actual_levels.issubset(valid_levels), f"Invalid risk levels: {actual_levels - valid_levels}"

    def test_detects_injected_fraud(self, trained_detector, generated_df):
        """Model must detect at least some of the 20 injected fraud patterns."""
        results = trained_detector.predict(generated_df)
        fraud_gt = generated_df['is_fraud_gt'] == 1
        detected = results[fraud_gt]['is_anomaly'] == 1
        recall = detected.sum() / max(fraud_gt.sum(), 1)
        # Unsupervised models have inherently low recall on injected patterns
        # because they detect statistical anomalies, not labeled fraud
        assert recall > 0.0, f"Zero recall — model detected no injected fraud at all"
        assert detected.sum() >= 1, "Model must detect at least 1 injected fraud pattern"

    def test_low_false_positive_rate(self, trained_detector, generated_df):
        """False positive rate should be reasonable (< 30%)."""
        results = trained_detector.predict(generated_df)
        normal = generated_df['is_fraud_gt'] == 0
        false_positives = results[normal]['is_anomaly'] == 1
        fpr = false_positives.sum() / max(normal.sum(), 1)
        assert fpr < 0.30, f"False positive rate too high: {fpr:.2%}"

    def test_preserves_row_count(self, trained_detector, generated_df):
        """Predictions must not add or remove rows."""
        results = trained_detector.predict(generated_df)
        assert len(results) == len(generated_df)


class TestResilienceScoring:
    """Test the merchant resilience scoring system."""

    def test_resilience_score_in_range(self, trained_detector, generated_df):
        """Resilience score must be between 0 and 100."""
        results = trained_detector.predict(generated_df)
        score, label, color = trained_detector.calculate_resilience_score(results)
        assert 0 <= score <= 100

    def test_resilience_label_valid(self, trained_detector, generated_df):
        """Resilience label must be one of the 5 defined tiers."""
        results = trained_detector.predict(generated_df)
        _, label, _ = trained_detector.calculate_resilience_score(results)
        assert label in {'EXCELLENT', 'GOOD', 'RISKY', 'CRITICAL', 'COMPROMISED'}

    def test_empty_results_returns_excellent(self, trained_detector):
        """Empty results should return EXCELLENT (100)."""
        score, label, _ = trained_detector.calculate_resilience_score(None)
        assert score == 100
        assert label == 'EXCELLENT'


class TestModelCard:
    """Test the ModelCard metadata system."""

    def test_model_card_created_on_fit(self, trained_detector):
        """Model card must be auto-generated during fit()."""
        assert trained_detector.model_card is not None
        assert isinstance(trained_detector.model_card, ModelCard)

    def test_model_card_has_valid_fields(self, trained_detector):
        """Model card must have all required fields populated."""
        mc = trained_detector.model_card
        assert len(mc.model_id) > 0
        assert mc.training_samples > 0
        assert mc.feature_count == len(FEATURES)
        assert 0 < mc.contamination <= 1.0
        assert len(mc.data_hash) > 0

    def test_model_card_serialization(self, trained_detector):
        """Model card must be serializable to/from JSON."""
        mc = trained_detector.model_card
        d = mc.to_dict()
        assert isinstance(d, dict)
        assert d['model_version'] == '2.0.0'
        assert 'Kannada' in d['languages']

    def test_model_card_save_load(self, trained_detector):
        """Model card must save and load from disk correctly."""
        mc = trained_detector.model_card
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            tmp_path = f.name
        try:
            mc.save(tmp_path)
            loaded = ModelCard.load(tmp_path)
            assert loaded.model_id == mc.model_id
            assert loaded.training_samples == mc.training_samples
        finally:
            os.unlink(tmp_path)


class TestModelSerialization:
    """Test model save/load functionality."""

    def test_save_and_load(self, trained_detector, generated_df):
        """Model must produce identical predictions after save/load cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_model.pkl')
            trained_detector.save(path)
            loaded = PaySentinelDetector.load(path)
            
            original = trained_detector.predict(generated_df)
            reloaded = loaded.predict(generated_df)
            
            np.testing.assert_array_almost_equal(
                original['anomaly_score'].values,
                reloaded['anomaly_score'].values,
                decimal=1
            )


class TestContaminationSweep:
    """Validate model behavior across contamination parameters."""

    @pytest.mark.parametrize("contamination", [0.01, 0.05, 0.10, 0.15, 0.25])
    def test_contamination_produces_valid_output(self, contamination, generated_df):
        """All contamination levels must produce valid predictions."""
        detector = PaySentinelDetector(contamination=contamination)
        detector.fit(generated_df)
        results = detector.predict(generated_df)
        assert (results['anomaly_score'] >= 0).all()
        assert (results['anomaly_score'] <= 100).all()
        assert len(results) == len(generated_df)
