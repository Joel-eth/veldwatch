"""Threshold and anomaly alerting for agent runs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from veldwatch.store import BaseStore


@dataclass
class AlertRule:
    """Defines a condition that triggers an alert."""

    name: str
    condition: Callable[[dict[str, Any]], bool]
    message: str = ""
    severity: str = "warning"  # "info", "warning", "critical"


@dataclass
class AlertEngine:
    """Evaluates runs/events against alert rules and persists triggered alerts."""

    store: BaseStore
    rules: list[AlertRule] = field(default_factory=list)

    def add_rule(self, rule: AlertRule) -> None:
        self.rules.append(rule)

    def remove_rule(self, name: str) -> None:
        self.rules = [r for r in self.rules if r.name != name]

    def evaluate_run(self, run: dict[str, Any]) -> list[dict[str, Any]]:
        """Check a run dict against all rules. Returns list of triggered alerts."""
        triggered: list[dict[str, Any]] = []
        for rule in self.rules:
            try:
                if rule.condition(run):
                    alert = {
                        "alert_id": uuid.uuid4().hex,
                        "run_id": run.get("run_id"),
                        "rule_name": rule.name,
                        "message": rule.message or f"Rule '{rule.name}' triggered",
                        "severity": rule.severity,
                        "triggered_at": datetime.now(timezone.utc).isoformat(),
                        "resolved": False,
                    }
                    self.store.save_alert(alert)
                    triggered.append(alert)
            except Exception:
                pass  # Don't let a bad rule crash the engine
        return triggered

    def evaluate_event(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        """Check an event dict against all rules. Returns list of triggered alerts."""
        triggered: list[dict[str, Any]] = []
        for rule in self.rules:
            try:
                if rule.condition(event):
                    alert = {
                        "alert_id": uuid.uuid4().hex,
                        "run_id": event.get("run_id"),
                        "rule_name": rule.name,
                        "message": rule.message or f"Rule '{rule.name}' triggered",
                        "severity": rule.severity,
                        "triggered_at": datetime.now(timezone.utc).isoformat(),
                        "resolved": False,
                    }
                    self.store.save_alert(alert)
                    triggered.append(alert)
            except Exception:
                pass
        return triggered


# -- Built-in rule factories --

def max_duration_rule(threshold_ms: float, severity: str = "warning") -> AlertRule:
    """Alert when a run/event latency exceeds a threshold."""
    return AlertRule(
        name=f"max_duration_{threshold_ms}ms",
        condition=lambda data: (data.get("latency_ms") or 0) > threshold_ms,
        message=f"Duration exceeded {threshold_ms}ms",
        severity=severity,
    )


def error_status_rule(severity: str = "critical") -> AlertRule:
    """Alert when a run has failed status."""
    return AlertRule(
        name="error_status",
        condition=lambda data: data.get("status") == "failed",
        message="Run failed",
        severity=severity,
    )
