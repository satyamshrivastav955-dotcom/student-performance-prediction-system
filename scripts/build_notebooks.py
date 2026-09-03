"""
Generate the Jupyter notebooks in ``notebooks/`` from plain Python source.

Why generate them instead of hand-editing .ipynb files?
    A notebook is a large JSON document. Editing it by hand is error-prone, it
    produces unreadable git diffs, and it invites the classic problem of a
    notebook whose stored output no longer matches its code. Writing the cells
    here means the notebooks are reproducible build artifacts: delete them and
    run ``python scripts/build_notebooks.py`` to get them back, always in sync
    with the modules in ``src/``.

The notebooks are a *presentation* layer over ``src/`` — they import the same
functions the pipeline and dashboard use rather than re-implementing anything.
That is deliberate: a notebook that quietly reimplements the preprocessing is
how a project ends up with two different answers to the same question.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

BOOTSTRAP = """\
# Make `src` importable no matter where Jupyter was launched from.
import sys, warnings
from pathlib import Path

ROOT = Path.cwd()
while not (ROOT / "config" / "config.yaml").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

print(f"Project root: {ROOT}")
"""


def md(text: str) -> Dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": text.rstrip().split("\n")}


def code(text: str) -> Dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.rstrip().split("\n"),
    }


def write_notebook(name: str, cells: List[Dict[str, Any]]) -> Path:
    """Serialise cells into a valid nbformat 4 notebook."""
    # nbformat stores each line with its trailing newline except the last.
    for cell in cells:
        src = cell["source"]
        cell["source"] = [line + "\n" for line in src[:-1]] + [src[-1]] if src else []

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    path = NOTEBOOK_DIR / name
    path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    return path


# =============================================================================
# 01 — Exploratory Data Analysis
# =============================================================================

def notebook_eda() -> List[Dict[str, Any]]:
    return [
        md("""\
# 01 — Exploratory Data Analysis

**Student Performance Prediction System**

This notebook covers Module 2 of the brief: understand the dataset before
modelling anything. We look at attendance, participation, resource use and
parental involvement, and check how each relates to the Low / Medium / High
performance band.

Everything here calls into `src/` — the same code the dashboard and the API
use — so nothing in this notebook can drift away from what actually ships."""),

        code(BOOTSTRAP),

        md("## 1. Load and clean\n\nThe raw file goes through schema validation and then cleaning: duplicate removal, whitespace trimming, missing-value imputation and range clipping."),

        code("""\
from src.data.load_data import load_raw_data, validate_schema
from src.data.preprocess import clean_dataframe
from src.utils.config import load_config

cfg = load_config()
raw = load_raw_data(cfg=cfg)
schema_report = validate_schema(raw, cfg, strict=True)

print(f"Raw shape:            {raw.shape}")
print(f"Missing values:       {schema_report['missing_values_total']}")
print(f"Exact duplicate rows: {schema_report['exact_duplicate_rows']}")
raw.head()"""),

        code("""\
df, cleaning_report = clean_dataframe(raw, cfg)

print(f"Rows in:  {cleaning_report['rows_in']}")
print(f"Rows out: {cleaning_report['rows_out']}")
print(f"Duplicates removed: {cleaning_report['exact_duplicates_removed']}")
print(f"Class distribution: {cleaning_report['class_distribution']}")
df.head()"""),

        md("""\
## 2. What is in the dataset?

16 features and one target. The features split into three kinds:

- **Behavioural counters** (0-100): hands raised, resources opened, announcements read, discussion posts. These are the dataset's proxies for participation and study effort.
- **Attendance**: `StudentAbsenceDays`, a two-level flag for under vs. 7-or-more days absent.
- **Context and demographics**: nationality, subject, grade, section, and which parent is responsible — plus two parental-engagement survey fields."""),

        code("""\
overview = df.describe(include="all").T
overview["dtype"] = df.dtypes.astype(str)
overview[["dtype", "count", "unique", "top", "freq", "mean", "std", "min", "max"]]"""),

        md("## 3. Class balance\n\nThe target is already L/M/H in the source data — no post-hoc bucketing of a continuous grade required. This is the main reason we chose this dataset over the UCI alternative."),

        code("""\
from src.analysis.eda import apply_house_style, plot_class_distribution
apply_house_style()

path, caption = plot_class_distribution(df, cfg)
print(caption)
from IPython.display import Image, display
display(Image(str(path)))"""),

        md("""\
## 4. Engagement behaviour across the three bands

The question: do students in different performance bands actually *behave*
differently, or does it just feel that way?"""),

        code("""\
from src.analysis.eda import plot_numeric_distributions, plot_boxplots_by_class

for fn in (plot_numeric_distributions, plot_boxplots_by_class):
    p, cap = fn(df, cfg)
    display(Image(str(p)))
    print(cap, "\\n")"""),

        code("""\
# The same comparison as a table — group means for every engagement counter.
numeric = cfg["data"]["numeric_features"]
df.groupby("Class")[numeric].agg(["mean", "median", "std"]).round(1).reindex(["L", "M", "H"])"""),

        md("## 5. Attendance — the headline factor\n\nThis single two-level column turns out to carry more signal than any other feature in the dataset."),

        code("""\
from src.analysis.eda import plot_absence_vs_class

p, cap = plot_absence_vs_class(df, cfg)
display(Image(str(p)))
print(cap)"""),

        code("""\
import pandas as pd
pd.crosstab(df["StudentAbsenceDays"], df["Class"], normalize="index").round(3)[["L", "M", "H"]]"""),

        md("## 6. Parental involvement and demographics\n\nNote the gender panel below. It differs noticeably between bands — which is exactly why this project runs a formal fairness audit later rather than assuming the model is even-handed."),

        code("""\
from src.analysis.eda import plot_categorical_panel

p, cap = plot_categorical_panel(df, cfg)
display(Image(str(p)))
print(cap)"""),

        md("## 7. Do the engagement measures overlap?\n\nIf two features carried identical information we would want to drop one. Spearman correlation (rank-based, so it is not distorted by skew) says they are related but distinct."),

        code("""\
from src.analysis.eda import plot_correlation_heatmap, plot_engagement_scatter

for fn in (plot_correlation_heatmap, plot_engagement_scatter):
    p, cap = fn(df, cfg)
    display(Image(str(p)))
    print(cap, "\\n")"""),

        md("## 8. Subject-wise view\n\nRequired by Module 4 (subject-wise analysis) and surfaced on the dashboard's Overview page."),

        code("""\
from src.analysis.eda import plot_topic_breakdown

p, cap = plot_topic_breakdown(df, cfg)
display(Image(str(p)))
print(cap)"""),

        md("""\
## 9. What we take into modelling

1. **Attendance** is the strongest single discriminator by a wide margin.
2. **Resource use and hands raised** separate the bands almost as cleanly.
3. **Discussion posts** are far weaker than the other three counters — worth keeping, but not worth building an intervention around.
4. **Parental engagement** tracks strongly with outcomes.
5. **Gender differs across bands**, so fairness needs formal testing rather than assumption.

All five of these are eyeball impressions at this point. Notebook `02`
tests them properly."""),

        code("""\
from src.analysis.eda import dataset_overview
import json
print(json.dumps(dataset_overview(df, cfg), indent=2))"""),
    ]


# =============================================================================
# 02 — Statistical testing
# =============================================================================

def notebook_stats() -> List[Dict[str, Any]]:
    return [
        md("""\
# 02 — Statistical Testing

**Turning "the chart looks different" into evidence.**

Notebook 01 produced visual impressions. This one tests them. For each factor
we ask a precise question with a precise answer:

| Test | Question it answers |
|---|---|
| One-way ANOVA | Do the Low/Medium/High groups have genuinely different average engagement? |
| Levene's test | Is the ANOVA's equal-variance assumption actually satisfied? |
| Kruskal-Wallis | Does the finding survive without any distribution assumptions? |
| Chi-square | Is this categorical factor independent of performance, or not? |
| Eta² / Cramer's V | The effect is real — but is it *big enough to act on*? |
| Holm-Bonferroni | Having run ~16 tests, which results survive correction for multiple comparisons? |

The last two rows are what separate this from a typical submission. A p-value
alone tells you an effect exists; it says nothing about whether the effect is
large enough to justify spending a school's intervention budget."""),

        code(BOOTSTRAP),

        code("""\
from src.data.preprocess import load_processed
from src.analysis.statistical_tests import run_all_tests, summarise_findings, SCIPY_AVAILABLE
from src.utils.config import load_config

cfg = load_config()
df = load_processed(cfg)
print(f"Students: {len(df)}   |   SciPy backend available: {SCIPY_AVAILABLE}")"""),

        md("""\
## 1. Run the full test battery

One call runs every ANOVA, every chi-square, both assumption checks, and the
multiple-comparison correction across the whole family at once."""),

        code("""\
results = run_all_tests(df, cfg)
print(summarise_findings(results, top_n=8))"""),

        md("""\
## 2. ANOVA results in detail

`F` is the ratio of between-group variance to within-group variance —
"how far apart are the group averages, relative to how noisy each group is
internally?"

`eta²` is the share of the feature's total variance explained by performance
band. Conventional bands: 0.01 small, 0.06 medium, 0.14 large."""),

        code("""\
import pandas as pd

anova_rows = []
for feature, r in results["anova"].items():
    anova_rows.append({
        "Factor": r["friendly_name"],
        "F": r["f_statistic"],
        "p (raw)": r["p_value"],
        "p (Holm)": r["p_value_adjusted"],
        "eta²": r["eta_squared"],
        "Effect": r["effect_size_label"],
        "Mean L": r["group_means"]["L"],
        "Mean M": r["group_means"]["M"],
        "Mean H": r["group_means"]["H"],
        "Significant": r["significant"],
    })

pd.DataFrame(anova_rows).sort_values("eta²", ascending=False).reset_index(drop=True)"""),

        md("""\
### Assumption checks — being honest about ANOVA

ANOVA assumes the three groups have roughly equal variance. Levene's test
checks that. Where the assumption fails, the ANOVA p-value on its own is not
fully trustworthy — so we report Kruskal-Wallis, which makes no such
assumption, right next to it.

**When both agree, the conclusion is safe no matter which assumptions you are
willing to make.** That agreement column is the one that matters."""),

        code("""\
assumption_rows = []
for feature, r in results["anova"].items():
    assumption_rows.append({
        "Factor": r["friendly_name"],
        "Levene W": r["levene_w"],
        "Levene p": round(r["levene_p"], 4),
        "Equal variance OK?": r["equal_variance_assumption_holds"],
        "Kruskal H": r["kruskal_h"],
        "Kruskal p": r["kruskal_p"],
        "Both tests agree?": r["parametric_and_nonparametric_agree"],
    })

pd.DataFrame(assumption_rows)"""),

        md("""\
## 3. Chi-square results

For categorical factors the null hypothesis is independence: "knowing this
feature tells you nothing about the performance band."

`min_expected` is the assumption check. The standard rule is that no expected
cell count should drop below 5 — where it does, the chi-square approximation
becomes unreliable and we flag it rather than quietly reporting the number."""),

        code("""\
chi_rows = []
for feature, r in results["chi_square"].items():
    chi_rows.append({
        "Factor": r["friendly_name"],
        "chi²": r["chi2"],
        "dof": r["dof"],
        "p (raw)": r["p_value"],
        "p (Holm)": r["p_value_adjusted"],
        "Cramer's V": r["cramers_v"],
        "Effect": r["effect_size_label"],
        "Min expected": r["min_expected"],
        "Assumption OK?": r["assumption_ok"],
        "Significant": r["significant"],
    })

pd.DataFrame(chi_rows).sort_values("Cramer's V", ascending=False).reset_index(drop=True)"""),

        md("""\
## 4. Why we corrected for multiple comparisons

We ran 16 hypothesis tests. If every null hypothesis were true, the chance of
at least one "significant" result purely by luck is:

$$1 - (1 - 0.05)^{16} \\approx 56\\%$$

More likely than a coin flip. Holm-Bonferroni controls that family-wise error
rate while rejecting more nulls than plain Bonferroni would, so it costs less
real signal. The cell below shows what the correction actually changed."""),

        code("""\
n = results["n_tests_in_family"]
print(f"Tests run: {n}")
print(f"P(at least one false positive without correction): {1 - 0.95 ** n:.1%}\\n")

changed = [
    r for r in results["ranked_factors"]
    if (r["p_value"] < 0.05) != (r["p_value_adjusted"] < 0.05)
]
if changed:
    print("Results that changed verdict after correction:")
    for r in changed:
        print(f"  {r['friendly_name']}: raw p={r['p_value']:.4f} -> Holm p={r['p_value_adjusted']:.4f}")
else:
    print("No result changed verdict — every finding survives correction.")"""),

        md("## 5. The ranking that drives the whole project\n\nEverything downstream — which features the recommendation engine talks about, which levers the cohort simulator exposes — traces back to this ordering."),

        code("""\
from src.analysis.eda import apply_house_style, plot_effect_sizes
from IPython.display import Image, display

apply_house_style()
p, cap = plot_effect_sizes(results, cfg)
display(Image(str(p)))
print(cap)"""),

        md("""\
## 6. Checkpoint summary

Write-up for the report, generated from the numbers above rather than typed
by hand."""),

        code("""\
print(summarise_findings(results, top_n=6))
print()
print("Factors with NO significant relationship to performance:")
for r in results["ranked_factors"]:
    if not r["significant"]:
        print(f"  - {r['friendly_name']}: p={r['p_value']:.3f} (Holm-adjusted {r['p_value_adjusted']:.3f})")"""),

        md("""\
### What this means in practice

The significant, actionable factors are attendance, resource use, hands raised
and announcements read. Those four are what a school can realistically move.

Nationality, place of birth and gender are also statistically significant —
but they are **not levers**. They are demographic attributes, and a system that
"recommended" changing them would be both useless and offensive. Their
significance here is precisely the reason Phase 6 runs a fairness audit: if
these attributes correlate with the outcome, we have to check whether the model
is quietly using them to make decisions."""),
    ]


def notebook_models() -> List[Dict[str, Any]]:
    return [
        md("""\
# 03 — Model Development, Evaluation & Explainability

**Student Performance Prediction System**

This notebook covers Module 3:
1. Classical ML model comparisons (Logistic Regression, Decision Tree, Random Forest, HistGradientBoosting)
2. Stratified 5-fold cross-validation & hyperparameter tuning
3. Bootstrapped 95% confidence intervals on Macro-F1 & Accuracy
4. McNemar's statistical test comparing top 2 models
5. SHAP explainability (Global importance + local waterflow explanations)
"""),
        code(BOOTSTRAP),
        md("## 1. Load Preprocessed Data & Inspect Targets"),
        code("""\
from src.data.preprocess import load_processed, split_features_target, encode_target
from src.utils.config import load_config

cfg = load_config()
df = load_processed(cfg)
X, y = split_features_target(df, cfg)
y_encoded, class_order = encode_target(y, cfg)

print(f"Features: {X.shape[1]} | Samples: {len(X)}")
print(f"Class order: {class_order}")
"""),
        md("## 2. Load Evaluation Metrics from Training Run\n\nAll metrics are stored in `reports/artifacts/metrics.json` for full reproducibility."),
        code("""\
from src.utils.config import get_path, load_json
import pandas as pd

metrics = load_json(get_path("metrics_file", cfg))
print("Best selected model:", metrics.get("best_model"))
print("Runner-up model:   ", metrics.get("runner_up_model"))

test_results = metrics.get("test_metrics", {})
summary_rows = []
for name, m in test_results.items():
    summary_rows.append({
        "Model": name,
        "Accuracy": m["accuracy"],
        "Macro-F1": m["f1_macro"],
    })
pd.DataFrame(summary_rows).sort_values(by="Macro-F1", ascending=False)
"""),
        md("## 3. Bootstrapped Confidence Intervals (95%)"),
        code("""\
bootstrap = metrics.get("bootstrap", {})
for model_name, b in bootstrap.items():
    f1_ci = b["f1_macro"]
    print(f"{model_name:20s}: Macro-F1 = {f1_ci['point_estimate']:.4f} [95% CI: {f1_ci['ci_lower']:.4f} - {f1_ci['ci_upper']:.4f}]")
"""),
        md("## 4. McNemar's Test: Statistical Significance of Winner vs Runner-up"),
        code("""\
mc = metrics.get("mcnemar", {})
print("McNemar's Test:", mc.get("model_a"), "vs", mc.get("model_b"))
print(f"p-value: {mc.get('p_value'):.4e} (Significant: {mc.get('significant')})")
print("Interpretation:", mc.get("interpretation"))
"""),
        md("## 5. SHAP Global Feature Importance"),
        code("""\
from IPython.display import Image, display
from src.utils.config import get_path

shap_plot = get_path("figures_dir", cfg) / "12_shap_global_importance.png"
if shap_plot.exists():
    display(Image(str(shap_plot)))
"""),
    ]


def main() -> None:
    written = [
        write_notebook("01_eda.ipynb", notebook_eda()),
        write_notebook("02_statistical_tests.ipynb", notebook_stats()),
        write_notebook("03_model_experiments.ipynb", notebook_models()),
    ]

    for p in written:
        print(f"wrote {p.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
