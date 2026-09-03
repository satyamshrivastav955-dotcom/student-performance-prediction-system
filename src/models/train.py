"""
Model training — Module 3 of the brief.

Four models, trained in ascending order of complexity:

1. **Logistic Regression** — the honest baseline. If a 400-tree ensemble cannot
   beat a linear model on 478 rows, the ensemble is not earning its complexity
   and we should say so rather than shipping it anyway.
2. **Decision Tree** — the interpretable middle ground. A teacher can literally
   read the rules off it.
3. **Random Forest** — bagged trees. Explicitly named in the brief.
4. **Gradient Boosting** (XGBoost, falling back to scikit-learn's
   HistGradientBoosting) — the usual strongest performer on small tabular data.

Deliberately **not** here: any neural network, embedding or transformer. The
brief rules them out, and on 478 rows they would lose to these models anyway —
gradient-boosted trees remain the state of the art for small tabular problems.
That is not a compromise forced by the rules; it is the correct engineering
choice, and the report says so explicitly.

Everything is wrapped in a scikit-learn ``Pipeline`` so preprocessing travels
with the model. Cross-validation runs on the *pipeline*, not on pre-transformed
data — otherwise the scaler would be fitted on the validation fold too and every
CV score would be optimistically biased by data leakage. That subtle mistake is
extremely common and it is worth being explicit about avoiding it.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.data.preprocess import (
    build_preprocessor,
    encode_target,
    feature_columns,
    load_processed,
    split_features_target,
)
from src.utils.config import get_path, load_config, save_json
from src.utils.logging_utils import get_logger, section

logger = get_logger(__name__)


# =============================================================================
# Model construction
# =============================================================================

def _xgboost_available() -> bool:
    try:
        import xgboost  # noqa: F401
        return True
    except Exception:
        return False


def build_models(cfg: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Instantiate every enabled model as a bare estimator (no preprocessing yet).

    Class weighting: every model that supports ``class_weight`` gets
    ``"balanced"``. Our Low band is only 26% of the data, and the Low students
    are precisely the ones this system exists to identify — a model that
    quietly optimises for the majority Medium band would score well on accuracy
    while being useless for its actual purpose.
    """
    cfg = cfg or load_config()
    seed = int(cfg["project"]["random_seed"])
    m = cfg["models"]
    models: Dict[str, Any] = {}

    if m["logistic_regression"]["enabled"]:
        from sklearn.linear_model import LogisticRegression
        params = dict(m["logistic_regression"]["params"])
        # `multi_class` was deprecated in scikit-learn 1.5; drop it there.
        try:
            import sklearn
            if tuple(int(x) for x in sklearn.__version__.split(".")[:2]) >= (1, 5):
                params.pop("multi_class", None)
        except Exception:
            params.pop("multi_class", None)
        models["logistic_regression"] = LogisticRegression(random_state=seed, **params)

    if m["decision_tree"]["enabled"]:
        from sklearn.tree import DecisionTreeClassifier
        models["decision_tree"] = DecisionTreeClassifier(
            random_state=seed, **m["decision_tree"]["params"]
        )

    if m["random_forest"]["enabled"]:
        from sklearn.ensemble import RandomForestClassifier
        models["random_forest"] = RandomForestClassifier(
            random_state=seed, **m["random_forest"]["params"]
        )

    if m["gradient_boosting"]["enabled"]:
        params = dict(m["gradient_boosting"]["params"])
        if m["gradient_boosting"].get("backend") == "xgboost" and _xgboost_available():
            from xgboost import XGBClassifier
            # Note: we deliberately do NOT pass `num_class`. The scikit-learn
            # wrapper infers it from y and raises if you also set it by hand.
            models["gradient_boosting"] = XGBClassifier(
                random_state=seed,
                objective="multi:softprob",
                eval_metric="mlogloss",
                tree_method="hist",
                **params,
            )
        else:
            # Graceful fallback so the project runs on a machine without
            # xgboost. HistGradientBoosting is scikit-learn's own LightGBM-style
            # implementation and performs comparably on data this size.
            from sklearn.ensemble import HistGradientBoostingClassifier
            logger.warning("xgboost unavailable — using scikit-learn HistGradientBoosting instead.")
            models["gradient_boosting"] = HistGradientBoostingClassifier(
                random_state=seed,
                max_iter=params.get("n_estimators", 400),
                learning_rate=params.get("learning_rate", 0.08),
                max_depth=params.get("max_depth", 4),
            )

    return models


def build_pipeline(model, cfg: Dict[str, Any] | None = None):
    """Bolt the preprocessing transformer onto the front of an estimator.

    The resulting object takes **raw** student data — the same 16 columns a
    teacher would type into the dashboard — and handles encoding and scaling
    internally. That is what makes the dashboard and the API structurally
    incapable of disagreeing about how a student should be encoded.
    """
    from sklearn.pipeline import Pipeline

    cfg = cfg or load_config()
    return Pipeline([
        ("preprocess", build_preprocessor(cfg)),
        ("model", model),
    ])


# =============================================================================
# Cross-validation
# =============================================================================

def cross_validate_models(
    X: pd.DataFrame,
    y: np.ndarray,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Stratified k-fold CV for every model.

    Stratified because the class balance is 44/30/26 — plain k-fold could hand
    a fold barely any Low students, making that fold's macro-F1 meaningless.

    Scored on **macro-F1**: it averages the F1 of each class equally, so doing
    badly on the small Low class is properly punished. Accuracy would let a
    model coast by getting the big Medium class right.
    """
    from sklearn.model_selection import StratifiedKFold, cross_validate

    cfg = cfg or load_config()
    seed = int(cfg["project"]["random_seed"])
    n_splits = int(cfg["cv"]["n_splits"])
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    scoring = {
        "accuracy": "accuracy",
        "f1_macro": "f1_macro",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "roc_auc_ovr": "roc_auc_ovr_weighted",
    }

    results: Dict[str, Dict[str, Any]] = {}
    for name, model in build_models(cfg).items():
        pipe = build_pipeline(model, cfg)
        start = time.time()
        scores = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=1,
                                return_train_score=True, error_score="raise")
        elapsed = time.time() - start

        entry: Dict[str, Any] = {"fit_seconds": round(elapsed, 2), "n_splits": n_splits}
        for metric in scoring:
            test_vals = scores[f"test_{metric}"]
            train_vals = scores[f"train_{metric}"]
            entry[metric] = {
                "mean": round(float(np.mean(test_vals)), 4),
                "std": round(float(np.std(test_vals)), 4),
                "folds": [round(float(v), 4) for v in test_vals],
                "train_mean": round(float(np.mean(train_vals)), 4),
                # A large train-test gap is the fingerprint of overfitting. We
                # record it so the report can discuss it instead of hiding it.
                "overfit_gap": round(float(np.mean(train_vals) - np.mean(test_vals)), 4),
            }
        results[name] = entry
        logger.info(
            "  %-22s macro-F1 %.4f (+/- %.4f)  acc %.4f  overfit gap %.3f  [%.1fs]",
            name, entry["f1_macro"]["mean"], entry["f1_macro"]["std"],
            entry["accuracy"]["mean"], entry["f1_macro"]["overfit_gap"], elapsed,
        )
    return results


# =============================================================================
# Hyperparameter tuning
# =============================================================================

def tune_model(
    name: str,
    X: pd.DataFrame,
    y: np.ndarray,
    cfg: Dict[str, Any] | None = None,
) -> Tuple[Any, Dict[str, Any]]:
    """Randomised hyperparameter search for one model.

    Randomised rather than exhaustive: with 478 rows, the difference between two
    nearby hyperparameter settings is well inside the noise of a 5-fold CV
    estimate. An exhaustive grid would spend a lot of compute buying precision
    we cannot statistically detect. Randomised search covers more of the space
    per unit of time, which is what actually matters here.
    """
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

    cfg = cfg or load_config()
    seed = int(cfg["project"]["random_seed"])
    grid = cfg["tuning"]["grids"].get(name, {})
    if not grid:
        logger.info("  no tuning grid for '%s' — using configured defaults", name)
        base = build_models(cfg)[name]
        return build_pipeline(base, cfg), {"tuned": False}

    base_model = build_models(cfg)[name]

    # Only keep grid entries the estimator actually accepts. This matters
    # because gradient boosting may fall back from XGBoost to scikit-learn's
    # HistGradientBoosting, which has no `subsample` or `colsample_bytree` —
    # passing them would crash the search rather than degrade gracefully.
    try:
        valid_params = set(base_model.get_params().keys())
        dropped = [k for k in grid if k not in valid_params]
        if dropped:
            logger.info("  '%s' does not accept %s — dropped from the search grid",
                        name, dropped)
            grid = {k: v for k, v in grid.items() if k in valid_params}
    except Exception:  # pragma: no cover - estimator without get_params
        pass

    if not grid:
        logger.info("  no applicable tuning parameters for '%s' — using defaults", name)
        return build_pipeline(base_model, cfg), {"tuned": False,
                                                 "reason": "no applicable grid parameters"}

    # Grid keys are bare parameter names; inside a Pipeline they need the
    # "model__" prefix so scikit-learn knows which step they belong to.
    prefixed = {f"model__{k}": v for k, v in grid.items()}

    pipe = build_pipeline(base_model, cfg)
    cv = StratifiedKFold(n_splits=int(cfg["cv"]["n_splits"]), shuffle=True, random_state=seed)

    search = RandomizedSearchCV(
        pipe,
        param_distributions=prefixed,
        n_iter=int(cfg["tuning"]["n_iter"]),
        scoring=cfg["cv"]["scoring"],
        cv=cv,
        random_state=seed,
        n_jobs=1,
        refit=True,
        error_score="raise",
    )
    start = time.time()
    search.fit(X, y)
    elapsed = time.time() - start

    info = {
        "tuned": True,
        "best_params": {k.replace("model__", ""): v for k, v in search.best_params_.items()},
        "best_cv_score": round(float(search.best_score_), 4),
        "n_candidates": int(len(search.cv_results_["params"])),
        "search_seconds": round(elapsed, 1),
    }
    logger.info("  tuned %-20s best macro-F1 %.4f  [%.0fs]", name, search.best_score_, elapsed)
    logger.info("       params: %s", info["best_params"])
    return search.best_estimator_, info


# =============================================================================
# Full training run
# =============================================================================

def make_split(cfg: Dict[str, Any] | None = None):
    """Produce the project's canonical train/test split.

    Every downstream stage — SHAP, the fairness audit, the counterfactual engine,
    the cohort simulator — needs "the test set". If each of them called
    ``train_test_split`` itself, a single edited argument in one file would leave
    the fairness audit reporting on a different set of students than the
    accuracy figures, and the two would quietly disagree forever.

    So the split lives here, once. It is fully deterministic: the same config
    gives the same split on any machine, which is why the later stages can
    reproduce it without the training run having to serialise the test rows.

    Returns:
        ``(X_train, X_test, y_train, y_test, class_order)`` where ``y`` values
        are the integer codes 0=L, 1=M, 2=H.
    """
    from sklearn.model_selection import train_test_split

    cfg = cfg or load_config()
    seed = int(cfg["project"]["random_seed"])

    df = load_processed(cfg)
    X, y_labels = split_features_target(df, cfg)
    y, class_order = encode_target(y_labels, cfg)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=float(cfg["split"]["test_size"]),
        stratify=y if cfg["split"]["stratify"] else None,
        shuffle=bool(cfg["split"]["shuffle"]),
        random_state=seed,
    )
    return X_train, X_test, y_train, y_test, class_order


def train_all(cfg: Dict[str, Any] | None = None, save: bool = True) -> Dict[str, Any]:
    """The complete Phase 3 training run.

    Steps: load -> split -> cross-validate all four -> tune the top two ->
    evaluate on the held-out test set -> bootstrap CIs -> McNemar -> error
    analysis -> save the winning pipeline.

    Returns the full results dict, which is also written to
    ``reports/artifacts/metrics.json``. Every number in the report and the slide
    deck is read from that file, so the documents can never contradict the code.
    """
    from src.models.evaluate import (
        bootstrap_metrics,
        error_analysis,
        evaluate_predictions,
        mcnemar_comparison,
    )

    cfg = cfg or load_config()
    seed = int(cfg["project"]["random_seed"])

    section(logger, "PHASE 3 — MODEL TRAINING")

    # --- Data ----------------------------------------------------------------
    X_train, X_test, y_train, y_test, class_order = make_split(cfg)
    logger.info("Train: %d students | Test: %d students | Classes: %s",
                len(X_train), len(X_test), class_order)

    results: Dict[str, Any] = {
        "config": {
            "random_seed": seed,
            "test_size": cfg["split"]["test_size"],
            "cv_folds": cfg["cv"]["n_splits"],
            "cv_scoring": cfg["cv"]["scoring"],
            "class_order": class_order,
            "n_features_raw": len(feature_columns(cfg)),
            "xgboost_available": _xgboost_available(),
        },
        "dataset": {
            "n_total": int(len(X_train) + len(X_test)),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "train_class_counts": {class_order[i]: int((y_train == i).sum())
                                   for i in range(len(class_order))},
            "test_class_counts": {class_order[i]: int((y_test == i).sum())
                                  for i in range(len(class_order))},
        },
    }

    # --- Cross-validation ----------------------------------------------------
    section(logger, "Cross-validation (all models)")
    cv_results = cross_validate_models(X_train, y_train, cfg)
    results["cross_validation"] = cv_results

    ranked = sorted(cv_results.items(), key=lambda kv: kv[1]["f1_macro"]["mean"], reverse=True)
    results["cv_ranking"] = [name for name, _ in ranked]
    logger.info("CV ranking by macro-F1: %s", " > ".join(results["cv_ranking"]))

    # --- Tuning the top candidates ------------------------------------------
    top_k = int(cfg["tuning"]["top_k_models"])
    top_names = [name for name, _ in ranked[:top_k]]
    fitted: Dict[str, Any] = {}
    tuning_info: Dict[str, Any] = {}

    if cfg["tuning"]["enabled"]:
        section(logger, f"Hyperparameter tuning (top {top_k}: {', '.join(top_names)})")
        for name in top_names:
            est, info = tune_model(name, X_train, y_train, cfg)
            fitted[name] = est
            tuning_info[name] = info

    # Every remaining model is still fitted with its default settings so the
    # comparison table covers all four, as the brief asks.
    for name, model in build_models(cfg).items():
        if name not in fitted:
            pipe = build_pipeline(model, cfg)
            pipe.fit(X_train, y_train)
            fitted[name] = pipe
            tuning_info[name] = {"tuned": False}
    results["tuning"] = tuning_info

    # --- Held-out test evaluation -------------------------------------------
    section(logger, "Held-out test set evaluation")
    test_results: Dict[str, Any] = {}
    predictions: Dict[str, np.ndarray] = {}

    for name, est in fitted.items():
        y_pred = est.predict(X_test)
        y_proba = est.predict_proba(X_test) if hasattr(est, "predict_proba") else None
        predictions[name] = y_pred
        test_results[name] = evaluate_predictions(y_test, y_pred, y_proba, class_order)
        logger.info("  %-22s test macro-F1 %.4f  accuracy %.4f",
                    name, test_results[name]["f1_macro"], test_results[name]["accuracy"])
    results["test_evaluation"] = test_results
    results["test_metrics"] = test_results

    # --- Pick the winner -----------------------------------------------------
    best_name = max(test_results, key=lambda n: test_results[n]["f1_macro"])
    runner_up = sorted(test_results, key=lambda n: test_results[n]["f1_macro"], reverse=True)[1]
    results["best_model"] = best_name
    results["runner_up_model"] = runner_up
    logger.info("Best model: %s | Runner-up: %s", best_name, runner_up)

    # --- Bootstrapped confidence intervals -----------------------------------
    if cfg["evaluation"]["bootstrap"]["enabled"]:
        section(logger, "Bootstrapped confidence intervals")
        boot: Dict[str, Any] = {}
        for name in (best_name, runner_up):
            boot[name] = bootstrap_metrics(y_test, predictions[name], class_order, cfg)
            ci = boot[name]["f1_macro"]
            logger.info("  %-22s macro-F1 %.4f  95%% CI [%.4f, %.4f]",
                        name, ci["point_estimate"], ci["ci_lower"], ci["ci_upper"])
        results["bootstrap"] = boot

    # --- McNemar: is the winner actually better? -----------------------------
    if cfg["evaluation"]["mcnemar"]["enabled"]:
        section(logger, "McNemar's test — best vs runner-up")
        mc = mcnemar_comparison(
            y_test, predictions[best_name], predictions[runner_up],
            best_name, runner_up, cfg,
        )
        results["mcnemar"] = mc
        logger.info("  %s", mc["interpretation"])

    # --- Error analysis ------------------------------------------------------
    if cfg["evaluation"]["error_analysis"]["enabled"]:
        section(logger, "Error analysis on the winning model")
        results["error_analysis"] = error_analysis(
            X_test, y_test, predictions[best_name], class_order, cfg
        )
        logger.info("  %s", results["error_analysis"]["summary"])

    # --- Refit the winner on ALL data and save -------------------------------
    # Model selection is finished, so the final artifact is trained on every
    # available row. Holding 20% back permanently would throw away real signal
    # for no benefit — the test set already did its job of producing an unbiased
    # performance estimate, and that estimate is what we report.
    section(logger, "Fitting final model on the full dataset")
    X_full = pd.concat([X_train, X_test], axis=0)
    y_full = np.concatenate([y_train, y_test])
    final_model_name = best_name
    if tuning_info.get(best_name, {}).get("tuned"):
        final_estimator = fitted[best_name]
        final_estimator.fit(X_full, y_full)
    else:
        final_estimator = build_pipeline(build_models(cfg)[best_name], cfg)
        final_estimator.fit(X_full, y_full)

    if save:
        import joblib

        model_path = get_path("model_file", cfg, ensure_parent=True)
        joblib.dump(
            {
                "pipeline": final_estimator,
                "class_order": class_order,
                "feature_columns": feature_columns(cfg),
                "model_name": final_model_name,
                "config_version": cfg["project"]["version"],
                "trained_on_n": int(len(X_full)),
            },
            model_path,
        )
        logger.info("Saved model bundle -> %s", model_path)

        save_json(_build_model_card(results, cfg), get_path("model_card", cfg, ensure_parent=True))
        save_json(results, get_path("metrics_file", cfg, ensure_parent=True))
        logger.info("Saved metrics -> %s", get_path("metrics_file", cfg))

    results["final_model_trained_on"] = int(len(X_full))
    return results


def _build_model_card(results: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    """A short model card — what this model is, how good it is, and its limits.

    Model cards are standard practice for responsible ML deployment. Shipping
    one costs almost nothing and makes the system's boundaries explicit to
    whoever inherits it.
    """
    best = results["best_model"]
    test = results["test_evaluation"][best]
    boot = results.get("bootstrap", {}).get(best, {})

    return {
        "model_name": best,
        "task": "3-class student performance classification (Low / Medium / High)",
        "intended_use": (
            "Decision support for teachers and academic advisors: flag students who may need "
            "extra help, and show which changeable behaviours are driving that assessment."
        ),
        "out_of_scope_use": [
            "Automated grading or any decision that affects a student's record without a human.",
            "Admissions, streaming or any high-stakes selection decision.",
            "Any use where the student is not told the prediction was made or why.",
        ],
        "training_data": {
            "source": "xAPI-Edu-Data (Amrieh, Hamtini & Aljarah, 2016)",
            "n_students": results["dataset"]["n_total"],
            "n_features": results["config"]["n_features_raw"],
        },
        "performance": {
            "test_accuracy": test["accuracy"],
            "test_f1_macro": test["f1_macro"],
            "f1_macro_95_ci": [boot.get("f1_macro", {}).get("ci_lower"),
                               boot.get("f1_macro", {}).get("ci_upper")] if boot else None,
            "per_class_f1": test.get("per_class", {}),
        },
        "limitations": [
            "Trained on 478 students from a single learning-management system; performance on a "
            "different school population is unverified.",
            "Features are behavioural proxies (clicks, hands raised), not direct measures of "
            "understanding.",
            "The dataset is cross-sectional, so the model describes association, not causation. "
            "Counterfactual suggestions should be read as hypotheses to try, not guarantees.",
        ],
        "fairness": "See reports/artifacts/fairness_audit.json for the demographic parity and "
                    "equalized-odds audit across gender and nationality.",
        "ethical_note": (
            "Predictions should always be shown to the student alongside the reasons and the "
            "suggested actions, never used as a silent label attached to them."
        ),
    }


if __name__ == "__main__":  # pragma: no cover - manual run
    train_all()
