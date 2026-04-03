"""Pydantic models for Veldwatch API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# -- Runs --

class RunCreate(BaseModel):
    agent_id: str | None = None
    metadata: dict[str, Any] | None = None


class RunUpdate(BaseModel):
    status: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class RunResponse(BaseModel):
    run_id: str
    agent_id: str | None = None
    status: str
    started_at: str
    ended_at: str | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None


class RunListResponse(BaseModel):
    runs: list[RunResponse]
    total: int


# -- Events --

class EventCreate(BaseModel):
    event_type: str
    payload: dict[str, Any] | None = None
    latency_ms: float | None = None


class EventResponse(BaseModel):
    event_id: str
    run_id: str
    event_type: str
    timestamp: str
    latency_ms: float | None = None
    payload: dict[str, Any] | None = None


class EventListResponse(BaseModel):
    events: list[EventResponse]


# -- Alerts --

class AlertRuleCreate(BaseModel):
    rule_name: str
    field: str = Field(description="Field to check: 'latency_ms', 'status', etc.")
    operator: str = Field(description="Comparison: 'gt', 'lt', 'eq', 'neq'")
    value: Any = Field(description="Threshold value")
    severity: str = "warning"
    message: str = ""


class AlertRuleResponse(BaseModel):
    rule_name: str
    field: str
    operator: str
    value: Any
    severity: str
    message: str


class AlertResponse(BaseModel):
    alert_id: str
    run_id: str | None = None
    rule_name: str
    message: str
    severity: str
    triggered_at: str
    resolved: bool


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
