"""
Tests for the preprocessing pipeline.

Checks that:
- Cleaned data has no duplicates
- All expected columns are present
- Numeric features are within valid ranges
- Target column has only valid classes
- Encoding functions round-trip correctly
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.preprocess import (
    build_preprocessor,
    clean_dataframe,
    decode_target,
    encode_target,
    feature_columns,
    load_processed,
    split_features_target,
)
from src.utils.config import load_config


@pytest.fixture
def cfg():
    return load_config()


@pytest.fixture
def cleaned_df(cfg):
    return load_processed(cfg)


class TestCleanDataframe:
    def test_no_duplicates(self, cleaned_df):
        """After cleaning, there should be zero exact duplicate rows."""
        assert cleaned_df.duplicated().sum() == 0

    def test_has_all_feature_columns(self, cleaned_df, cfg):
        """Every feature column listed in config should exist in the data."""
        cols = feature_columns(cfg)
        missing = [c for c in cols if c not in cleaned_df.columns]
        assert missing == [], f"Missing columns: {missing}"

    def test_has_target_column(self, cleaned_df, cfg):
        target = cfg["data"]["target"]
        assert target in cleaned_df.columns

    def test_numeric_features_in_range(self, cleaned_df, cfg):
        """Numeric engagement counters should be between 0 and 100."""
        for col in cfg["data"]["numeric_features"]:
            assert cleaned_df[col].min() >= 0, f"{col} has values below 0"
            assert cleaned_df[col].max() <= 100, f"{col} has values above 100"

    def test_target_classes_valid(self, cleaned_df, cfg):
        """Target should contain only the classes defined in config."""
        valid = set(cfg["data"]["target_classes"])
        actual = set(cleaned_df[cfg["data"]["target"]].unique())
        assert actual.issubset(valid), f"Unexpected classes: {actual - valid}"

    def test_no_missing_in_features(self, cleaned_df, cfg):
        """After cleaning, no feature column should have missing values."""
        cols = feature_columns(cfg)
        for col in cols:
            assert cleaned_df[col].isna().sum() == 0, f"Missing values in {col}"


class TestEncodeTarget:
    def test_encode_produces_integers(self, cleaned_df, cfg):
        target = cfg["data"]["target"]
        encoded, classes = encode_target(cleaned_df[target], cfg)
        assert encoded.dtype in (np.int32, np.int64, int)
        assert set(encoded) <= {0, 1, 2}

    def test_encode_decode_roundtrip(self, cleaned_df, cfg):
        """encode -> decode should recover the original labels."""
        target = cfg["data"]["target"]
        original = cleaned_df[target].values
        encoded, classes = encode_target(cleaned_df[target], cfg)
        decoded = decode_target(encoded, cfg)
        assert list(decoded) == list(original)

    def test_class_order_is_semantic(self, cfg):
        """L=0, M=1, H=2 — so higher code = better outcome."""
        classes = cfg["data"]["target_classes"]
        assert classes == ["L", "M", "H"]


class TestFeatureColumns:
    def test_returns_list(self, cfg):
        cols = feature_columns(cfg)
        assert isinstance(cols, list)
        assert len(cols) > 0

    def test_no_duplicates(self, cfg):
        cols = feature_columns(cfg)
        assert len(cols) == len(set(cols)), "Duplicate feature columns"


class TestPreprocessor:
    def test_builds_without_error(self, cfg):
        """The ColumnTransformer should construct successfully."""
        preprocessor = build_preprocessor(cfg)
        assert preprocessor is not None

    def test_transforms_cleaned_data(self, cleaned_df, cfg):
        """Fitting and transforming should produce a numeric matrix."""
        preprocessor = build_preprocessor(cfg)
        X, _ = split_features_target(cleaned_df, cfg)
        transformed = preprocessor.fit_transform(X)
        assert isinstance(transformed, np.ndarray)
        assert transformed.shape[0] == len(X)
        assert not np.isnan(transformed).any(), "NaN values after preprocessing"
