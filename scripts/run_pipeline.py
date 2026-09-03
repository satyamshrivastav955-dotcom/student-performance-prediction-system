"""
One command to run the whole project end to end.

    python scripts/run_pipeline.py                  # everything
    python scripts/run_pipeline.py --only train     # just one stage
    python scripts/run_pipeline.py --from train     # this stage onwards
    python scripts/run_pipeline.py --skip simulation reports
    python scripts/run_pipeline.py --list           # what stages exist

Why a single entry point?
    An evaluator (or a future you) should be able to clone the repo, install the
    requirements and get every artifact — figures, statistics, trained model,
    SHAP values, fairness audit, report, deck — from one command. If reproducing
    the results requires running seven scripts in the right order from memory,
    the project is not really reproducible.

Stages run in dependency order and each one writes its output to disk, so a
later stage can always pick up where an earlier one left off. Stages that fail
are reported clearly and, unless they are required by what follows, the run
continues — a broken slide-deck generator should not cost you a trained model.
"""

from __future__ import annotations

import argparse
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import load_config  # noqa: E402
from src.utils.logging_utils import get_logger, section  # noqa: E402

logger = get_logger("pipeline")


# =============================================================================
# Stage definitions
# =============================================================================

@dataclass
class Stage:
    """One step of the pipeline.

    ``run`` is stored as a zero-argument callable that does its own importing.
    Importing lazily matters: it means ``--only data`` works even if SHAP is not
    installed, instead of dying at module import time on a dependency the stage
    you asked for never needed.
    """

    name: str
    description: str
    run: Callable[[], None]
    required_by_later_stages: bool = False
    optional_dependency: str | None = None   # pip package that may be absent
    produces: List[str] = field(default_factory=list)


def _stage_data() -> None:
    from src.data.preprocess import run_preprocessing
    df = run_preprocessing(save=True)
    counts = df["Class"].value_counts().reindex(["L", "M", "H"]).to_dict()
    logger.info("Cleaned dataset: %d students x %d columns", len(df), df.shape[1])
    logger.info("Class distribution: %s", counts)


def _stage_eda() -> None:
    from src.analysis.eda import generate_all_figures
    from src.data.preprocess import load_processed
    figures = generate_all_figures(load_processed())
    logger.info("Generated %d figures in reports/figures/", len(figures))


def _stage_stats() -> None:
    from src.analysis.statistical_tests import run_all_tests, summarise_findings
    from src.data.preprocess import load_processed
    results = run_all_tests(load_processed(), save=True)
    logger.info(
        "%d of %d tests significant after Holm correction",
        len(results["significant_factors"]), results["n_tests_in_family"],
    )
    print("\n" + summarise_findings(results, top_n=6) + "\n")


def _stage_train() -> None:
    from src.models.train import train_all
    results = train_all(save=True)
    best = results["best_model"]
    logger.info("Selected model: %s", best)
    test = results["test_metrics"][best]
    logger.info("Test macro-F1 %.4f | accuracy %.4f", test["f1_macro"], test["accuracy"])


def _stage_explain() -> None:
    from src.explainability.shap_utils import run_explainability
    run_explainability(save=True)


def _stage_counterfactuals() -> None:
    from src.counterfactuals.dice_engine import run_counterfactual_analysis
    run_counterfactual_analysis(save=True)


def _stage_fairness() -> None:
    from src.fairness.audit import run_fairness_audit
    audit = run_fairness_audit(save=True)
    verdict = audit.get("overall_verdict", {}).get("headline", "see reports/artifacts/fairness.json")
    logger.info("Fairness verdict: %s", verdict)


def _stage_simulation() -> None:
    from src.simulation.cohort_simulator import run_all_scenarios
    run_all_scenarios(save=True)


def _stage_recommendations() -> None:
    from src.recommendations.engine import warm_cache
    warm_cache(save=True)


def _stage_reports() -> None:
    from src.reporting.build_documents import build_all_documents
    written = build_all_documents()
    for path in written:
        logger.info("Wrote %s", Path(path).relative_to(PROJECT_ROOT))


def _stage_notebooks() -> None:
    from scripts.build_notebooks import main as build_notebooks
    build_notebooks()


STAGES: List[Stage] = [
    Stage(
        name="data",
        description="Load, validate and clean the raw dataset",
        run=_stage_data,
        required_by_later_stages=True,
        produces=["data/processed/cleaned.csv", "data/processed/schema_report.json"],
    ),
    Stage(
        name="eda",
        description="Generate all exploratory figures",
        run=_stage_eda,
        produces=["reports/figures/*.png"],
    ),
    Stage(
        name="stats",
        description="ANOVA, chi-square, effect sizes, Holm correction",
        run=_stage_stats,
        produces=["reports/artifacts/statistical_tests.json"],
    ),
    Stage(
        name="train",
        description="Train and compare four models, tune, evaluate, save the best",
        run=_stage_train,
        required_by_later_stages=True,
        produces=["models/model.joblib", "models/model_card.json",
                  "reports/artifacts/metrics.json"],
    ),
    Stage(
        name="explain",
        description="SHAP global and per-student explanations",
        run=_stage_explain,
        optional_dependency="shap",
        produces=["reports/artifacts/shap_global.json",
                  "reports/figures/12_shap_global_importance.png"],
    ),
    Stage(
        name="counterfactuals",
        description="What would need to change for a better outcome",
        run=_stage_counterfactuals,
        optional_dependency="dice-ml",
        produces=["reports/artifacts/counterfactual_examples.json"],
    ),
    Stage(
        name="fairness",
        description="Demographic parity and equalized odds audit",
        run=_stage_fairness,
        optional_dependency="fairlearn",
        produces=["reports/artifacts/fairness.json"],
    ),
    Stage(
        name="simulation",
        description="Monte Carlo cohort intervention simulator",
        run=_stage_simulation,
        produces=["reports/artifacts/simulation.json"],
    ),
    Stage(
        name="recommendations",
        description="Pre-compute the recommendation cache",
        run=_stage_recommendations,
        produces=["reports/artifacts/recommendations_sample.json"],
    ),
    Stage(
        name="notebooks",
        description="Rebuild the Jupyter notebooks from source",
        run=_stage_notebooks,
        produces=["notebooks/*.ipynb"],
    ),
    Stage(
        name="reports",
        description="Build project_report.docx and presentation.pptx from the artifacts",
        run=_stage_reports,
        optional_dependency="python-docx / python-pptx",
        produces=["reports/project_report.docx", "reports/presentation.pptx"],
    ),
]

STAGE_NAMES = [s.name for s in STAGES]


# =============================================================================
# Runner
# =============================================================================

def select_stages(args: argparse.Namespace) -> List[Stage]:
    """Work out which stages to run from the command-line flags."""
    if args.only:
        unknown = [n for n in args.only if n not in STAGE_NAMES]
        if unknown:
            raise SystemExit(f"Unknown stage(s): {unknown}. Valid: {STAGE_NAMES}")
        chosen = [s for s in STAGES if s.name in args.only]
    else:
        chosen = list(STAGES)
        if args.from_stage:
            if args.from_stage not in STAGE_NAMES:
                raise SystemExit(f"Unknown stage '{args.from_stage}'. Valid: {STAGE_NAMES}")
            start = STAGE_NAMES.index(args.from_stage)
            chosen = chosen[start:]
        if args.skip:
            chosen = [s for s in chosen if s.name not in args.skip]
    return chosen


def run_stage(stage: Stage) -> Dict[str, object]:
    """Execute one stage, timing it and turning any failure into a report entry."""
    section(logger, f"STAGE: {stage.name} — {stage.description}")
    started = time.perf_counter()
    try:
        stage.run()
        elapsed = time.perf_counter() - started
        logger.info("Stage '%s' finished in %.1fs", stage.name, elapsed)
        return {"stage": stage.name, "status": "ok", "seconds": round(elapsed, 1)}

    except ImportError as exc:
        elapsed = time.perf_counter() - started
        hint = (
            f"Install it with: pip install {stage.optional_dependency}"
            if stage.optional_dependency
            else "This looks like a missing dependency — try: pip install -r requirements.txt"
        )
        logger.warning("Stage '%s' skipped — %s. %s", stage.name, exc, hint)
        return {"stage": stage.name, "status": "skipped",
                "reason": str(exc), "hint": hint, "seconds": round(elapsed, 1)}

    except FileNotFoundError as exc:
        elapsed = time.perf_counter() - started
        logger.error("Stage '%s' failed — a required input is missing: %s", stage.name, exc)
        return {"stage": stage.name, "status": "failed",
                "reason": str(exc), "seconds": round(elapsed, 1)}

    except Exception as exc:  # noqa: BLE001 — we deliberately want the run to continue
        elapsed = time.perf_counter() - started
        logger.error("Stage '%s' failed: %s", stage.name, exc)
        logger.debug(traceback.format_exc())
        return {"stage": stage.name, "status": "failed", "reason": str(exc),
                "traceback": traceback.format_exc(), "seconds": round(elapsed, 1)}


def print_summary(results: Sequence[Dict[str, object]], total_seconds: float) -> int:
    """Print the end-of-run table. Returns the process exit code."""
    print("\n" + "=" * 74)
    print("PIPELINE SUMMARY")
    print("=" * 74)

    symbols = {"ok": "  OK   ", "skipped": " SKIP  ", "failed": " FAIL  "}
    for r in results:
        print(f"[{symbols.get(str(r['status']), '  ?   ')}] {str(r['stage']):<18} "
              f"{str(r['seconds']):>6}s   {r.get('reason', '')}")

    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_skip = sum(1 for r in results if r["status"] == "skipped")
    n_fail = sum(1 for r in results if r["status"] == "failed")

    print("-" * 74)
    print(f"{n_ok} succeeded, {n_skip} skipped, {n_fail} failed "
          f"in {total_seconds:.1f}s total")

    if n_skip:
        print("\nSkipped stages are usually a missing optional package:")
        for r in results:
            if r["status"] == "skipped":
                print(f"  - {r['stage']}: {r.get('hint', '')}")

    if n_fail:
        print("\nFailed stages — rerun one on its own to see the full traceback:")
        for r in results:
            if r["status"] == "failed":
                print(f"  python scripts/run_pipeline.py --only {r['stage']}")
        return 1

    print("\nArtifacts are in reports/, models/ and data/processed/.")
    print("Launch the dashboard with:  streamlit run app/dashboard.py")
    print("=" * 74)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Student Performance Prediction pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Stages, in order: " + " -> ".join(STAGE_NAMES),
    )
    parser.add_argument("--only", nargs="+", metavar="STAGE",
                        help="Run only these stages.")
    parser.add_argument("--from", dest="from_stage", metavar="STAGE",
                        help="Start at this stage and run everything after it.")
    parser.add_argument("--skip", nargs="+", default=[], metavar="STAGE",
                        help="Run everything except these stages.")
    parser.add_argument("--list", action="store_true",
                        help="List the stages and what each one produces, then exit.")
    args = parser.parse_args(argv)

    if args.list:
        print(f"\n{'STAGE':<18} {'DESCRIPTION':<52} PRODUCES")
        print("-" * 110)
        for s in STAGES:
            print(f"{s.name:<18} {s.description:<52} {', '.join(s.produces)}")
        print()
        return 0

    cfg = load_config()
    section(logger, f"{cfg['project']['name']} v{cfg['project']['version']}")
    logger.info("Random seed: %s (every split, model and simulation uses this)",
                cfg["project"]["random_seed"])

    stages = select_stages(args)
    logger.info("Running %d stage(s): %s", len(stages), ", ".join(s.name for s in stages))

    started = time.perf_counter()
    results: List[Dict[str, object]] = []
    for stage in stages:
        result = run_stage(stage)
        results.append(result)

        # If a stage everything downstream depends on has failed, stopping now
        # gives a clear error instead of ten confusing ones.
        if result["status"] == "failed" and stage.required_by_later_stages:
            logger.error(
                "Stage '%s' is required by the stages that follow it — stopping here.",
                stage.name,
            )
            break

    return print_summary(results, time.perf_counter() - started)


if __name__ == "__main__":
    raise SystemExit(main())
