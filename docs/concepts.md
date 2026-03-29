# Core Concepts

## Run

A **Run** represents a single end-to-end agent execution. Every time your decorated agent function is called, Veldwatch creates a new Run with a unique ID, tracks its lifecycle (running → completed / failed), and records all associated events.

## Trace

A **Trace** is the full sequence of steps and tool calls within a Run. It provides a timeline view of everything the agent did — which LLMs it called, which tools it used, and in what order.

## Event

An **Event** is a single atomic action within a trace: an LLM call, a tool invocation, a memory read, an error, etc. Each event captures:
- Event type (llm_call, tool_use, error, etc.)
- Timestamp
- Latency
- Input/output payloads
- Token counts and cost estimates (for LLM calls)

## Watch

A **Watch** is a live subscription to an active Run's event stream. It enables real-time monitoring of what an agent is doing right now.

## Alert

An **Alert** is a triggered notification when a Run or its events exceed defined thresholds — for example, cost exceeding a budget, duration exceeding a timeout, or error rate crossing a threshold.
