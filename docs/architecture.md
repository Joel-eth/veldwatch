# Veldwatch Architecture

## Overview

Veldwatch is structured as a three-tier system:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   SDK        │───▶│   API        │───▶│  Dashboard   │
│  (Python)    │    │  (FastAPI)   │    │  (Next.js)   │
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │
       ▼                   ▼
  Agent code          Database
  (your app)       (SQLite / Postgres)
```

### SDK Layer
The Python SDK provides decorators (`@watch`, `@trace`) that developers attach to their agent functions. These decorators capture telemetry (start/end times, errors, tool calls, LLM responses) and emit structured events to the API layer.

### API Layer
A FastAPI server that receives, stores, and serves run and event data. It provides RESTful endpoints for creating runs, appending events, querying traces, and managing alert rules.

### Dashboard Layer
A Next.js web application that consumes the API and renders real-time visualizations of agent runs, traces, costs, and alerts.

## Data Flow

1. Developer decorates agent function with `@watch`
2. When the function executes, the SDK creates a **Run** and emits **Events**
3. Events are sent to the API via HTTP (or buffered locally in SQLite)
4. The API persists events to the database
5. The Dashboard polls/subscribes to the API for real-time updates
6. Alert rules evaluate incoming events and trigger notifications

## Storage

- **Development:** SQLite — zero-config, embedded, file-based
- **Production:** PostgreSQL via SQLAlchemy — scalable, concurrent
- **Event queue:** Redis Streams — async ingestion buffer for high-throughput
