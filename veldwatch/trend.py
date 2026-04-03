"""RunTrendEngine — cross-run failure rate and duration regression detection."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from veldwatch.store import BaseStore


@dataclass
class RunTrendMetric:
    name: str
    slope: float  # OLS slope; negative = degrading for success_rate, positive for duration
    direction: str  # "improving" | "degrading" | "stable"
    start_value: float
    end_value: float


@dataclass
class RunTrendReport:
    window: int
    run_count: int
    success_rate_trend: RunTrendMetric
    avg_duration_trend: RunTrendMetric
    any_regression: bool = False


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _compute_slope(xs: list[int], ys: list[float]) -> float:
    try:
        slope, _ = statistics.linear_regression(xs, ys)
        return slope
    except statistics.StatisticsError:
        return 0.0


class RunTrendEngine:
    """Detect behavioural slope across a sliding window of sequential runs.

    Uses Python 3.10+ ``statistics.linear_regression`` — zero extra
    dependencies.  Reads ``BaseStore.list_runs()`` directly, so it works
    with both SQLite and PostgreSQL backends unchanged.
    """

    def __init__(self, store: BaseStore, *, window: int = 20) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        self.store = store
        self.window = window

    def analyze(self) -> RunTrendReport:
        """Return a RunTrendReport for the last *window* runs (oldest → newest)."""
        # list_runs returns newest-first; reverse for chronological order
        raw: list[dict[str, Any]] = list(
            reversed(self.store.list_runs(limit=self.window))
        )
        run_count = len(raw)

        empty_metric = RunTrendMetric("success_rate", 0.0, "stable", 0.0, 0.0)
        empty_dur = RunTrendMetric("avg_duration_s", 0.0, "stable", 0.0, 0.0)

        if run_count < 3:
            return RunTrendReport(
                window=self.window,
                run_count=run_count,
                success_rate_trend=empty_metric,
                avg_duration_trend=empty_dur,
            )

        xs = list(range(run_count))

        # ── success-rate slope ────────────────────────────────────────────
        completed_flags = [
            1.0 if r.get("status") == "completed" else 0.0 for r in raw
        ]
        slope_s = round(_compute_slope(xs, completed_flags), 5)
        dir_s: str
        if slope_s > 0.01:
            dir_s = "improving"
        elif slope_s < -0.01:
            dir_s = "degrading"
        else:
            dir_s = "stable"

        # ── duration slope ────────────────────────────────────────────────
        durations: list[float] = []
        for r in raw:
            start_dt = _parse_dt(r.get("started_at"))
            end_dt = _parse_dt(r.get("ended_at"))
            if start_dt and end_dt:
                durations.append((end_dt - start_dt).total_seconds())
            else:
                durations.append(0.0)

        slope_d = round(_compute_slope(xs, durations), 5)
        dir_d: str
        if slope_d > 0.1:
            dir_d = "degrading"
        elif slope_d < -0.1:
            dir_d = "improving"
        else:
            dir_d = "stable"

        any_regression = dir_s == "degrading" or dir_d == "degrading"

        return RunTrendReport(
            window=self.window,
            run_count=run_count,
            success_rate_trend=RunTrendMetric(
                name="success_rate",
                slope=slope_s,
                direction=dir_s,
                start_value=completed_flags[0],
                end_value=completed_flags[-1],
            ),
            avg_duration_trend=RunTrendMetric(
                name="avg_duration_s",
                slope=slope_d,
                direction=dir_d,
                start_value=durations[0],
                end_value=durations[-1],
            ),
            any_regression=any_regression,
        )
