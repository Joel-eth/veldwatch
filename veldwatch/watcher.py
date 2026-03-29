"""Real-time run observer — live subscriptions to agent event streams."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any, Callable

from veldwatch.store import BaseStore

EventCallback = Callable[[dict[str, Any]], None]


class Watcher:
    """Polls the store for new events on active runs and dispatches to subscribers.

    This is the local/dev watcher. The production hosted version will use
    Redis Streams or WebSockets (Phase 3+).
    """

    def __init__(
        self,
        store: BaseStore,
        poll_interval: float = 1.0,
    ) -> None:
        self.store = store
        self.poll_interval = poll_interval
        self._subscribers: dict[str, list[EventCallback]] = defaultdict(list)
        self._global_subscribers: list[EventCallback] = []
        self._seen_events: set[str] = set()
        self._running = False
        self._thread: threading.Thread | None = None

    def subscribe(
        self,
        callback: EventCallback,
        *,
        run_id: str | None = None,
    ) -> None:
        """Register a callback for events. If run_id is None, subscribes to all."""
        if run_id:
            self._subscribers[run_id].append(callback)
        else:
            self._global_subscribers.append(callback)

    def unsubscribe_all(self, *, run_id: str | None = None) -> None:
        """Remove all subscribers, or just those for a specific run."""
        if run_id:
            self._subscribers.pop(run_id, None)
        else:
            self._subscribers.clear()
            self._global_subscribers.clear()

    def start(self) -> None:
        """Start polling for new events in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.poll_interval + 1)
            self._thread = None

    def _poll_loop(self) -> None:
        while self._running:
            try:
                self._check_runs()
            except Exception:
                pass  # Don't crash the watcher thread
            time.sleep(self.poll_interval)

    def _check_runs(self) -> None:
        # Check runs that have active subscribers
        run_ids = list(self._subscribers.keys())
        # If there are global subscribers, also check recent runs
        if self._global_subscribers:
            recent = self.store.list_runs(limit=10)
            for run in recent:
                if run["run_id"] not in run_ids:
                    run_ids.append(run["run_id"])

        for run_id in run_ids:
            events = self.store.list_events(run_id)
            for event in events:
                eid = event["event_id"]
                if eid in self._seen_events:
                    continue
                self._seen_events.add(eid)
                self._dispatch(run_id, event)

    def _dispatch(self, run_id: str, event: dict[str, Any]) -> None:
        for cb in self._subscribers.get(run_id, []):
            try:
                cb(event)
            except Exception:
                pass
        for cb in self._global_subscribers:
            try:
                cb(event)
            except Exception:
                pass
