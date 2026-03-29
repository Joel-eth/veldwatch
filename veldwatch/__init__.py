"""Veldwatch — AI agent observability and oversight platform."""

__version__ = "0.1.0"

from veldwatch.alert import AlertEngine, AlertRule
from veldwatch.logger import EventLogger, get_logger
from veldwatch.store import BaseStore, SQLiteStore
from veldwatch.tracer import Tracer
from veldwatch.watcher import Watcher

__all__ = [
    "AlertEngine",
    "AlertRule",
    "BaseStore",
    "EventLogger",
    "SQLiteStore",
    "Tracer",
    "Watcher",
    "get_logger",
]
