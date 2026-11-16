"""Bounded Guardian health evidence and dependency-aware restart decisions."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
import re
from typing import Any


MAX_RESTART_ATTEMPTS = 5
MAX_REASON_LENGTH = 256
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class GuardianHealthError(ValueError):
    """Raised when bounded health evidence is malformed."""


@dataclass(frozen=True)
class ProbeResult:
    """A bounded observation supplied by a trusted probe producer."""

    ok: bool
    reason: str = "ok"
    elapsed_ms: int = 0

    def __post_init__(self) -> None:
        if type(self.ok) is not bool:
            raise GuardianHealthError("probe result status must be boolean")
        if (
            type(self.reason) is not str
            or not self.reason
            or len(self.reason) > MAX_REASON_LENGTH
            or any(ord(char) < 32 for char in self.reason)
        ):
            raise GuardianHealthError("probe result reason is invalid")
        if type(self.elapsed_ms) is not int or not 0 <= self.elapsed_ms <= 60_000:
            raise GuardianHealthError("probe duration is outside the bounded range")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class HealthEvidence:
    """A read-only assessment; it never performs the requested restart."""

    component_id: str
    state: str
    reason: str
    dependencies_checked: bool
    restart_allowed: bool
    restart_attempts: int
    max_restart_attempts: int
    liveness: ProbeResult
    readiness: ProbeResult
    dependencies: tuple[tuple[str, ProbeResult], ...]

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["dependencies"] = {
            name: observation.as_dict()
            for name, observation in self.dependencies
        }
        result["liveness"] = self.liveness.as_dict()
        result["readiness"] = self.readiness.as_dict()
        return result


class GuardianHealthEvaluator:
    """Evaluate health only after dependency state has been made explicit."""

    def assess(
        self,
        component_id: str,
        *,
        liveness: ProbeResult,
        readiness: ProbeResult,
        required_dependencies: Iterable[str] = (),
        dependencies: Mapping[str, ProbeResult | bool] | None = None,
        restart_enabled: bool = True,
        restart_attempts: int = 0,
        max_restart_attempts: int = 3,
    ) -> HealthEvidence:
        component_id = _identifier(component_id, "component id")
        if not isinstance(liveness, ProbeResult) or not isinstance(readiness, ProbeResult):
            raise GuardianHealthError("liveness and readiness observations are required")
        if type(restart_enabled) is not bool:
            raise GuardianHealthError("restart policy must be boolean")
        if (
            type(restart_attempts) is not int
            or not 0 <= restart_attempts <= MAX_RESTART_ATTEMPTS
        ):
            raise GuardianHealthError("restart attempts are outside the bounded range")
        if (
            type(max_restart_attempts) is not int
            or not 0 <= max_restart_attempts <= MAX_RESTART_ATTEMPTS
            or restart_attempts > max_restart_attempts
        ):
            raise GuardianHealthError("restart budget is outside the bounded range")

        required = _identifiers(required_dependencies, "required dependencies")
        if dependencies is None:
            supplied = {}
        elif not isinstance(dependencies, Mapping):
            raise GuardianHealthError("dependencies must be a mapping")
        else:
            supplied = dict(dependencies)
        normalized_supplied = {
            _identifier(name, "dependency name"): _dependency_result(value)
            for name, value in supplied.items()
        }
        if set(normalized_supplied) != set(required):
            return HealthEvidence(
                component_id=component_id,
                state="dependency_unknown",
                reason="dependency_not_checked",
                dependencies_checked=False,
                restart_allowed=False,
                restart_attempts=restart_attempts,
                max_restart_attempts=max_restart_attempts,
                liveness=liveness,
                readiness=readiness,
                dependencies=tuple(
                    (name, normalized_supplied[name])
                    for name in sorted(normalized_supplied)
                ),
            )
        normalized = tuple(
            (name, normalized_supplied[name]) for name in required
        )
        failed = tuple(name for name, result in normalized if not result.ok)
        if failed:
            return self._evidence(
                component_id,
                state="dependency_wait",
                reason="dependency_failed",
                dependencies_checked=True,
                restart_allowed=False,
                restart_attempts=restart_attempts,
                max_restart_attempts=max_restart_attempts,
                liveness=liveness,
                readiness=readiness,
                dependencies=normalized,
            )
        if liveness.ok and readiness.ok:
            return self._evidence(
                component_id,
                state="healthy",
                reason="probes_healthy",
                dependencies_checked=True,
                restart_allowed=False,
                restart_attempts=restart_attempts,
                max_restart_attempts=max_restart_attempts,
                liveness=liveness,
                readiness=readiness,
                dependencies=normalized,
            )
        if not restart_enabled:
            reason = "restart_disabled"
            state = "degraded"
            allowed = False
        elif restart_attempts >= max_restart_attempts:
            reason = "restart_budget_exhausted"
            state = "quarantined"
            allowed = False
        else:
            reason = "probe_failed_after_dependency_check"
            state = "restartable"
            allowed = True
        return self._evidence(
            component_id,
            state=state,
            reason=reason,
            dependencies_checked=True,
            restart_allowed=allowed,
            restart_attempts=restart_attempts,
            max_restart_attempts=max_restart_attempts,
            liveness=liveness,
            readiness=readiness,
            dependencies=normalized,
        )

    @staticmethod
    def _evidence(component_id: str, **values: Any) -> HealthEvidence:
        return HealthEvidence(component_id=component_id, **values)


def _valid_identifier(value: str) -> bool:
    return bool(_IDENTIFIER.fullmatch(value))


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _valid_identifier(value):
        raise GuardianHealthError(f"invalid {label}")
    return value


def _identifiers(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, str):
        raise GuardianHealthError(f"{label} must be an iterable of identifiers")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise GuardianHealthError(f"{label} must be iterable") from exc
    try:
        unique = len(normalized) == len(set(normalized))
    except TypeError as exc:
        raise GuardianHealthError(f"{label} must contain strings") from exc
    if not unique:
        raise GuardianHealthError(f"{label} must not contain duplicates")
    return tuple(_identifier(value, label) for value in normalized)


def _dependency_result(value: ProbeResult | bool) -> ProbeResult:
    if isinstance(value, ProbeResult):
        return value
    if type(value) is bool:
        return ProbeResult(ok=value, reason="dependency_healthy" if value else "dependency_failed")
    raise GuardianHealthError("dependency observation is invalid")


__all__ = [
    "GuardianHealthError",
    "GuardianHealthEvaluator",
    "HealthEvidence",
    "MAX_RESTART_ATTEMPTS",
    "ProbeResult",
]
