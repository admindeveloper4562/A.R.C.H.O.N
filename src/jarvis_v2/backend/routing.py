"""Bounded provider routing with sticky affinity, outage fencing and budgets."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
import re
import time

from .provider_registry import ProviderRegistry, ProviderRequirements


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class RoutingError(ValueError):
    """Raised when a routing control value is invalid."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise RoutingError(f"invalid {label}")
    return value


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class StickyRouter:
    """Keep an affinity key on one provider until an explicit handoff."""

    def __init__(self, routes: Mapping[str, str] | None = None) -> None:
        self._routes: dict[str, str] = {}
        for affinity_key, provider_id in (routes or {}).items():
            self.bind(affinity_key, provider_id)

    def provider_for(self, affinity_key: str) -> str | None:
        return self._routes.get(_identifier(affinity_key, "affinity key"))

    def bind(self, affinity_key: str, provider_id: str, *, replace_existing: bool = False) -> str:
        affinity_key = _identifier(affinity_key, "affinity key")
        provider_id = _identifier(provider_id, "provider id")
        existing = self._routes.get(affinity_key)
        if existing is not None and existing != provider_id and not replace_existing:
            raise RoutingError("sticky provider conflict")
        self._routes[affinity_key] = provider_id
        return provider_id

    def handoff(self, affinity_key: str, provider_id: str) -> str:
        return self.bind(affinity_key, provider_id, replace_existing=True)

    def forget(self, affinity_key: str) -> None:
        self._routes.pop(_identifier(affinity_key, "affinity key"), None)


class CircuitBreaker:
    """Open after repeated failures and allow one timed half-open probe."""

    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        reset_timeout: float = 30.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if type(failure_threshold) is not int or failure_threshold < 1:
            raise RoutingError("failure threshold must be a positive integer")
        if type(reset_timeout) not in (int, float) or reset_timeout <= 0:
            raise RoutingError("reset timeout must be positive")
        if clock is not None and not callable(clock):
            raise RoutingError("clock must be callable")
        self.failure_threshold = failure_threshold
        self.reset_timeout = float(reset_timeout)
        self._clock = clock or time.monotonic
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at: float | None = None
        self._probe_in_flight = False

    @property
    def state(self) -> CircuitState:
        self._refresh()
        return self._state

    @property
    def failures(self) -> int:
        return self._failures

    def allow(self) -> bool:
        self._refresh()
        if self._state is CircuitState.CLOSED:
            return True
        if self._state is CircuitState.HALF_OPEN and not self._probe_in_flight:
            self._probe_in_flight = True
            return True
        return False

    def record_success(self) -> None:
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = None
        self._probe_in_flight = False

    def record_failure(self) -> None:
        self._probe_in_flight = False
        if self._state is CircuitState.HALF_OPEN:
            self._open()
            return
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._open()

    def reset(self) -> None:
        self.record_success()

    def _refresh(self) -> None:
        if (
            self._state is CircuitState.OPEN
            and self._opened_at is not None
            and self._clock() - self._opened_at >= self.reset_timeout
        ):
            self._state = CircuitState.HALF_OPEN
            self._probe_in_flight = False

    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()


class UsageBudget:
    """Bounded units that can be reserved or consumed by one provider."""

    def __init__(self, limit: int) -> None:
        if type(limit) is not int or limit < 0:
            raise RoutingError("usage limit must be a non-negative integer")
        self.limit = limit
        self._remaining = limit
        self._reserved = 0
        self._used = 0

    @property
    def remaining(self) -> int:
        return self._remaining

    @property
    def reserved(self) -> int:
        return self._reserved

    @property
    def used(self) -> int:
        return self._used

    def can_consume(self, units: int = 1) -> bool:
        self._validate_units(units)
        return self._remaining >= units

    def reserve(self, units: int = 1) -> bool:
        self._validate_units(units)
        if self._remaining < units:
            return False
        self._remaining -= units
        self._reserved += units
        return True

    def commit(self, units: int = 1) -> None:
        self._validate_units(units)
        if self._reserved < units:
            raise RoutingError("usage reservation is insufficient")
        self._reserved -= units
        self._used += units

    def consume(self, units: int = 1) -> bool:
        if not self.reserve(units):
            return False
        self.commit(units)
        return True

    def release(self, units: int = 1) -> None:
        self._validate_units(units)
        if self._reserved < units:
            raise RoutingError("usage reservation is insufficient")
        self._reserved -= units
        self._remaining += units

    @staticmethod
    def _validate_units(units: int) -> None:
        if type(units) is not int or units < 1:
            raise RoutingError("usage units must be a positive integer")


@dataclass(frozen=True)
class RouteDecision:
    """Auditable result of one route admission."""

    status: str
    affinity_key: str
    provider_id: str | None
    model: str | None
    reason: str


class GatewayRouter:
    """Combine registry checks with explicit sticky and handoff policy."""

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        budgets: Mapping[str, UsageBudget] | None = None,
        circuits: Mapping[str, CircuitBreaker] | None = None,
        sticky: StickyRouter | None = None,
    ) -> None:
        if not isinstance(registry, ProviderRegistry):
            raise RoutingError("provider registry is required")
        self.registry = registry
        self.budgets = dict(budgets or {})
        self.circuits = dict(circuits or {})
        if any(not isinstance(key, str) or not isinstance(value, UsageBudget) for key, value in self.budgets.items()):
            raise RoutingError("budgets must map provider ids to usage budgets")
        for provider_id, capability in registry.providers.items():
            self.budgets.setdefault(provider_id, UsageBudget(capability.quota_remaining))
        if any(not isinstance(key, str) or not isinstance(value, CircuitBreaker) for key, value in self.circuits.items()):
            raise RoutingError("circuits must map provider ids to circuit breakers")
        self.sticky = sticky or StickyRouter()

    def route(
        self,
        affinity_key: str,
        requirements: ProviderRequirements,
        *,
        allow_handoff: bool = False,
        handoff_provider: str | None = None,
    ) -> RouteDecision:
        affinity_key = _identifier(affinity_key, "affinity key")
        if not isinstance(requirements, ProviderRequirements):
            raise RoutingError("provider requirements are required")
        if type(allow_handoff) is not bool:
            raise RoutingError("handoff policy must be boolean")
        if handoff_provider is not None:
            handoff_provider = _identifier(handoff_provider, "handoff provider")
        sticky_provider = self.sticky.provider_for(affinity_key)
        if (
            sticky_provider is not None
            and requirements.requested_provider is not None
            and requirements.requested_provider != sticky_provider
            and not allow_handoff
        ):
            return self._paused(affinity_key, "sticky_provider_required")
        if sticky_provider is not None and not allow_handoff:
            candidates: Iterable[str | None] = (sticky_provider,)
        elif sticky_provider is not None:
            if handoff_provider is None:
                return self._paused(affinity_key, "handoff_target_required")
            candidates = (handoff_provider,)
        elif requirements.requested_provider is not None:
            candidates = (requirements.requested_provider, handoff_provider) if (
                allow_handoff
                and handoff_provider is not None
                and handoff_provider != requirements.requested_provider
            ) else (requirements.requested_provider,)
        elif handoff_provider is not None:
            candidates = (handoff_provider,)
        else:
            candidates = (None,)

        last_reason = "no_route"
        for provider_id in candidates:
            result = self._try_provider(affinity_key, requirements, provider_id)
            if result.status == "routed":
                if sticky_provider != result.provider_id:
                    self.sticky.bind(
                        affinity_key,
                        result.provider_id or "",
                        replace_existing=allow_handoff,
                    )
                return result
            last_reason = result.reason
        return self._paused(affinity_key, last_reason)

    def record_success(self, provider_id: str) -> None:
        self._circuit(provider_id).record_success()

    def record_failure(self, provider_id: str) -> None:
        self._circuit(provider_id).record_failure()

    def _try_provider(
        self,
        affinity_key: str,
        requirements: ProviderRequirements,
        provider_id: str | None,
    ) -> RouteDecision:
        scoped = requirements if provider_id is None else replace(requirements, requested_provider=provider_id)
        resolution = self.registry.negotiate(scoped)
        if resolution.status != "available" or resolution.selected_provider is None:
            return RouteDecision(
                "paused", affinity_key, None, None, resolution.reason,
            )
        selected = resolution.selected_provider
        circuit = self._circuit(selected)
        if not circuit.allow():
            return RouteDecision("paused", affinity_key, None, None, "circuit_open")
        budget = self.budgets.get(selected)
        if budget is not None and not budget.consume(requirements.quota_units):
            return RouteDecision("paused", affinity_key, None, None, "usage_budget_exhausted")
        return RouteDecision(
            "routed", affinity_key, selected, resolution.selected_model, "route_admitted",
        )

    def _circuit(self, provider_id: str) -> CircuitBreaker:
        return self.circuits.setdefault(provider_id, CircuitBreaker())

    @staticmethod
    def _paused(affinity_key: str, reason: str) -> RouteDecision:
        return RouteDecision("paused", affinity_key, None, None, reason)


__all__ = [
    "CircuitBreaker",
    "CircuitState",
    "GatewayRouter",
    "RouteDecision",
    "RoutingError",
    "StickyRouter",
    "UsageBudget",
]
