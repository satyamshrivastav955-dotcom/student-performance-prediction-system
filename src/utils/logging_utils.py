"""Small logging helper so every script prints in the same readable format."""

from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "spps", level: int = logging.INFO) -> logging.Logger:
    """Return a console logger with a consistent format.

    Configured once per process — repeated calls reuse the same handler instead
    of stacking duplicates (a classic cause of every log line printing twice).
    """
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
        )
        root = logging.getLogger("spps")
        root.handlers.clear()
        root.addHandler(handler)
        root.setLevel(level)
        root.propagate = False
        _CONFIGURED = True
    logger.setLevel(level)
    return logger


def section(logger: logging.Logger, title: str) -> None:
    """Print a visual divider so long pipeline runs stay skimmable."""
    logger.info("")
    logger.info("=" * 72)
    logger.info(title)
    logger.info("=" * 72)
