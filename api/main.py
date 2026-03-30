"""Veldwatch API — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import get_store
from api.routes.alerts import router as alerts_router
from api.routes.runs import router as runs_router
from api.routes.traces import router as traces_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the database is initialized on startup
    get_store()
    yield


app = FastAPI(
    title="Veldwatch API",
    description="AI agent observability and oversight platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router)
app.include_router(traces_router)
app.include_router(alerts_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
