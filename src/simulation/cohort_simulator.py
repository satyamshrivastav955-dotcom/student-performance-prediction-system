"""
Monte Carlo cohort simulator — from per-student to policy-level.

Most student prediction systems answer "how is *this* student doing?" This
module answers a harder, more valuable question: "if we changed something about
the whole class, how would the distribution of outcomes shift?"

Example
-------
A teacher wonders: "If participation across my class improved by 15%, how many
students would move from Low to Medium?" The simulator models this by:

1. Taking every student in the dataset.
2. Applying the intervention (e.g., +15% to ``raisedhands`` and
   ``VisITedResources``), with per-student noise to reflect that not every
   student responds identically.
3. Re-scoring the whole class with the trained model.
4. Repeating steps 2–3 many times (Monte Carlo) to build a distribution of
   plausible outcomes rather than one fragile point estimate.
5. Reporting the mean shift in L/M/H proportions with confidence intervals.

Why Monte Carlo and not just "apply the shift once"?
    Because a single deterministic shift overstates our certainty. In reality,
    some students will respond more than 15% and others less. The noise term
    models this heterogeneity, and repeating many times lets us report how sure
    we are about the aggregate shift — which is the number a decision-maker
    actually needs.

Interventions are specified as percentage changes to existing values (not
absolute values), capped at the feature's permitted range from config. This
prevents nonsensical outputs like "200 hands raised in class".
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from src.data.preprocess import feature_columns, load_processed, split_features_target
from src.models.predict import load_model_bundle, prepare_input
from src.utils.config import (
    class_label,
    friendly,
    get_path,
    get_seed,
    load_config,
    save_json,
)
from src.utils.logging_utils import get_logger, section

logger = get_logger(__name__)


# =============================================================================
# Intervention application
# =============================================================================

def apply_intervention(
    X: pd.DataFrame,
    intervention: Dict[str, float],
    cfg: Dict[str, Any],
    rng: np.random.Generator | None = None,
    noise_std_fraction: float = 0.10,
) -> pd.DataFrame:
    """Apply a percentage-based intervention with per-student noise.

    Args:
        X:  Student features (raw, pre-preprocessing).
        intervention:  Mapping of feature name -> percentage change. Positive
                       means increase (e.g., 15 = +15% of each student's
                       current value). For StudentAbsenceDays, the semantics
                       are inverted: a positive number means *fewer* absences.
        cfg:  Project config dict.
        rng:  numpy random generator for reproducibility.
        noise_std_fraction:  Standard deviation of the noise as a fraction of
                             the intervention size. 0.10 means ±10%.

    Returns:
        A copy of X with the intervention applied.
    """
    if rng is None:
        rng = np.random.default_rng(get_seed(cfg))

    numeric_features = set(cfg["data"]["numeric_features"])
    counterfactual_cfg = cfg.get("counterfactuals", {})
    permitted = counterfactual_cfg.get("permitted_range", {})

    X_new = X.copy()

    for feat, pct in intervention.items():
        if feat not in X_new.columns:
            logger.warning("Intervention feature '%s' not in data — skipping.", feat)
            continue

        if feat in numeric_features:
            current = X_new[feat].astype(float).values
            # The noise models heterogeneous student response: not everyone
            # benefits equally from the same policy.
            noise = rng.normal(loc=1.0, scale=noise_std_fraction, size=len(current))
            shift = current * (pct / 100.0) * noise

            # Special handling for absence: a "reduction" is an improvement
            if feat == "StudentAbsenceDays":
                # This is binary (0=Under-7, 1=Above-7) after encoding,
                # but we handle the raw version here too
                pass

            new_values = current + shift

            # Clip to permitted range
            lo, hi = 0, 100
            if feat in permitted:
                lo, hi = permitted[feat]
            new_values = np.clip(new_values, lo, hi)
            X_new[feat] = np.round(new_values).astype(int)

        elif feat == "StudentAbsenceDays" and pct != 0:
            # Binary feature: we model a percentage of "Above-7" students
            # flipping to "Under-7" (i.e., improving attendance)
            above_mask = X_new[feat] == "Above-7"
            n_above = above_mask.sum()
            n_to_flip = int(round(n_above * abs(pct) / 100.0))
            if n_to_flip > 0 and pct > 0:
                flip_indices = rng.choice(
                    X_new.index[above_mask], size=min(n_to_flip, n_above), replace=False
                )
                X_new.loc[flip_indices, feat] = "Under-7"

    return X_new


# =============================================================================
# Single simulation run
# =============================================================================

def _class_distribution(
    y_pred: np.ndarray, class_order: List[str]
) -> Dict[str, float]:
    """Compute the fraction of students in each class."""
    n = len(y_pred)
    dist: Dict[str, float] = {}
    for i, cls in enumerate(class_order):
        dist[cls] = round(float(np.sum(y_pred == i)) / n, 4) if n > 0 else 0.0
    return dist


def _class_counts(
    y_pred: np.ndarray, class_order: List[str]
) -> Dict[str, int]:
    """Count students in each class."""
    counts: Dict[str, int] = {}
    for i, cls in enumerate(class_order):
        counts[cls] = int(np.sum(y_pred == i))
    return counts


def simulate_intervention(
    X: pd.DataFrame,
    intervention: Dict[str, float],
    cfg: Dict[str, Any],
    n_runs: int | None = None,
    noise_std: float | None = None,
) -> Dict[str, Any]:
    """Run a Monte Carlo simulation for one intervention scenario.

    Applies the intervention ``n_runs`` times with different random noise seeds,
    scores every student each time, and aggregates the resulting L/M/H
    distributions into means and confidence intervals.

    Args:
        X:  Raw student features (all students in the cohort).
        intervention:  Feature -> percentage change dict.
        cfg:  Project config.
        n_runs:  Number of Monte Carlo repetitions (default from config).
        noise_std:  Per-student noise fraction (default from config).

    Returns:
        Dict with baseline distribution, simulated distribution (mean + CI),
        and the shift.
    """
    sim_cfg = cfg.get("simulation", {})
    n_runs = n_runs or sim_cfg.get("n_runs", 500)
    noise_std = noise_std if noise_std is not None else sim_cfg.get("noise_std_fraction", 0.10)
    seed = get_seed(cfg)

    bundle = load_model_bundle()
    pipeline = bundle["pipeline"]
    class_order: List[str] = list(bundle["class_order"])
    n_classes = len(class_order)
    n_students = len(X)

    # Baseline prediction (no intervention)
    X_base = prepare_input(X, cfg)
    y_baseline = pipeline.predict(X_base)
    baseline_dist = _class_distribution(y_baseline, class_order)
    baseline_counts = _class_counts(y_baseline, class_order)

    # Monte Carlo runs
    all_dists = np.zeros((n_runs, n_classes))
    for run in range(n_runs):
        rng = np.random.default_rng(seed + run)
        X_modified = apply_intervention(X, intervention, cfg, rng=rng, noise_std_fraction=noise_std)
        X_prepared = prepare_input(X_modified, cfg)
        y_sim = pipeline.predict(X_prepared)

        for i in range(n_classes):
            all_dists[run, i] = np.sum(y_sim == i) / n_students

    # Aggregate results
    mean_dist = {
        cls: round(float(np.mean(all_dists[:, i])), 4)
        for i, cls in enumerate(class_order)
    }
    ci_lower = {
        cls: round(float(np.percentile(all_dists[:, i], 2.5)), 4)
        for i, cls in enumerate(class_order)
    }
    ci_upper = {
        cls: round(float(np.percentile(all_dists[:, i], 97.5)), 4)
        for i, cls in enumerate(class_order)
    }
    std_dist = {
        cls: round(float(np.std(all_dists[:, i])), 4)
        for i, cls in enumerate(class_order)
    }

    # Shift = simulated - baseline
    shift = {
        cls: round(mean_dist[cls] - baseline_dist[cls], 4)
        for cls in class_order
    }

    # Mean simulated counts
    mean_counts = {
        cls: round(float(np.mean(all_dists[:, i]) * n_students), 1)
        for i, cls in enumerate(class_order)
    }

    return {
        "intervention": intervention,
        "intervention_description": _describe_intervention(intervention, cfg),
        "n_runs": n_runs,
        "n_students": n_students,
        "baseline": {
            "distribution": baseline_dist,
            "counts": baseline_counts,
        },
        "simulated": {
            "distribution_mean": mean_dist,
            "distribution_ci_lower": ci_lower,
            "distribution_ci_upper": ci_upper,
            "distribution_std": std_dist,
            "mean_counts": mean_counts,
        },
        "shift": shift,
        "summary": _summarise_shift(baseline_dist, mean_dist, shift, class_order, cfg),
    }


def _describe_intervention(
    intervention: Dict[str, float], cfg: Dict[str, Any]
) -> str:
    """Human-readable description of an intervention."""
    parts = []
    for feat, pct in intervention.items():
        name = friendly(feat, cfg)
        direction = "increase" if pct > 0 else "decrease"
        parts.append(f"{name}: {direction} by {abs(pct):.0f}%")
    return "; ".join(parts) if parts else "No change (baseline)"


def _summarise_shift(
    baseline: Dict[str, float],
    simulated: Dict[str, float],
    shift: Dict[str, float],
    class_order: List[str],
    cfg: Dict[str, Any],
) -> str:
    """One-paragraph summary of the simulation result."""
    lines = []
    for cls in class_order:
        label = class_label(cls, cfg)
        b = baseline[cls] * 100
        s = simulated[cls] * 100
        d = shift[cls] * 100
        direction = "↑" if d > 0 else "↓" if d < 0 else "→"
        lines.append(f"{label}: {b:.1f}% → {s:.1f}% ({direction}{abs(d):.1f}pp)")

    return " | ".join(lines)


# =============================================================================
# Pre-defined intervention scenarios
# =============================================================================

def default_scenarios(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The built-in intervention scenarios that appear in the dashboard.

    These are designed to answer the kinds of questions a school administrator
    would actually ask:
    - "What if we boosted class participation?"
    - "What if we improved attendance?"
    - "What if we ran a combined engagement programme?"
    """
    return [
        {
            "name": "Boost Participation (+15%)",
            "description": "All students raise their hands and visit resources 15% more often.",
            "intervention": {
                "raisedhands": 15,
                "VisITedResources": 15,
            },
        },
        {
            "name": "Improve Attendance",
            "description": "30% of students with high absences switch to low absences.",
            "intervention": {
                "StudentAbsenceDays": 30,
            },
        },
        {
            "name": "Discussion Focus (+20%)",
            "description": "All students increase their discussion participation by 20%.",
            "intervention": {
                "Discussion": 20,
            },
        },
        {
            "name": "Combined Engagement Programme",
            "description": (
                "A realistic multi-factor intervention: participation up 15%, "
                "resource visits up 15%, discussions up 10%, and 25% of high-absence "
                "students shift to low absence."
            ),
            "intervention": {
                "raisedhands": 15,
                "VisITedResources": 15,
                "Discussion": 10,
                "StudentAbsenceDays": 25,
            },
        },
        {
            "name": "Announcements Campaign (+25%)",
            "description": "All students read 25% more announcements.",
            "intervention": {
                "AnnouncementsView": 25,
            },
        },
    ]


# =============================================================================
# Run all scenarios (pipeline stage)
# =============================================================================

def run_all_scenarios(
    cfg: Dict[str, Any] | None = None,
    save: bool = True,
) -> Dict[str, Any]:
    """Run every default scenario and report the results.

    This is the pipeline entry point called by ``scripts/run_pipeline.py``.
    """
    cfg = cfg or load_config()
    section(logger, "Cohort Intervention Simulator")

    if not cfg.get("simulation", {}).get("enabled", True):
        logger.info("Simulation disabled in config — skipping.")
        return {"enabled": False}

    df = load_processed(cfg)
    X, _ = split_features_target(df, cfg)

    scenarios = default_scenarios(cfg)
    results: List[Dict[str, Any]] = []

    for scenario in scenarios:
        logger.info("Scenario: %s", scenario["name"])
        sim_result = simulate_intervention(X, scenario["intervention"], cfg)
        sim_result["scenario_name"] = scenario["name"]
        sim_result["scenario_description"] = scenario["description"]
        results.append(sim_result)
        logger.info("  %s", sim_result["summary"])

    report = {
        "n_scenarios": len(results),
        "scenarios": results,
        "methodology": (
            "Monte Carlo simulation with per-student Gaussian noise. Each scenario "
            "applies a percentage-based intervention to the feature(s), adds noise "
            "to model heterogeneous student response, re-scores the whole cohort, "
            "and repeats N times. Results report mean class distribution shifts with "
            "95% confidence intervals."
        ),
    }

    if save:
        out_path = get_path("simulation_file", cfg, ensure_parent=True)
        save_json(report, out_path)
        logger.info("Saved simulation results -> %s", out_path)

    return report


# =============================================================================
# Dashboard-friendly single-scenario runner
# =============================================================================

def simulate_custom(
    intervention: Dict[str, float],
    cfg: Dict[str, Any] | None = None,
    n_runs: int = 200,
) -> Dict[str, Any]:
    """Run a single custom scenario — called from the dashboard sliders.

    Uses fewer Monte Carlo runs than the full pipeline (200 vs 500) for faster
    interactive response, while still giving a reasonable CI.
    """
    cfg = cfg or load_config()
    df = load_processed(cfg)
    X, _ = split_features_target(df, cfg)
    return simulate_intervention(X, intervention, cfg, n_runs=n_runs)


if __name__ == "__main__":  # pragma: no cover - manual run
    run_all_scenarios()
