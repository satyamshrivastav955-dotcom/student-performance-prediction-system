"""
SHAP explanations — making the model justify itself.

Two audiences, two questions:

  * **Global** ("what does this model pay attention to overall?") — for the
    evaluator and the report. Answered by averaging the magnitude of each
    feature's contribution across every student.
  * **Local** ("why *this* student?") — for the teacher looking at one child.
    Answered by the individual contributions for that single row.

What a SHAP value actually is, without the game theory
------------------------------------------------------
Start from the average prediction across the whole dataset — call it the *base
value*. For any one student, the model's prediction differs from that average.
SHAP splits that difference into one number per feature, and those numbers sum
*exactly* back to the gap:

    base value + sum(shap values) = this student's predicted probability

So "resources opened: +0.21" means precisely: this student's resource usage
pushed their probability of the predicted class up by 0.21 compared with a
typical student. That exact additivity is the property plain feature importance
lacks — importance is one global number per feature and can never explain an
individual.

Two engineering details that cause most SHAP bugs, handled here
---------------------------------------------------------------
1. **Shape.** For multiclass tree models, the SHAP library has returned the
   values as a list of per-class arrays in some versions and as a single
   3-D array in others, with the class axis in different positions. We normalise
   to ``(n_samples, n_features, n_classes)`` once, in one place, and assert it.

2. **Encoded vs. human features.** SHAP runs on the matrix the model sees, where
   ``Topic`` has become 12 one-hot columns. A teacher must never see
   ``Topic_Chemistry``. We map every encoded column back to its source feature
   and sum the contributions, so the UI shows one row for "Subject".
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd

from src.data.preprocess import feature_columns, get_transformed_feature_names
from src.models.predict import load_model_bundle, prepare_input
from src.utils.config import class_label, friendly, get_path, load_config, save_json
from src.utils.logging_utils import get_logger, section

logger = get_logger(__name__)


# =============================================================================
# Mapping encoded columns back to the features a human recognises
# =============================================================================

def build_feature_map(
    encoded_names: Sequence[str],
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, str]:
    """Map each encoded column name onto the original feature it came from.

    ``"Topic_Chemistry" -> "Topic"``, ``"raisedhands" -> "raisedhands"``.

    We match against the known original names rather than splitting on ``"_"``,
    because several original column names contain underscores themselves and a
    naive split would mangle them.
    """
    cfg = cfg or load_config()
    originals = feature_columns(cfg)
    # Longest first, so "PlaceofBirth" is tested before any shorter prefix that
    # happens to also match.
    originals_sorted = sorted(originals, key=len, reverse=True)

    mapping: Dict[str, str] = {}
    for enc in encoded_names:
        if enc in originals:
            mapping[enc] = enc
            continue
        match = next((o for o in originals_sorted if enc.startswith(f"{o}_")), None)
        mapping[enc] = match if match else enc
    return mapping


def aggregate_to_original(
    values: np.ndarray,
    encoded_names: Sequence[str],
    cfg: Dict[str, Any] | None = None,
) -> Tuple[np.ndarray, List[str]]:
    """Collapse per-encoded-column SHAP values down to per-original-feature.

    Summing (not averaging) is the right operation: SHAP values are additive
    contributions, and the twelve one-hot ``Topic_*`` columns between them
    contribute exactly what "Subject" contributed. Averaging would shrink the
    effect by a factor of twelve and make categorical features look artificially
    unimportant next to numeric ones.

    Args:
        values: ``(n_samples, n_encoded)`` or ``(n_encoded,)``.

    Returns:
        ``(aggregated_values, original_feature_names)`` in the canonical
        ``feature_columns()`` order.
    """
    cfg = cfg or load_config()
    mapping = build_feature_map(encoded_names, cfg)
    originals = feature_columns(cfg)

    single_row = values.ndim == 1
    v = values.reshape(1, -1) if single_row else values

    out = np.zeros((v.shape[0], len(originals)))
    index_of = {name: i for i, name in enumerate(originals)}
    for col_idx, enc in enumerate(encoded_names):
        target = mapping.get(enc)
        if target in index_of:
            out[:, index_of[target]] += v[:, col_idx]

    return (out[0] if single_row else out), originals


# =============================================================================
# Computing SHAP values
# =============================================================================

def _split_pipeline(pipeline) -> Tuple[Any, Any]:
    """Pull the fitted preprocessor and the fitted estimator out of the bundle.

    SHAP's fast tree path needs the bare estimator plus an already-transformed
    matrix — it cannot see through a ``Pipeline``.
    """
    return pipeline.named_steps["preprocess"], pipeline.named_steps["model"]


def _is_tree_model(estimator) -> bool:
    """Can we use the exact, fast TreeExplainer, or do we need the slow sampler?

    TreeExplainer computes exact SHAP values for tree ensembles in polynomial
    time. For anything else (our logistic-regression baseline) we fall back to
    KernelExplainer, which approximates by sampling and is orders of magnitude
    slower — hence the small background set.
    """
    name = type(estimator).__name__.lower()
    return any(k in name for k in
               ("forest", "tree", "boost", "xgb", "lgbm", "gradientboosting"))


def _normalise_shap_output(raw, n_samples: int, n_features: int, n_classes: int) -> np.ndarray:
    """Force SHAP's output into a predictable ``(samples, features, classes)`` array.

    This function exists because the shape SHAP hands back has genuinely varied:
    a list of per-class ``(samples, features)`` arrays in older versions, a
    single ``(samples, features, classes)`` array in newer ones, and for some
    binary models just ``(samples, features)``. Rather than hoping, we detect
    and reshape, then assert. A silent transpose here would put one class's
    explanation under another class's label — a bug that produces plausible,
    confidently wrong output, which is the worst kind.
    """
    if isinstance(raw, list):
        # list of per-class (n_samples, n_features)
        arr = np.stack([np.asarray(a) for a in raw], axis=-1)
    else:
        arr = np.asarray(raw)

    if arr.ndim == 2:
        # A single output — add a trailing class axis for uniformity.
        arr = arr[:, :, None]

    if arr.ndim != 3:
        raise ValueError(f"Unexpected SHAP output with {arr.ndim} dimensions, shape {arr.shape}")

    # Some versions return (classes, samples, features); detect and move the axis.
    if arr.shape[0] == n_classes and arr.shape[1] == n_samples and arr.shape[2] == n_features:
        arr = np.transpose(arr, (1, 2, 0))

    if arr.shape[:2] != (n_samples, n_features):
        raise ValueError(
            f"Could not normalise SHAP output. Got {arr.shape}, "
            f"expected ({n_samples}, {n_features}, {n_classes})."
        )
    return arr


@lru_cache(maxsize=1)
def _cached_explainer_state() -> Tuple[Any, Any, Tuple[str, ...], Any]:
    """Build the explainer once and reuse it.

    Cached because the Streamlit dashboard explains a new student on every
    interaction, and rebuilding a KernelExplainer's background set each time
    would make the page unusable.

    Returns ``(explainer, estimator, encoded_names, preprocessor)``.
    """
    import shap

    cfg = load_config()
    bundle = load_model_bundle()
    pipeline = bundle["pipeline"]
    preprocessor, estimator = _split_pipeline(pipeline)
    encoded_names = tuple(get_transformed_feature_names(preprocessor, cfg))

    if _is_tree_model(estimator):
        explainer = shap.TreeExplainer(estimator)
        logger.info("Using TreeExplainer (exact) for %s", type(estimator).__name__)
    else:
        from src.models.train import make_split

        n_bg = int(cfg["explainability"]["shap"]["background_samples"])
        X_train, _, _, _, _ = make_split(cfg)
        background = preprocessor.transform(X_train.sample(
            min(n_bg, len(X_train)), random_state=int(cfg["project"]["random_seed"])
        ))
        # shap.sample keeps the background small; KernelExplainer cost grows
        # linearly with it and we would otherwise wait minutes per student.
        explainer = shap.KernelExplainer(estimator.predict_proba, background)
        logger.info("Using KernelExplainer (approximate, %d background rows) for %s",
                    len(background), type(estimator).__name__)

    return explainer, estimator, encoded_names, preprocessor


def shap_values_for(
    students: pd.DataFrame,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compute SHAP values for one or more students.

    Returns a dict with both the encoded-level values (for the technical plots)
    and the aggregated original-feature values (for anything a human reads).
    """
    cfg = cfg or load_config()
    bundle = load_model_bundle()
    class_order: List[str] = list(bundle["class_order"])

    explainer, estimator, encoded_names, preprocessor = _cached_explainer_state()

    X = prepare_input(students, cfg)
    X_enc = preprocessor.transform(X)
    X_enc = np.asarray(X_enc)

    raw = explainer.shap_values(X_enc)
    values = _normalise_shap_output(raw, X_enc.shape[0], X_enc.shape[1], len(class_order))

    # Aggregate one class at a time, then restack.
    agg_per_class = []
    for k in range(values.shape[2]):
        agg, originals = aggregate_to_original(values[:, :, k], list(encoded_names), cfg)
        agg_per_class.append(agg)
    aggregated = np.stack(agg_per_class, axis=-1)   # (samples, originals, classes)

    base = np.atleast_1d(np.asarray(explainer.expected_value, dtype=float)).ravel()
    if base.size == 1 and len(class_order) > 1:
        base = np.repeat(base, len(class_order))

    return {
        "values_encoded": values,
        "encoded_names": list(encoded_names),
        "values": aggregated,
        "feature_names": originals,
        "base_values": base,
        "class_order": class_order,
        "X_raw": X,
    }


# =============================================================================
# Global explanation
# =============================================================================

def global_importance(
    n_samples: int | None = None,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Rank features by mean absolute SHAP value across the test set.

    "Mean absolute" because we want influence, not direction. A feature that
    pushes half the students up and half down has a mean near zero but is highly
    influential — averaging the raw values would hide it completely.
    """
    from src.models.train import make_split

    cfg = cfg or load_config()
    _, X_test, _, y_test, class_order = make_split(cfg)

    if n_samples is not None and n_samples < len(X_test):
        X_test = X_test.sample(n_samples, random_state=int(cfg["project"]["random_seed"]))

    logger.info("Computing SHAP values for %d test students...", len(X_test))
    result = shap_values_for(X_test, cfg)

    values = result["values"]                      # (samples, features, classes)
    names = result["feature_names"]

    # Average the magnitude over samples and classes.
    mean_abs = np.abs(values).mean(axis=(0, 2))
    total = mean_abs.sum() or 1.0

    ranked = sorted(
        (
            {
                "feature": names[i],
                "friendly_name": friendly(names[i], cfg),
                "mean_abs_shap": round(float(mean_abs[i]), 5),
                "share_of_total": round(float(mean_abs[i] / total), 4),
                "actionable": names[i] in cfg["data"]["actionable_features"],
                "sensitive": names[i] in cfg["data"]["sensitive_features"],
            }
            for i in range(len(names))
        ),
        key=lambda r: r["mean_abs_shap"],
        reverse=True,
    )

    # Per-class direction: does high resource use push toward High or away?
    per_class: Dict[str, List[Dict[str, Any]]] = {}
    for k, cls in enumerate(class_order):
        class_mean_abs = np.abs(values[:, :, k]).mean(axis=0)
        order = np.argsort(class_mean_abs)[::-1][:10]
        per_class[cls] = [
            {
                "feature": names[i],
                "friendly_name": friendly(names[i], cfg),
                "mean_abs_shap": round(float(class_mean_abs[i]), 5),
                "mean_signed_shap": round(float(values[:, i, k].mean()), 5),
            }
            for i in order
        ]

    return {
        "n_students_explained": int(len(X_test)),
        "model_name": load_model_bundle().get("model_name"),
        "ranked_features": ranked,
        "top_features": [r["feature"] for r in ranked[:10]],
        "per_class": per_class,
        "sensitive_feature_influence": [
            r for r in ranked if r["sensitive"]
        ],
        "narrative": _global_narrative(ranked, cfg),
    }


def _global_narrative(ranked: List[Dict[str, Any]], cfg: Dict[str, Any]) -> str:
    """Plain-English summary of the global ranking, for the report and dashboard."""
    if not ranked:
        return "No SHAP results available."

    top3 = ranked[:3]
    top3_share = sum(r["share_of_total"] for r in top3)
    names = ", ".join(r["friendly_name"] for r in top3)

    actionable_top = [r for r in ranked[:5] if r["actionable"]]
    sensitive = [r for r in ranked if r["sensitive"]]

    lines = [
        f"The three features the model relies on most are {names}, which together "
        f"account for {top3_share:.0%} of its total decision weight.",
    ]

    if actionable_top:
        lines.append(
            f"{len(actionable_top)} of the top five are things a school can actually change "
            f"({', '.join(r['friendly_name'] for r in actionable_top)}), which is what makes "
            "the recommendations that follow worth acting on rather than merely descriptive."
        )
    else:
        lines.append(
            "None of the top five features are changeable by a school, which limits how "
            "useful the recommendations can be — worth stating plainly rather than glossing over."
        )

    if sensitive:
        top_sensitive = sensitive[0]
        rank = next(i for i, r in enumerate(ranked, 1) if r["feature"] == top_sensitive["feature"])
        lines.append(
            f"The most influential demographic attribute is {top_sensitive['friendly_name']}, "
            f"ranked {rank} of {len(ranked)} with {top_sensitive['share_of_total']:.1%} of the "
            "decision weight. Influence alone is not proof of unfair treatment, but it is the "
            "reason the fairness audit is a required part of this project rather than an optional extra."
        )

    return " ".join(lines)


# =============================================================================
# Local explanation — one student
# =============================================================================

def explain_student(
    student: Mapping[str, Any] | pd.Series,
    cfg: Dict[str, Any] | None = None,
    top_n: int | None = None,
) -> Dict[str, Any]:
    """Explain a single prediction in terms a teacher can act on.

    Returns the contributions for the predicted class, split into what pushed
    the student toward that outcome and what pushed against it, plus a written
    sentence for each.
    """
    from src.models.predict import predict_one

    cfg = cfg or load_config()
    top_n = top_n or int(cfg["explainability"]["shap"]["max_display"])

    prediction = predict_one(student, cfg=cfg)
    result = shap_values_for(pd.DataFrame([dict(student)]) if not isinstance(student, pd.DataFrame)
                             else student, cfg)

    class_order = result["class_order"]
    k = class_order.index(prediction["predicted_class"])

    values = result["values"][0, :, k]
    names = result["feature_names"]
    row = result["X_raw"].iloc[0]

    contributions = [
        {
            "feature": names[i],
            "friendly_name": friendly(names[i], cfg),
            "value": _clean_value(row[names[i]]),
            "shap": round(float(values[i]), 5),
            "direction": "increases" if values[i] > 0 else "decreases",
            "actionable": names[i] in cfg["data"]["actionable_features"],
        }
        for i in range(len(names))
    ]
    contributions.sort(key=lambda c: abs(c["shap"]), reverse=True)
    top = contributions[:top_n]

    pushing_toward = [c for c in top if c["shap"] > 0]
    pushing_against = [c for c in top if c["shap"] < 0]

    for c in top:
        c["sentence"] = _contribution_sentence(c, prediction["predicted_label"], cfg)

    return {
        "prediction": prediction,
        "base_value": round(float(result["base_values"][k]), 5)
        if len(result["base_values"]) > k else None,
        "contributions": top,
        "all_contributions": contributions,
        "pushing_toward": pushing_toward,
        "pushing_against": pushing_against,
        "explained_class": prediction["predicted_class"],
        "summary": _local_narrative(prediction, pushing_toward, pushing_against, cfg),
    }


def _clean_value(v: Any) -> Any:
    """Make a cell JSON-friendly and readable."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 2)
    return str(v)


def _contribution_sentence(c: Dict[str, Any], predicted_label: str, cfg: Dict[str, Any]) -> str:
    """One line explaining a single feature's contribution."""
    verb = "supports" if c["shap"] > 0 else "argues against"
    return (
        f"{c['friendly_name']} = {c['value']} {verb} the {predicted_label} prediction "
        f"(contribution {c['shap']:+.3f})."
    )


def _local_narrative(
    prediction: Dict[str, Any],
    toward: List[Dict[str, Any]],
    against: List[Dict[str, Any]],
    cfg: Dict[str, Any],
) -> str:
    """A short paragraph a teacher could paste into a parent email."""
    label = prediction["predicted_label"]
    conf = prediction.get("confidence", 0.0)

    parts = [f"The model predicts {label} performance with {conf:.0%} confidence."]

    if toward:
        top = toward[:3]
        listed = ", ".join(f"{c['friendly_name']} ({c['value']})" for c in top)
        parts.append(f"The strongest support for this comes from {listed}.")

    if against:
        top_against = against[0]
        parts.append(
            f"Working in the other direction, {top_against['friendly_name']} "
            f"({top_against['value']}) is the clearest factor pointing away from {label}."
        )

    actionable = [c for c in toward + against if c["actionable"]]
    if actionable and prediction["predicted_class"] != "H":
        lever = max(actionable, key=lambda c: abs(c["shap"]))
        parts.append(
            f"Of the factors a school can influence, {lever['friendly_name']} carries the "
            "most weight here — the counterfactual view shows what changing it would take."
        )

    return " ".join(parts)


# =============================================================================
# Plots
# =============================================================================

def plot_global_importance(
    importance: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
) -> Tuple[Path, str]:
    """Horizontal bar chart of the global ranking, in the project's house style."""
    import matplotlib.pyplot as plt

    from src.analysis.eda import ACCENT, MUTED, TEXT, _despine, _save, apply_house_style

    cfg = cfg or load_config()
    apply_house_style()

    top = importance["ranked_features"][:int(cfg["explainability"]["shap"]["max_display"])]
    top = list(reversed(top))
    labels = [r["friendly_name"] for r in top]
    vals = [r["mean_abs_shap"] for r in top]
    # Highlight the levers a school can actually pull.
    colors = [ACCENT if r["actionable"] else MUTED for r in top]

    fig, ax = plt.subplots(figsize=(9, 0.42 * len(top) + 1.6))
    ax.barh(labels, vals, color=colors, height=0.7, edgecolor="none")
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.012, i, f"{v:.3f}", va="center", fontsize=8.5, color=TEXT)

    ax.set_xlabel("Mean |SHAP value| — average influence on the prediction")
    ax.set_title("What the model actually pays attention to", fontsize=13, fontweight="600")
    ax.set_xlim(0, max(vals) * 1.14)
    ax.grid(axis="y", visible=False)
    _despine(ax)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=ACCENT),
        plt.Rectangle((0, 0), 1, 1, color=MUTED),
    ]
    ax.legend(handles, ["School can influence", "Fixed / demographic"],
              loc="lower right", frameon=False, fontsize=9)
    fig.tight_layout()

    path = _save(fig, "12_shap_global_importance.png", cfg)
    caption = (
        "Features ranked by how much they move the model's output on average. Blue bars are "
        "levers a school can pull; grey bars are attributes it cannot. The ranking is computed "
        f"across {importance['n_students_explained']} held-out students."
    )
    return path, caption


def plot_local_explanation(
    explanation: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    filename: str = "13_shap_local_example.png",
) -> Tuple[Path, str]:
    """Diverging bar chart for a single student — the 'why this child' view."""
    import matplotlib.pyplot as plt

    from src.analysis.eda import CLASS_COLORS, TEXT, _despine, _save, apply_house_style

    cfg = cfg or load_config()
    apply_house_style()

    contribs = list(reversed(explanation["contributions"][:10]))
    labels = [f"{c['friendly_name']} = {c['value']}" for c in contribs]
    vals = [c["shap"] for c in contribs]
    pos, neg = CLASS_COLORS["H"], CLASS_COLORS["L"]
    colors = [pos if v > 0 else neg for v in vals]

    fig, ax = plt.subplots(figsize=(9.5, 0.44 * len(contribs) + 1.8))
    ax.barh(labels, vals, color=colors, height=0.7, edgecolor="none")
    ax.axvline(0, color=TEXT, linewidth=1)

    span = max(abs(min(vals)), abs(max(vals))) or 1.0
    for i, v in enumerate(vals):
        offset = span * 0.02
        ax.text(v + (offset if v > 0 else -offset), i, f"{v:+.3f}",
                va="center", ha="left" if v > 0 else "right", fontsize=8.5, color=TEXT)
    ax.set_xlim(-span * 1.28, span * 1.28)

    pred = explanation["prediction"]
    ax.set_xlabel(f"Contribution to the '{pred['predicted_label']}' prediction")
    ax.set_title(
        f"Why this student was predicted {pred['predicted_label']} "
        f"({pred.get('confidence', 0):.0%} confidence)",
        fontsize=13, fontweight="600",
    )
    ax.grid(axis="y", visible=False)
    _despine(ax)
    fig.tight_layout()

    path = _save(fig, filename, cfg)
    caption = (
        "Each bar is one factor's contribution for this individual student. Green pushes toward "
        "the predicted band, red pushes away. The bars sum to the gap between this student's "
        "prediction and the dataset average."
    )
    return path, caption


# =============================================================================
# Pipeline entry point
# =============================================================================

def run_explainability(cfg: Dict[str, Any] | None = None, save: bool = True) -> Dict[str, Any]:
    """Phase 4 entry point: global ranking, two example students, both plots."""
    from src.models.train import make_split

    cfg = cfg or load_config()
    section(logger, "PHASE 4 — SHAP EXPLAINABILITY")

    importance = global_importance(cfg=cfg)
    logger.info("Top features: %s", ", ".join(importance["top_features"][:5]))

    figures = {}
    path, caption = plot_global_importance(importance, cfg)
    figures["global"] = {"path": str(path), "filename": path.name, "caption": caption}

    # Explain two contrasting students so the report can show both ends of the
    # scale — a struggling student and a thriving one.
    _, X_test, _, y_test, class_order = make_split(cfg)
    examples: Dict[str, Any] = {}

    for target_cls, tag in (("L", "at_risk"), ("H", "thriving")):
        idx = np.where(y_test == class_order.index(target_cls))[0]
        if len(idx) == 0:
            continue
        student = X_test.iloc[int(idx[0])]
        expl = explain_student(student, cfg)
        examples[tag] = {
            "actual_class": target_cls,
            "predicted_class": expl["prediction"]["predicted_class"],
            "confidence": expl["prediction"].get("confidence"),
            "summary": expl["summary"],
            "contributions": expl["contributions"][:8],
        }
        if tag == "at_risk":
            p, c = plot_local_explanation(expl, cfg)
            figures["local_at_risk"] = {"path": str(p), "filename": p.name, "caption": c}

    output = {
        "global": importance,
        "examples": examples,
        "figures": figures,
        "method": (
            "TreeExplainer (exact SHAP values) where the final model is tree-based, "
            "KernelExplainer (sampled approximation) otherwise. One-hot columns are summed "
            "back to their source feature so every number is reported against a name a "
            "teacher recognises."
        ),
    }

    if save:
        out_path = get_path("shap_file", cfg, ensure_parent=True)
        save_json(output, out_path)
        logger.info("Saved SHAP artifacts -> %s", out_path)

    return output


if __name__ == "__main__":
    run_explainability()
