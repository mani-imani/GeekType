"""Logging to ``~/.local/state/geektype/geektype.log`` (small, rotated)."""

from __future__ import annotations

import logging
import logging.handlers
import os


def log_file() -> str:
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(os.path.expanduser("~"), ".local", "state")
    return os.path.join(base, "geektype", "geektype.log")


def setup(verbose: bool = False) -> None:
    logger = logging.getLogger("geektype")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    if logger.handlers:
        return
    try:
        path = log_file()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(path, maxBytes=200000, backupCount=1, encoding="utf-8")
    except OSError:
        handler = logging.NullHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
