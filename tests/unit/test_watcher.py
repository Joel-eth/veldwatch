import time
from pathlib import Path

from veldwatch.store import SQLiteStore
from veldwatch.tracer import Tracer
from veldwatch.watcher import Watcher


def test_watcher_dispatches_events(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="watched")
    tracer.start_run()
    tracer.add_event("llm_call", payload={"model": "gpt-4"})

    received = []
    watcher = Watcher(store, poll_interval=0.1)
    watcher.subscribe(lambda e: received.append(e), run_id=tracer.run_id)
    watcher.start()
    time.sleep(0.3)
    watcher.stop()

    assert len(received) == 1
    assert received[0]["event_type"] == "llm_call"


def test_watcher_global_subscriber(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="global")
    tracer.start_run()
    tracer.add_event("tool_call")

    received = []
    watcher = Watcher(store, poll_interval=0.1)
    watcher.subscribe(lambda e: received.append(e))
    watcher.start()
    time.sleep(0.3)
    watcher.stop()

    assert len(received) >= 1


def test_watcher_no_duplicate_dispatch(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="dedup")
    tracer.start_run()
    tracer.add_event("tool_call")

    received = []
    watcher = Watcher(store, poll_interval=0.1)
    watcher.subscribe(lambda e: received.append(e), run_id=tracer.run_id)
    watcher.start()
    time.sleep(0.4)  # Multiple poll cycles
    watcher.stop()

    assert len(received) == 1  # No duplicates


def test_watcher_unsubscribe(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    watcher = Watcher(store)
    watcher.subscribe(lambda e: None, run_id="r1")
    watcher.subscribe(lambda e: None)
    assert len(watcher._subscribers["r1"]) == 1
    assert len(watcher._global_subscribers) == 1

    watcher.unsubscribe_all(run_id="r1")
    assert "r1" not in watcher._subscribers
    assert len(watcher._global_subscribers) == 1

    watcher.unsubscribe_all()
    assert len(watcher._global_subscribers) == 0
