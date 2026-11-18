"""Resource-aware local model routing.

The router coordinates requests; it deliberately does not manage the Colibri
process or claim that a model is available until the provider reports it.
"""
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Any

from .colibri import ColibriClient


_HEAVY_MODEL = re.compile(r"(?:30b|32b|70b|72b|110b|coder[-_]?30)", re.I)


@dataclass(frozen=True)
class RouterConfig:
    request_budget_seconds: float = 60.0


@dataclass
class RouterTelemetry:
    requests: int = 0
    completed: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0
    by_model: dict[str, int] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        average = self.total_latency_ms / self.completed if self.completed else 0.0
        return {"requests": self.requests, "completed": self.completed,
                "failed": self.failed, "average_latency_ms": round(average, 2),
                "by_model": dict(self.by_model)}


class ResourceAwareRouter:
    """Route local requests while preventing concurrent heavy model work."""

    def __init__(self, client: ColibriClient | None = None,
                 config: RouterConfig | None = None) -> None:
        self.client = client or ColibriClient()
        self.config = config or RouterConfig()
        if self.config.request_budget_seconds <= 0:
            raise ValueError("request_budget_seconds must be positive")
        self._heavy_slot = asyncio.Lock()
        self.telemetry = RouterTelemetry()

    @staticmethod
    def is_heavy(model: str) -> bool:
        return bool(_HEAVY_MODEL.search(model))

    def choose_model(self, requested: str | None = None) -> str:
        status = self.client.status()
        available = {item["id"] for item in status.get("models", [])
                     if isinstance(item, dict) and isinstance(item.get("id"), str)}
        selected = requested or status.get("preferred_model")
        if not selected or selected not in available:
            raise ConnectionError("requested local model is unavailable")
        return selected

    async def complete(self, message: str, model: str | None = None) -> dict:
        selected = self.choose_model(model)
        self.telemetry.requests += 1
        started = time.monotonic()
        lock = self._heavy_slot if self.is_heavy(selected) else _NullAsyncLock()
        try:
            async with lock:
                result = await asyncio.wait_for(
                    self.client.complete_async(message, selected),
                    timeout=self.config.request_budget_seconds,
                )
            self.telemetry.completed += 1
            self.telemetry.total_latency_ms += (time.monotonic() - started) * 1000
            self.telemetry.by_model[selected] = self.telemetry.by_model.get(selected, 0) + 1
            return result
        except BaseException:
            self.telemetry.failed += 1
            raise

    def status(self) -> dict[str, Any]:
        result = self.client.status()
        result["router"] = self.telemetry.snapshot()
        result["heavy_models_exclusive"] = True
        result["request_budget_seconds"] = self.config.request_budget_seconds
        return result


class _NullAsyncLock:
    async def __aenter__(self) -> "_NullAsyncLock":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None
