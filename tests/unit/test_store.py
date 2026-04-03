from pathlib import Path

from veldwatch.store import SQLiteStore


def test_save_and_get_run(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    run = {
        "run_id": "run-001",
        "agent_id": "agent-a",
        "status": "running",
        "started_at": "2026-01-01T00:00:00Z",
        "metadata": {"key": "value"},
    }
    store.save_run(run)

    fetched = store.get_run("run-001")
    assert fetched is not None
    assert fetched["run_id"] == "run-001"
    assert fetched["agent_id"] == "agent-a"
    assert fetched["status"] == "running"
    assert fetched["metadata"] == {"key": "value"}


def test_update_run(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    store.save_run(
        {
            "run_id": "run-002",
            "agent_id": "a",
            "status": "running",
            "started_at": "2026-01-01T00:00:00Z",
        }
    )
    store.update_run("run-002", {"status": "completed", "ended_at": "2026-01-01T00:01:00Z"})

    fetched = store.get_run("run-002")
    assert fetched["status"] == "completed"
    assert fetched["ended_at"] == "2026-01-01T00:01:00Z"


def test_list_runs_ordering(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    store.save_run({"run_id": "r1", "status": "completed", "started_at": "2026-01-01T00:00:00Z"})
    store.save_run({"run_id": "r2", "status": "completed", "started_at": "2026-01-02T00:00:00Z"})
    store.save_run({"run_id": "r3", "status": "completed", "started_at": "2026-01-03T00:00:00Z"})

    runs = store.list_runs(limit=2)
    assert len(runs) == 2
    assert runs[0]["run_id"] == "r3"  # most recent first


def test_get_nonexistent_run(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    assert store.get_run("does-not-exist") is None


def test_save_and_list_events(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    store.save_run({"run_id": "r1", "status": "running", "started_at": "2026-01-01T00:00:00Z"})

    store.save_event({
        "event_id": "e1", "run_id": "r1", "event_type": "llm_call",
        "timestamp": "2026-01-01T00:00:01Z", "latency_ms": 150.5,
        "payload": {"model": "gpt-4"},
    })
    store.save_event({
        "event_id": "e2", "run_id": "r1", "event_type": "tool_call",
        "timestamp": "2026-01-01T00:00:02Z", "latency_ms": 50.0,
        "payload": {"tool": "search"},
    })

    events = store.list_events("r1")
    assert len(events) == 2
    assert events[0]["event_id"] == "e1"
    assert events[0]["payload"] == {"model": "gpt-4"}
    assert events[1]["latency_ms"] == 50.0


def test_save_and_list_alerts(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")

    store.save_alert({
        "alert_id": "a1", "run_id": "r1", "rule_name": "max_duration",
        "message": "Too slow", "severity": "warning",
        "triggered_at": "2026-01-01T00:00:00Z", "resolved": False,
    })
    store.save_alert({
        "alert_id": "a2", "run_id": "r2", "rule_name": "error_status",
        "message": "Run failed", "severity": "critical",
        "triggered_at": "2026-01-01T00:01:00Z", "resolved": True,
    })

    all_alerts = store.list_alerts()
    assert len(all_alerts) == 2

    unresolved = store.list_alerts(resolved=False)
    assert len(unresolved) == 1
    assert unresolved[0]["alert_id"] == "a1"

    resolved = store.list_alerts(resolved=True)
    assert len(resolved) == 1
    assert resolved[0]["alert_id"] == "a2"
