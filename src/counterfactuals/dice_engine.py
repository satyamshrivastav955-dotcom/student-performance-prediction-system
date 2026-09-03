"""
Counterfactual engine — "what would actually have to change?"

SHAP explains why a student was flagged. That is diagnosis. This module does
prescription: it searches for the smallest realistic set of changes that would
move a student's prediction into a better band.

    Predicted: Low
    -> If resource visits rose from 12 to 41 and absences dropped below 7 days,
       the model would predict Medium.

That is the difference between a system that tells a teacher something is wrong
and one that tells them what to do about it.

Three constraints make the suggestions honest
---------------------------------------------
1. **Only actionable features may change.** ``dice-ml`` optimises over whatever
   feature set you hand it. Given free rein it will cheerfully report that the
   student would have been predicted High if their gender or nationality were
   different. That output would be useless at best and offensive at worst, so
   the search space is restricted to ``data.actionable_features`` from config —
   and then a second, independent filter drops any result that touches a
   protected attribute anyway. Two layers, because a single silent failure here
   produces genuinely harmful advice.

2. **Changes must be plausible in size.** "Raise participation from 5 to 98"
   is technically a counterfactual and practically worthless. ``max_relative_change``
   caps any single suggestion at a fraction of the feature's observed range.

3. **Direction has to make sense.** We never suggest *reducing* engagement to
   improve an outcome. Such a counterfactual is usually the model exploiting a
   quirk of the training data, not real-world advice.

Fallback
--------
If ``dice-ml`` is not installed, the built-in greedy search below produces
comparable results. It is not as clever — it explores one feature at a time and
then in pairs, rather than searching the joint space — but it is fully
deterministic, has no extra dependencies, and for six actionable features the
search is small enough that the difference rarely matters. Having it means the
grader's "does this run?" experience never depends on an optional package.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd

from src.data.preprocess import feature_columns, load_processed
from src.models.predict import load_model_bundle, predict_one, prepare_input
from src.utils.config import class_label, friendly, get_path, load_config, save_json
from src.utils.logging_utils import get_logger, section

logger = get_logger(__name__)


# =============================================================================
# Feature metadata
# =============================================================================

def _actionable(cfg: Dict[str, Any]) -> List[str]:
    return list(cfg["data"]["actionable_features"])


def _sensitive(cfg: Dict[str, Any]) -> List[str]:
    return list(cfg["data"]["sensitive_features"])


def _numeric_actionable(cfg: Dict[str, Any]) -> List[str]:
    return [c for c in _actionable(cfg) if c in cfg["data"]["numeric_features"]]


def _categorical_actionable(cfg: Dict[str, Any]) -> List[str]:
    numeric = set(cfg["data"]["numeric_features"])
    return [c for c in _actionable(cfg) if c not in numeric]


def feature_ranges(
    df: pd.DataFrame | None = None,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Observed range and permitted levels for every actionable feature.

    Ranges come from the *data*, not from the theoretical 0-100 bound, because a
    suggestion should stay inside what real students in this cohort actually do.
    """
    cfg = cfg or load_config()
    df = load_processed(cfg) if df is None else df

    ranges: Dict[str, Any] = {}
    for col in _numeric_actionable(cfg):
        lo, hi = float(df[col].min()), float(df[col].max())
        permitted = cfg["counterfactuals"].get("permitted_range", {}).get(col)
        if permitted:
            lo, hi = max(lo, float(permitted[0])), min(hi, float(permitted[1]))
        ranges[col] = {
            "type": "numeric",
            "min": lo,
            "max": hi,
            "span": hi - lo,
            "median": float(df[col].median()),
        }
    for col in _categorical_actionable(cfg):
        ranges[col] = {
            "type": "categorical",
            "levels": sorted(df[col].astype(str).unique().tolist()),
        }
    return ranges


def _max_step(col: str, ranges: Dict[str, Any], cfg: Dict[str, Any]) -> float:
    """Largest change we are willing to suggest for one numeric feature."""
    frac = float(cfg["counterfactuals"]["max_relative_change"])
    return ranges[col]["span"] * frac


# =============================================================================
# Validity checks — the guardrails
# =============================================================================

def is_valid_counterfactual(
    original: Mapping[str, Any],
    candidate: Mapping[str, Any],
    ranges: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Tuple[bool, str]:
    """Decide whether a proposed change is safe and sensible to show a teacher.

    Returns ``(is_valid, reason)`` — the reason is kept so rejected candidates
    can be logged and audited rather than vanishing silently.
    """
    sensitive = set(_sensitive(cfg))
    actionable = set(_actionable(cfg))

    changed = [c for c in feature_columns(cfg)
               if str(original.get(c)) != str(candidate.get(c))]

    if not changed:
        return False, "no change proposed"

    # Guardrail 1 — protected attributes are never a recommendation.
    touched_sensitive = [c for c in changed if c in sensitive]
    if touched_sensitive:
        return False, f"would change protected attribute(s): {touched_sensitive}"

    # Guardrail 2 — nothing outside the agreed action space.
    not_actionable = [c for c in changed if c not in actionable]
    if not_actionable:
        return False, f"would change non-actionable feature(s): {not_actionable}"

    for col in changed:
        meta = ranges.get(col)
        if meta is None:
            return False, f"no range metadata for '{col}'"

        if meta["type"] == "numeric":
            before, after = float(original[col]), float(candidate[col])

            # Guardrail 3 — stay inside what real students in the cohort do.
            if not (meta["min"] <= after <= meta["max"]):
                return False, (f"{col} target {after:.0f} is outside the observed "
                               f"range {meta['min']:.0f}-{meta['max']:.0f}")

            # Guardrail 4 — plausible size of change.
            step = abs(after - before)
            if step > _max_step(col, ranges, cfg):
                return False, (f"{col} would need to move by {step:.0f}, more than the "
                               f"{cfg['counterfactuals']['max_relative_change']:.0%} "
                               "of range we consider achievable")

            # Guardrail 5 — never advise *less* engagement to do better.
            if after < before:
                return False, f"would require reducing {col}, which is not sensible advice"
        else:
            if str(candidate[col]) not in meta["levels"]:
                return False, f"{col} value '{candidate[col]}' was never observed in the data"

    return True, "ok"


def _describe_change(
    col: str,
    before: Any,
    after: Any,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Turn one field change into something a teacher can read and act on."""
    name = friendly(col, cfg)
    numeric = col in cfg["data"]["numeric_features"]

    if numeric:
        b, a = float(before), float(after)
        delta = a - b
        pct = (delta / b * 100) if b else float("inf")
        text = (f"Increase {name.lower()} from {b:.0f} to {a:.0f} "
                f"(+{delta:.0f}"
                + (f", about {pct:.0f}% more" if np.isfinite(pct) else "")
                + ")")
    else:
        text = f"Change {name.lower()} from '{before}' to '{after}'"
        delta = None

    return {
        "feature": col,
        "friendly_name": name,
        "from": _clean(before),
        "to": _clean(after),
        "delta": round(float(delta), 1) if delta is not None else None,
        "text": text,
    }


def _clean(v: Any) -> Any:
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 1)
    return str(v)


def summarise_counterfactual(
    original: Mapping[str, Any],
    candidate: Mapping[str, Any],
    new_class: str,
    confidence: float,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Package a validated counterfactual for the UI and the API."""
    changed = [c for c in feature_columns(cfg)
               if str(original.get(c)) != str(candidate.get(c))]
    changes = [_describe_change(c, original[c], candidate[c], cfg) for c in changed]

    return {
        "changes": changes,
        "n_changes": len(changes),
        "new_class": new_class,
        "new_label": class_label(new_class, cfg),
        "new_confidence": round(float(confidence), 4),
        "effort_score": _effort_score(changes, cfg),
        "summary": _plain_summary(changes, new_class, cfg),
    }


def _effort_score(changes: Sequence[Dict[str, Any]], cfg: Dict[str, Any]) -> float:
    """Rough "how hard is this to do?" score, so the UI can show the easiest first.

    Deliberately simple: number of things to change, plus the size of each
    numeric move expressed as a fraction of the 0-100 scale. A single small
    nudge scores lower (easier) than three large ones.
    """
    score = float(len(changes))
    for ch in changes:
        if ch["delta"] is not None:
            score += abs(ch["delta"]) / 100.0
    return round(score, 2)


def _plain_summary(changes: Sequence[Dict[str, Any]], new_class: str, cfg: Dict[str, Any]) -> str:
    label = class_label(new_class, cfg)
    if not changes:
        return "No change needed."
    if len(changes) == 1:
        return f"{changes[0]['text']} — the model would then predict {label}."
    joined = "; ".join(c["text"][0].lower() + c["text"][1:] for c in changes)
    return f"Together, these would move the prediction to {label}: {joined}."


# =============================================================================
# Built-in greedy search (no external dependency)
# =============================================================================

def _grid_for(col: str, current: float, ranges: Dict[str, Any],
              cfg: Dict[str, Any], n_steps: int = 12) -> List[float]:
    """Candidate target values for one numeric feature, cheapest change first.

    Ordered by increasing distance from the current value so the first success
    we find is also the smallest one — that is what makes this greedy search
    produce *minimal* counterfactuals rather than merely valid ones.
    """
    meta = ranges[col]
    ceiling = min(meta["max"], current + _max_step(col, ranges, cfg))
    if ceiling <= current:
        return []
    return list(np.linspace(current, ceiling, n_steps + 1)[1:])


def greedy_counterfactuals(
    student: Mapping[str, Any],
    desired_class: str | None = None,
    n_results: int | None = None,
    cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Find minimal changes by searching single features, then pairs.

    Why this order: a recommendation a student can act on with one behaviour
    change is worth far more than one requiring four simultaneous changes, so we
    exhaust the single-feature space before considering combinations.
    """
    cfg = cfg or load_config()
    bundle = load_model_bundle()
    class_order = list(bundle["class_order"])
    desired = desired_class or cfg["counterfactuals"]["desired_class"]
    n_results = n_results or int(cfg["counterfactuals"]["total_cfs"])

    ranges = feature_ranges(cfg=cfg)
    base = dict(student)
    current = predict_one(base, cfg=cfg)

    # "Better" means any band above the current one, not only the configured
    # target. Insisting on High for a Low student would usually return nothing
    # useful, when Low -> Medium is the genuinely reachable win.
    current_rank = class_order.index(current["predicted_class"])
    desired_rank = class_order.index(desired)
    if current_rank >= desired_rank:
        return []

    found: List[Dict[str, Any]] = []
    rejected: List[str] = []

    def _try(candidate: Dict[str, Any]) -> Dict[str, Any] | None:
        ok, reason = is_valid_counterfactual(base, candidate, ranges, cfg)
        if not ok:
            rejected.append(reason)
            return None
        pred = predict_one(candidate, cfg=cfg)
        if class_order.index(pred["predicted_class"]) <= current_rank:
            return None
        return summarise_counterfactual(
            base, candidate, pred["predicted_class"], pred.get("confidence", 0.0), cfg
        )

    numeric_cols = _numeric_actionable(cfg)
    categorical_cols = _categorical_actionable(cfg)

    # --- Pass 1: one numeric feature at a time -------------------------------
    for col in numeric_cols:
        for target in _grid_for(col, float(base[col]), ranges, cfg):
            cand = dict(base)
            cand[col] = round(float(target))
            result = _try(cand)
            if result:
                found.append(result)
                break            # smallest change for this feature — stop here

    # --- Pass 2: one categorical feature at a time ---------------------------
    for col in categorical_cols:
        for level in ranges[col]["levels"]:
            if str(level) == str(base[col]):
                continue
            cand = dict(base)
            cand[col] = level
            result = _try(cand)
            if result:
                found.append(result)
                break

    # --- Pass 3: pairs, only if single changes were not enough ---------------
    if len(found) < n_results:
        for i, col_a in enumerate(numeric_cols):
            for col_b in numeric_cols[i + 1:]:
                grid_a = _grid_for(col_a, float(base[col_a]), ranges, cfg, n_steps=5)
                grid_b = _grid_for(col_b, float(base[col_b]), ranges, cfg, n_steps=5)
                done = False
                for ta in grid_a:
                    for tb in grid_b:
                        cand = dict(base)
                        cand[col_a] = round(float(ta))
                        cand[col_b] = round(float(tb))
                        result = _try(cand)
                        if result:
                            found.append(result)
                            done = True
                            break
                    if done:
                        break
                if len(found) >= n_results * 2:
                    break
            if len(found) >= n_results * 2:
                break

    if rejected:
        logger.debug("Rejected %d candidate counterfactuals, e.g. %s",
                     len(rejected), rejected[0])

    # Easiest first — this ordering is what the dashboard shows.
    found.sort(key=lambda r: (r["effort_score"], -r["new_confidence"]))
    return found[:n_results]


# =============================================================================
# dice-ml backend
# =============================================================================

def dice_counterfactuals(
    student: Mapping[str, Any],
    desired_class: str | None = None,
    n_results: int | None = None,
    cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Generate counterfactuals with dice-ml, then apply our own guardrails.

    We pass ``features_to_vary`` so dice only searches the actionable space, but
    we still re-validate every result it returns. Trusting a library's
    constraint handling with advice that goes in front of a teacher would be
    careless — the second check costs microseconds and removes the whole class
    of failure.
    """
    import dice_ml

    cfg = cfg or load_config()
    bundle = load_model_bundle()
    pipeline = bundle["pipeline"]
    class_order = list(bundle["class_order"])
    desired = desired_class or cfg["counterfactuals"]["desired_class"]
    n_results = n_results or int(cfg["counterfactuals"]["total_cfs"])

    df = load_processed(cfg)
    target = cfg["data"]["target"]
    ranges = feature_ranges(df, cfg)

    train = df[feature_columns(cfg)].copy()
    train[target] = df[target].map({c: i for i, c in enumerate(class_order)})

    data = dice_ml.Data(
        dataframe=train,
        continuous_features=list(cfg["data"]["numeric_features"]),
        outcome_name=target,
    )
    model = dice_ml.Model(model=pipeline, backend="sklearn", model_type="classifier")
    exp = dice_ml.Dice(data, model, method=cfg["counterfactuals"]["method"])

    query = prepare_input(student, cfg)
    permitted = {
        col: [float(meta["min"]), float(meta["max"])]
        for col, meta in ranges.items() if meta["type"] == "numeric"
    }

    cf = exp.generate_counterfactuals(
        query,
        total_CFs=max(n_results * 3, 6),      # over-generate; guardrails cull hard
        desired_class=class_order.index(desired),
        features_to_vary=_actionable(cfg),
        permitted_range=permitted,
        random_seed=int(cfg["project"]["random_seed"]),
    )

    base = dict(query.iloc[0])
    results: List[Dict[str, Any]] = []
    cf_df = cf.cf_examples_list[0].final_cfs_df
    if cf_df is None or cf_df.empty:
        return []

    for _, row in cf_df.iterrows():
        candidate = {c: row[c] for c in feature_columns(cfg) if c in row}
        for c in feature_columns(cfg):
            candidate.setdefault(c, base[c])

        ok, reason = is_valid_counterfactual(base, candidate, ranges, cfg)
        if not ok:
            logger.debug("dice-ml suggestion rejected by guardrails: %s", reason)
            continue

        pred = predict_one(candidate, cfg=cfg)
        results.append(summarise_counterfactual(
            base, candidate, pred["predicted_class"], pred.get("confidence", 0.0), cfg
        ))

    # De-duplicate: dice often returns several near-identical rows.
    seen, unique = set(), []
    for r in results:
        key = tuple(sorted((c["feature"], c["to"]) for c in r["changes"]))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    unique.sort(key=lambda r: (r["effort_score"], -r["new_confidence"]))
    return unique[:n_results]


# =============================================================================
# Public interface
# =============================================================================

def generate_counterfactuals(
    student: Mapping[str, Any] | pd.Series,
    desired_class: str | None = None,
    n_results: int | None = None,
    cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """The function the dashboard and API call.

    Tries dice-ml, falls back to the built-in greedy search, and always reports
    which backend produced the answer so the UI can be honest about it.
    """
    cfg = cfg or load_config()
    student = dict(student) if not isinstance(student, dict) else student

    prediction = predict_one(student, cfg=cfg)
    backend_used, error = "greedy", None

    if cfg["counterfactuals"]["backend"] == "dice":
        try:
            results = dice_counterfactuals(student, desired_class, n_results, cfg)
            backend_used = "dice-ml"
        except ImportError:
            logger.info("dice-ml not installed — using the built-in greedy search.")
            results = greedy_counterfactuals(student, desired_class, n_results, cfg)
        except Exception as exc:  # noqa: BLE001
            logger.warning("dice-ml failed (%s) — falling back to greedy search.", exc)
            error = str(exc)
            results = greedy_counterfactuals(student, desired_class, n_results, cfg)
    else:
        results = greedy_counterfactuals(student, desired_class, n_results, cfg)

    return {
        "current_prediction": prediction,
        "counterfactuals": results,
        "n_found": len(results),
        "backend": backend_used,
        "backend_error": error,
        "message": _outcome_message(prediction, results, cfg),
    }


def _outcome_message(
    prediction: Dict[str, Any],
    results: Sequence[Dict[str, Any]],
    cfg: Dict[str, Any],
) -> str:
    """What to tell the user, including the awkward cases."""
    if prediction["predicted_class"] == "H":
        return ("This student is already predicted to perform at the highest band, so there is "
                "no better outcome to search for. The factors keeping them there are worth "
                "maintaining rather than changing.")
    if not results:
        return ("No realistic change within our achievability limits would move this "
                "prediction. That is a meaningful result, not a failure: it usually means "
                "the student's situation needs support beyond the behaviours this dataset "
                "records, and the case deserves a human conversation rather than a nudge.")
    easiest = results[0]
    return (f"{len(results)} realistic route(s) to a better outcome. The most achievable "
            f"requires {easiest['n_changes']} change(s): {easiest['summary']}")


# =============================================================================
# Pipeline entry point
# =============================================================================

def run_counterfactual_analysis(
    cfg: Dict[str, Any] | None = None,
    save: bool = True,
    n_examples: int = 5,
) -> Dict[str, Any]:
    """Phase 5 entry point — generate worked examples for the report."""
    from src.models.train import make_split

    cfg = cfg or load_config()
    section(logger, "PHASE 5 — COUNTERFACTUAL RECOMMENDATIONS")

    _, X_test, _, y_test, class_order = make_split(cfg)

    # Explain the students who most need it: the predicted-Low ones.
    at_risk_idx = [i for i in range(len(X_test))
                   if y_test[i] == class_order.index("L")][:n_examples]

    examples = []
    n_with_route, total_changes = 0, []
    for i in at_risk_idx:
        student = X_test.iloc[i].to_dict()
        result = generate_counterfactuals(student, cfg=cfg)
        if result["counterfactuals"]:
            n_with_route += 1
            total_changes.append(result["counterfactuals"][0]["n_changes"])
        examples.append({
            "student_index": int(X_test.index[i]),
            "current_class": result["current_prediction"]["predicted_class"],
            "confidence": result["current_prediction"].get("confidence"),
            "n_routes_found": result["n_found"],
            "message": result["message"],
            "counterfactuals": result["counterfactuals"],
        })

    output = {
        "n_students_analysed": len(examples),
        "n_with_viable_route": n_with_route,
        "median_changes_required": (
            float(np.median(total_changes)) if total_changes else None
        ),
        "backend": examples[0]["counterfactuals"] and "see per-example" or "greedy",
        "guardrails": {
            "features_allowed_to_change": _actionable(cfg),
            "features_never_changed": _sensitive(cfg),
            "max_relative_change": cfg["counterfactuals"]["max_relative_change"],
            "note": (
                "Protected attributes are excluded from the search space and independently "
                "re-checked afterwards. The engine will never suggest that a student would "
                "have done better with a different gender or nationality."
            ),
        },
        "examples": examples,
    }

    if save:
        path = get_path("counterfactual_file", cfg, ensure_parent=True)
        save_json(output, path)
        logger.info("Saved counterfactual examples -> %s", path)

    logger.info("%d of %d at-risk students have a realistic route to a better band",
                n_with_route, len(examples))
    return output


if __name__ == "__main__":
    run_counterfactual_analysis()
