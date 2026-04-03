"""Alert rule and alert routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response

from api.deps import get_store
from api.models import (
    AlertListResponse,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from veldwatch.store import BaseStore

router = APIRouter(prefix="/alerts", tags=["alerts"])

# In-memory rule registry (persisted rules are a Phase 4+ feature)
_rules: dict[str, AlertRuleCreate] = {}


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(body: AlertRuleCreate) -> AlertRuleResponse:
    _rules[body.rule_name] = body
    return AlertRuleResponse(
        rule_name=body.rule_name,
        field=body.field,
        operator=body.operator,
        value=body.value,
        severity=body.severity,
        message=body.message,
    )


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules() -> list[AlertRuleResponse]:
    return [
        AlertRuleResponse(
            rule_name=r.rule_name,
            field=r.field,
            operator=r.operator,
            value=r.value,
            severity=r.severity,
            message=r.message,
        )
        for r in _rules.values()
    ]


@router.delete("/rules/{rule_name}", status_code=204, response_class=Response)
async def delete_alert_rule(rule_name: str) -> Response:
    _rules.pop(rule_name, None)
    return Response(status_code=204)


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    resolved: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    store: BaseStore = Depends(get_store),
) -> AlertListResponse:
    alerts = store.list_alerts(resolved=resolved, limit=limit)
    return AlertListResponse(alerts=[AlertResponse(**a) for a in alerts])
