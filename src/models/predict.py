"""
Prediction service — the one and only path from a student's data to a result.

The dashboard, the API and the counterfactual engine all call into this module.
That is the entire point: there is exactly one implementation of "how do we turn
a student into a prediction", so the dashboard and the API cannot possibly
disagree. The test suite asserts that equivalence explicitly.

The model bundle on disk contains the fitted ``Pipeline`` (preprocessing and
estimator together), the class order, and the expected column list — so this
module never has to re-derive any encoding logic.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
import pandas as pd

from src.data.preprocess import feature_columns
from src.utils.config import class_label, friendly, get_path, load_config
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ModelNotTrainedError(RuntimeError):
    """Raised when no saved model exists yet, with instructions for fixing it."""


@lru_cache(maxsize=2)
def load_model_bundle(model_path: str | None = None) -> Dict[str, Any]:
    """Load ``models/model.joblib`` (cached).

    Cached because Streamlit re-runs the whole script on every widget
    interaction — without this, moving a slider would reload a 400-tree forest
    from disk each time and the UI would feel broken.
    """
    import joblib

    cfg = load_config()
    path = Path(model_path) if model_path else get_path("model_file", cfg)
    if not path.exists():
        raise ModelNotTrainedError(
            f"No trained model found at {path}.\n"
            "Run the training pipeline first:\n"
            "    python scripts/run_pipeline.py\n"
            "or, to train only:\n"
            "    python -m src.models.train"
        )
    bundle = joblib.load(path)
    logger.info("Loaded model '%s' (trained on %s students)",
                bundle.get("model_name"), bundle.get("trained_on_n"))
    return bundle


def model_is_available(model_path: str | None = None) -> bool:
    """Cheap check the dashboard uses to show a friendly message instead of a stack trace."""
    cfg = load_config()
    path = Path(model_path) if model_path else get_path("model_file", cfg)
    return path.exists()


def prepare_input(
    student: Mapping[str, Any] | pd.DataFrame | pd.Series,
    cfg: Dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Coerce whatever the caller supplied into the exact frame the pipeline wants.

    Accepts a dict (from the API), a Series (a row selected in the dashboard) or
    an already-formed DataFrame. Validates that every required column is present
    and puts them in the canonical order — column *order* matters to a fitted
    ``ColumnTransformer``, and getting it wrong silently produces nonsense rather
    than an error.
    """
    cfg = cfg or load_config()
    cols = feature_columns(cfg)

    if isinstance(student, pd.DataFrame):
        df = student.copy()
    elif isinstance(student, pd.Series):
        df = student.to_frame().T.copy()
    else:
        df = pd.DataFrame([dict(student)])

    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required student fields: {missing}. "
            f"All {len(cols)} fields are required: {cols}"
        )

    df = df[cols]

    # Numeric fields sometimes arrive as strings from JSON or a form widget.
    for col in cfg["data"]["numeric_features"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Field '{col}' must be a number between 0 and 100.")
        if ((df[col] < 0) | (df[col] > 100)).any():
            raise ValueError(f"Field '{col}' must be between 0 and 100.")

    for col in list(cfg["data"]["nominal_features"]) + list(cfg["data"]["binary_features"].keys()):
        df[col] = df[col].astype(str).str.strip()

    return df.reset_index(drop=True)


def predict_one(
    student: Mapping[str, Any] | pd.Series,
    model_path: str | None = None,
    cfg: Dict[str, Any] | None = None,
    include_probabilities: bool = True,
) -> Dict[str, Any]:
    """Predict the performance band for a single student.

    Returns the predicted class (both code and word), the model's confidence,
    the full probability distribution, and a short plain-English confidence
    note. That last field matters: a 41% "most likely Medium" is a materially
    different thing to show a teacher than a 96% one, and the UI should never
    present them identically.
    """
    cfg = cfg or load_config()
    bundle = load_model_bundle(model_path)
    pipeline = bundle["pipeline"]
    class_order: List[str] = list(bundle["class_order"])

    X = prepare_input(student, cfg)
    pred_code = int(pipeline.predict(X)[0])
    predicted = class_order[pred_code]

    result: Dict[str, Any] = {
        "predicted_class": predicted,
        "predicted_label": class_label(predicted, cfg),
        "model_name": bundle.get("model_name"),
    }

    if include_probabilities and hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)[0]
        result["probabilities"] = {
            class_order[i]: round(float(proba[i]), 4) for i in range(len(class_order))
        }
        result["probabilities_labelled"] = {
            class_label(class_order[i], cfg): round(float(proba[i]), 4)
            for i in range(len(class_order))
        }
        confidence = float(proba[pred_code])
        result["confidence"] = round(confidence, 4)
        result["confidence_level"] = _confidence_band(confidence)
        result["confidence_note"] = _confidence_note(confidence, predicted, proba, class_order, cfg)

        # Runner-up matters for borderline students: "Medium, but nearly High"
        # is far more useful to a teacher than a bare label.
        ranked = np.argsort(proba)[::-1]
        if len(ranked) > 1:
            result["runner_up_class"] = class_order[int(ranked[1])]
            result["runner_up_probability"] = round(float(proba[ranked[1]]), 4)
            result["margin"] = round(float(proba[ranked[0]] - proba[ranked[1]]), 4)
            result["is_borderline"] = bool(result["margin"] < 0.15)

    return result


def predict_batch(
    students: pd.DataFrame,
    model_path: str | None = None,
    cfg: Dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Predict for many students at once.

    Vectorised through the pipeline in a single call rather than looping — which
    matters for the cohort simulator, where we score the whole class hundreds of
    times.
    """
    cfg = cfg or load_config()
    bundle = load_model_bundle(model_path)
    pipeline = bundle["pipeline"]
    class_order: List[str] = list(bundle["class_order"])

    X = prepare_input(students, cfg)
    codes = pipeline.predict(X)

    out = pd.DataFrame(index=X.index)
    out["predicted_class"] = [class_order[int(c)] for c in codes]
    out["predicted_label"] = [class_label(c, cfg) for c in out["predicted_class"]]

    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)
        for i, cls in enumerate(class_order):
            out[f"prob_{cls}"] = np.round(proba[:, i], 4)
        out["confidence"] = np.round(proba.max(axis=1), 4)
    return out


def predict_proba_matrix(
    students: pd.DataFrame,
    model_path: str | None = None,
    cfg: Dict[str, Any] | None = None,
) -> np.ndarray:
    """Raw probability matrix — used by the Monte Carlo cohort simulator."""
    cfg = cfg or load_config()
    bundle = load_model_bundle(model_path)
    X = prepare_input(students, cfg)
    return bundle["pipeline"].predict_proba(X)


def _confidence_band(p: float) -> str:
    """Bucket a probability into a word the UI can show as a chip."""
    if p >= 0.80:
        return "high"
    if p >= 0.60:
        return "moderate"
    return "low"


def _confidence_note(
    confidence: float,
    predicted: str,
    proba: np.ndarray,
    class_order: Sequence[str],
    cfg: Dict[str, Any],
) -> str:
    """A one-line, jargon-free explanation of how much to trust this prediction."""
    label = class_label(predicted, cfg)
    ranked = np.argsort(proba)[::-1]
    runner = class_label(class_order[int(ranked[1])], cfg) if len(ranked) > 1 else None
    margin = float(proba[ranked[0]] - proba[ranked[1]]) if len(ranked) > 1 else 1.0

    if confidence >= 0.80:
        return (
            f"The model is confident about this: {label} with {confidence:.0%} certainty, "
            "well clear of the alternatives."
        )
    if margin < 0.15 and runner:
        return (
            f"This student sits close to the boundary between {label} and {runner} "
            f"({confidence:.0%} vs {float(proba[ranked[1]]):.0%}). Treat the band as indicative "
            "and pay attention to the individual factors below rather than the label alone."
        )
    return (
        f"Moderate confidence: {label} at {confidence:.0%}. Worth combining with your own "
        "knowledge of the student rather than taking on its own."
    )


def sample_student(cfg: Dict[str, Any] | None = None, index: int = 0) -> Dict[str, Any]:
    """A real student row from the dataset — handy for demos, docs and tests."""
    from src.data.preprocess import load_processed

    cfg = cfg or load_config()
    df = load_processed(cfg)
    row = df.iloc[index]
    return {c: (int(row[c]) if c in cfg["data"]["numeric_features"] else str(row[c]))
            for c in feature_columns(cfg)}


def describe_student(student: Mapping[str, Any], cfg: Dict[str, Any] | None = None) -> str:
    """Readable one-line summary of a student, for logs and API examples."""
    cfg = cfg or load_config()
    parts = [
        f"{friendly(c, cfg)}: {student[c]}"
        for c in cfg["data"]["actionable_features"] if c in student
    ]
    return " | ".join(parts)
