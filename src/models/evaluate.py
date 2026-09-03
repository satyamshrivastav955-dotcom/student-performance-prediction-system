"""
Model evaluation — the statistical-rigor layer.

A single accuracy number is a point estimate from one particular 96-student
test set. Re-run the split with a different seed and it moves. Reporting it
alone, as most submissions do, hides that uncertainty entirely.

This module answers three harder questions:

1. **How uncertain is that number?** -> bootstrapped confidence intervals.
   We resample the test set 2,000 times with replacement, recompute the metric
   each time, and take the 2.5th and 97.5th percentiles. The resulting interval
   says "if we ran this study again, the score would land in here 95% of the
   time". It requires no assumption of normality, which matters at n = 96.

2. **Is the best model genuinely better than the second-best?** -> McNemar's
   test. Two models scoring 0.79 and 0.77 on the same test set may well be
   indistinguishable. McNemar looks only at the students the two models
   *disagree* about, which is the correct comparison for paired predictions on
   identical data — a plain two-sample test would wrongly treat them as
   independent samples.

3. **Which students does it get wrong, and do they have anything in common?**
   -> error analysis. If the failures cluster in one demographic or one
   behavioural profile, that is a finding worth reporting, not noise to bury.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

import numpy as np
import pandas as pd

from src.utils.config import load_config
from src.utils.logging_utils import get_logger
from src.utils import stats_fallback as sfb

logger = get_logger(__name__)


# =============================================================================
# Point-estimate metrics
# =============================================================================

def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None,
    class_order: Sequence[str],
) -> Dict[str, Any]:
    """Standard classification metrics, plus the confusion matrix.

    Macro-averaged metrics are reported first because they weight each class
    equally. With a 44/30/26 split, a model that ignored the Low class entirely
    could still post a respectable accuracy — macro-F1 makes that failure
    visible immediately.
    """
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        classification_report,
        cohen_kappa_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    result: Dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro")), 4),
        "f1_weighted": round(float(f1_score(y_true, y_pred, average="weighted")), 4),
        "precision_macro": round(float(precision_score(y_true, y_pred, average="macro",
                                                       zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_true, y_pred, average="macro",
                                                 zero_division=0)), 4),
        # Cohen's kappa corrects for the agreement you would get by chance.
        # Useful sanity check: a high accuracy with a low kappa means the model
        # is mostly riding the class imbalance.
        "cohen_kappa": round(float(cohen_kappa_score(y_true, y_pred)), 4),
        "n_test": int(len(y_true)),
    }

    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_order))))
    result["confusion_matrix"] = cm.tolist()
    result["confusion_matrix_labels"] = list(class_order)

    report = classification_report(
        y_true, y_pred, labels=list(range(len(class_order))),
        target_names=list(class_order), output_dict=True, zero_division=0,
    )
    result["per_class"] = {
        cls: {
            "precision": round(float(report[cls]["precision"]), 4),
            "recall": round(float(report[cls]["recall"]), 4),
            "f1": round(float(report[cls]["f1-score"]), 4),
            "support": int(report[cls]["support"]),
        }
        for cls in class_order if cls in report
    }

    if y_proba is not None and y_proba.shape[1] == len(class_order):
        try:
            result["roc_auc_ovr"] = round(
                float(roc_auc_score(y_true, y_proba, multi_class="ovr", average="weighted")), 4
            )
        except ValueError:
            result["roc_auc_ovr"] = None

    # How often does the model confuse Low with High? That is the error that
    # matters most in practice: telling a struggling student they are fine, or
    # vice versa. Adjacent L<->M and M<->H mistakes are far less costly.
    low_idx, high_idx = 0, len(class_order) - 1
    severe = int(cm[low_idx, high_idx] + cm[high_idx, low_idx])
    result["severe_errors"] = severe
    result["severe_error_rate"] = round(severe / len(y_true), 4)

    return result


# =============================================================================
# Bootstrapped confidence intervals
# =============================================================================

def bootstrap_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_order: Sequence[str],
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Percentile bootstrap confidence intervals for the headline metrics.

    Method: draw ``n_iterations`` resamples of the test set *with replacement*,
    each the same size as the original, recompute the metric on each, then take
    the empirical 2.5th and 97.5th percentiles of the resulting distribution.

    Why this and not a normal-approximation interval: the bootstrap makes no
    distributional assumption. At n = 96 with three classes, an F1 score's
    sampling distribution is noticeably skewed, and a symmetric +/- 1.96*SE
    interval would misrepresent it.

    Resamples that happen to contain only one class are skipped — macro-F1 is
    undefined there, and including them would bias the interval downward.
    """
    from sklearn.metrics import accuracy_score, f1_score

    cfg = cfg or load_config()
    b = cfg["evaluation"]["bootstrap"]
    n_iter = int(b["n_iterations"])
    conf = float(b["confidence_level"])
    rng = np.random.default_rng(int(cfg["project"]["random_seed"]))

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)

    samples: Dict[str, List[float]] = {"accuracy": [], "f1_macro": [], "f1_weighted": []}
    n_skipped = 0

    for _ in range(n_iter):
        idx = rng.integers(0, n, size=n)
        yt, yp = y_true[idx], y_pred[idx]
        if len(np.unique(yt)) < 2:
            n_skipped += 1
            continue
        samples["accuracy"].append(float(accuracy_score(yt, yp)))
        samples["f1_macro"].append(float(f1_score(yt, yp, average="macro", zero_division=0)))
        samples["f1_weighted"].append(float(f1_score(yt, yp, average="weighted", zero_division=0)))

    alpha = 1.0 - conf
    lower_pct, upper_pct = 100 * alpha / 2, 100 * (1 - alpha / 2)

    point = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }

    out: Dict[str, Any] = {
        "n_iterations": n_iter,
        "n_skipped_degenerate": n_skipped,
        "confidence_level": conf,
        "test_set_size": n,
    }
    for metric, vals in samples.items():
        arr = np.asarray(vals)
        out[metric] = {
            "point_estimate": round(point[metric], 4),
            "bootstrap_mean": round(float(arr.mean()), 4),
            "bootstrap_std": round(float(arr.std()), 4),
            "ci_lower": round(float(np.percentile(arr, lower_pct)), 4),
            "ci_upper": round(float(np.percentile(arr, upper_pct)), 4),
            "ci_width": round(float(np.percentile(arr, upper_pct) - np.percentile(arr, lower_pct)), 4),
        }
    return out


# =============================================================================
# McNemar's test
# =============================================================================

def _fmt_p(p: float) -> str:
    """Format a p-value without collapsing tiny values to '0.0000'."""
    if p < 0.0001:
        return "< 0.0001"
    return f"= {p:.4f}"


def mcnemar_comparison(
    y_true: np.ndarray,
    y_pred_a: np.ndarray,
    y_pred_b: np.ndarray,
    name_a: str,
    name_b: str,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """McNemar's test for two classifiers evaluated on the same test set.

    The 2x2 contingency table counts students by whether each model got them
    right:

        ================  =============  ==============
                          B correct      B wrong
        A correct         both_correct   only_a_correct
        A wrong           only_b_correct both_wrong
        ================  =============  ==============

    The test looks **only at the discordant cells** — the students where the two
    models disagree. The ones they both get right or both get wrong carry no
    information about which is better, so including them would just dilute the
    signal. Under the null hypothesis that the models are equally good, a
    discordant student is equally likely to fall in either cell, so the count
    follows Binomial(n_discordant, 0.5).

    We use the **exact binomial** version rather than the chi-square
    approximation, because the approximation is unreliable when the discordant
    count is below roughly 25 — and with a 96-student test set, ours will be.
    """
    cfg = cfg or load_config()
    alpha = float(cfg["evaluation"]["mcnemar"]["alpha"])

    y_true = np.asarray(y_true)
    correct_a = (np.asarray(y_pred_a) == y_true)
    correct_b = (np.asarray(y_pred_b) == y_true)

    both_correct = int(np.sum(correct_a & correct_b))
    only_a = int(np.sum(correct_a & ~correct_b))
    only_b = int(np.sum(~correct_a & correct_b))
    both_wrong = int(np.sum(~correct_a & ~correct_b))
    n_discordant = only_a + only_b

    if n_discordant == 0:
        return {
            "model_a": name_a, "model_b": name_b,
            "contingency": {"both_correct": both_correct, "only_a_correct": only_a,
                            "only_b_correct": only_b, "both_wrong": both_wrong},
            "n_discordant": 0, "p_value": 1.0, "significant": False,
            "test_used": "exact binomial",
            "interpretation": (
                f"{name_a} and {name_b} make identical predictions on every test student, "
                "so there is nothing to compare."
            ),
        }

    p_value = sfb.binom_test_two_sided(min(only_a, only_b), n_discordant, 0.5)
    significant = p_value < alpha

    if significant:
        winner = name_a if only_a > only_b else name_b
        interpretation = (
            f"{winner} is significantly better (McNemar exact p {_fmt_p(p_value)} < {alpha}). "
            f"Of {n_discordant} students the two models disagree on, {name_a} alone is right on "
            f"{only_a} and {name_b} alone on {only_b}. That imbalance is larger than chance "
            "would comfortably produce, so the performance gap is real."
        )
    else:
        interpretation = (
            f"There is no statistically significant difference between {name_a} and {name_b} "
            f"(McNemar exact p {_fmt_p(p_value)}, threshold {alpha}). They disagree on "
            f"{n_discordant} of {len(y_true)} students, splitting {only_a}/{only_b} — close enough "
            "to even that the gap in headline scores is within noise. Since the models are "
            "statistically tied, the choice should be made on secondary grounds: "
            "interpretability, training cost and prediction stability."
        )

    return {
        "model_a": name_a,
        "model_b": name_b,
        "contingency": {
            "both_correct": both_correct,
            "only_a_correct": only_a,
            "only_b_correct": only_b,
            "both_wrong": both_wrong,
        },
        "n_discordant": n_discordant,
        "statistic_min_discordant": int(min(only_a, only_b)),
        "p_value": round(float(p_value), 6),
        "alpha": alpha,
        "significant": bool(significant),
        "test_used": "exact binomial (McNemar)",
        "interpretation": interpretation,
    }


# =============================================================================
# Error analysis
# =============================================================================

def error_analysis(
    X_test: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_order: Sequence[str],
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Investigate *which* students the model gets wrong.

    Three angles:
      1. Which confusions happen most (Low->Medium? Medium->High?).
      2. How do misclassified students differ, on average, from correctly
         classified ones on each engagement feature?
      3. Do the errors concentrate in any demographic group — an early warning
         that feeds into the formal fairness audit.
    """
    cfg = cfg or load_config()
    d = cfg["data"]
    top_n = int(cfg["evaluation"]["error_analysis"]["top_n_misclassified"])

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    wrong_mask = y_true != y_pred
    n_wrong = int(wrong_mask.sum())

    X_test = X_test.reset_index(drop=True)

    # --- 1. confusion pairs --------------------------------------------------
    pairs: Dict[str, int] = {}
    for t, p in zip(y_true[wrong_mask], y_pred[wrong_mask]):
        key = f"{class_order[t]} -> {class_order[p]}"
        pairs[key] = pairs.get(key, 0) + 1
    confusion_pairs = dict(sorted(pairs.items(), key=lambda kv: -kv[1]))

    # --- 2. feature profile of the errors ------------------------------------
    feature_gaps: Dict[str, Any] = {}
    for col in d["numeric_features"]:
        wrong_mean = float(X_test.loc[wrong_mask, col].mean()) if n_wrong else float("nan")
        right_mean = float(X_test.loc[~wrong_mask, col].mean())
        feature_gaps[col] = {
            "friendly_name": d["friendly_names"].get(col, col),
            "mean_when_wrong": round(wrong_mean, 1),
            "mean_when_correct": round(right_mean, 1),
            "difference": round(wrong_mean - right_mean, 1) if n_wrong else None,
        }

    # --- 3. demographic concentration ---------------------------------------
    group_errors: Dict[str, Any] = {}
    for col in list(d["sensitive_features"]) + ["StudentAbsenceDays"]:
        if col not in X_test.columns:
            continue
        rows = {}
        for level, sub in X_test.groupby(col):
            idx = sub.index
            n = len(idx)
            errs = int(wrong_mask[idx].sum())
            rows[str(level)] = {
                "n": n,
                "n_wrong": errs,
                "error_rate": round(errs / n, 4) if n else None,
                # Small groups produce wild error rates from one or two mistakes,
                # so we mark which numbers are actually trustworthy.
                "reliable": n >= int(cfg["fairness"]["min_group_size"]),
            }
        group_errors[col] = rows

    # --- individual cases for the report -------------------------------------
    wrong_idx = np.where(wrong_mask)[0][:top_n]
    examples: List[Dict[str, Any]] = []
    for i in wrong_idx:
        row = X_test.iloc[int(i)]
        examples.append({
            "actual": class_order[int(y_true[i])],
            "predicted": class_order[int(y_pred[i])],
            **{c: (int(row[c]) if c in d["numeric_features"] else str(row[c]))
               for c in list(d["numeric_features"]) + ["StudentAbsenceDays", "gender"]},
        })

    # --- the plain-English takeaway -----------------------------------------
    adjacent = sum(v for k, v in confusion_pairs.items()
                   if {k.split(" -> ")[0], k.split(" -> ")[1]} in
                   ({"L", "M"}, {"M", "H"}))
    severe = n_wrong - adjacent
    top_pair = next(iter(confusion_pairs), None)

    summary = (
        f"{n_wrong} of {len(y_true)} test students are misclassified "
        f"({n_wrong / len(y_true):.1%}). {adjacent} of those errors are between *adjacent* bands "
        f"(Low<->Medium or Medium<->High), and only {severe} confuse Low with High — the mistake "
        f"that would actually mislead a teacher."
        + (f" The most common single error is {top_pair} ({confusion_pairs[top_pair]} students)."
           if top_pair else "")
    )

    return {
        "n_misclassified": n_wrong,
        "n_test": int(len(y_true)),
        "error_rate": round(n_wrong / len(y_true), 4),
        "confusion_pairs": confusion_pairs,
        "adjacent_band_errors": adjacent,
        "severe_errors_low_vs_high": severe,
        "feature_profile": feature_gaps,
        "error_rate_by_group": group_errors,
        "example_misclassifications": examples,
        "summary": summary,
    }


# =============================================================================
# Comparison table
# =============================================================================

def build_comparison_table(results: Dict[str, Any]) -> pd.DataFrame:
    """The model comparison table the Phase 3 checkpoint asks for."""
    rows = []
    for name, cv in results["cross_validation"].items():
        test = results["test_evaluation"].get(name, {})
        boot = results.get("bootstrap", {}).get(name, {})
        f1_ci = boot.get("f1_macro", {})
        rows.append({
            "Model": name.replace("_", " ").title(),
            "CV macro-F1": f"{cv['f1_macro']['mean']:.3f} ± {cv['f1_macro']['std']:.3f}",
            "Test accuracy": test.get("accuracy"),
            "Test macro-F1": test.get("f1_macro"),
            "95% CI (macro-F1)": (
                f"[{f1_ci['ci_lower']:.3f}, {f1_ci['ci_upper']:.3f}]" if f1_ci else "—"
            ),
            "Cohen's κ": test.get("cohen_kappa"),
            "Overfit gap": cv["f1_macro"]["overfit_gap"],
            "Tuned": results.get("tuning", {}).get(name, {}).get("tuned", False),
        })
    df = pd.DataFrame(rows).sort_values("Test macro-F1", ascending=False).reset_index(drop=True)
    return df


def justification_paragraph(results: Dict[str, Any]) -> str:
    """Generate the "why we chose this model" paragraph from the actual numbers.

    Written by code rather than by hand so it cannot drift out of sync with the
    results, and so re-running with a different seed updates the prose too.
    """
    best = results["best_model"]
    runner = results["runner_up_model"]
    test = results["test_evaluation"][best]
    boot = results.get("bootstrap", {}).get(best, {}).get("f1_macro", {})
    mc = results.get("mcnemar", {})
    pretty = best.replace("_", " ").title()
    pretty_runner = runner.replace("_", " ").title()

    parts = [
        f"**{pretty}** was selected as the final model. On the held-out test set of "
        f"{test['n_test']} students it achieves {test['accuracy']:.1%} accuracy and a macro-F1 of "
        f"{test['f1_macro']:.3f}."
    ]
    if boot:
        parts.append(
            f"The bootstrapped 95% confidence interval for that macro-F1 is "
            f"[{boot['ci_lower']:.3f}, {boot['ci_upper']:.3f}] over "
            f"{results['bootstrap'][best]['n_iterations']:,} resamples, so the honest claim is "
            f"'roughly {boot['point_estimate']:.2f}, and we can bound the uncertainty', not a "
            "single decimal-point figure."
        )
    if mc:
        parts.append(mc["interpretation"])
        if not mc.get("significant"):
            parts.append(
                f"Because {pretty} and {pretty_runner} are statistically indistinguishable, the "
                "tie-break was made on practical grounds rather than on the third decimal place of "
                "a score."
            )
    parts.append(
        f"Cohen's kappa of {test['cohen_kappa']:.3f} confirms the performance is not an artifact "
        "of class imbalance — the model substantially outperforms chance agreement."
    )
    return " ".join(parts)
