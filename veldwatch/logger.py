"""Structured event logging for agent runs."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Custom TRACE level (below DEBUG=10)
TRACE = 5
logging.addLevelName(TRACE, "TRACE")


class StructuredFormatter(logging.Formatter):
    """Outputs log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        # Merge extra structured fields
        extra: dict[str, Any] | None = getattr(record, "structured", None)
        if extra:
            entry["data"] = extra
        if record.exc_info and record.exc_info[1]:
            entry["error"] = str(record.exc_info[1])
        return json.dumps(entry, default=str)


def get_logger(
    name: str = "veldwatch",
    *,
    level: int | str = logging.INFO,
    file_path: str | Path | None = None,
    structured: bool = True,
) -> logging.Logger:
    """Create or retrieve a Veldwatch logger.

    Args:
        name: Logger name.
        level: Log level (int or string like "INFO", "TRACE").
        file_path: Optional file sink for log output.
        structured: If True, use JSON formatter; otherwise use plain text.

    Returns:
        A configured logging.Logger.
    """
    logger = logging.getLogger(name)

    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
        if isinstance(level, str):  # getLevelName returns str if unknown
            level = logging.INFO
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter: logging.Formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if file_path:
        file_handler = logging.FileHandler(str(file_path))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


class EventLogger:
    """High-level helper that logs structured agent events."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or get_logger()

    def trace(self, message: str, **data: Any) -> None:
        self._log(TRACE, message, data)

    def info(self, message: str, **data: Any) -> None:
        self._log(logging.INFO, message, data)

    def warn(self, message: str, **data: Any) -> None:
        self._log(logging.WARNING, message, data)

    def error(self, message: str, **data: Any) -> None:
        self._log(logging.ERROR, message, data)

    def _log(self, level: int, message: str, data: dict[str, Any]) -> None:
        if not self._logger.isEnabledFor(level):
            return
        record = self._logger.makeRecord(
            name=self._logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        if data:
            record.structured = data  # type: ignore[attr-defined]
        self._logger.handle(record)
