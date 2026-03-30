"""Trace and event routes."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_store
from api.models import EventCreate, EventResponse, EventListResponse
from veldwatch.store import BaseStore

router = APIRouter(tags=["events"])


@router.post(
    "/runs/{run_id}/events",
    response_model=EventResponse,
    status_code=201,
)
async def create_event(
    run_id: str,
    body: EventCreate,
    store: BaseStore = Depends(get_store),
) -> EventResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    event_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    event = {
        "event_id": event_id,
        "run_id": run_id,
        "event_type": body.event_type,
        "timestamp": now,
        "latency_ms": body.latency_ms,
        "payload": body.payload,
    }
    store.save_event(event)
    return EventResponse(**event)


@router.get(
    "/runs/{run_id}/events",
    response_model=EventListResponse,
)
async def list_events(
    run_id: str,
    store: BaseStore = Depends(get_store),
) -> EventListResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    events = store.list_events(run_id)
    return EventListResponse(events=[EventResponse(**e) for e in events])
