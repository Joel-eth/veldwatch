"""Shared dependencies for the API."""

from __future__ import annotations

import os
from functools import lru_cache

from veldwatch.store import BaseStore, SQLiteStore


@lru_cache
def get_store() -> BaseStore:
    db_url = os.environ.get("VELDWATCH_DB_URL", "sqlite:///./veldwatch.db")
    # Extract path from sqlite:/// prefix
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        db_path = "veldwatch.db"
    return SQLiteStore(db_path)
