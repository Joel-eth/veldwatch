"""SDK decorators — @watch and @trace for instrumenting agent functions."""

from __future__ import annotations

import functools
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from veldwatch.store import BaseStore, SQLiteStore

# Module-level default store (lazy singleton)
_default_store: BaseStore | None = None


def get_default_store() -> BaseStore:
    global _default_store
    if _default_store is None:
        _default_store = SQLiteStore()
    return _default_store


def set_default_store(store: BaseStore) -> None:
    global _default_store
    _default_store = store


def watch(
    agent_id: str | None = None,
    *,
    store: BaseStore | None = None,
) -> Callable[..., Any]:
    """Decorator that wraps an agent function to capture run-level telemetry.

    Creates a Run when the function is called, records start/end/errors,
    and stores everything via the configured store.

    Usage:
        @watch(agent_id="my-agent")
        def run_agent(prompt):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _store = store or get_default_store()
            run_id = uuid.uuid4().hex
            started_at = datetime.now(UTC).isoformat()

            _store.save_run(
                {
                    "run_id": run_id,
                    "agent_id": agent_id or func.__name__,
                    "status": "running",
                    "started_at": started_at,
                    "metadata": {"function": func.__qualname__},
                }
            )

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                _store.update_run(
                    run_id,
                    {
                        "status": "completed",
                        "ended_at": datetime.now(UTC).isoformat(),
                    },
                )
                _store.save_event(
                    {
                        "event_id": uuid.uuid4().hex,
                        "run_id": run_id,
                        "event_type": "run_completed",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "latency_ms": elapsed,
                        "payload": None,
                    }
                )
                return result
            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000
                _store.update_run(
                    run_id,
                    {
                        "status": "failed",
                        "ended_at": datetime.now(UTC).isoformat(),
                        "error": str(exc),
                    },
                )
                _store.save_event(
                    {
                        "event_id": uuid.uuid4().hex,
                        "run_id": run_id,
                        "event_type": "run_failed",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "latency_ms": elapsed,
                        "payload": {"error": str(exc), "error_type": type(exc).__name__},
                    }
                )
                raise

        wrapper._veldwatch_run_id = None  # type: ignore[attr-defined]
        return wrapper

    return decorator


def trace(
    name: str | None = None,
    *,
    event_type: str = "tool_call",
    store: BaseStore | None = None,
) -> Callable[..., Any]:
    """Decorator that wraps a tool/LLM call to capture event-level telemetry.

    Records a single event with timing information.

    Usage:
        @trace(name="llm-call", event_type="llm_call")
        def call_llm(prompt):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _store = store or get_default_store()
            # Try to find a run_id from the call context
            run_id = kwargs.pop("_veldwatch_run_id", None) or "untracked"

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                _store.save_event(
                    {
                        "event_id": uuid.uuid4().hex,
                        "run_id": run_id,
                        "event_type": event_type,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "latency_ms": elapsed,
                        "payload": {
                            "name": name or func.__name__,
                            "status": "ok",
                        },
                    }
                )
                return result
            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000
                _store.save_event(
                    {
                        "event_id": uuid.uuid4().hex,
                        "run_id": run_id,
                        "event_type": event_type,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "latency_ms": elapsed,
                        "payload": {
                            "name": name or func.__name__,
                            "status": "error",
                            "error": str(exc),
                        },
                    }
                )
                raise

        return wrapper

    return decorator
