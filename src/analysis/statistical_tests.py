"""
Statistical hypothesis testing — the evidence layer behind the EDA.

The brief asks us to "identify key factors affecting performance". Most
submissions answer that with a bar chart and the sentence "as we can see,
students with more absences perform worse". That is an *observation*, not
evidence — it has no way of distinguishing a real effect from sampling noise.

This module answers the same question with actual hypothesis tests:

* **One-way ANOVA** for each continuous engagement feature across the three
  performance classes. Null hypothesis: the mean of this feature is identical
  in the Low, Medium and High groups. A small p-value says the differences we
  can see in the chart are larger than chance would produce.

* **Levene's test** (median-centred, i.e. Brown-Forsythe) as an assumption
  check. ANOVA assumes the groups have roughly equal variance. If Levene says
  they do not, the ANOVA p-value is no longer trustworthy on its own — so we
  also report **Kruskal-Wallis**, the rank-based non-parametric equivalent that
  makes no such assumption. Reporting both is what an honest analysis looks
  like; quietly reporting only the one that agrees with you is not.

* **Chi-square test of independence** for each categorical feature against the
  class. Null hypothesis: the feature and performance class are independent.

* **Effect sizes** alongside every p-value — eta-squared for ANOVA, Cramer's V
  for chi-square. This matters: with enough data, a p-value can be tiny for an
  effect far too small to act on. The p-value tells you the effect is *real*;
  the effect size tells you whether it is *big enough to care about*. A school
  deciding where to spend intervention budget needs the second number.

* **Holm-Bonferroni correction** across the whole family of tests. We run ~13
  tests here. At alpha = 0.05, running 13 independent tests gives roughly a 49%
  chance of at least one false positive purely by luck. Holm controls that
  family-wise error rate while being uniformly more powerful than plain
  Bonferroni, so it costs us less real signal.

SciPy does the work when installed. If it is not, we fall back to
:mod:`src.utils.stats_fallback`, which computes the same distributions in pure
Python. The test suite checks the two agree.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from src.utils.config import get_path, load_config, save_json
from src.utils.logging_utils import get_logger
from src.utils import stats_fallback as sfb

logger = get_logger(__name__)

# Prefer SciPy; degrade gracefully. ``SCIPY_AVAILABLE`` is recorded in the JSON
# artifact so the report can state which backend produced its numbers.
try:  # pragma: no cover - environment dependent
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except Exception:  # pragma: no cover
    scipy_stats = None
    SCIPY_AVAILABLE = False


# =============================================================================
# Core tests
# =============================================================================

def one_way_anova(groups: Sequence[Sequence[float]]) -> Tuple[float, float, int, int]:
    """One-way ANOVA F test.

    Returns ``(F, p, df_between, df_within)``.

    The F statistic is the ratio of between-group variance to within-group
    variance. Intuitively: "how far apart are the group means, measured in units
    of how noisy each group is internally?" A large F means the gap between the
    Low/Medium/High averages is big relative to the spread inside each group.
    """
    arrays = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    k = len(arrays)
    if k < 2:
        return float("nan"), float("nan"), 0, 0

    n_total = sum(len(a) for a in arrays)
    grand_mean = float(np.concatenate(arrays).mean())

    ss_between = sum(len(a) * (a.mean() - grand_mean) ** 2 for a in arrays)
    ss_within = sum(((a - a.mean()) ** 2).sum() for a in arrays)

    df_between = k - 1
    df_within = n_total - k
    if df_within <= 0 or ss_within <= 0:
        return float("inf"), 0.0, df_between, max(df_within, 0)

    f_stat = (ss_between / df_between) / (ss_within / df_within)
    if SCIPY_AVAILABLE:
        p = float(scipy_stats.f.sf(f_stat, df_between, df_within))
    else:
        p = sfb.f_sf(f_stat, df_between, df_within)
    return float(f_stat), p, df_between, df_within


def eta_squared(groups: Sequence[Sequence[float]]) -> float:
    """Eta-squared: the share of a feature's total variance explained by class.

    Ranges 0-1. Conventional reading: 0.01 small, 0.06 medium, 0.14 large.
    So eta^2 = 0.35 means "35% of the variation in this behaviour is accounted
    for by which performance group the student is in" — a strong signal.
    """
    arrays = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    if len(arrays) < 2:
        return float("nan")
    allv = np.concatenate(arrays)
    grand_mean = float(allv.mean())
    ss_between = sum(len(a) * (a.mean() - grand_mean) ** 2 for a in arrays)
    ss_total = float(((allv - grand_mean) ** 2).sum())
    return float(ss_between / ss_total) if ss_total > 0 else float("nan")


def levene_test(groups: Sequence[Sequence[float]]) -> Tuple[float, float]:
    """Brown-Forsythe (median-centred) Levene test for equal variances.

    We centre on the median rather than the mean because the median version is
    far more robust to the skew our engagement counters actually have.

    A *small* p-value here is bad news for ANOVA's assumptions — it says the
    groups have significantly different spread, so we should lean on the
    Kruskal-Wallis result instead.
    """
    arrays = [np.asarray(g, dtype=float) for g in groups if len(g) > 1]
    k = len(arrays)
    if k < 2:
        return float("nan"), float("nan")

    z_groups = [np.abs(a - np.median(a)) for a in arrays]
    n_total = sum(len(z) for z in z_groups)
    z_grand = float(np.concatenate(z_groups).mean())

    numer = sum(len(z) * (z.mean() - z_grand) ** 2 for z in z_groups) / (k - 1)
    denom = sum(((z - z.mean()) ** 2).sum() for z in z_groups) / (n_total - k)
    if denom <= 0:
        return float("nan"), float("nan")

    w = numer / denom
    if SCIPY_AVAILABLE:
        p = float(scipy_stats.f.sf(w, k - 1, n_total - k))
    else:
        p = sfb.f_sf(w, k - 1, n_total - k)
    return float(w), p


def kruskal_wallis(groups: Sequence[Sequence[float]]) -> Tuple[float, float]:
    """Kruskal-Wallis H test — the rank-based, distribution-free alternative.

    Instead of comparing means it compares mean *ranks*, so it does not care
    whether the data are normal or whether the groups have equal variance. We
    report it next to every ANOVA as a robustness check: when both agree, the
    finding is solid regardless of which assumptions you are willing to make.
    """
    arrays = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    k = len(arrays)
    if k < 2:
        return float("nan"), float("nan")

    combined = np.concatenate(arrays)
    n = len(combined)
    ranks, tie_correction = sfb.rankdata_average(combined)
    ranks = np.asarray(ranks, dtype=float)

    h = 0.0
    idx = 0
    for a in arrays:
        r = ranks[idx: idx + len(a)]
        h += (r.sum() ** 2) / len(a)
        idx += len(a)
    h = 12.0 / (n * (n + 1)) * h - 3.0 * (n + 1)
    if tie_correction > 0:
        h /= tie_correction

    df = k - 1
    p = float(scipy_stats.chi2.sf(h, df)) if SCIPY_AVAILABLE else sfb.chi2_sf(h, df)
    return float(h), p


def chi_square_test(x: pd.Series, y: pd.Series) -> Dict[str, Any]:
    """Chi-square test of independence between two categorical variables.

    Also returns Cramer's V (the effect size) and a flag for whether the
    expected-count assumption holds. The standard rule is that no expected cell
    count should fall below 5; when it does, the chi-square approximation gets
    unreliable and we say so rather than quietly reporting the p-value anyway.
    """
    table = pd.crosstab(x, y)
    observed = table.to_numpy(dtype=float)
    n = observed.sum()
    if n == 0 or observed.shape[0] < 2 or observed.shape[1] < 2:
        return {"chi2": float("nan"), "p_value": float("nan"), "dof": 0,
                "cramers_v": float("nan"), "assumption_ok": False,
                "min_expected": float("nan"), "n": int(n)}

    row_totals = observed.sum(axis=1, keepdims=True)
    col_totals = observed.sum(axis=0, keepdims=True)
    expected = row_totals @ col_totals / n

    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = float(np.nansum((observed - expected) ** 2 / expected))
    dof = int((observed.shape[0] - 1) * (observed.shape[1] - 1))
    p = float(scipy_stats.chi2.sf(chi2, dof)) if SCIPY_AVAILABLE else sfb.chi2_sf(chi2, dof)

    min_dim = min(observed.shape) - 1
    cramers_v = float(np.sqrt(chi2 / (n * min_dim))) if min_dim > 0 and n > 0 else float("nan")
    min_expected = float(expected.min())

    return {
        "chi2": chi2,
        "p_value": p,
        "dof": dof,
        "cramers_v": cramers_v,
        "min_expected": min_expected,
        "assumption_ok": bool(min_expected >= 5.0),
        "n": int(n),
        "n_levels": int(observed.shape[0]),
    }


def holm_bonferroni(p_values: Sequence[float], alpha: float = 0.05) -> Tuple[List[float], List[bool]]:
    """Holm-Bonferroni step-down correction for multiple comparisons.

    Procedure: sort the p-values ascending, then compare the i-th smallest
    against ``alpha / (m - i)``. Equivalently we return *adjusted* p-values that
    can be read against the original alpha, which is friendlier in a report.

    Why correct at all: running 13 tests at alpha = 0.05 gives about a 49%
    chance of at least one spurious "significant" result. Holm keeps the
    family-wise error rate at 5% while rejecting more nulls than Bonferroni.
    """
    m = len(p_values)
    if m == 0:
        return [], []
    order = sorted(range(m), key=lambda i: (np.inf if np.isnan(p_values[i]) else p_values[i]))
    adjusted = [1.0] * m
    running_max = 0.0
    for rank, idx in enumerate(order):
        p = p_values[idx]
        if np.isnan(p):
            adjusted[idx] = float("nan")
            continue
        adj = min(1.0, (m - rank) * p)
        running_max = max(running_max, adj)   # enforce monotonicity
        adjusted[idx] = running_max
    significant = [(not np.isnan(a)) and a < alpha for a in adjusted]
    return adjusted, significant


def correlation_matrix(df: pd.DataFrame, columns: Sequence[str], method: str = "spearman") -> pd.DataFrame:
    """Correlation among the numeric features.

    Spearman by default: it measures monotonic association via ranks, so it is
    not distorted by the right-skew in the engagement counters the way Pearson
    would be.
    """
    return df[list(columns)].corr(method=method)


# =============================================================================
# Orchestration
# =============================================================================

def run_all_tests(df: pd.DataFrame, cfg: Dict[str, Any] | None = None, save: bool = True) -> Dict[str, Any]:
    """Run every test, apply the correction, and write the JSON artifact.

    This is the Phase 2 checkpoint. The returned dict is what the report and the
    dashboard's statistics section read from — no number in the write-up is
    typed by hand.
    """
    cfg = cfg or load_config()
    d = cfg["data"]
    s = cfg["statistics"]
    alpha = float(s["alpha"])
    target = d["target"]
    class_order = list(d["target_classes"])

    results: Dict[str, Any] = {
        "backend": "scipy" if SCIPY_AVAILABLE else "pure-python fallback",
        "alpha": alpha,
        "correction": s.get("multiple_testing_correction", "holm"),
        "n_students": int(len(df)),
        "class_distribution": {str(k): int(v) for k, v in df[target].value_counts().items()},
        "anova": {},
        "chi_square": {},
    }

    # --- ANOVA + assumption checks for continuous features -------------------
    for col in d["numeric_features"]:
        groups = [df.loc[df[target] == c, col].to_numpy(dtype=float) for c in class_order]
        f_stat, p, df_b, df_w = one_way_anova(groups)
        eta = eta_squared(groups)
        lev_w, lev_p = levene_test(groups)
        h_stat, kw_p = kruskal_wallis(groups)

        results["anova"][col] = {
            "friendly_name": d["friendly_names"].get(col, col),
            "f_statistic": round(f_stat, 4),
            "p_value": p,
            "df_between": df_b,
            "df_within": df_w,
            "eta_squared": round(eta, 4),
            "effect_size_label": _eta_label(eta),
            "group_means": {c: round(float(g.mean()), 2) for c, g in zip(class_order, groups)},
            "group_stds": {c: round(float(g.std(ddof=1)), 2) for c, g in zip(class_order, groups)},
            "group_sizes": {c: int(len(g)) for c, g in zip(class_order, groups)},
            "levene_w": round(lev_w, 4),
            "levene_p": lev_p,
            "equal_variance_assumption_holds": bool(lev_p >= alpha) if not np.isnan(lev_p) else None,
            "kruskal_h": round(h_stat, 4),
            "kruskal_p": kw_p,
            "parametric_and_nonparametric_agree": bool((p < alpha) == (kw_p < alpha)),
        }

    # --- Chi-square for categorical features ---------------------------------
    categorical = list(d["nominal_features"]) + list(d["binary_features"].keys())
    for col in categorical:
        if col not in df.columns:
            continue
        res = chi_square_test(df[col], df[target])
        res["friendly_name"] = d["friendly_names"].get(col, col)
        res["effect_size_label"] = _cramers_label(res["cramers_v"])
        res["chi2"] = round(res["chi2"], 4)
        res["cramers_v"] = round(res["cramers_v"], 4)
        res["min_expected"] = round(res["min_expected"], 2)
        results["chi_square"][col] = res

    # --- Holm correction across the whole family -----------------------------
    keys: List[Tuple[str, str]] = (
        [("anova", k) for k in results["anova"]] + [("chi_square", k) for k in results["chi_square"]]
    )
    raw_p = [results[fam][k]["p_value"] for fam, k in keys]
    adjusted, significant = holm_bonferroni(raw_p, alpha)
    for (fam, k), adj, sig in zip(keys, adjusted, significant):
        results[fam][k]["p_value_adjusted"] = adj
        results[fam][k]["significant"] = bool(sig)
    results["n_tests_in_family"] = len(keys)

    # --- Ranked summary the report can quote directly ------------------------
    ranked: List[Dict[str, Any]] = []
    for col, r in results["anova"].items():
        ranked.append({
            "feature": col, "friendly_name": r["friendly_name"], "test": "ANOVA",
            "statistic": r["f_statistic"], "p_value": r["p_value"],
            "p_value_adjusted": r["p_value_adjusted"], "effect_size": r["eta_squared"],
            "effect_size_metric": "eta_squared", "effect_size_label": r["effect_size_label"],
            "significant": r["significant"],
        })
    for col, r in results["chi_square"].items():
        ranked.append({
            "feature": col, "friendly_name": r["friendly_name"], "test": "Chi-square",
            "statistic": r["chi2"], "p_value": r["p_value"],
            "p_value_adjusted": r["p_value_adjusted"], "effect_size": r["cramers_v"],
            "effect_size_metric": "cramers_v", "effect_size_label": r["effect_size_label"],
            "significant": r["significant"],
        })
    ranked.sort(key=lambda r: (-(r["effect_size"] if not np.isnan(r["effect_size"]) else -1)))
    results["ranked_factors"] = ranked
    results["significant_factors"] = [r["feature"] for r in ranked if r["significant"]]
    results["n_significant"] = len(results["significant_factors"])

    # --- Correlations among the numeric features -----------------------------
    corr = correlation_matrix(df, d["numeric_features"], method="spearman")
    results["spearman_correlation"] = {
        r: {c: round(float(corr.loc[r, c]), 3) for c in corr.columns} for r in corr.index
    }

    if save:
        path = save_json(results, get_path("stats_file", cfg, ensure_parent=True))
        logger.info("Wrote statistical test results -> %s", path)

    logger.info(
        "Statistical testing complete: %d/%d factors significant after %s correction",
        results["n_significant"], len(keys), results["correction"],
    )
    return results


def _eta_label(eta: float) -> str:
    """Cohen's conventional bands for eta-squared."""
    if np.isnan(eta):
        return "unknown"
    if eta < 0.01:
        return "negligible"
    if eta < 0.06:
        return "small"
    if eta < 0.14:
        return "medium"
    return "large"


def _cramers_label(v: float) -> str:
    """Conventional bands for Cramer's V."""
    if np.isnan(v):
        return "unknown"
    if v < 0.10:
        return "negligible"
    if v < 0.20:
        return "small"
    if v < 0.35:
        return "medium"
    return "large"


def summarise_findings(results: Dict[str, Any], top_n: int = 5) -> str:
    """Turn the numbers into the paragraph the Phase 2 checkpoint asks for."""
    lines: List[str] = []
    sig = [r for r in results["ranked_factors"] if r["significant"]][:top_n]
    lines.append(
        f"Across {results['n_tests_in_family']} hypothesis tests on {results['n_students']} students, "
        f"{results['n_significant']} factors are statistically significant at alpha = {results['alpha']} "
        f"after {results['correction'].title()} correction for multiple comparisons."
    )
    lines.append("")
    lines.append(f"The {len(sig)} strongest factors, ranked by effect size:")
    for i, r in enumerate(sig, 1):
        p_txt = "< 0.001" if r["p_value"] < 0.001 else f"= {r['p_value']:.4f}"
        lines.append(
            f"  {i}. {r['friendly_name']} — {r['test']} statistic {r['statistic']:.2f}, "
            f"p {p_txt}, {r['effect_size_metric']} = {r['effect_size']:.3f} ({r['effect_size_label']} effect)."
        )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - manual run
    from src.data.preprocess import load_processed

    out = run_all_tests(load_processed())
    print(summarise_findings(out))
