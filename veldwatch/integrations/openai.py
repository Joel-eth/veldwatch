"""OpenAI integration — wraps chat completions to capture tokens, cost, latency.

Wraps ``openai.OpenAI`` (or ``openai.AsyncOpenAI``) so every
``chat.completions.create`` call is automatically traced without changing
the rest of your code.

Usage::

    from openai import OpenAI
    from veldwatch.integrations.openai import instrument_openai
    from veldwatch.store import SQLiteStore

    store = SQLiteStore()
    client = instrument_openai(OpenAI(), store=store, run_id="my-run")
    # All subsequent client.chat.completions.create(...) calls are recorded.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from veldwatch.store import BaseStore, SQLiteStore

# Cost per 1 K tokens for common OpenAI models (input, output) in USD.
# Updated April 2026 — keep in sync as models evolve.
_COST_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4": (0.03, 0.06),
    "gpt-3.5-turbo": (0.0005, 0.0015),
}


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Return estimated USD cost for the given token counts."""
    prefix = model.split("-20")[0]  # strip date suffixes like gpt-4o-2024-05-13
    for key, (inp, out) in _COST_PER_1K.items():
        if prefix.startswith(key):
            return (prompt_tokens * inp + completion_tokens * out) / 1000
    return 0.0


class _TracedCompletions:
    """Wraps the ``chat.completions`` namespace."""

    def __init__(
        self,
        completions: Any,
        store: BaseStore,
        run_id: str,
    ) -> None:
        self._completions = completions
        self._store = store
        self._run_id = run_id

    def create(self, *args: Any, **kwargs: Any) -> Any:
        model: str = kwargs.get("model", "unknown")
        t0 = time.perf_counter()
        response = self._completions.create(*args, **kwargs)
        latency_ms = (time.perf_counter() - t0) * 1000

        prompt_tokens = 0
        completion_tokens = 0
        try:
            usage = response.usage
            if usage:
                prompt_tokens = usage.prompt_tokens or 0
                completion_tokens = usage.completion_tokens or 0
        except AttributeError:
            pass

        cost_usd = _estimate_cost(model, prompt_tokens, completion_tokens)

        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "llm_call",
                "latency_ms": round(latency_ms, 2),
                "payload": {
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "cost_usd": round(cost_usd, 6),
                },
            }
        )
        return response


class _TracedChat:
    def __init__(self, chat: Any, store: BaseStore, run_id: str) -> None:
        self._chat = chat
        self.completions = _TracedCompletions(chat.completions, store, run_id)


class InstrumentedOpenAI:
    """Thin proxy around ``openai.OpenAI`` that records every completion."""

    def __init__(self, client: Any, store: BaseStore, run_id: str) -> None:
        self._client = client
        self.chat = _TracedChat(client.chat, store, run_id)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


def instrument_openai(
    client: Any,
    *,
    store: BaseStore | None = None,
    run_id: str | None = None,
) -> InstrumentedOpenAI:
    """Wrap an ``openai.OpenAI`` client with Veldwatch tracing.

    Args:
        client: An ``openai.OpenAI`` instance.
        store:  Storage backend.  Defaults to a local SQLiteStore.
        run_id: Associate all captured events with this run.  A new UUID is
                generated if omitted.

    Returns:
        A drop-in replacement for *client* that records every
        ``chat.completions.create`` call.
    """
    _store = store or SQLiteStore()
    _run_id = run_id or uuid.uuid4().hex
    return InstrumentedOpenAI(client, _store, _run_id)

