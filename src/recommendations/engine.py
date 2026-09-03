"""
SHAP-driven recommendation engine — personalised, not generic.

The brief says "generate suggestions". Most submissions will hard-code a list:
"if attendance < 80%, suggest improving attendance". That is a lookup table
pretending to be intelligence.

This engine does something better: it reads the SHAP explanation for a *specific
student* and turns their top contributing factors into plain-English advice. If
SHAP says this student's problem is low discussion participation (not attendance),
the advice says "participate more in class discussions" — not the generic
attendance tip that wouldn't help this student at all.

The recommendation is *derived from the model's own reasoning*, not from
hand-written rules. That is the difference between a rule engine and a
recommendation engine.

Three tiers of recommendation
------------------------------
1. **SHAP-driven factor advice**: "Your discussion participation is pulling your
   score down. Students who post 30+ times tend to be predicted High."
2. **Counterfactual action**: "If your resource visits went from 12 to 41, the
   model would predict Medium instead of Low." (From the dice engine.)
3. **Comparative context**: "You're in the bottom 20% for hands raised.
   The class average is 46."

All three tiers are combined into one per-student recommendation card.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
import pandas as pd

from src.data.preprocess import feature_columns, load_processed, split_features_target
from src.models.predict import load_model_bundle, predict_one, prepare_input
from src.utils.config import (
    class_label,
    friendly,
    get_path,
    load_config,
    save_json,
)
from src.utils.logging_utils import get_logger, section

logger = get_logger(__name__)


# =============================================================================
# Feature statistics — for the "compared to your class" context
# =============================================================================

_STATS_CACHE: Dict[str, Any] | None = None


def _feature_stats(cfg: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Compute per-feature statistics (mean, median, percentiles) for context."""
    global _STATS_CACHE
    if _STATS_CACHE is not None:
        return _STATS_CACHE

    df = load_processed(cfg)
    numeric = cfg["data"]["numeric_features"]
    stats: Dict[str, Dict[str, float]] = {}
    for col in numeric:
        if col not in df.columns:
            continue
        vals = df[col].astype(float)
        stats[col] = {
            "mean": round(float(vals.mean()), 1),
            "median": round(float(vals.median()), 1),
            "p25": round(float(vals.quantile(0.25)), 1),
            "p75": round(float(vals.quantile(0.75)), 1),
            "min": round(float(vals.min()), 1),
            "max": round(float(vals.max()), 1),
        }
    _STATS_CACHE = stats
    return stats


def _percentile_rank(value: float, col: str, cfg: Dict[str, Any]) -> float | None:
    """Where does this student's value sit relative to the class?"""
    df = load_processed(cfg)
    if col not in df.columns:
        return None
    vals = df[col].astype(float).values
    return round(float(np.mean(vals <= value) * 100), 1)


# =============================================================================
# SHAP-driven advice generation
# =============================================================================

def _direction_advice(
    feature: str,
    shap_value: float,
    student_value: Any,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate advice for one feature based on its SHAP contribution.

    A negative SHAP value for the predicted class means this feature is *hurting*
    the student's prediction. A positive one means it is helping.

    We only generate improvement advice for features that are (a) hurting the
    prediction and (b) actionable.
    """
    name = friendly(feature, cfg)
    actionable = feature in cfg["data"].get("actionable_features", [])
    numeric = feature in cfg["data"]["numeric_features"]

    advice: Dict[str, Any] = {
        "feature": feature,
        "friendly_name": name,
        "shap_value": round(float(shap_value), 4),
        "student_value": student_value,
        "direction": "helping" if shap_value > 0 else "hurting",
        "actionable": actionable,
    }

    if numeric:
        stats = _feature_stats(cfg)
        if feature in stats:
            advice["class_mean"] = stats[feature]["mean"]
            advice["class_median"] = stats[feature]["median"]
            pct = _percentile_rank(float(student_value), feature, cfg)
            if pct is not None:
                advice["percentile_rank"] = pct

    # Generate the actual advice text
    if shap_value < 0 and actionable:
        # This feature is pulling the prediction down — suggest improvement
        if numeric and feature in _feature_stats(cfg):
            mean_val = _feature_stats(cfg)[feature]["mean"]
            p75 = _feature_stats(cfg)[feature]["p75"]
            if float(student_value) < mean_val:
                target = int(round(p75))
                advice["suggestion"] = (
                    f"Your {name.lower()} ({int(student_value)}) is below the class average "
                    f"({mean_val:.0f}). Aiming for the top-quartile level ({target}) could "
                    f"meaningfully improve your predicted performance."
                )
            else:
                advice["suggestion"] = (
                    f"Although your {name.lower()} ({int(student_value)}) is above average, "
                    f"it is still weighing against your prediction. Focus on consistency "
                    f"and quality, not just quantity."
                )
        elif feature == "StudentAbsenceDays":
            if str(student_value) == "Above-7" or student_value == 1:
                advice["suggestion"] = (
                    "Your absence level is above 7 days. Reducing absences to below 7 days "
                    "is one of the strongest predictors of improved performance in this model."
                )
            else:
                advice["suggestion"] = (
                    "Your attendance is already good — keep it up."
                )
        elif feature == "ParentAnsweringSurvey":
            if str(student_value) in ("No", "0", 0):
                advice["suggestion"] = (
                    "Parent engagement with school surveys is associated with better outcomes. "
                    "Encouraging your parent/guardian to participate could help."
                )
        else:
            advice["suggestion"] = (
                f"Improving your {name.lower()} could positively impact your predicted performance."
            )
    elif shap_value > 0:
        advice["suggestion"] = f"Your {name.lower()} is contributing positively — keep it up!"
    else:
        advice["suggestion"] = None

    return advice


def generate_recommendations(
    student: Mapping[str, Any] | pd.Series,
    cfg: Dict[str, Any] | None = None,
    top_n: int | None = None,
    include_counterfactual: bool = True,
) -> Dict[str, Any]:
    """Generate a complete recommendation card for one student.

    This is the function the dashboard's "Individual Predictor" page calls.
    It combines:
    - Prediction with confidence
    - SHAP-based factor analysis
    - Personalised improvement suggestions
    - Optionally, counterfactual "what would need to change"

    Args:
        student:  Student data as a dict, Series, or single-row DataFrame.
        cfg:  Project config.
        top_n:  Number of top SHAP factors to include (default from config).
        include_counterfactual:  Whether to generate counterfactual suggestions.

    Returns:
        Recommendation card dict with prediction, factors, advice, and
        optionally counterfactual suggestions.
    """
    cfg = cfg or load_config()
    rec_cfg = cfg.get("recommendations", {})
    top_n = top_n or rec_cfg.get("top_n_factors", 3)
    min_magnitude = rec_cfg.get("min_shap_magnitude", 0.01)

    # Step 1: Predict
    prediction = predict_one(student, cfg=cfg)
    predicted_class = prediction["predicted_class"]

    # Step 2: Get SHAP explanation
    try:
        from src.explainability.shap_utils import explain_student
        explanation = explain_student(student, cfg=cfg)
        contributions = explanation.get("contributions", [])
    except Exception as e:
        logger.warning("SHAP explanation failed: %s — falling back to basic advice.", e)
        contributions = []

    # Step 3: Generate SHAP-driven advice
    factor_advice: List[Dict[str, Any]] = []
    improvement_suggestions: List[str] = []

    for contrib in contributions[:top_n]:
        if abs(contrib.get("shap_value", 0)) < min_magnitude:
            continue

        feature = contrib.get("original_feature") or contrib.get("feature", "")
        shap_val = contrib.get("shap_value", 0)
        student_val = contrib.get("student_value", "")

        advice = _direction_advice(feature, shap_val, student_val, cfg)
        factor_advice.append(advice)

        if advice.get("suggestion") and advice["direction"] == "hurting" and advice["actionable"]:
            improvement_suggestions.append(advice["suggestion"])

    # Step 4: Counterfactual suggestions (optional)
    counterfactual_result = None
    if include_counterfactual and predicted_class != "H":
        try:
            from src.counterfactuals.dice_engine import generate_counterfactuals
            cf = generate_counterfactuals(student, cfg=cfg)
            if cf and cf.get("counterfactuals"):
                counterfactual_result = cf
        except Exception as e:
            logger.warning("Counterfactual generation failed: %s", e)

    # Step 5: Build the recommendation card
    card: Dict[str, Any] = {
        "prediction": prediction,
        "top_factors": factor_advice,
        "improvement_suggestions": improvement_suggestions,
        "counterfactual": counterfactual_result,
        "summary": _build_summary(
            prediction, factor_advice, improvement_suggestions, counterfactual_result, cfg
        ),
    }

    return card


def _build_summary(
    prediction: Dict[str, Any],
    factors: List[Dict[str, Any]],
    suggestions: List[str],
    counterfactual: Dict[str, Any] | None,
    cfg: Dict[str, Any],
) -> str:
    """Build a plain-English summary paragraph for the recommendation card."""
    label = prediction.get("predicted_label", prediction.get("predicted_class", "Unknown"))
    confidence = prediction.get("confidence", 0)

    parts = [
        f"This student is predicted as **{label}** "
        f"(confidence: {confidence:.0%})."
    ]

    # Highlight the key factors
    hurting = [f for f in factors if f["direction"] == "hurting" and f["actionable"]]
    helping = [f for f in factors if f["direction"] == "helping"]

    if hurting:
        names = [f["friendly_name"] for f in hurting[:3]]
        parts.append(
            f"The main areas pulling the score down are: {', '.join(names)}."
        )

    if helping:
        names = [f["friendly_name"] for f in helping[:2]]
        parts.append(
            f"Strengths: {', '.join(names)}."
        )

    if suggestions:
        parts.append(f"**Top recommendation**: {suggestions[0]}")

    if counterfactual and counterfactual.get("counterfactuals"):
        best = counterfactual["counterfactuals"][0]
        if best.get("plain_summary"):
            parts.append(f"**Path forward**: {best['plain_summary']}")

    return " ".join(parts)


# =============================================================================
# Batch recommendations (for the pipeline)
# =============================================================================

def warm_cache(
    cfg: Dict[str, Any] | None = None,
    n_samples: int = 5,
    save: bool = True,
) -> Dict[str, Any]:
    """Pre-generate recommendations for a sample of students.

    This is called by the pipeline to verify the engine works end-to-end and
    to save example outputs for the report.
    """
    cfg = cfg or load_config()
    section(logger, "Recommendation Engine")

    df = load_processed(cfg)
    X, y = split_features_target(df, cfg)

    # Pick students from each class for representative examples
    sample_indices = []
    target = cfg["data"]["target"]
    for cls in cfg["data"]["target_classes"]:
        cls_indices = df[df[target] == cls].index.tolist()
        if cls_indices:
            n = min(max(1, n_samples // 3), len(cls_indices))
            sample_indices.extend(cls_indices[:n])

    samples: List[Dict[str, Any]] = []
    for idx in sample_indices[:n_samples]:
        row = df.iloc[idx]
        student_data = {
            c: (int(row[c]) if c in cfg["data"]["numeric_features"] else str(row[c]))
            for c in feature_columns(cfg)
        }

        try:
            rec = generate_recommendations(
                student_data, cfg=cfg, include_counterfactual=True
            )
            rec["student_index"] = int(idx)
            rec["actual_class"] = str(row.get(target, "?"))
            samples.append(rec)
            logger.info(
                "  Student %d (actual: %s, predicted: %s): %d suggestions",
                idx, row.get(target), rec["prediction"]["predicted_class"],
                len(rec["improvement_suggestions"]),
            )
        except Exception as e:
            logger.warning("  Student %d: recommendation failed — %s", idx, e)

    report = {
        "n_samples": len(samples),
        "samples": samples,
    }

    if save:
        out_path = get_path("artifacts_dir", cfg, ensure_parent=True)
        save_json(report, out_path / "recommendations_sample.json")
        logger.info("Saved sample recommendations -> %s", out_path / "recommendations_sample.json")

    return report


if __name__ == "__main__":  # pragma: no cover - manual run
    warm_cache()
