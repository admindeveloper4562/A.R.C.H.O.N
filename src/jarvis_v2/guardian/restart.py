"""Bounded local restart admission and cooldown accounting."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import re
import time
from typing import Any


MAX_RESTART_ATTEMPTS = 5
MAX_COOLDOWN_SECONDS = 3_600
MAX_REASON_LENGTH = 256
MAX_ATTEMPT_RECORDS = 256
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_OUTCOMES = frozenset({"pending", "succeeded", "failed", "unknown"})


class RestartBudgetError(ValueError):
    """Raised when restart admission or evidence is invalid."""


@dataclass(frozen=True)
class RestartAttempt:
    """A bounded restart record containing references, not process output."""

    generation: int
    attempt: int
    outcome: str
    reason: str
    evidence_ref: str
    requested_at: float
    completed_at: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RestartDecision:
    """The result of one deterministic restart admission check."""

    component_id: str
    generation: int
    state: str
    allowed: bool
    reason: str
    attempt: int
    attempts: int
    max_attempts: int
    cooldown_until: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RestartBudget:
    """Gate local restart requests without executing the restart itself.

    A request reserves one attempt and enters cooldown immediately. A pending
    request cannot be replayed until its outcome is recorded, which protects
    against duplicate effects after a controller crash. Attempts are scoped
    to a generation; ``new_generation`` is explicit and keeps prior records.
    """

    def __init__(
        self,
        component_id: str,
        *,
        enabled: bool = True,
        max_attempts: int = 3,
        cooldown_seconds: int = 30,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.component_id = _identifier(component_id, "component id")
        if type(enabled) is not bool:
            raise RestartBudgetError("restart policy must be boolean")
        if type(max_attempts) is not int or not 0 <= max_attempts <= MAX_RESTART_ATTEMPTS:
            raise RestartBudgetError("restart attempts are outside the bounded range")
        if (
            type(cooldown_seconds) is not int
            or not 1 <= cooldown_seconds <= MAX_COOLDOWN_SECONDS
        ):
            raise RestartBudgetError("restart cooldown is outside the bounded range")
        self.enabled = enabled
        self.max_attempts = max_attempts
        self.cooldown_seconds = cooldown_seconds
        self._clock = clock or time.monotonic
        self._generation = 0
        self._attempts = 0
        self._cooldown_until = 0.0
        self._pending: int | None = None
        self._last_outcome: str | None = None
        self._history: list[RestartAttempt] = []

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def history(self) -> tuple[RestartAttempt, ...]:
        return tuple(self._history)

    def snapshot(self, *, now: float | None = None) -> RestartDecision:
        """Return the current admission state without changing it."""
        current = self._now(now)
        state, reason = self._state(current)
        return RestartDecision(
            component_id=self.component_id,
            generation=self._generation,
            state=state,
            allowed=False,
            reason=reason,
            attempt=self._attempts,
            attempts=self._attempts,
            max_attempts=self.max_attempts,
            cooldown_until=self._cooldown_until,
        )

    def request(
        self,
        *,
        reason: str,
        evidence_ref: str = "",
        now: float | None = None,
    ) -> RestartDecision:
        """Reserve one restart if policy, cooldown and budget permit it."""
        reason = _reason(reason)
        evidence_ref = _evidence_ref(evidence_ref)
        current = self._now(now)
        state, diagnostic = self._state(current)
        if state != "ready":
            return self._decision(state, diagnostic, allowed=False)
        if len(self._history) >= MAX_ATTEMPT_RECORDS:
            raise RestartBudgetError("restart history limit reached")

        self._attempts += 1
        self._pending = self._attempts
        self._cooldown_until = current + self.cooldown_seconds
        self._last_outcome = "pending"
        self._append(
            RestartAttempt(
                generation=self._generation,
                attempt=self._attempts,
                outcome="pending",
                reason=reason,
                evidence_ref=evidence_ref,
                requested_at=current,
            )
        )
        return self._decision("cooldown", "restart_admitted", allowed=True)

    admit = request

    def record_outcome(
        self,
        attempt: int,
        outcome: str,
        *,
        evidence_ref: str = "",
        now: float | None = None,
    ) -> RestartDecision:
        """Close one admitted attempt; unknown keeps the budget fenced."""
        if type(attempt) is not int or attempt < 1 or attempt != self._pending:
            raise RestartBudgetError("restart attempt is not pending")
        if outcome not in _OUTCOMES.difference({"pending"}):
            raise RestartBudgetError("invalid restart outcome")
        evidence_ref = _evidence_ref(evidence_ref)
        current = self._now(now)
        index = self._history_index(attempt)
        previous = self._history[index]
        if evidence_ref == "":
            evidence_ref = previous.evidence_ref
        self._history[index] = RestartAttempt(
            generation=previous.generation,
            attempt=previous.attempt,
            outcome=outcome,
            reason=previous.reason,
            evidence_ref=evidence_ref,
            requested_at=previous.requested_at,
            completed_at=current,
        )
        self._pending = None
        self._last_outcome = outcome
        return self.snapshot(now=current)

    def resolve_unknown(
        self,
        attempt: int,
        outcome: str,
        *,
        evidence_ref: str,
        now: float | None = None,
    ) -> RestartDecision:
        """Resolve an earlier unknown outcome without replaying the attempt."""
        if type(attempt) is not int or attempt < 1:
            raise RestartBudgetError("restart attempt is invalid")
        if outcome not in {"succeeded", "failed"}:
            raise RestartBudgetError("unknown outcome needs a final result")
        evidence_ref = _evidence_ref(evidence_ref)
        if not evidence_ref:
            raise RestartBudgetError("unknown outcome needs evidence")
        index = self._history_index(attempt)
        previous = self._history[index]
        if previous.outcome != "unknown":
            raise RestartBudgetError("restart outcome is not unknown")
        current = self._now(now)
        self._history[index] = RestartAttempt(
            generation=previous.generation,
            attempt=previous.attempt,
            outcome=outcome,
            reason=previous.reason,
            evidence_ref=evidence_ref,
            requested_at=previous.requested_at,
            completed_at=current,
        )
        self._last_outcome = outcome
        return self.snapshot(now=current)

    def new_generation(self) -> RestartDecision:
        """Start a new component generation while retaining prior attempts."""
        if self._pending is not None:
            raise RestartBudgetError("pending restart must be reconciled")
        if self._last_outcome == "unknown":
            raise RestartBudgetError("unknown restart outcome requires resolution")
        self._generation += 1
        self._attempts = 0
        self._cooldown_until = 0.0
        self._last_outcome = None
        return self.snapshot()

    def _state(self, now: float) -> tuple[str, str]:
        if not self.enabled:
            return "disabled", "restart_disabled"
        if self._pending is not None:
            return "pending", "restart_attempt_unreconciled"
        if self._last_outcome == "succeeded":
            return "generation_complete", "generation_reset_required"
        if self._last_outcome == "unknown":
            return "needs_reconciliation", "restart_outcome_unknown"
        if self._attempts >= self.max_attempts:
            return "escalated", "restart_budget_exhausted"
        if now < self._cooldown_until:
            return "cooldown", "restart_cooldown_active"
        return "ready", "restart_available"

    def _decision(self, state: str, reason: str, *, allowed: bool) -> RestartDecision:
        return RestartDecision(
            component_id=self.component_id,
            generation=self._generation,
            state=state,
            allowed=allowed,
            reason=reason,
            attempt=self._attempts,
            attempts=self._attempts,
            max_attempts=self.max_attempts,
            cooldown_until=self._cooldown_until,
        )

    def _history_index(self, attempt: int) -> int:
        for index in range(len(self._history) - 1, -1, -1):
            record = self._history[index]
            if record.generation == self._generation and record.attempt == attempt:
                return index
        raise RestartBudgetError("restart attempt record is missing")

    def _append(self, record: RestartAttempt) -> None:
        self._history.append(record)

    def _now(self, value: float | None) -> float:
        current = self._clock() if value is None else value
        if isinstance(current, bool) or not isinstance(current, (int, float)):
            raise RestartBudgetError("restart clock value is invalid")
        if current < 0:
            raise RestartBudgetError("restart clock value is invalid")
        return float(current)


LocalRestartBudget = RestartBudget


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise RestartBudgetError(f"invalid {label}")
    return value


def _reason(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_REASON_LENGTH
        or any(ord(char) < 32 for char in value)
    ):
        raise RestartBudgetError("invalid restart reason")
    return value


def _evidence_ref(value: str) -> str:
    if value == "":
        return value
    return _identifier(value, "evidence reference")


__all__ = [
    "LocalRestartBudget",
    "MAX_ATTEMPT_RECORDS",
    "MAX_COOLDOWN_SECONDS",
    "MAX_RESTART_ATTEMPTS",
    "RestartAttempt",
    "RestartBudget",
    "RestartBudgetError",
    "RestartDecision",
]
