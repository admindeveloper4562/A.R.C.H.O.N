"""Bounded chat streaming with success-only durable conversation history."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Mapping
import inspect
import re
from typing import Any
from uuid import uuid4

from jarvis_v2.backend.conversation import (
    ConversationStore,
    ConversationStoreError,
    MAX_TURN_CONTENT_BYTES,
)


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MAX_MODEL_BYTES = 256


class ChatServiceError(ValueError):
    """Raised when a chat request cannot be prepared safely."""


Provider = Callable[[str], Any]


class ChatService:
    """Stream provider deltas and persist only a completed exchange."""

    def __init__(self, conversations: ConversationStore):
        if not isinstance(conversations, ConversationStore):
            raise ChatServiceError("conversation store is required")
        self.conversations = conversations

    async def stream(
        self,
        conversation_id: str,
        message: str,
        provider: Provider,
        *,
        provider_id: str = "runtime",
        model: str = "",
        cancel_event: Any = None,
        idempotency_key: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Yield ``delta`` events, then ``done`` only after durable persistence."""
        self._validate_request(conversation_id, message, provider_id, model, provider)
        try:
            self.conversations.open_conversation(conversation_id)
        except ConversationStoreError:
            yield self._error("history_unavailable", "Conversation history is unavailable; try again.")
            return
        if self._cancelled(cancel_event):
            yield self._error("cancelled", "The response was cancelled before it was saved.")
            return

        response_parts: list[str] = []
        response_bytes = 0
        try:
            stream = provider(message)
            if inspect.isawaitable(stream):
                stream = await stream
            if not hasattr(stream, "__aiter__"):
                raise ChatServiceError("provider stream is invalid")
            async for delta in stream:
                if self._cancelled(cancel_event):
                    yield self._error("cancelled", "The response was cancelled before it was saved.")
                    return
                content = self._delta_content(delta)
                if len(content.encode("utf-8")) > MAX_TURN_CONTENT_BYTES:
                    yield self._error("provider_invalid", "The response exceeded the allowed size; nothing was saved.")
                    return
                response_parts.append(content)
                response_bytes += len(content.encode("utf-8"))
                if response_bytes > MAX_TURN_CONTENT_BYTES:
                    yield self._error("provider_invalid", "The response exceeded the allowed size; nothing was saved.")
                    return
                yield {"type": "delta", "content": content}
        except asyncio.CancelledError:
            return
        except TimeoutError:
            yield self._error("provider_timeout", "The response provider timed out; nothing was saved.")
            return
        except (ConnectionError, OSError):
            yield self._error("provider_unavailable", "The response provider is unavailable; nothing was saved.")
            return
        except ChatServiceError:
            yield self._error("provider_invalid", "The response provider returned invalid data; nothing was saved.")
            return
        except Exception:
            yield self._error("provider_failed", "The response could not be completed; nothing was saved.")
            return

        if self._cancelled(cancel_event):
            yield self._error("cancelled", "The response was cancelled before it was saved.")
            return
        response = "".join(response_parts)
        if not response:
            yield self._error("empty_response", "The response was empty; nothing was saved.")
            return
        try:
            base_key = idempotency_key or uuid4().hex
            if not _IDENTIFIER.fullmatch(base_key) or len(base_key) > 126:
                raise ChatServiceError("invalid idempotency key")
            user_turn = self.conversations.append_turn(
                conversation_id,
                role="user",
                provider=provider_id,
                model=model,
                content=message,
                idempotency_key=f"{base_key}:u",
            )
            assistant_turn = self.conversations.append_turn(
                conversation_id,
                role="assistant",
                provider=provider_id,
                model=model,
                content=response,
                idempotency_key=f"{base_key}:a",
            )
        except ConversationStoreError:
            yield self._error("history_unavailable", "The response was not saved; try again.")
            return
        except ChatServiceError:
            yield self._error("invalid_request", "The request could not be saved; try again.")
            return
        yield {
            "type": "done",
            "status": "completed",
            "conversation_id": conversation_id,
            "user_turn_id": user_turn["turn_id"],
            "assistant_turn_id": assistant_turn["turn_id"],
        }

    @staticmethod
    def _validate_request(
        conversation_id: str,
        message: str,
        provider_id: str,
        model: str,
        provider: Provider,
    ) -> None:
        if not isinstance(conversation_id, str) or not _IDENTIFIER.fullmatch(conversation_id):
            raise ChatServiceError("invalid conversation_id")
        if not isinstance(message, str) or not message or len(message.encode("utf-8")) > MAX_TURN_CONTENT_BYTES:
            raise ChatServiceError("invalid message")
        if not isinstance(provider_id, str) or not _IDENTIFIER.fullmatch(provider_id):
            raise ChatServiceError("invalid provider")
        if not isinstance(model, str) or len(model.encode("utf-8")) > _MAX_MODEL_BYTES:
            raise ChatServiceError("invalid model")
        if not callable(provider):
            raise ChatServiceError("provider is required")

    @staticmethod
    def _delta_content(delta: Any) -> str:
        if not isinstance(delta, Mapping) or not isinstance(delta.get("content"), str):
            raise ChatServiceError("provider delta is invalid")
        content = delta["content"]
        if not content:
            raise ChatServiceError("provider delta is empty")
        return content

    @staticmethod
    def _cancelled(cancel_event: Any) -> bool:
        return cancel_event is not None and bool(cancel_event.is_set())

    @staticmethod
    def _error(code: str, message: str) -> dict[str, Any]:
        return {"type": "error", "error": {"code": code, "message": message}}


__all__ = ["ChatService", "ChatServiceError", "Provider"]
