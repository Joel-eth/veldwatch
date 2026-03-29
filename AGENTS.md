# AGENTS.md — Veldwatch Build Philosophy

This document describes the high-level build plan and agent rules for the Veldwatch project.

## Build Phases

| Phase | Goal | Status |
|---|---|---|
| **0 — Bootstrap** | Repository structure, README, CI skeleton | ✅ Complete |
| **1 — Core SDK** | Tracer, logger, store, `@watch`/`@trace` decorators | 🔲 Planned |
| **2 — API Layer** | FastAPI backend for runs, events, alerts | 🔲 Planned |
| **3 — Integrations** | LangChain, OpenAI, AutoGen support | 🔲 Planned |
| **4 — Dashboard** | Next.js web UI for runs, traces, alerts | 🔲 Planned |
| **5 — Docker** | One-command local deployment | 🔲 Planned |
| **6 — CI/CD** | Automated testing and publishing | 🔲 Planned |
| **7 — Polish & Launch** | Full docs, CONTRIBUTING, v0.1.0 tag | 🔲 Planned |

## Agent Rules

| Rule | Detail |
|---|---|
| **One phase at a time** | Do not start Phase N+1 until Phase N tests pass |
| **Test before commit** | Every feature must have a corresponding test |
| **No secrets in code** | All credentials via `.env` / GitHub Secrets only |
| **Semantic commits** | `feat:`, `fix:`, `chore:`, `ci:`, `docs:` prefixes always |
| **API first** | Dashboard only consumes the API — never hits the DB directly |
| **No breaking changes** | Follow semver strictly |
| **Document as you build** | `docs/` updated in the same PR as the feature |

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
| Package | PyPI (`veldwatch`) |
