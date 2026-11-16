"""Explicit offline model selection with a safe paused state."""
from __future__ import annotations

from collections.abc import AsyncIterator, Callable
import re
from typing import Any

from jarvis_v2.core import ModelPolicy, ModelPolicyError

from .chat import ChatService, ChatServiceError


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class OfflineChatServiceError(ValueError):
    """Raised when offline chat configuration is invalid."""


LocalAdapter = Callable[[str, str], Any]


class OfflineChatService:
    """Use a configured local adapter, or pause without inventing an answer."""

    def __init__(
        self,
        chat: ChatService,
        available_models: set[str] | frozenset[str],
        *,
        adapter: LocalAdapter | None = None,
        fallback_model: str | None = None,
        allow_fallback: bool = False,
        provider_id: str = "local",
    ) -> None:
        if not isinstance(chat, ChatService):
            raise OfflineChatServiceError("chat service is required")
        if not isinstance(allow_fallback, bool):
            raise OfflineChatServiceError("fallback policy must be boolean")
        if not isinstance(provider_id, str) or not _IDENTIFIER.fullmatch(provider_id):
            raise OfflineChatServiceError("invalid provider")
        try:
            self.policy = ModelPolicy(available_models)
        except ModelPolicyError as exc:
            raise OfflineChatServiceError("invalid local model policy") from exc
        if fallback_model is not None:
            try:
                ModelPolicy({fallback_model})
            except ModelPolicyError as exc:
                raise OfflineChatServiceError("invalid fallback model") from exc
        if adapter is not None and not callable(adapter):
            raise OfflineChatServiceError("local adapter must be callable")
        self.chat = chat
        self.adapter = adapter
        self.fallback_model = fallback_model
        self.allow_fallback = allow_fallback
        self.provider_id = provider_id

    async def stream(
        self,
        conversation_id: str,
        message: str,
        requested_model: str,
        *,
        cancel_event: Any = None,
        idempotency_key: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Yield a pause event until a registered model and adapter are available."""
        try:
            resolution = self.policy.resolve(
                requested_model,
                fallback=self.fallback_model,
                allow_fallback=self.allow_fallback,
            )
        except ModelPolicyError:
            yield self._paused(requested_model, None, "invalid_model", "The requested model is invalid.")
            return
        if resolution.status == "blocked" or resolution.selected is None:
            yield self._paused(
                resolution.requested,
                None,
                resolution.reason,
                "The requested model is unavailable; no answer was generated.",
            )
            return
        adapter = self.adapter
        selected_model = resolution.selected
        if adapter is None or selected_model is None:
            yield self._paused(
                resolution.requested,
                selected_model,
                "adapter_unavailable",
                "No authorized local adapter is available; no answer was generated.",
            )
            return
        if resolution.status == "fallback":
            yield {
                "type": "fallback",
                "status": "fallback",
                "requested_model": resolution.requested,
                "selected_model": selected_model,
                "reason": resolution.reason,
            }

        def provider(prompt: str) -> Any:
            return adapter(prompt, selected_model)

        try:
            async for event in self.chat.stream(
                conversation_id,
                message,
                provider,
                provider_id=self.provider_id,
                model=selected_model,
                cancel_event=cancel_event,
                idempotency_key=idempotency_key,
            ):
                yield event
        except ChatServiceError:
            yield self._paused(
                resolution.requested,
                selected_model,
                "chat_unavailable",
                "Offline chat is unavailable; no answer was generated.",
            )

    @staticmethod
    def _paused(
        requested_model: str,
        selected_model: str | None,
        reason: str,
        message: str,
    ) -> dict[str, Any]:
        return {
            "type": "paused",
            "status": "paused",
            "requested_model": requested_model,
            "selected_model": selected_model,
            "reason": reason,
            "message": message,
        }


__all__ = ["LocalAdapter", "OfflineChatService", "OfflineChatServiceError"]
