"""Deterministic provider capability registration and pre-dispatch checks."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re
from types import MappingProxyType

from .event_bus import PRIVACY_SCOPES


LOCALITIES = frozenset({"local", "remote"})
REQUEST_LOCALITIES = frozenset({"any", *LOCALITIES})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_TOOL = re.compile(r"^[a-z][a-z0-9_.:-]{0,63}$")


class ProviderRegistryError(ValueError):
    """Raised when a provider capability or dispatch request is invalid."""


def _bounded(value: str, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ProviderRegistryError(f"invalid {label}")
    return value


def _tools(values: Iterable[str]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise ProviderRegistryError("tools must be a collection")
    result = frozenset(_bounded(value, _TOOL, "tool") for value in values)
    if len(result) > 64:
        raise ProviderRegistryError("too many tools")
    return result


@dataclass(frozen=True)
class ProviderCapability:
    """The bounded capabilities advertised by one provider/model pair."""

    provider_id: str
    model: str
    context_window: int
    tools: frozenset[str]
    privacy_scopes: frozenset[str]
    locality: str
    quota_remaining: int
    available: bool = True

    def __post_init__(self) -> None:
        _bounded(self.provider_id, _IDENTIFIER, "provider_id")
        _bounded(self.model, _MODEL, "model")
        if type(self.context_window) is not int or not 1 <= self.context_window <= 1_000_000:
            raise ProviderRegistryError("context window is outside the bounded range")
        if not isinstance(self.tools, frozenset) or not self.tools <= frozenset(_bounded(item, _TOOL, "tool") for item in self.tools):
            raise ProviderRegistryError("provider tools are invalid")
        if not isinstance(self.privacy_scopes, frozenset) or not self.privacy_scopes or not self.privacy_scopes <= PRIVACY_SCOPES:
            raise ProviderRegistryError("provider privacy scopes are invalid")
        if self.locality not in LOCALITIES:
            raise ProviderRegistryError("provider locality is invalid")
        if type(self.quota_remaining) is not int or self.quota_remaining < 0:
            raise ProviderRegistryError("provider quota is invalid")
        if type(self.available) is not bool:
            raise ProviderRegistryError("provider availability is invalid")


@dataclass(frozen=True)
class ProviderRequirements:
    """Requirements that must pass before a dispatch can be admitted."""

    context_tokens: int
    tools: frozenset[str]
    privacy_scope: str
    locality: str = "any"
    quota_units: int = 1
    requested_provider: str | None = None
    requested_model: str | None = None

    def __post_init__(self) -> None:
        if type(self.context_tokens) is not int or not 1 <= self.context_tokens <= 1_000_000:
            raise ProviderRegistryError("context requirement is outside the bounded range")
        if not isinstance(self.tools, frozenset):
            raise ProviderRegistryError("required tools must be a frozenset")
        _tools(self.tools)
        if self.privacy_scope not in PRIVACY_SCOPES:
            raise ProviderRegistryError("privacy scope is invalid")
        if self.locality not in REQUEST_LOCALITIES:
            raise ProviderRegistryError("requested locality is invalid")
        if type(self.quota_units) is not int or not 1 <= self.quota_units <= 1_000_000:
            raise ProviderRegistryError("quota requirement is outside the bounded range")
        if self.requested_provider is not None:
            _bounded(self.requested_provider, _IDENTIFIER, "requested provider")
        if self.requested_model is not None:
            _bounded(self.requested_model, _MODEL, "requested model")


@dataclass(frozen=True)
class ProviderResolution:
    """The auditable result of one capability negotiation."""

    requested_provider: str | None
    requested_model: str | None
    selected_provider: str | None
    selected_model: str | None
    status: str
    reason: str


class ProviderRegistry:
    """Hold immutable provider snapshots and select only compatible entries."""

    def __init__(self, capabilities: Iterable[ProviderCapability] = ()) -> None:
        self._providers: dict[str, ProviderCapability] = {}
        for capability in capabilities:
            self.register(capability)

    @property
    def providers(self) -> MappingProxyType:
        return MappingProxyType(self._providers)

    def register(self, capability: ProviderCapability) -> ProviderCapability:
        if not isinstance(capability, ProviderCapability):
            raise ProviderRegistryError("provider capability is required")
        existing = self._providers.get(capability.provider_id)
        if existing is not None and existing != capability:
            raise ProviderRegistryError("provider capability conflict")
        self._providers[capability.provider_id] = capability
        return capability

    def negotiate(self, requirements: ProviderRequirements) -> ProviderResolution:
        if not isinstance(requirements, ProviderRequirements):
            raise ProviderRegistryError("provider requirements are required")
        candidates = list(self._providers.values())
        if requirements.requested_provider is not None:
            candidates = [item for item in candidates if item.provider_id == requirements.requested_provider]
            if not candidates:
                return self._blocked(requirements, "requested_provider_unavailable")
        if requirements.requested_model is not None:
            candidates = [item for item in candidates if item.model == requirements.requested_model]
            if not candidates:
                return self._blocked(requirements, "requested_model_unavailable")
        for capability in sorted(candidates, key=lambda item: item.provider_id):
            reason = self._incompatibility(capability, requirements)
            if reason is None:
                return ProviderResolution(
                    requirements.requested_provider, requirements.requested_model,
                    capability.provider_id, capability.model, "available", "capabilities_satisfied",
                )
        return self._blocked(requirements, self._first_reason(candidates, requirements))

    @staticmethod
    def _incompatibility(capability: ProviderCapability, requirements: ProviderRequirements) -> str | None:
        if not capability.available:
            return "provider_unavailable"
        if capability.context_window < requirements.context_tokens:
            return "context_window_insufficient"
        if not requirements.tools <= capability.tools:
            return "tool_support_missing"
        if requirements.privacy_scope not in capability.privacy_scopes:
            return "privacy_scope_unavailable"
        if requirements.locality != "any" and capability.locality != requirements.locality:
            return "locality_mismatch"
        if capability.quota_remaining < requirements.quota_units:
            return "quota_unavailable"
        return None

    @classmethod
    def _blocked(cls, requirements: ProviderRequirements, reason: str) -> ProviderResolution:
        return ProviderResolution(
            requirements.requested_provider, requirements.requested_model,
            None, None, "blocked", reason,
        )

    @classmethod
    def _first_reason(cls, candidates: list[ProviderCapability], requirements: ProviderRequirements) -> str:
        if not candidates:
            return "no_provider_registered"
        return cls._incompatibility(candidates[0], requirements) or "no_compatible_provider"


__all__ = [
    "LOCALITIES",
    "ProviderCapability",
    "ProviderRegistry",
    "ProviderRegistryError",
    "ProviderRequirements",
    "ProviderResolution",
    "REQUEST_LOCALITIES",
]
