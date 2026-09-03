"""
Configuration and path handling.

Everything in this project reads its settings from ``config/config.yaml``.
This module is the only place that knows where that file lives, and the only
place that turns the relative paths inside it into real absolute paths.

Why bother with a module for this?
    Because scripts get run from all sorts of places — the project root, the
    ``notebooks/`` folder, Streamlit Cloud, a Render container. If we used
    plain relative paths like ``"data/raw/..."`` they would silently resolve
    against whatever the current working directory happens to be and break.
    ``PROJECT_ROOT`` is computed from *this file's own location*, so it is
    correct no matter where Python was launched from.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

# src/utils/config.py -> src/utils -> src -> <project root>
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
CONFIG_PATH: Path = PROJECT_ROOT / "config" / "config.yaml"


@lru_cache(maxsize=1)
def load_config(config_path: str | os.PathLike[str] | None = None) -> Dict[str, Any]:
    """Load ``config/config.yaml`` into a plain dictionary.

    The result is cached, so calling this a hundred times across a dashboard
    session costs one file read. Pass an explicit ``config_path`` in tests when
    you want to load a different config without polluting the cache.
    """
    path = Path(config_path) if config_path is not None else CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. Expected it at <project root>/config/config.yaml"
        )
    with path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict):
        raise ValueError(f"Config at {path} did not parse into a mapping.")
    return cfg


def resolve_path(relative_path: str, ensure_parent: bool = False) -> Path:
    """Turn a config-relative path into an absolute one.

    ``resolve_path("data/processed/cleaned.csv")`` always points at the same
    file regardless of the current working directory.

    Args:
        relative_path: A path as written in ``config.yaml``.
        ensure_parent: If True, create the parent directory if it is missing.
                       Handy right before writing an output file.
    """
    path = Path(relative_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if ensure_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_path(key: str, cfg: Dict[str, Any] | None = None, ensure_parent: bool = False) -> Path:
    """Look up ``paths.<key>`` in the config and resolve it to an absolute path."""
    cfg = cfg or load_config()
    paths = cfg.get("paths", {})
    if key not in paths:
        raise KeyError(f"'{key}' is not defined under 'paths:' in config.yaml")
    return resolve_path(paths[key], ensure_parent=ensure_parent)


def get_seed(cfg: Dict[str, Any] | None = None) -> int:
    """The single random seed used across splits, models, bootstrap and simulation."""
    cfg = cfg or load_config()
    return int(cfg["project"]["random_seed"])


def save_json(obj: Any, path: str | os.PathLike[str], indent: int = 2) -> Path:
    """Write a JSON artifact, creating parent directories as needed.

    Every analysis stage in this project dumps its results to JSON under
    ``reports/artifacts/``. The report and the slide deck are then generated
    *from those JSON files* rather than from numbers typed by hand — which means
    the document can never drift out of sync with the code that produced it.
    """
    out = Path(path)
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, default=_json_fallback)
    return out


def load_json(path: str | os.PathLike[str]) -> Any:
    """Read back a JSON artifact written by :func:`save_json`."""
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _json_fallback(obj: Any) -> Any:
    """Make numpy scalars and Paths JSON-serialisable.

    ``json`` chokes on ``numpy.int64`` and friends, which appear constantly when
    you serialise pandas output. This keeps the call sites clean.
    """
    if hasattr(obj, "item"):          # numpy scalar types
        try:
            return obj.item()
        except Exception:  # pragma: no cover - defensive
            pass
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "tolist"):        # numpy arrays
        return obj.tolist()
    return str(obj)


def friendly(name: str, cfg: Dict[str, Any] | None = None) -> str:
    """Translate a raw column name into human-readable text.

    ``friendly("VisITedResources")`` -> ``"Learning resources opened"``.
    Used everywhere the output is read by a student or teacher rather than by
    an engineer.
    """
    cfg = cfg or load_config()
    return cfg["data"].get("friendly_names", {}).get(name, name)


def class_label(code: str, cfg: Dict[str, Any] | None = None) -> str:
    """Map the raw target code to its word: ``"H"`` -> ``"High"``."""
    cfg = cfg or load_config()
    return cfg["data"].get("target_labels", {}).get(code, code)
