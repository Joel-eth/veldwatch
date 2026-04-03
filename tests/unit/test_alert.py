from pathlib import Path

from veldwatch.alert import AlertEngine, AlertRule, error_status_rule, max_duration_rule
from veldwatch.store import SQLiteStore


def test_alert_rule_triggers(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)
    engine.add_rule(
        AlertRule(
            name="test_rule",
            condition=lambda data: data.get("status") == "failed",
            message="Run failed!",
            severity="critical",
        )
    )

    triggered = engine.evaluate_run({"run_id": "r1", "status": "failed"})
    assert len(triggered) == 1
    assert triggered[0]["rule_name"] == "test_rule"
    assert triggered[0]["severity"] == "critical"

    # Verify it was persisted
    alerts = store.list_alerts()
    assert len(alerts) == 1


def test_alert_rule_does_not_trigger(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)
    engine.add_rule(
        AlertRule(
            name="fail_only",
            condition=lambda data: data.get("status") == "failed",
        )
    )

    triggered = engine.evaluate_run({"run_id": "r1", "status": "completed"})
    assert len(triggered) == 0
    assert len(store.list_alerts()) == 0


def test_max_duration_rule_factory(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)
    engine.add_rule(max_duration_rule(1000))

    # Should trigger — 1500ms > 1000ms
    triggered = engine.evaluate_event({"run_id": "r1", "latency_ms": 1500})
    assert len(triggered) == 1

    # Should NOT trigger — 500ms < 1000ms
    triggered = engine.evaluate_event({"run_id": "r2", "latency_ms": 500})
    assert len(triggered) == 0


def test_error_status_rule_factory(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)
    engine.add_rule(error_status_rule())

    triggered = engine.evaluate_run({"run_id": "r1", "status": "failed"})
    assert len(triggered) == 1
    assert triggered[0]["severity"] == "critical"


def test_remove_rule(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)
    engine.add_rule(AlertRule(name="a", condition=lambda d: True))
    engine.add_rule(AlertRule(name="b", condition=lambda d: True))
    assert len(engine.rules) == 2

    engine.remove_rule("a")
    assert len(engine.rules) == 1
    assert engine.rules[0].name == "b"


def test_bad_rule_does_not_crash(tmp_path: Path):
    store = SQLiteStore(tmp_path / "test.db")
    engine = AlertEngine(store=store)

    def bad_condition(data):
        raise RuntimeError("boom")

    engine.add_rule(AlertRule(name="bad", condition=bad_condition))
    engine.add_rule(AlertRule(name="good", condition=lambda d: True, message="ok"))

    triggered = engine.evaluate_run({"run_id": "r1"})
    # Bad rule should be skipped, good rule should fire
    assert len(triggered) == 1
    assert triggered[0]["rule_name"] == "good"
