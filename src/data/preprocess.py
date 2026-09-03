"""
Preprocessing — Module 1 of the brief.

Two things live here, and the split matters:

1. :func:`clean_dataframe` — pure pandas. Removes duplicates, trims whitespace,
   fills missing values. Produces ``data/processed/cleaned.csv``, the honest,
   human-readable artifact that the EDA notebooks and the report read from.

2. :func:`build_preprocessor` — a scikit-learn ``ColumnTransformer`` that does
   the encoding and scaling. This one is *never* run standalone. It gets bolted
   onto the front of the model inside a single ``Pipeline`` object, so the saved
   ``model.joblib`` contains preprocessing + model together.

Why keep encoding inside the pipeline instead of writing an encoded CSV?
    Because the alternative is the classic production bug: you encode your
    training data in a notebook, save only the model, and then at serving time
    the API has to re-implement the exact same encoding by hand. The moment the
    two implementations drift — a different category order, a different scaler
    mean — predictions are silently wrong. Bundling the transformer with the
    model makes that class of bug structurally impossible: the dashboard and
    the API both feed in *raw* student data and the pipeline handles the rest.

Encoding choices, and the reasoning behind each:

* Numeric engagement counters -> ``StandardScaler``.
  Logistic Regression needs comparably-scaled inputs or the regularisation
  penalty hits large-range features harder. Tree models are invariant to any
  monotonic rescaling, so this is free for them.

* Unordered categories (nationality, topic, section...) -> ``OneHotEncoder``.
  Label-encoding these would invent an ordering that does not exist. A linear
  model reading ``NationalITy = 7`` would treat it as "more than" ``= 3``,
  which is meaningless. One-hot costs us extra columns and buys correctness.

* Two-level categories -> ``OrdinalEncoder`` with an explicit category order.
  With exactly two levels, ordinal and one-hot encode identical information,
  but ordinal keeps one column instead of two. That keeps the SHAP plots
  readable: one bar labelled "Absence level" instead of two mirror-image bars.
  The order is pinned in ``config.yaml`` (``Under-7`` -> 0, ``Above-7`` -> 1) so
  "higher value = worse attendance" stays true and the SHAP sign is meaningful.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.utils.config import get_path, load_config, save_json
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# Part 1 — pandas-only cleaning (no scikit-learn required)
# =============================================================================

def clean_dataframe(
    df: pd.DataFrame, cfg: Dict[str, Any] | None = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean the raw dataset with pandas only.

    Steps, in order:
      1. Trim whitespace from every text cell and column header.
      2. Drop exact duplicate rows (the raw file contains a couple).
      3. Impute missing values — median for numeric, mode for categorical.
      4. Coerce the engagement counters to numeric and clip to their 0-100 range.

    Returns:
        ``(cleaned_dataframe, cleaning_report)``. The report records exactly
        what was changed, so the write-up can state "we removed N duplicates"
        with a number that came from the code rather than from memory.
    """
    cfg = cfg or load_config()
    d = cfg["data"]
    p = cfg["preprocess"]

    report: Dict[str, Any] = {"rows_in": int(len(df))}
    out = df.copy()

    # --- 1. whitespace -------------------------------------------------------
    out.columns = [str(c).strip() for c in out.columns]
    obj_cols = out.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        out[col] = out[col].astype(str).str.strip()
    report["text_columns_trimmed"] = list(obj_cols)

    # --- 2. duplicates -------------------------------------------------------
    # These are genuine duplicates across all 17 columns. With no student ID in
    # the dataset we cannot prove they are data-entry errors rather than two
    # students who happen to match on every field — but the probability of the
    # latter across 4 continuous counters is negligible, so we drop them. Left
    # in, they would leak an identical row into both train and test.
    n_dupes = int(out.duplicated().sum())
    if p.get("drop_exact_duplicates", True) and n_dupes > 0:
        out = out.drop_duplicates().reset_index(drop=True)
    report["exact_duplicates_removed"] = n_dupes if p.get("drop_exact_duplicates", True) else 0

    # --- 3. missing values ---------------------------------------------------
    # xAPI-Edu-Data is complete, so in practice this is a no-op. We implement it
    # anyway because the brief requires it and because a pipeline that only
    # works on perfectly clean input is not a pipeline.
    filled: Dict[str, Any] = {}
    for col in d["numeric_features"]:
        if col in out.columns and out[col].isna().any():
            fill = float(out[col].median())
            filled[col] = {"strategy": p["missing_value_strategy"]["numeric"], "value": fill,
                           "n_filled": int(out[col].isna().sum())}
            out[col] = out[col].fillna(fill)

    categorical_cols = list(d["nominal_features"]) + list(d["binary_features"].keys())
    for col in categorical_cols:
        if col in out.columns and out[col].isna().any():
            mode = out[col].mode()
            fill = mode.iloc[0] if len(mode) else "Unknown"
            filled[col] = {"strategy": p["missing_value_strategy"]["categorical"], "value": fill,
                           "n_filled": int(out[col].isna().sum())}
            out[col] = out[col].fillna(fill)
    report["missing_values_filled"] = filled

    # Rows missing the target cannot be used for supervised learning and cannot
    # be imputed without inventing a label, so they go.
    target = d["target"]
    if target in out.columns:
        n_missing_target = int(out[target].isna().sum())
        if n_missing_target:
            out = out[out[target].notna()].reset_index(drop=True)
        report["rows_dropped_missing_target"] = n_missing_target

    # --- 4. numeric coercion and clipping ------------------------------------
    clipped: Dict[str, int] = {}
    for col in d["numeric_features"]:
        if col not in out.columns:
            continue
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())
        n_out_of_range = int(((out[col] < 0) | (out[col] > 100)).sum())
        if n_out_of_range:
            out[col] = out[col].clip(0, 100)
            clipped[col] = n_out_of_range
        out[col] = out[col].astype(int)
    report["values_clipped_to_range"] = clipped

    report["rows_out"] = int(len(out))
    report["class_distribution"] = (
        {str(k): int(v) for k, v in out[target].value_counts().items()} if target in out.columns else {}
    )

    logger.info(
        "Cleaned dataset: %d -> %d rows (%d duplicates removed, %d values imputed)",
        report["rows_in"], report["rows_out"], report["exact_duplicates_removed"], len(filled),
    )
    return out, report


def split_features_target(
    df: pd.DataFrame, cfg: Dict[str, Any] | None = None
) -> Tuple[pd.DataFrame, pd.Series]:
    """Separate the model inputs (X) from the label (y)."""
    cfg = cfg or load_config()
    d = cfg["data"]
    target = d["target"]
    feature_cols = feature_columns(cfg)
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Cleaned data is missing feature columns: {missing}")
    return df[feature_cols].copy(), df[target].copy()


def feature_columns(cfg: Dict[str, Any] | None = None) -> List[str]:
    """The model's input columns, in a fixed order.

    Order matters: it is the contract between the dashboard, the API and the
    saved pipeline. Deriving it from config in one place means all three agree
    by construction.
    """
    cfg = cfg or load_config()
    d = cfg["data"]
    return list(d["numeric_features"]) + list(d["nominal_features"]) + list(d["binary_features"].keys())


def run_preprocessing(cfg: Dict[str, Any] | None = None, save: bool = True) -> pd.DataFrame:
    """End-to-end Phase 1: load raw -> validate -> clean -> save.

    This is what ``scripts/run_pipeline.py`` calls, and it is the Phase 1
    checkpoint: if this returns without raising, the data layer is sound.
    """
    from src.data.load_data import load_and_validate  # local import avoids a cycle

    cfg = cfg or load_config()
    raw, schema_report = load_and_validate(cfg=cfg)
    cleaned, clean_report = clean_dataframe(raw, cfg)

    if save:
        out_path = get_path("processed_data", cfg, ensure_parent=True)
        cleaned.to_csv(out_path, index=False)
        save_json(
            {"schema_check": schema_report, "cleaning": clean_report},
            get_path("processed_meta", cfg, ensure_parent=True),
        )
        logger.info("Wrote cleaned dataset -> %s", out_path)

    return cleaned


def load_processed(cfg: Dict[str, Any] | None = None) -> pd.DataFrame:
    """Read ``data/processed/cleaned.csv``, building it first if absent."""
    cfg = cfg or load_config()
    path = get_path("processed_data", cfg)
    if not path.exists():
        logger.info("Processed data not found; running preprocessing now.")
        return run_preprocessing(cfg)
    return pd.read_csv(path)


# =============================================================================
# Part 2 — the scikit-learn transformer that ships inside the model
# =============================================================================

def _binary_categories(cfg: Dict[str, Any]) -> Tuple[List[str], List[List[str]]]:
    """Turn the config's binary mappings into ordered category lists.

    ``{"Under-7": 0, "Above-7": 1}`` becomes ``["Under-7", "Above-7"]`` — the
    order ``OrdinalEncoder`` needs to reproduce exactly the codes we documented.
    """
    cols: List[str] = []
    cats: List[List[str]] = []
    for col, mapping in cfg["data"]["binary_features"].items():
        cols.append(col)
        cats.append([lvl for lvl, _ in sorted(mapping.items(), key=lambda kv: kv[1])])
    return cols, cats


def _make_onehot():
    """Construct a OneHotEncoder that works across scikit-learn versions.

    ``sparse`` was renamed to ``sparse_output`` in scikit-learn 1.2. Rather than
    pinning users to one version, we try the modern signature and fall back.
    """
    from sklearn.preprocessing import OneHotEncoder

    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # scikit-learn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_preprocessor(cfg: Dict[str, Any] | None = None):
    """Build the ``ColumnTransformer`` that turns raw student rows into a matrix.

    Every branch handles unknown categories gracefully (``handle_unknown``),
    because the API will eventually receive a nationality or topic that was not
    in the training set, and a 500 error is a much worse answer than a slightly
    less confident prediction.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline as SkPipeline
    from sklearn.preprocessing import OrdinalEncoder, StandardScaler

    cfg = cfg or load_config()
    d = cfg["data"]
    p = cfg["preprocess"]

    numeric_steps = [("impute", SimpleImputer(strategy=p["missing_value_strategy"]["numeric"]))]
    if p.get("scale_numeric", True):
        numeric_steps.append(("scale", StandardScaler()))
    numeric_pipe = SkPipeline(numeric_steps)

    nominal_pipe = SkPipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", _make_onehot()),
    ])

    bin_cols, bin_cats = _binary_categories(cfg)
    binary_pipe = SkPipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(
            categories=bin_cats,
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        )),
    ])

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipe, list(d["numeric_features"])),
            ("nominal", nominal_pipe, list(d["nominal_features"])),
            ("binary", binary_pipe, bin_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def get_transformed_feature_names(preprocessor, cfg: Dict[str, Any] | None = None) -> List[str]:
    """Recover readable names for the columns coming out of the transformer.

    SHAP plots are worthless without these — otherwise every bar is labelled
    ``Feature 34``. Falls back to reconstructing the names by hand on older
    scikit-learn versions that lack ``get_feature_names_out``.
    """
    cfg = cfg or load_config()
    try:
        return [str(n) for n in preprocessor.get_feature_names_out()]
    except Exception:  # pragma: no cover - very old scikit-learn
        d = cfg["data"]
        names = list(d["numeric_features"])
        for col in d["nominal_features"]:
            try:
                cats = preprocessor.named_transformers_["nominal"].named_steps["onehot"].categories_
                idx = list(d["nominal_features"]).index(col)
                names += [f"{col}_{c}" for c in cats[idx]]
            except Exception:
                names.append(col)
        names += list(d["binary_features"].keys())
        return names


def encode_target(y: pd.Series, cfg: Dict[str, Any] | None = None) -> Tuple[np.ndarray, List[str]]:
    """Map the L/M/H labels onto integers 0/1/2 in *semantic* order.

    We do not use ``LabelEncoder`` here on purpose. It sorts alphabetically,
    which would give H=0, L=1, M=2 — an order where the integer codes carry no
    meaning. Pinning the order to ``["L", "M", "H"]`` from config means "higher
    code = better outcome", which makes confusion matrices and fairness
    selection rates read the way a human expects.
    """
    cfg = cfg or load_config()
    classes = list(cfg["data"]["target_classes"])
    lookup = {c: i for i, c in enumerate(classes)}
    unknown = set(y.dropna().unique()) - set(classes)
    if unknown:
        raise ValueError(f"Target contains values outside {classes}: {sorted(unknown)}")
    return y.map(lookup).to_numpy(dtype=int), classes


def decode_target(codes, cfg: Dict[str, Any] | None = None) -> List[str]:
    """Inverse of :func:`encode_target` — integer codes back to L/M/H."""
    cfg = cfg or load_config()
    classes = list(cfg["data"]["target_classes"])
    return [classes[int(c)] for c in np.asarray(codes).ravel()]


if __name__ == "__main__":  # pragma: no cover - manual smoke check
    frame = run_preprocessing()
    print(frame.head())
    print(frame.shape)
