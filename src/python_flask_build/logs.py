"""Logging to stdout as text or JSON lines; containers collect stdout, so nothing writes files."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from python_flask_build.config import LogFormat

# Attributes every LogRecord has; anything else came through `extra=` and is logged as a field.
_RESERVED = frozenset(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update({k: v for k, v in vars(record).items() if k not in _RESERVED})
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


class TextFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(asctime)s %(levelname)-8s %(name)s: %(message)s")

    def formatMessage(self, record: logging.LogRecord) -> str:
        # Fields go on the message line, before any traceback format() appends.
        line = super().formatMessage(record)
        fields = " ".join(f"{k}={v}" for k, v in vars(record).items() if k not in _RESERVED)
        return f"{line} {fields}" if fields else line


class _AppHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """Marks the handler configure_logging owns, so a second call replaces it and nothing else."""


def configure_logging(level: str, fmt: LogFormat) -> None:
    """Send root logging to stdout. Idempotent; handlers others installed (pytest, a host) stay."""
    handler = _AppHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if fmt == "json" else TextFormatter())
    root = logging.getLogger()
    for old in [h for h in root.handlers if isinstance(h, _AppHandler)]:
        root.removeHandler(old)
    root.addHandler(handler)
    root.setLevel(level)
