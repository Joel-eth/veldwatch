from pathlib import Path

from veldwatch.store import SQLiteStore
from veldwatch.tracer import Tracer


def test_tracer_start_and_end_run(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="test-agent")

    run_id = tracer.start_run()
    assert run_id == tracer.run_id

    run = store.get_run(run_id)
    assert run is not None
    assert run["status"] == "running"

    tracer.end_run(status="completed")
    run = store.get_run(run_id)
    assert run["status"] == "completed"
    assert run["ended_at"] is not None


def test_tracer_end_run_with_error(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="err-agent")
    tracer.start_run()
    tracer.end_run(status="failed", error="something went wrong")

    run = store.get_run(tracer.run_id)
    assert run["status"] == "failed"
    assert run["error"] == "something went wrong"


def test_tracer_add_event(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="event-agent")
    tracer.start_run()

    event_id = tracer.add_event(
        "llm_call",
        payload={"model": "gpt-4", "tokens": 100},
        latency_ms=250.3,
    )

    events = store.list_events(tracer.run_id)
    assert len(events) == 1
    assert events[0]["event_id"] == event_id
    assert events[0]["event_type"] == "llm_call"
    assert events[0]["payload"]["model"] == "gpt-4"


def test_tracer_trace_call_context_manager(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="ctx-agent")
    tracer.start_run()

    with tracer.trace_call("tool_call") as ctx:
        ctx["payload"] = {"tool": "search", "query": "test"}

    events = store.list_events(tracer.run_id)
    assert len(events) == 1
    assert events[0]["event_type"] == "tool_call"
    assert events[0]["latency_ms"] >= 0


def test_tracer_idempotent_start_end(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="idem-agent")

    # Double start should be safe
    id1 = tracer.start_run()
    id2 = tracer.start_run()
    assert id1 == id2

    # Double end should be safe
    tracer.end_run()
    tracer.end_run()

    runs = store.list_runs()
    assert len(runs) == 1


def test_tracer_custom_run_id(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    tracer = Tracer(store, agent_id="custom", run_id="my-custom-id-123")
    tracer.start_run()

    run = store.get_run("my-custom-id-123")
    assert run is not None
