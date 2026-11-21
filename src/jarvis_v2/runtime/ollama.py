"""Explicit adapter from the local Ollama gateway to offline chat."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from ..backend.ollama_gateway import LocalOllamaGateway, OllamaGatewayError


class OllamaOfflineAdapter:
    """Use only the configured loopback model; never falls back remotely."""

    def __init__(self, gateway: LocalOllamaGateway) -> None:
        if not isinstance(gateway, LocalOllamaGateway):
            raise TypeError("a local Ollama gateway is required")
        self.gateway = gateway

    @property
    def model_alias(self) -> str:
        return self.gateway.profile.model.replace(":", "-")

    async def __call__(self, prompt: str, model: str) -> AsyncIterator[dict[str, Any]]:
        if model != self.model_alias:
            raise OllamaGatewayError("inference_model_not_allowlisted")
        response = await asyncio.to_thread(
            self.gateway.complete,
            prompt,
            model=self.gateway.profile.model,
        )
        if response.content:
            yield {"content": response.content}


__all__ = ["OllamaOfflineAdapter"]
