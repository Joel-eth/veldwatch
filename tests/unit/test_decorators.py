import tempfile
from pathlib import Path

from veldwatch.sdk.decorators import watch, trace, set_default_store
from veldwatch.store import SQLiteStore


def _make_store(tmp_path: Path) -> SQLiteStore:
    store = SQLiteStore(tmp_path / "test.db")
    set_default_store(store)
    return store


def test_watch_records_successful_run(tmp_path):
    store = _make_store(tmp_path)

    @watch(agent_id="test-agent", store=store)
    def dummy_agent(prompt: str) -> str:
        return f"response to: {prompt}"

    result = dummy_agent("hello")
    assert result == "response to: hello"

    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0]["agent_id"] == "test-agent"
    assert runs[0]["status"] == "completed"


def test_watch_records_failed_run(tmp_path):
    store = _make_store(tmp_path)

    @watch(agent_id="fail-agent", store=store)
    def bad_agent():
        raise ValueError("something broke")

    try:
        bad_agent()
    except ValueError:
        pass

    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0]["status"] == "failed"
    assert "something broke" in runs[0]["error"]


def test_watch_creates_events(tmp_path):
    store = _make_store(tmp_path)

    @watch(agent_id="evented", store=store)
    def evented_agent():
        return 42

    evented_agent()
    runs = store.list_runs()
    events = store.list_events(runs[0]["run_id"])
    assert len(events) >= 1
    assert events[0]["event_type"] == "run_completed"
    assert events[0]["latency_ms"] >= 0


def test_trace_decorator_passthrough(tmp_path):
    store = _make_store(tmp_path)

    @trace(name="test-tool", store=store)
    def dummy_tool(x: int) -> int:
        return x * 2

    result = dummy_tool(5)
    assert result == 10


def test_watch_default_agent_id(tmp_path):
    store = _make_store(tmp_path)

    @watch(store=store)
    def my_special_agent():
        return "ok"

    my_special_agent()
    runs = store.list_runs()
    assert runs[0]["agent_id"] == "my_special_agent"
