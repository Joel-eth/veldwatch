<div align="center">

# 🌾 Veldwatch

**Open-source AI agent observability and oversight platform.**

*Real-time monitoring, tracing, logging, and safety controls for autonomous AI agents.*

[![CI](https://github.com/Joel-eth/veldwatch/actions/workflows/ci.yml/badge.svg)](https://github.com/Joel-eth/veldwatch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/veldwatch)](https://pypi.org/project/veldwatch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

> *"Veld" — open, wild terrain. "Watch" — vigilant observation.*
>
> Veldwatch is the open field where your AI agents run — and the eye that never looks away.

## The Problem

AI agents are powerful but opaque. When you deploy agents built with LangChain, AutoGen, CrewAI, or custom frameworks, you lose visibility into:

- **What** your agents are doing (which tools they call, what prompts they send)
- **Why** they made specific decisions (trace the reasoning chain)
- **When** things go wrong (failures, cost overruns, hallucinations)
- **How** to stop them before they cause damage (circuit breakers, policy enforcement)

Veldwatch makes your agents **legible, measurable, and controllable**.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      VELDWATCH                          │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────┐  │
│  │ Telemetry  │  │   Evals    │  │ Circuit Breakers  │  │
│  │ (traces)   │  │ (quality)  │  │ (fault tolerance) │  │
│  └────────────┘  └────────────┘  └───────────────────┘  │
│  ┌───────────────────┐  ┌────────────────────────────┐  │
│  │ Policy Enforcer   │  │  Dashboard / Alerts        │  │
│  │ (governance)      │  │  (visibility)              │  │
│  └───────────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

| Subsystem | What it does |
|---|---|
| **Telemetry** | Records every agent action — prompts, tool calls, latencies, responses |
| **Evals** | Scores agent output quality automatically (correctness, relevance, safety) |
| **Circuit Breakers** | Stops failing agents before they cascade |
| **Policy Enforcer** | Blocks banned tools, PII leaks, and cost overruns |
| **Dashboard** | Real-time human-readable view of everything above |

## Quick Start

### Install the SDK

```bash
pip install veldwatch
```

### Instrument your agent

```python
from veldwatch.sdk import watch, trace

@watch(agent_id="my-researcher")
def run_agent(prompt):
    result = call_llm(prompt)
    return result
```

### Run the dashboard

```bash
git clone https://github.com/Joel-eth/veldwatch
cd veldwatch
cp .env.example .env
docker compose -f docker/docker-compose.yml up
# Dashboard → http://localhost:3000
# API docs  → http://localhost:8000/docs
```

## Core Concepts

| Concept | Description |
|---|---|
| **Run** | A single end-to-end agent execution |
| **Trace** | The full sequence of steps/tool calls within a run |
| **Event** | A single atomic action: LLM call, tool use, memory read, etc. |
| **Watch** | A live subscription to an active run's event stream |
| **Alert** | A triggered rule when a run exceeds cost/time/error thresholds |

## Tech Stack

| Layer | Technology |
|---|---|
| SDK | Python 3.11+ |
| API | FastAPI + Uvicorn |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Queue | Redis Streams |
| Dashboard | Next.js 14 + Tailwind CSS + shadcn/ui |
| Deployment | Docker Compose |
| CI/CD | GitHub Actions |

## Integrations

Veldwatch provides zero-config support for popular agent frameworks:

- **LangChain** — callback handler that captures all LLM and tool events
- **OpenAI** — wrapper that tracks tokens, costs, and latencies
- **AutoGen** — hooks into multi-agent message passing

## Project Structure

```
veldwatch/
├── veldwatch/          # Core Python SDK
│   ├── sdk/            # @watch, @trace decorators
│   ├── integrations/   # LangChain, OpenAI, AutoGen
│   ├── tracer.py       # Run tracing
│   ├── logger.py       # Structured logging
│   ├── watcher.py      # Real-time observer
│   ├── store.py        # Storage abstraction
│   └── alert.py        # Alerting rules
├── api/                # FastAPI backend
├── dashboard/          # Next.js web UI
├── docker/             # Docker Compose setup
├── docs/               # Documentation
└── tests/              # Unit & integration tests
```

## Roadmap

- [x] Repository & project structure
- [ ] Core SDK (tracer, logger, store, decorators)
- [ ] REST API (runs, events, alerts)
- [ ] Framework integrations (LangChain, OpenAI, AutoGen)
- [ ] Web dashboard
- [ ] Docker Compose local deployment
- [ ] CI/CD pipelines
- [ ] PyPI package publish
- [ ] Hosted version

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
