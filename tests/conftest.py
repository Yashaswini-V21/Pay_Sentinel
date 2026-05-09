"""
PaySentinel shared test fixtures.
Run: pytest tests/ -v
"""
import sys
import os
import pytest
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_df():
    """Minimal valid transaction DataFrame."""
    return pd.DataFrame([
        {"date": "2026-05-01", "hour": 10, "amount": 200, "sender": "priya@okaxis", "description": "Groceries"},
        {"date": "2026-05-01", "hour": 12, "amount": 350, "sender": "suresh@oksbi", "description": "Vegetables"},
        {"date": "2026-05-01", "hour": 14, "amount": 150, "sender": "kavitha@ybl", "description": "Milk"},
        {"date": "2026-05-01", "hour": 16, "amount": 500, "sender": "rajesh@okicici", "description": "Rice"},
        {"date": "2026-05-02", "hour": 11, "amount": 120, "sender": "anita@okaxis", "description": "Bread"},
    ])


@pytest.fixture
def generated_df():
    """Full 60-day synthetic dataset with 20 fraud patterns."""
    from generate_data import generate_merchant_transactions
    return generate_merchant_transactions(merchant_name="Test Store", days=60, seed=42)


@pytest.fixture
def trained_detector(generated_df):
    """Pre-trained detector on full synthetic data."""
    from model import PaySentinelDetector
    detector = PaySentinelDetector(contamination=0.05)
    detector.fit(generated_df)
    return detector
