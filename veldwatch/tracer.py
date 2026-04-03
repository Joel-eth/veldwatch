"""Agent run tracing — captures the full sequence of steps in a run."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime
from typing import Any

from veldwatch.store import BaseStore


class Tracer:
    """Manages the lifecycle of a single agent run and its events."""

    def __init__(
        self,
        store: BaseStore,
        agent_id: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.store = store
        self.agent_id = agent_id
        self.run_id = run_id or uuid.uuid4().hex
        self.metadata = metadata
        self._started = False
        self._ended = False

    def start_run(self) -> str:
        """Open a new run. Returns the run_id."""
        if self._started:
            return self.run_id
        self.store.save_run(
            {
                "run_id": self.run_id,
                "agent_id": self.agent_id,
                "status": "running",
                "started_at": datetime.now(UTC).isoformat(),
                "metadata": self.metadata,
            }
        )
        self._started = True
        return self.run_id

    def end_run(self, *, status: str = "completed", error: str | None = None) -> None:
        """Close the current run."""
        if self._ended:
            return
        updates: dict[str, Any] = {
            "status": status,
            "ended_at": datetime.now(UTC).isoformat(),
        }
        if error:
            updates["error"] = error
        self.store.update_run(self.run_id, updates)
        self._ended = True

    def add_event(
        self,
        event_type: str,
        *,
        payload: dict[str, Any] | None = None,
        latency_ms: float | None = None,
    ) -> str:
        """Append an event to the current run. Returns event_id."""
        event_id = uuid.uuid4().hex
        self.store.save_event(
            {
                "event_id": event_id,
                "run_id": self.run_id,
                "event_type": event_type,
                "timestamp": datetime.now(UTC).isoformat(),
                "latency_ms": latency_ms,
                "payload": payload,
            }
        )
        return event_id

    def trace_call(self, event_type: str = "tool_call"):
        """Context manager that times a block and records it as an event.

        Usage:
            with tracer.trace_call("llm_call") as ctx:
                result = call_llm(prompt)
                ctx["payload"] = {"model": "gpt-4", "tokens": 150}
        """
        return _TraceCallContext(self, event_type)


class _TraceCallContext:
    """Context manager returned by Tracer.trace_call()."""

    def __init__(self, tracer: Tracer, event_type: str) -> None:
        self._tracer = tracer
        self._event_type = event_type
        self._data: dict[str, Any] = {}
        self._start: float = 0.0

    def __enter__(self) -> dict[str, Any]:
        self._start = time.perf_counter()
        return self._data

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        payload = self._data.get("payload")
        if exc_val is not None:
            payload = payload or {}
            payload["error"] = str(exc_val)
        self._tracer.add_event(
            self._event_type, payload=payload, latency_ms=elapsed_ms
        )
