"""Unit tests for veldwatch.trend.RunTrendEngine."""

from pathlib import Path

from veldwatch.store import SQLiteStore
from veldwatch.trend import RunTrendEngine, RunTrendReport


def _make_run(
    run_id: str,
    status: str = "completed",
    started_at: str = "2026-01-01T00:00:00Z",
    ended_at: str | None = "2026-01-01T00:00:01Z",
) -> dict:
    r: dict = {
        "run_id": run_id,
        "agent_id": "test-agent",
        "status": status,
        "started_at": started_at,
    }
    if ended_at:
        r["ended_at"] = ended_at
    return r


def test_too_few_runs_returns_stable(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    store.save_run(_make_run("r1"))
    store.save_run(_make_run("r2"))

    engine = RunTrendEngine(store, window=20)
    report = engine.analyze()

    assert report.run_count == 2
    assert report.success_rate_trend.direction == "stable"
    assert report.avg_duration_trend.direction == "stable"
    assert report.any_regression is False


def test_all_completed_is_improving_or_stable(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    for i in range(10):
        store.save_run(_make_run(f"r{i}"))

    engine = RunTrendEngine(store, window=10)
    report = engine.analyze()

    assert report.run_count == 10
    assert report.success_rate_trend.direction in ("improving", "stable")
    assert report.any_regression is False


def test_increasing_failures_flagged_as_regression(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    # Oldest runs succeed; newest fail — clear downward slope on success_rate
    statuses = ["completed"] * 8 + ["failed"] * 7
    for i, status in enumerate(statuses):
        store.save_run(_make_run(f"r{i:02d}", status=status))

    engine = RunTrendEngine(store, window=len(statuses))
    report = engine.analyze()

    assert report.success_rate_trend.direction == "degrading"
    assert report.any_regression is True


def test_window_parameter_limits_runs(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    for i in range(20):
        store.save_run(_make_run(f"r{i:02d}"))

    engine = RunTrendEngine(store, window=5)
    report = engine.analyze()

    assert report.run_count <= 5


def test_returns_run_trend_report_type(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    for i in range(5):
        store.save_run(_make_run(f"r{i}"))

    result = RunTrendEngine(store).analyze()
    assert isinstance(result, RunTrendReport)


def test_invalid_window_raises(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    try:
        RunTrendEngine(store, window=1)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass
