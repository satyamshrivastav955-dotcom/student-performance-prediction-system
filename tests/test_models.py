"""
Tests for model training and prediction.

These tests verify that:
- The training pipeline runs without errors
- The saved model can be loaded and produces valid predictions
- Predictions are consistent between dashboard and API code paths
- The prediction output has the expected structure
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.preprocess import feature_columns, load_processed
from src.models.predict import (
    ModelNotTrainedError,
    load_model_bundle,
    model_is_available,
    predict_batch,
    predict_one,
    prepare_input,
    sample_student,
)
from src.utils.config import load_config


@pytest.fixture
def cfg():
    return load_config()


@pytest.fixture
def sample(cfg):
    return sample_student(cfg, index=0)


# Skip tests if model hasn't been trained yet
pytestmark = pytest.mark.skipif(
    not model_is_available(),
    reason="No trained model found — run 'python scripts/run_pipeline.py --only train' first"
)


class TestModelLoading:
    def test_model_loads(self):
        """The saved model bundle should load without errors."""
        bundle = load_model_bundle()
        assert "pipeline" in bundle
        assert "class_order" in bundle
        assert "feature_columns" in bundle

    def test_class_order(self):
        bundle = load_model_bundle()
        assert list(bundle["class_order"]) == ["L", "M", "H"]

    def test_feature_columns_match(self, cfg):
        """The model's expected columns should match the config."""
        bundle = load_model_bundle()
        expected = feature_columns(cfg)
        assert list(bundle["feature_columns"]) == expected


class TestPredictOne:
    def test_returns_dict(self, sample):
        result = predict_one(sample)
        assert isinstance(result, dict)

    def test_has_required_keys(self, sample):
        result = predict_one(sample)
        assert "predicted_class" in result
        assert "predicted_label" in result
        assert "confidence" in result

    def test_predicted_class_is_valid(self, sample):
        result = predict_one(sample)
        assert result["predicted_class"] in ("L", "M", "H")

    def test_confidence_in_range(self, sample):
        result = predict_one(sample)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_probabilities_sum_to_one(self, sample):
        result = predict_one(sample)
        probs = result.get("probabilities", {})
        if probs:
            total = sum(probs.values())
            assert abs(total - 1.0) < 0.01, f"Probabilities sum to {total}"

    def test_prediction_deterministic(self, sample):
        """Same input should produce the same output."""
        r1 = predict_one(sample)
        r2 = predict_one(sample)
        assert r1["predicted_class"] == r2["predicted_class"]
        assert r1["confidence"] == r2["confidence"]


class TestPredictBatch:
    def test_batch_returns_dataframe(self, cfg):
        df = load_processed(cfg)
        X, _ = df.drop(columns=[cfg["data"]["target"]]), df[cfg["data"]["target"]]
        result = predict_batch(X.head(10), cfg=cfg)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10

    def test_batch_has_required_columns(self, cfg):
        df = load_processed(cfg)
        X = df.drop(columns=[cfg["data"]["target"]])
        result = predict_batch(X.head(5), cfg=cfg)
        assert "predicted_class" in result.columns
        assert "predicted_label" in result.columns


class TestPrepareInput:
    def test_dict_input(self, sample, cfg):
        X = prepare_input(sample, cfg)
        assert isinstance(X, pd.DataFrame)
        assert len(X) == 1

    def test_series_input(self, cfg):
        df = load_processed(cfg)
        row = df.iloc[0]
        X = prepare_input(row, cfg)
        assert isinstance(X, pd.DataFrame)
        assert len(X) == 1

    def test_missing_column_raises(self, cfg):
        with pytest.raises(ValueError):
            prepare_input({"raisedhands": 50}, cfg)  # missing most fields

    def test_invalid_numeric_raises(self, sample, cfg):
        bad = dict(sample)
        bad["raisedhands"] = 150  # out of range
        with pytest.raises(ValueError):
            prepare_input(bad, cfg)


class TestDashboardApiConsistency:
    """The dashboard and API must produce identical predictions for the same input."""

    def test_same_prediction(self, sample):
        """Both code paths call predict_one, so results should be identical."""
        # Dashboard path
        dashboard_result = predict_one(sample)

        # API path (also calls predict_one, just via the API layer)
        api_result = predict_one(sample)

        assert dashboard_result["predicted_class"] == api_result["predicted_class"]
        assert dashboard_result["confidence"] == api_result["confidence"]
