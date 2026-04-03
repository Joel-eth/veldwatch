"""LangChain integration — VeldwatchCallbackHandler.

Zero-config capture of every LLM call, tool invocation and chain step inside
a LangChain agent.  Drop-in replacement for any existing callback list.

Usage::

    from veldwatch.integrations.langchain import VeldwatchCallbackHandler
    from veldwatch.store import SQLiteStore

    store = SQLiteStore()
    handler = VeldwatchCallbackHandler(store=store, agent_id="my-lc-agent")

    chain.invoke({"input": "..."}, config={"callbacks": [handler]})
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Sequence
from typing import Any

from veldwatch.store import BaseStore, SQLiteStore


class VeldwatchCallbackHandler:
    """LangChain callback handler that records runs and events in Veldwatch.

    Compatible with ``langchain_core.callbacks.BaseCallbackHandler``.  We do
    **not** inherit from it to avoid adding LangChain as a hard dependency.
    Passing this object to any LangChain ``callbacks=`` parameter works via
    duck-typing: LangChain calls the recognised ``on_*`` methods and ignores
    the rest.
    """

    def __init__(
        self,
        *,
        store: BaseStore | None = None,
        agent_id: str = "langchain-agent",
    ) -> None:
        self._store: BaseStore = store or SQLiteStore()
        self._agent_id = agent_id
        self._run_id: str | None = None
        self._llm_starts: dict[str, float] = {}

    # ── run lifecycle ──────────────────────────────────────────────────────

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        self._run_id = uuid.uuid4().hex
        self._store.save_run(
            {
                "run_id": self._run_id,
                "agent_id": self._agent_id,
                "status": "running",
                "metadata": {
                    "chain": serialized.get("id", ["unknown"])[-1],
                },
            }
        )

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        if self._run_id:
            self._store.update_run(self._run_id, {"status": "completed"})

    def on_chain_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        if self._run_id:
            self._store.update_run(
                self._run_id,
                {"status": "failed", "error": str(error)},
            )

    # ── LLM calls ─────────────────────────────────────────────────────────

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: Sequence[str],
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        key = str(run_id or id(prompts))
        self._llm_starts[key] = time.perf_counter()

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        if self._run_id is None:
            return
        key = str(run_id or "")
        latency_ms: float | None = None
        if key in self._llm_starts:
            latency_ms = (time.perf_counter() - self._llm_starts.pop(key)) * 1000

        # Extract token usage if present
        payload: dict[str, Any] = {}
        try:
            usage = response.llm_output.get("token_usage", {})  # type: ignore[union-attr]
            payload["prompt_tokens"] = usage.get("prompt_tokens")
            payload["completion_tokens"] = usage.get("completion_tokens")
            payload["total_tokens"] = usage.get("total_tokens")
        except AttributeError:
            pass

        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "llm_call",
                "latency_ms": latency_ms,
                "payload": payload or None,
            }
        )

    def on_llm_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        if self._run_id is None:
            return
        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "llm_error",
                "payload": {"error": str(error)},
            }
        )

    # ── tool calls ────────────────────────────────────────────────────────

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        if self._run_id is None:
            return
        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "tool_start",
                "payload": {
                    "tool": serialized.get("name", "unknown"),
                    "input": input_str,
                },
            }
        )

    def on_tool_end(
        self,
        output: str,
        **kwargs: Any,
    ) -> None:
        if self._run_id is None:
            return
        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "tool_end",
                "payload": {"output": output[:500]},
            }
        )

    def on_tool_error(
        self,
        error: BaseException,
        **kwargs: Any,
    ) -> None:
        if self._run_id is None:
            return
        self._store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": self._run_id,
                "event_type": "tool_error",
                "payload": {"error": str(error)},
            }
        )

