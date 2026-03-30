"""Run management routes."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import get_store
from api.models import RunCreate, RunUpdate, RunResponse, RunListResponse
from veldwatch.store import BaseStore

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=201)
async def create_run(
    body: RunCreate,
    store: BaseStore = Depends(get_store),
) -> RunResponse:
    run_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    run = {
        "run_id": run_id,
        "agent_id": body.agent_id,
        "status": "running",
        "started_at": now,
        "metadata": body.metadata,
    }
    store.save_run(run)
    saved = store.get_run(run_id)
    return RunResponse(**saved)


@router.get("", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    store: BaseStore = Depends(get_store),
) -> RunListResponse:
    runs = store.list_runs(limit=limit, offset=offset)
    return RunListResponse(
        runs=[RunResponse(**r) for r in runs],
        total=len(runs),
    )


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    store: BaseStore = Depends(get_store),
) -> RunResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(**run)


@router.patch("/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: str,
    body: RunUpdate,
    store: BaseStore = Depends(get_store),
) -> RunResponse:
    existing = store.get_run(run_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Run not found")

    updates = body.model_dump(exclude_none=True)
    if updates.get("status") in ("completed", "failed") and not existing.get("ended_at"):
        updates["ended_at"] = datetime.now(timezone.utc).isoformat()

    store.update_run(run_id, updates)
    updated = store.get_run(run_id)
    return RunResponse(**updated)
