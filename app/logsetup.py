"""Application file logger setup.

Creates ./log directory at runtime (if missing) and configures a singleton
`logging.Logger` with both console and rotating file handlers.
"""
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
import atexit
from pathlib import Path
import os
from typing import Optional
from datetime import datetime

_LOGGER: Optional[logging.Logger] = None

# Counters
USER_WARN_COUNT = 0
USER_ERROR_COUNT = 0
PY_WARN_COUNT = 0
PY_ERROR_COUNT = 0
_SUMMARY_WRITTEN = False

DEFAULT_LOG_DIR = Path(os.getenv("LOG_DIR", "log"))
# Defer dynamic file naming until logger init; placeholder if user forces name.
DEFAULT_LOG_FILE = os.getenv("LOG_FILE", "")
DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

FORMAT = "%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "FonDeDeNaJa") -> logging.Logger:
    """Return a configured singleton logger.

    Creates directory, attaches handlers only once, and reuses across imports.
    """
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    # Avoid duplicate handlers if reconfigured
    if logger.handlers:
        _LOGGER = logger
        return logger

    level = getattr(logging, DEFAULT_LEVEL, logging.INFO)
    logger.setLevel(level)

    # Decide filename: use provided LOG_FILE or generate timestamped name.
    if os.getenv("LOG_FILE"):
        chosen = os.getenv("LOG_FILE")
    else:
        chosen = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        # Persist so other modules can discover it
        os.environ["LOG_FILE"] = chosen
    os.environ["ACTIVE_LOG_FILE"] = chosen
    file_path = DEFAULT_LOG_DIR / chosen

    # File handler (size-based rotation)
    f_handler = RotatingFileHandler(file_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    c_handler = logging.StreamHandler()

    class _CountHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
            global PY_WARN_COUNT, PY_ERROR_COUNT
            if record.levelno == logging.WARNING:
                PY_WARN_COUNT += 1
            elif record.levelno >= logging.ERROR:
                PY_ERROR_COUNT += 1

    count_handler = _CountHandler()
    count_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter(FORMAT, DATEFMT)
    f_handler.setFormatter(formatter)
    c_handler.setFormatter(formatter)

    logger.addHandler(f_handler)
    logger.addHandler(c_handler)
    logger.addHandler(count_handler)
    logger.propagate = False

    _LOGGER = logger
    logger.debug("Logger initialized (file=%s level=%s)", file_path, DEFAULT_LEVEL)
    return logger


def inc_user_warning():  # Increment user-defined warning count
    global USER_WARN_COUNT
    USER_WARN_COUNT += 1


def inc_user_error():  # Increment user-defined error count
    global USER_ERROR_COUNT
    USER_ERROR_COUNT += 1


def _write_summary() -> None:
    global _SUMMARY_WRITTEN
    if _SUMMARY_WRITTEN:
        return
    lg = get_logger()
    lg.info("--- SESSION SUMMARY ---")
    lg.info("User-defined warnings: %s", USER_WARN_COUNT)
    lg.info("User-defined errors: %s", USER_ERROR_COUNT)
    lg.info("Python logger warnings: %s", PY_WARN_COUNT)
    lg.info("Python logger errors: %s", PY_ERROR_COUNT)
    _SUMMARY_WRITTEN = True


def flush_summary():  # Allow manual flush before process exit
    _write_summary()


atexit.register(_write_summary)


def enable_debug() -> None:
    """Elevate logger level to DEBUG at runtime."""
    lg = get_logger()
    lg.setLevel(logging.DEBUG)
    lg.debug("Logging level elevated to DEBUG")


def log_exception(msg: str = "Unhandled exception"):
    """Decorator: log exceptions with stack trace and re-raise."""
    def deco(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                get_logger().exception("%s: %s", msg, e)
                raise
        return wrapper
    return deco
