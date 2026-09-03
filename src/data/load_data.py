"""
Data loading and schema validation.

Module 1 of the brief ("Data Collection & Preprocessing") starts here. This
file is deliberately dumb: it *loads* and *validates*, it does not clean.
Cleaning lives in :mod:`src.data.preprocess`. Keeping the two apart means a
schema failure is never confused with a cleaning bug.

Dataset: xAPI-Edu-Data — "Students' Academic Performance Dataset"
(Amrieh, Hamtini & Aljarah, 2016). 480 students, 16 features, and a target
``Class`` that is already L / M / H.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from src.utils.config import get_path, load_config
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# The dataset ships with some awkward column names (mixed casing, typos like
# "NationalITy"). We keep the original names so the code matches the public
# dataset exactly and anyone cross-checking against Kaggle sees the same thing —
# but we normalise a couple of known variants that appear in some mirrors.
COLUMN_ALIASES: Dict[str, str] = {
    "Nationality": "NationalITy",
    "nationality": "NationalITy",
    "raisedHands": "raisedhands",
    "RaisedHands": "raisedhands",
    "VisitedResources": "VisITedResources",
    "gender ": "gender",
}


def load_raw_data(path: str | Path | None = None, cfg: Dict[str, Any] | None = None) -> pd.DataFrame:
    """Read the raw CSV from disk.

    Args:
        path: Override the configured location. Mostly useful in tests.
        cfg:  Pre-loaded config dict (avoids re-reading the YAML).

    Raises:
        FileNotFoundError: with an actionable message telling the user exactly
            where to put the file. A vague "file not found" is the single most
            common way a data project wastes someone's afternoon.
    """
    cfg = cfg or load_config()
    csv_path = Path(path) if path is not None else get_path("raw_data", cfg)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at:\n    {csv_path}\n\n"
            "Download 'Students' Academic Performance Dataset' (xAPI-Edu-Data.csv) "
            "from Kaggle and place it at that exact path, then re-run."
        )

    df = pd.read_csv(csv_path)
    df = _normalise_columns(df)
    logger.info("Loaded raw dataset: %d rows x %d columns from %s", len(df), df.shape[1], csv_path.name)
    return df


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip stray whitespace from headers and fix known naming variants."""
    df = df.rename(columns=lambda c: c.strip())
    renames = {c: COLUMN_ALIASES[c] for c in df.columns if c in COLUMN_ALIASES}
    if renames:
        logger.info("Normalised column names: %s", renames)
        df = df.rename(columns=renames)
    return df


def expected_columns(cfg: Dict[str, Any] | None = None) -> List[str]:
    """Every column the rest of the pipeline expects to exist."""
    cfg = cfg or load_config()
    d = cfg["data"]
    return (
        list(d["numeric_features"])
        + list(d["nominal_features"])
        + list(d["binary_features"].keys())
        + [d["target"]]
    )


def validate_schema(
    df: pd.DataFrame, cfg: Dict[str, Any] | None = None, strict: bool = True
) -> Dict[str, Any]:
    """Check the loaded frame actually looks like the dataset we planned for.

    This is the Phase-1 checkpoint. It answers four questions:
      1. Are all expected columns present?
      2. Are the numeric engagement counters actually numeric and in 0-100?
      3. Does the target contain only the three expected class codes?
      4. Do the binary columns contain only their two documented levels?

    Args:
        strict: raise on failure. Set False to get a report back and decide
            what to do yourself (the dashboard prefers a warning to a crash).

    Returns:
        A dict report suitable for dumping to JSON alongside the cleaned data.
    """
    cfg = cfg or load_config()
    d = cfg["data"]
    problems: List[str] = []
    warnings: List[str] = []

    # --- 1. presence ---------------------------------------------------------
    missing = [c for c in expected_columns(cfg) if c not in df.columns]
    if missing:
        problems.append(f"Missing expected columns: {missing}")

    # --- 2. numeric ranges ---------------------------------------------------
    numeric_report: Dict[str, Any] = {}
    for col in d["numeric_features"]:
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            problems.append(f"Column '{col}' should be numeric but is {df[col].dtype}.")
            continue
        lo, hi = float(df[col].min()), float(df[col].max())
        numeric_report[col] = {"min": lo, "max": hi, "mean": round(float(df[col].mean()), 2)}
        if lo < 0 or hi > 100:
            warnings.append(f"'{col}' has values outside the documented 0-100 range ({lo}-{hi}).")

    # --- 3. target -----------------------------------------------------------
    target = d["target"]
    target_report: Dict[str, Any] = {}
    if target in df.columns:
        found = set(df[target].dropna().unique())
        allowed = set(d["target_classes"])
        unexpected = found - allowed
        if unexpected:
            problems.append(f"Target '{target}' contains unexpected values: {sorted(unexpected)}")
        target_report = {str(k): int(v) for k, v in df[target].value_counts().items()}

    # --- 4. binary levels ----------------------------------------------------
    binary_report: Dict[str, Any] = {}
    for col, mapping in d["binary_features"].items():
        if col not in df.columns:
            continue
        found = set(df[col].dropna().unique())
        allowed = set(mapping.keys())
        binary_report[col] = sorted(str(x) for x in found)
        if not found.issubset(allowed):
            problems.append(
                f"Column '{col}' has values {sorted(found - allowed)} that are not in the "
                f"configured mapping {sorted(allowed)}."
            )

    report: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns": list(df.columns),
        "missing_values_total": int(df.isna().sum().sum()),
        "missing_by_column": {k: int(v) for k, v in df.isna().sum().items() if v > 0},
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": numeric_report,
        "class_distribution": target_report,
        "binary_levels": binary_report,
        "problems": problems,
        "warnings": warnings,
        "passed": len(problems) == 0,
    }

    for w in warnings:
        logger.warning(w)

    if problems and strict:
        raise ValueError("Schema validation failed:\n  - " + "\n  - ".join(problems))

    logger.info(
        "Schema check %s | %d rows, %d cols, %d nulls, %d duplicate rows",
        "PASSED" if report["passed"] else "FAILED",
        report["n_rows"],
        report["n_columns"],
        report["missing_values_total"],
        report["exact_duplicate_rows"],
    )
    return report


def load_and_validate(
    path: str | Path | None = None, cfg: Dict[str, Any] | None = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Convenience wrapper: load the CSV and immediately validate it."""
    cfg = cfg or load_config()
    df = load_raw_data(path, cfg)
    report = validate_schema(df, cfg, strict=True)
    return df, report


if __name__ == "__main__":  # pragma: no cover - manual smoke check
    frame, rep = load_and_validate()
    print(frame.head())
    print(rep)
