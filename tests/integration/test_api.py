"""Integration tests for the Veldwatch API."""

import os
import tempfile

from fastapi.testclient import TestClient

# Point the store at a temp DB before importing the app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["VELDWATCH_DB_URL"] = f"sqlite:///{_tmp.name}"
_tmp.close()

from api.deps import get_store  # noqa: E402
from api.main import app  # noqa: E402

# Clear the lru_cache so tests use the temp DB
get_store.cache_clear()

client = TestClient(app)


# -- Health --

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# -- Runs --

def test_create_run():
    resp = client.post("/runs", json={"agent_id": "test-agent"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["agent_id"] == "test-agent"
    assert data["status"] == "running"
    assert "run_id" in data


def test_list_runs():
    # Create a couple
    client.post("/runs", json={"agent_id": "a1"})
    client.post("/runs", json={"agent_id": "a2"})
    resp = client.get("/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["runs"]) >= 2


def test_get_run():
    create = client.post("/runs", json={"agent_id": "get-me"})
    run_id = create.json()["run_id"]

    resp = client.get(f"/runs/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["run_id"] == run_id


def test_get_run_not_found():
    resp = client.get("/runs/nonexistent-id")
    assert resp.status_code == 404


def test_update_run():
    create = client.post("/runs", json={"agent_id": "updatable"})
    run_id = create.json()["run_id"]

    resp = client.patch(f"/runs/{run_id}", json={"status": "completed"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["ended_at"] is not None


def test_update_run_failed():
    create = client.post("/runs", json={"agent_id": "fail-test"})
    run_id = create.json()["run_id"]

    resp = client.patch(
        f"/runs/{run_id}",
        json={"status": "failed", "error": "something broke"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "failed"
    assert resp.json()["error"] == "something broke"


# -- Events --

def test_create_event():
    create = client.post("/runs", json={"agent_id": "evented"})
    run_id = create.json()["run_id"]

    resp = client.post(
        f"/runs/{run_id}/events",
        json={
            "event_type": "llm_call",
            "payload": {"model": "gpt-4"},
            "latency_ms": 250.5,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["event_type"] == "llm_call"
    assert data["run_id"] == run_id
    assert data["payload"]["model"] == "gpt-4"


def test_create_event_run_not_found():
    resp = client.post(
        "/runs/nonexistent/events",
        json={"event_type": "test"},
    )
    assert resp.status_code == 404


def test_list_events():
    create = client.post("/runs", json={"agent_id": "multi-event"})
    run_id = create.json()["run_id"]

    client.post(f"/runs/{run_id}/events", json={"event_type": "llm_call"})
    client.post(f"/runs/{run_id}/events", json={"event_type": "tool_call"})

    resp = client.get(f"/runs/{run_id}/events")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["events"]) == 2


def test_list_events_run_not_found():
    resp = client.get("/runs/nonexistent/events")
    assert resp.status_code == 404


# -- Alert Rules --

def test_create_alert_rule():
    resp = client.post(
        "/alerts/rules",
        json={
            "rule_name": "slow_run",
            "field": "latency_ms",
            "operator": "gt",
            "value": 1000,
            "severity": "warning",
            "message": "Run too slow",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["rule_name"] == "slow_run"


def test_list_alert_rules():
    # Ensure at least one rule exists
    client.post(
        "/alerts/rules",
        json={
            "rule_name": "test_rule",
            "field": "status",
            "operator": "eq",
            "value": "failed",
        },
    )
    resp = client.get("/alerts/rules")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_delete_alert_rule():
    client.post(
        "/alerts/rules",
        json={
            "rule_name": "deleteme",
            "field": "status",
            "operator": "eq",
            "value": "failed",
        },
    )
    resp = client.delete("/alerts/rules/deleteme")
    assert resp.status_code == 204


def test_list_alerts():
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert "alerts" in resp.json()


# -- Run Trend --

def test_run_trend_insufficient_data():
    """Fewer than 3 runs → stable trends returned, no error."""
    resp = client.get("/runs/trend?window=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "success_rate_trend" in data
    assert "avg_duration_trend" in data
    assert "any_regression" in data


def test_run_trend_with_data():
    """Create 5 completed runs and verify trend endpoint returns valid shape."""
    for i in range(5):
        r = client.post("/runs", json={"agent_id": f"trend-agent-{i}"})
        run_id = r.json()["run_id"]
        client.patch(f"/runs/{run_id}", json={"status": "completed"})

    resp = client.get("/runs/trend?window=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["run_count"] >= 1
    assert data["success_rate_trend"]["name"] == "success_rate"
    assert data["avg_duration_trend"]["name"] == "avg_duration_s"
    assert isinstance(data["any_regression"], bool)


def test_run_trend_window_validation():
    """window < 3 should be rejected."""
    resp = client.get("/runs/trend?window=2")
    assert resp.status_code == 422
