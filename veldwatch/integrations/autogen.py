"""AutoGen integration — hooks into ConversableAgent message passing.

Instruments an AutoGen ``ConversableAgent`` (or any subclass) to forward
every sent/received message to Veldwatch as a structured event.

Usage::

    import autogen
    from veldwatch.integrations.autogen import instrument_autogen
    from veldwatch.store import SQLiteStore

    store = SQLiteStore()
    assistant = autogen.AssistantAgent("assistant", llm_config={...})
    user_proxy = autogen.UserProxyAgent("user_proxy")

    instrument_autogen(assistant, store=store, run_id="my-run")
    instrument_autogen(user_proxy, store=store, run_id="my-run")

    user_proxy.initiate_chat(assistant, message="Hello!")
"""

from __future__ import annotations

import uuid
from typing import Any

from veldwatch.store import BaseStore, SQLiteStore


def instrument_autogen(
    agent: Any,
    *,
    store: BaseStore | None = None,
    run_id: str | None = None,
) -> None:
    """Patch *agent* in-place to trace all message send/receive events.

    Wraps ``agent.send`` and ``agent.receive`` (the two core message-passing
    methods on ``ConversableAgent``) without altering any other behaviour.

    Args:
        agent:  An AutoGen ``ConversableAgent`` (or subclass) instance.
        store:  Veldwatch storage backend.  Defaults to SQLiteStore.
        run_id: Associate events with this run.  A new UUID is generated
                if omitted.
    """
    _store: BaseStore = store or SQLiteStore()
    _run_id: str = run_id or uuid.uuid4().hex

    original_send = agent.send
    original_receive = agent.receive

    def _patched_send(
        message: Any,
        recipient: Any,
        request_reply: bool | None = None,
        silent: bool | None = False,
    ) -> None:
        _store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": _run_id,
                "event_type": "agent_message_send",
                "payload": {
                    "sender": getattr(agent, "name", str(agent)),
                    "recipient": getattr(recipient, "name", str(recipient)),
                    "message": _truncate(message),
                },
            }
        )
        original_send(message, recipient, request_reply=request_reply, silent=silent)

    def _patched_receive(
        message: Any,
        sender: Any,
        request_reply: bool | None = None,
        silent: bool | None = False,
    ) -> None:
        _store.save_event(
            {
                "event_id": uuid.uuid4().hex,
                "run_id": _run_id,
                "event_type": "agent_message_receive",
                "payload": {
                    "recipient": getattr(agent, "name", str(agent)),
                    "sender": getattr(sender, "name", str(sender)),
                    "message": _truncate(message),
                },
            }
        )
        original_receive(message, sender, request_reply=request_reply, silent=silent)

    agent.send = _patched_send  # type: ignore[method-assign]
    agent.receive = _patched_receive  # type: ignore[method-assign]


def _truncate(message: Any, max_chars: int = 500) -> Any:
    """Truncate string messages to keep payloads manageable."""
    if isinstance(message, str) and len(message) > max_chars:
        return message[:max_chars] + "…"
    return message

