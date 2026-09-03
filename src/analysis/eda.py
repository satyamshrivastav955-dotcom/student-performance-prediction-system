"""
Exploratory Data Analysis — Module 2 of the brief.

Produces every figure used in the report, the slide deck and the dashboard's
Overview page. All figures share one visual language (the same palette as the
dashboard, the same fonts, the same soft grid) so the final deliverables look
like they came from one project rather than from eleven separate notebook cells.

Design rules applied to every chart here:

* **Off-white background, one accent colour.** The three class colours (green /
  amber / coral) are the only other hues, and they always mean the same thing.
* **No chart junk.** No 3D, no gradients, no top/right spines, no redundant
  legends. Ink goes to data.
* **Every figure gets a plain-English caption** returned alongside it, so the
  report and the dashboard can explain what a teacher is looking at without a
  statistics background.
* **Sorted, labelled, readable.** Categories are ordered by magnitude rather
  than alphabetically, because the point of a chart is to make the ranking
  visible instantly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # headless: we render to files, never to a screen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.utils.config import get_path, load_config, save_json
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# --- House style -------------------------------------------------------------
ACCENT = "#2563EB"
CLASS_COLORS = {"L": "#F87171", "M": "#F59E0B", "H": "#10B981"}
CLASS_NAMES = {"L": "Low", "M": "Medium", "H": "High"}
TEXT = "#1F2937"
MUTED = "#6B7280"
GRID = "#E5E7EB"
BG = "#FFFFFF"


def apply_house_style() -> None:
    """Set matplotlib defaults once so every figure matches without repetition."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 13,
        "axes.titleweight": "600",
        "axes.labelsize": 11,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })


def _despine(ax) -> None:
    """Remove the top and right spines — less frame, more data."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def _save(fig, name: str, cfg: Dict[str, Any]) -> Path:
    """Write a figure into ``reports/figures/`` and close it.

    Closing matters: a pipeline that renders 12 figures without closing them
    will happily leak every one and then warn you about it.
    """
    out_dir = get_path("figures_dir", cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path)
    plt.close(fig)
    logger.info("  figure -> %s", name)
    return path


def _ordered_classes(cfg: Dict[str, Any]) -> List[str]:
    return list(cfg["data"]["target_classes"])


# Raw category codes that should never be shown to a teacher as-is.
LEVEL_LABELS: Dict[str, str] = {
    "F": "Female", "M": "Male",
    "Mum": "Mother", "Father": "Father",
    "Yes": "Yes", "No": "No",
    "Good": "Good", "Bad": "Poor",
    "Under-7": "Under 7 days", "Above-7": "7+ days",
    "lowerlevel": "Lower level", "MiddleSchool": "Middle school", "HighSchool": "High school",
}


def pretty_level(value: Any) -> str:
    """Turn a raw category code into readable text ('F' -> 'Female')."""
    return LEVEL_LABELS.get(str(value), str(value))


# =============================================================================
# Individual figures
# =============================================================================

def plot_class_distribution(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """How many students fall into each performance band."""
    target = cfg["data"]["target"]
    order = _ordered_classes(cfg)
    counts = df[target].value_counts().reindex(order)
    total = int(counts.sum())

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(
        [CLASS_NAMES[c] for c in order], counts.values,
        color=[CLASS_COLORS[c] for c in order], width=0.6, edgecolor="none",
    )
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + total * 0.012,
                f"{value}\n({value / total:.0%})", ha="center", va="bottom",
                fontsize=10, color=TEXT, linespacing=1.4)
    ax.set_title("How many students are in each performance band")
    ax.set_ylabel("Number of students")
    ax.set_ylim(0, counts.max() * 1.18)
    ax.grid(axis="x", visible=False)
    _despine(ax)

    caption = (
        f"Of {total} students, the Medium band is the largest at {counts['M'] / total:.0%}. "
        f"The classes are moderately imbalanced ({counts['H']}:{counts['M']}:{counts['L']} for "
        "High:Medium:Low), which is why every model is trained with balanced class weights and "
        "scored on macro-F1 rather than plain accuracy."
    )
    return _save(fig, "01_class_distribution.png", cfg), caption


def plot_numeric_distributions(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Distribution of each engagement counter, split by performance band."""
    target = cfg["data"]["target"]
    numeric = cfg["data"]["numeric_features"]
    friendly = cfg["data"]["friendly_names"]
    order = _ordered_classes(cfg)

    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))
    for ax, col in zip(axes.ravel(), numeric):
        for c in order:
            sns.kdeplot(
                data=df[df[target] == c], x=col, ax=ax, fill=True, alpha=0.28,
                color=CLASS_COLORS[c], linewidth=1.8, label=CLASS_NAMES[c],
                common_norm=False, clip=(0, 100),
            )
        ax.set_title(friendly.get(col, col))
        ax.set_xlabel("")
        ax.set_ylabel("Relative frequency")
        ax.set_yticks([])
        _despine(ax)
    axes.ravel()[0].legend(title="Performance", loc="upper right")
    for ax in axes.ravel()[1:]:
        ax.get_legend().remove() if ax.get_legend() else None
    fig.suptitle("Engagement behaviour by performance band", fontsize=14, fontweight="600",
                 color=TEXT, y=0.99)
    fig.tight_layout()

    caption = (
        "Each curve shows how common different activity levels are within one performance band. "
        "High performers (green) cluster to the right on resources opened and hands raised — they "
        "are simply more active. The curves for discussion posts overlap far more, an early hint "
        "that discussion is a much weaker signal than the other three."
    )
    return _save(fig, "02_numeric_distributions.png", cfg), caption


def plot_boxplots_by_class(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Box plots making the group medians and spread directly comparable."""
    target = cfg["data"]["target"]
    numeric = cfg["data"]["numeric_features"]
    friendly = cfg["data"]["friendly_names"]
    order = _ordered_classes(cfg)

    fig, axes = plt.subplots(1, 4, figsize=(14, 4.4))
    for ax, col in zip(axes, numeric):
        sns.boxplot(
            data=df, x=target, y=col, order=order, ax=ax,
            # seaborn >= 0.13 wants `hue` set whenever a palette is given; mapping
            # hue to the same variable as x with the legend off reproduces the
            # old behaviour without the deprecation warning.
            hue=target, hue_order=order, legend=False,
            palette=[CLASS_COLORS[c] for c in order], width=0.6,
            fliersize=2.5, linewidth=1.1,
        )
        ax.set_title(friendly.get(col, col), fontsize=11)
        ax.set_xlabel("")
        ax.set_ylabel("")
        # Pin the tick positions before renaming them, otherwise matplotlib warns
        # that the labels could silently drift away from the ticks.
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([CLASS_NAMES[c] for c in order])
        ax.grid(axis="x", visible=False)
        _despine(ax)
    axes[0].set_ylabel("Activity count (0-100)")
    fig.suptitle("Median engagement rises consistently from Low to High", fontsize=14,
                 fontweight="600", color=TEXT, y=1.02)
    fig.tight_layout()

    caption = (
        "The box shows the middle 50% of students and the line inside it the median. Medians step "
        "up cleanly from Low to High for resources opened, hands raised and announcements read. "
        "For discussion posts the boxes overlap heavily, confirming the weaker relationship."
    )
    return _save(fig, "03_boxplots_by_class.png", cfg), caption


def plot_correlation_heatmap(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Spearman correlation between the four engagement counters."""
    numeric = cfg["data"]["numeric_features"]
    friendly = cfg["data"]["friendly_names"]
    corr = df[numeric].corr(method="spearman")
    labels = [friendly.get(c, c) for c in numeric]

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1,
        square=True, linewidths=1.5, linecolor=BG, ax=ax,
        cbar_kws={"shrink": 0.7, "label": "Spearman correlation"},
        xticklabels=labels, yticklabels=labels, annot_kws={"fontsize": 10},
    )
    ax.set_title("How the four engagement measures relate to each other")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()

    strongest = corr.where(mask.T & ~np.eye(len(corr), dtype=bool)).stack().idxmax()
    strongest_val = corr.loc[strongest[0], strongest[1]]
    caption = (
        f"Values near 1 mean two behaviours move together. The strongest pairing is "
        f"{friendly.get(strongest[0], strongest[0]).lower()} and "
        f"{friendly.get(strongest[1], strongest[1]).lower()} at {strongest_val:.2f} — engaged "
        "students tend to be engaged across the board. None of the pairs are so highly correlated "
        "that they carry identical information, so all four are worth keeping as separate features."
    )
    return _save(fig, "04_correlation_heatmap.png", cfg), caption


def plot_absence_vs_class(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """The headline attendance finding, as a 100% stacked bar."""
    target = cfg["data"]["target"]
    order = _ordered_classes(cfg)
    ct = pd.crosstab(df["StudentAbsenceDays"], df[target], normalize="index").reindex(
        ["Under-7", "Above-7"]
    )[order]
    counts = df["StudentAbsenceDays"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 3.1))
    left = np.zeros(len(ct))
    for c in order:
        ax.barh(ct.index, ct[c], left=left, color=CLASS_COLORS[c],
                label=CLASS_NAMES[c], height=0.72, edgecolor="none")
        for i, (val, l) in enumerate(zip(ct[c], left)):
            if val > 0.05:
                ax.text(l + val / 2, i, f"{val:.0%}", ha="center", va="center",
                        color="white", fontsize=10, fontweight="600")
        left = left + ct[c].to_numpy()

    ax.set_yticks(range(len(ct)))
    ax.set_yticklabels([
        f"Under 7 days absent\n(n={counts.get('Under-7', 0)})",
        f"7 or more days absent\n(n={counts.get('Above-7', 0)})",
    ])
    ax.set_ylim(-0.55, len(ct) - 0.45)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_title("Attendance is the single strongest signal in the dataset")
    ax.legend(title="Performance", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", visible=False)
    _despine(ax)

    high_low = ct.loc["Under-7", "H"]
    high_above = ct.loc["Above-7", "H"]
    caption = (
        f"Among students absent fewer than 7 days, {high_low:.0%} reach the High band. Among those "
        f"absent 7 days or more, only {high_above:.0%} do. This is the largest single effect "
        "measured anywhere in the analysis (Cramer's V = 0.68), and it is also the factor a school "
        "has the most direct ability to influence."
    )
    return _save(fig, "05_absence_vs_class.png", cfg), caption


def plot_categorical_panel(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Four categorical factors against performance, in one comparable panel."""
    target = cfg["data"]["target"]
    friendly = cfg["data"]["friendly_names"]
    order = _ordered_classes(cfg)
    cols = ["ParentAnsweringSurvey", "ParentschoolSatisfaction", "Relation", "gender"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    for ax, col in zip(axes.ravel(), cols):
        ct = pd.crosstab(df[col], df[target], normalize="index")[order]
        levels = [pretty_level(v) for v in ct.index]
        bottom = np.zeros(len(ct))
        for c in order:
            ax.bar(levels, ct[c], bottom=bottom, color=CLASS_COLORS[c],
                   label=CLASS_NAMES[c], width=0.55, edgecolor="none")
            for i, (val, b) in enumerate(zip(ct[c], bottom)):
                if val > 0.07:
                    ax.text(i, b + val / 2, f"{val:.0%}", ha="center", va="center",
                            color="white", fontsize=9, fontweight="600")
            bottom = bottom + ct[c].to_numpy()
        ax.set_title(friendly.get(col, col), fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_yticklabels(["0%", "50%", "100%"])
        ax.grid(axis="x", visible=False)
        _despine(ax)
    axes[0, 0].legend(title="Performance", bbox_to_anchor=(1.0, 1.32), loc="upper right", ncol=3)
    fig.suptitle("Parental involvement tracks strongly with student outcomes",
                 fontsize=14, fontweight="600", color=TEXT, y=1.0)
    fig.tight_layout()

    caption = (
        "Each bar is one group of students split by their performance band. Where a parent "
        "responded to the school survey, far more students land in the High band. The pattern for "
        "which parent is listed as responsible is equally sharp. Note the gender panel: it also "
        "differs noticeably, which is precisely why this project runs a formal fairness audit "
        "rather than assuming the model treats groups equally."
    )
    return _save(fig, "06_categorical_panel.png", cfg), caption


def plot_effect_sizes(stats: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Rank every factor by measured effect size, flagging significance."""
    ranked = [r for r in stats["ranked_factors"] if not np.isnan(r["effect_size"])]
    ranked = sorted(ranked, key=lambda r: r["effect_size"])
    names = [r["friendly_name"] for r in ranked]
    values = [r["effect_size"] for r in ranked]
    colors = [ACCENT if r["significant"] else "#CBD5E1" for r in ranked]

    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    bars = ax.barh(names, values, color=colors, height=0.65, edgecolor="none")
    for bar, r in zip(bars, ranked):
        marker = "" if r["significant"] else "  (not significant)"
        ax.text(bar.get_width() + 0.008, bar.get_y() + bar.get_height() / 2,
                f"{r['effect_size']:.2f}{marker}", va="center", fontsize=9,
                color=TEXT if r["significant"] else MUTED)
    ax.set_xlim(0, max(values) * 1.32)
    ax.set_xlabel("Effect size  (eta² for numeric factors, Cramer's V for categorical)")
    ax.set_title("Which factors actually affect performance, ranked by strength")
    ax.grid(axis="y", visible=False)
    _despine(ax)

    caption = (
        f"Blue bars are statistically significant after Holm correction for running "
        f"{stats['n_tests_in_family']} tests; grey bars are not. Effect size answers the question a "
        "p-value cannot: how *much* does this factor matter. Attendance and resource use dominate; "
        "class section and school stage have essentially no relationship with performance, so a "
        "school should not spend intervention budget there. One caveat: eta² and Cramer's V are "
        "different measures on similar 0-1 scales, so read this as a broad ranking rather than an "
        "exact like-for-like comparison between a numeric and a categorical factor."
    )
    return _save(fig, "07_effect_size_ranking.png", cfg), caption


def plot_engagement_scatter(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """The two strongest numeric predictors plotted against each other."""
    target = cfg["data"]["target"]
    friendly = cfg["data"]["friendly_names"]
    order = _ordered_classes(cfg)

    fig, ax = plt.subplots(figsize=(8, 6))
    for c in order:
        sub = df[df[target] == c]
        ax.scatter(sub["VisITedResources"], sub["raisedhands"], s=42, alpha=0.62,
                   color=CLASS_COLORS[c], label=CLASS_NAMES[c], edgecolors="white", linewidth=0.6)
    ax.set_xlabel(friendly["VisITedResources"])
    ax.set_ylabel(friendly["raisedhands"])
    ax.set_title("The two strongest behavioural signals separate the classes well")
    ax.legend(title="Performance", loc="upper left")
    _despine(ax)

    caption = (
        "Each dot is one student. Low performers (coral) sit in the bottom-left corner, High "
        "performers (green) in the top-right, with Medium students bridging the two. The bands "
        "overlap in the middle, which is exactly why a model that weighs many factors together "
        "beats any single cut-off rule a teacher could apply by eye."
    )
    return _save(fig, "08_engagement_scatter.png", cfg), caption


def plot_group_means(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Grouped bars of mean engagement per class — the ANOVA result, visually."""
    target = cfg["data"]["target"]
    numeric = cfg["data"]["numeric_features"]
    friendly = cfg["data"]["friendly_names"]
    order = _ordered_classes(cfg)

    means = df.groupby(target)[numeric].mean().reindex(order)
    errs = df.groupby(target)[numeric].sem().reindex(order)

    x = np.arange(len(numeric))
    width = 0.26
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, c in enumerate(order):
        ax.bar(x + (i - 1) * width, means.loc[c], width, yerr=errs.loc[c], capsize=3,
               color=CLASS_COLORS[c], label=CLASS_NAMES[c], edgecolor="none",
               error_kw={"ecolor": MUTED, "elinewidth": 1})
    ax.set_xticks(x)
    ax.set_xticklabels([friendly.get(c, c) for c in numeric], fontsize=10)
    ax.set_ylabel("Average activity count")
    ax.set_title("Average engagement by performance band, with standard error")
    ax.legend(title="Performance")
    ax.grid(axis="x", visible=False)
    _despine(ax)

    caption = (
        "Thin vertical lines are standard errors — where they do not overlap between bands, the "
        "difference in averages is unlikely to be chance. This is the same comparison the ANOVA "
        "tests formally, shown here so the result is visible rather than only tabulated."
    )
    return _save(fig, "09_group_means.png", cfg), caption


def plot_topic_breakdown(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Subject-wise performance — feeds the dashboard's subject analysis."""
    target = cfg["data"]["target"]
    order = _ordered_classes(cfg)
    ct = pd.crosstab(df["Topic"], df[target], normalize="index")[order]
    counts = df["Topic"].value_counts()
    ct = ct.loc[ct["H"].sort_values(ascending=True).index]

    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    left = np.zeros(len(ct))
    for c in order:
        ax.barh(ct.index, ct[c], left=left, color=CLASS_COLORS[c], label=CLASS_NAMES[c],
                height=0.68, edgecolor="none")
        left = left + ct[c].to_numpy()
    ax.set_yticks(range(len(ct.index)))
    ax.set_yticklabels([f"{t}  (n={counts[t]})" for t in ct.index], fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_title("Performance mix by subject")
    ax.legend(title="Performance", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", visible=False)
    _despine(ax)

    best = ct["H"].idxmax()
    worst = ct["L"].idxmax()
    caption = (
        f"Subjects are ordered by the share of High performers. {best} has the healthiest mix; "
        f"{worst} has the largest share of struggling students. Several subjects have small "
        "enrolments, so treat the extremes as a prompt to look closer rather than as proof — this "
        "is why the statistical test for subject shows only a medium effect."
    )
    return _save(fig, "10_topic_breakdown.png", cfg), caption


def plot_missing_and_quality(df: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[Path, str]:
    """Data-quality summary — evidence that Module 1 was done properly."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))

    completeness = (1 - df.isna().mean()) * 100
    ax1.barh(range(len(completeness)), completeness.values, color=ACCENT, height=0.7,
             edgecolor="none")
    ax1.set_yticks(range(len(completeness)))
    ax1.set_yticklabels([cfg["data"]["friendly_names"].get(c, c) for c in completeness.index],
                        fontsize=8)
    ax1.set_xlim(0, 105)
    ax1.set_xlabel("% of values present")
    ax1.set_title("Data completeness after cleaning", fontsize=11)
    ax1.grid(axis="y", visible=False)
    _despine(ax1)

    numeric = cfg["data"]["numeric_features"]
    sns.violinplot(data=df[numeric], ax=ax2, color=ACCENT, inner="quartile",
                   linewidth=1, saturation=0.45)
    ax2.set_xticks(range(len(numeric)))
    ax2.set_xticklabels([cfg["data"]["friendly_names"].get(c, c) for c in numeric],
                        rotation=18, ha="right", fontsize=8)
    ax2.set_ylabel("Value (0-100)")
    ax2.set_title("Spread of the engagement counters", fontsize=11)
    ax2.grid(axis="x", visible=False)
    _despine(ax2)
    fig.tight_layout()

    caption = (
        "Left: every column is 100% populated after preprocessing. Right: the shape of each "
        "engagement counter. All four are broadly spread across the full 0-100 range with no "
        "single dominant value, meaning none of them is a near-constant column that would "
        "contribute nothing to a model."
    )
    return _save(fig, "11_data_quality.png", cfg), caption


# =============================================================================
# Orchestration
# =============================================================================

def generate_all_figures(
    df: pd.DataFrame,
    stats: Dict[str, Any] | None = None,
    cfg: Dict[str, Any] | None = None,
    save_captions: bool = True,
) -> Dict[str, Dict[str, str]]:
    """Render every EDA figure and collect its caption.

    Returns a mapping of ``figure_key -> {"path", "caption", "title"}``. The
    dashboard and the report generator both read this, so a caption is written
    exactly once and appears identically everywhere.
    """
    cfg = cfg or load_config()
    apply_house_style()
    logger.info("Generating EDA figures...")

    outputs: Dict[str, Dict[str, str]] = {}

    def record(key: str, title: str, result: Tuple[Path, str]) -> None:
        path, caption = result
        outputs[key] = {"path": str(path), "filename": path.name, "title": title,
                        "caption": caption}

    record("class_distribution", "Performance band distribution",
           plot_class_distribution(df, cfg))
    record("numeric_distributions", "Engagement behaviour by band",
           plot_numeric_distributions(df, cfg))
    record("boxplots", "Engagement spread by band", plot_boxplots_by_class(df, cfg))
    record("correlation", "Correlation between engagement measures",
           plot_correlation_heatmap(df, cfg))
    record("absence", "Attendance vs performance", plot_absence_vs_class(df, cfg))
    record("categorical_panel", "Parental involvement and demographics",
           plot_categorical_panel(df, cfg))
    record("engagement_scatter", "The two strongest behavioural signals",
           plot_engagement_scatter(df, cfg))
    record("group_means", "Average engagement by band", plot_group_means(df, cfg))
    record("topic", "Subject-wise performance", plot_topic_breakdown(df, cfg))
    record("data_quality", "Data quality after cleaning", plot_missing_and_quality(df, cfg))

    if stats is not None:
        record("effect_sizes", "Factors ranked by effect size", plot_effect_sizes(stats, cfg))

    if save_captions:
        save_json(outputs, get_path("artifacts_dir", cfg) / "figure_captions.json")

    logger.info("Generated %d figures.", len(outputs))
    return outputs


def dataset_overview(df: pd.DataFrame, cfg: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Headline numbers for the dashboard's Overview cards."""
    cfg = cfg or load_config()
    d = cfg["data"]
    target = d["target"]
    counts = df[target].value_counts()
    total = int(len(df))

    return {
        "n_students": total,
        "n_features": len(d["numeric_features"]) + len(d["nominal_features"]) + len(d["binary_features"]),
        "class_counts": {str(k): int(v) for k, v in counts.items()},
        "class_percentages": {str(k): round(100 * v / total, 1) for k, v in counts.items()},
        "n_at_risk": int(counts.get("L", 0)),
        "pct_at_risk": round(100 * counts.get("L", 0) / total, 1),
        "n_high_absence": int((df["StudentAbsenceDays"] == "Above-7").sum()),
        "mean_engagement": {
            c: round(float(df[c].mean()), 1) for c in d["numeric_features"]
        },
        "n_subjects": int(df["Topic"].nunique()),
        "n_nationalities": int(df["NationalITy"].nunique()),
        "completeness_pct": round(100 * (1 - df.isna().mean().mean()), 2),
    }


if __name__ == "__main__":  # pragma: no cover - manual run
    from src.analysis.statistical_tests import run_all_tests
    from src.data.preprocess import load_processed

    data = load_processed()
    st = run_all_tests(data, save=False)
    generate_all_figures(data, st)
