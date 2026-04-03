"""Backend storage abstraction — SQLite (dev) and PostgreSQL (prod)."""

from __future__ import annotations

import json
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class BaseStore(ABC):
    """Abstract interface for persisting runs and events."""

    @abstractmethod
    def save_run(self, run: dict[str, Any]) -> None: ...

    @abstractmethod
    def update_run(self, run_id: str, updates: dict[str, Any]) -> None: ...

    @abstractmethod
    def get_run(self, run_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def list_runs(
        self, *, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    def save_event(self, event: dict[str, Any]) -> None: ...

    @abstractmethod
    def list_events(self, run_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def save_alert(self, alert: dict[str, Any]) -> None: ...

    @abstractmethod
    def list_alerts(
        self, *, resolved: bool | None = None, limit: int = 50
    ) -> list[dict[str, Any]]: ...


_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    agent_id    TEXT,
    status      TEXT NOT NULL DEFAULT 'running',
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    metadata    TEXT,
    error       TEXT
);

CREATE TABLE IF NOT EXISTS events (
    event_id    TEXT PRIMARY KEY,
    run_id      TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    latency_ms  REAL,
    payload     TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id    TEXT PRIMARY KEY,
    run_id      TEXT,
    rule_name   TEXT NOT NULL,
    message     TEXT NOT NULL,
    severity    TEXT NOT NULL DEFAULT 'warning',
    triggered_at TEXT NOT NULL,
    resolved    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_events_run_id ON events(run_id);
CREATE INDEX IF NOT EXISTS idx_alerts_run_id ON alerts(run_id);
"""


class SQLiteStore(BaseStore):
    """Thread-safe SQLite storage backend."""

    def __init__(self, db_path: str | Path = "veldwatch.db") -> None:
        self._db_path = str(db_path)
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn: sqlite3.Connection | None = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript(_SCHEMA)
        conn.commit()

    # -- Runs --

    def save_run(self, run: dict[str, Any]) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO runs (run_id, agent_id, status, started_at, metadata) "
            "VALUES (:run_id, :agent_id, :status, :started_at, :metadata)",
            {
                "run_id": run["run_id"],
                "agent_id": run.get("agent_id"),
                "status": run.get("status", "running"),
                "started_at": run.get(
                    "started_at", datetime.now(UTC).isoformat()
                ),
                "metadata": json.dumps(run.get("metadata")) if run.get("metadata") else None,
            },
        )
        conn.commit()

    def update_run(self, run_id: str, updates: dict[str, Any]) -> None:
        allowed = {"status", "ended_at", "error", "metadata"}
        fields = {k: v for k, v in updates.items() if k in allowed}
        if not fields:
            return
        if "metadata" in fields and not isinstance(fields["metadata"], str):
            fields["metadata"] = json.dumps(fields["metadata"])
        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        fields["run_id"] = run_id
        conn = self._get_conn()
        conn.execute(f"UPDATE runs SET {set_clause} WHERE run_id = :run_id", fields)
        conn.commit()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def list_runs(
        self, *, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY started_at DESC, rowid DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    # -- Events --

    def save_event(self, event: dict[str, Any]) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO events (event_id, run_id, event_type, timestamp, latency_ms, payload) "
            "VALUES (:event_id, :run_id, :event_type, :timestamp, :latency_ms, :payload)",
            {
                "event_id": event["event_id"],
                "run_id": event["run_id"],
                "event_type": event["event_type"],
                "timestamp": event.get(
                    "timestamp", datetime.now(UTC).isoformat()
                ),
                "latency_ms": event.get("latency_ms"),
                "payload": json.dumps(event.get("payload")) if event.get("payload") else None,
            },
        )
        conn.commit()

    def list_events(self, run_id: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM events WHERE run_id = ? ORDER BY timestamp ASC",
            (run_id,),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    # -- Alerts --

    def save_alert(self, alert: dict[str, Any]) -> None:
        conn = self._get_conn()
        cols = "alert_id, run_id, rule_name, message, severity, triggered_at, resolved"
        vals = ":alert_id, :run_id, :rule_name, :message, :severity, :triggered_at, :resolved"
        conn.execute(
            f"INSERT INTO alerts ({cols}) VALUES ({vals})",
            {
                "alert_id": alert["alert_id"],
                "run_id": alert.get("run_id"),
                "rule_name": alert["rule_name"],
                "message": alert["message"],
                "severity": alert.get("severity", "warning"),
                "triggered_at": alert.get(
                    "triggered_at", datetime.now(UTC).isoformat()
                ),
                "resolved": 1 if alert.get("resolved") else 0,
            },
        )
        conn.commit()

    def list_alerts(
        self, *, resolved: bool | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if resolved is None:
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY triggered_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE resolved = ? ORDER BY triggered_at DESC LIMIT ?",
                (1 if resolved else 0, limit),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    # -- Helpers --

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        for key in ("metadata", "payload"):
            if key in d and isinstance(d[key], str):
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        if "resolved" in d:
            d["resolved"] = bool(d["resolved"])
        return d
