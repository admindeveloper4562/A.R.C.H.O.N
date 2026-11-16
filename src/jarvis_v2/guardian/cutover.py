"""Readiness-gated writer cutover and explicit failback coordination."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any

from .fencing import WriterFence, WriterLease


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
_CONTROLS = ("STOP", "PAUSE", "PAUSED_QUOTA")
_FAILURES = frozenset({"failed", "unhealthy"})


class CutoverError(ValueError):
    """Raised when a guarded cutover or failback is not admissible."""


@dataclass(frozen=True)
class CutoverDecision:
    """Bounded readiness result; no route or writer is changed by ``prepare``."""

    state: str
    allowed: bool
    reasons: tuple[str, ...]
    component_schema: str
    state_schema: str
    artifact_sha256: str
    capacity_required: bool = True
    route_switched: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["reasons"] = list(self.reasons)
        return result


class CutoverCoordinator:
    """Coordinate one-writer handoff without owning deployment or routing."""

    def __init__(
        self,
        fence: WriterFence,
        *,
        component_schema: str,
        state_schema: str,
        expected_artifact_sha256: str,
        control_dir: str | Path | None = None,
    ) -> None:
        if not isinstance(fence, WriterFence):
            raise CutoverError("writer fence is required")
        self.fence = fence
        self.component_schema = _value(component_schema, "component schema")
        self.state_schema = _value(state_schema, "state schema")
        if not isinstance(expected_artifact_sha256, str) or not _SHA256.fullmatch(
            expected_artifact_sha256
        ):
            raise CutoverError("invalid expected artifact digest")
        self.expected_artifact_sha256 = expected_artifact_sha256
        self.control_dir = None if control_dir is None else Path(control_dir)

    def prepare(
        self, readiness: Mapping[str, object], *, capacity_available: bool
    ) -> CutoverDecision:
        """Validate sync/readiness without changing the current authority."""
        if not isinstance(readiness, Mapping):
            raise CutoverError("readiness must be a mapping")
        if type(capacity_available) is not bool:
            raise CutoverError("capacity availability must be explicit")
        reasons: list[str] = []
        component_schema = readiness.get("component_schema")
        state_schema = readiness.get("state_schema")
        artifact = readiness.get("artifact_sha256")
        if component_schema != self.component_schema:
            reasons.append("component_schema_mismatch")
        if state_schema != self.state_schema:
            reasons.append("state_schema_mismatch")
        if not isinstance(artifact, str) or not _SHA256.fullmatch(artifact):
            reasons.append("invalid_artifact_digest")
        elif artifact != self.expected_artifact_sha256:
            reasons.append("artifact_digest_mismatch")
        if readiness.get("sync_verified") is not True:
            reasons.append("sync_not_verified")
        if readiness.get("rollback_ready") is not True:
            reasons.append("rollback_not_ready")
        if readiness.get("health") != "healthy":
            reasons.append("standby_not_healthy")
        if readiness.get("route_gate") != {
            "mode": "inactive",
            "single_writer_fenced": True,
        }:
            reasons.append("route_gate_not_closed")
        if not capacity_available:
            reasons.append("capacity_unavailable")
        reasons.extend(self._active_controls())
        return CutoverDecision(
            state="ready" if not reasons else "degraded",
            allowed=not reasons,
            reasons=tuple(reasons),
            component_schema=self.component_schema,
            state_schema=self.state_schema,
            artifact_sha256=artifact if isinstance(artifact, str) else "",
        )

    def cutover(
        self,
        current: WriterLease,
        next_owner_id: str,
        readiness: Mapping[str, object],
        *,
        capacity_available: bool,
        ttl_seconds: int = 60,
    ) -> dict[str, Any]:
        """Handoff one fenced writer only after a complete ready decision."""
        decision = self.prepare(readiness, capacity_available=capacity_available)
        if not decision.allowed:
            raise CutoverError(",".join(decision.reasons))
        next_lease = self.fence.handoff(current, next_owner_id, ttl_seconds=ttl_seconds)
        return {
            "state": "cutover_complete",
            "route_switched": False,
            "old_writer_fenced": True,
            "new_lease": next_lease.as_dict(),
            "readiness": decision.as_dict(),
        }

    def failback(
        self,
        current: WriterLease,
        previous_owner_id: str,
        readiness: Mapping[str, object],
        *,
        capacity_available: bool,
        ttl_seconds: int = 60,
    ) -> dict[str, Any]:
        """Handoff back only for an observed failed or unhealthy standby."""
        if not isinstance(readiness, Mapping) or readiness.get("health") not in _FAILURES:
            raise CutoverError("failback requires a failed or unhealthy standby")
        if readiness.get("component_schema") != self.component_schema:
            raise CutoverError("component_schema_mismatch")
        if readiness.get("state_schema") != self.state_schema:
            raise CutoverError("state_schema_mismatch")
        if readiness.get("artifact_sha256") != self.expected_artifact_sha256:
            raise CutoverError("artifact_digest_mismatch")
        if readiness.get("route_gate") != {
            "mode": "inactive",
            "single_writer_fenced": True,
        }:
            raise CutoverError("route_gate_not_closed")
        if not capacity_available:
            raise CutoverError("capacity_unavailable")
        controls = self._active_controls()
        if controls:
            raise CutoverError(",".join(controls))
        next_lease = self.fence.handoff(current, previous_owner_id, ttl_seconds=ttl_seconds)
        return {
            "state": "failback_complete",
            "route_switched": False,
            "failed_writer_fenced": True,
            "new_lease": next_lease.as_dict(),
            "reason": "standby_health_failed",
        }

    def _active_controls(self) -> tuple[str, ...]:
        if self.control_dir is None:
            return ()
        return tuple(name for name in _CONTROLS if (self.control_dir / name).exists())


def _value(value: str, label: str) -> str:
    if not isinstance(value, str) or not _VALUE.fullmatch(value):
        raise CutoverError(f"invalid {label}")
    return value


__all__ = ["CutoverError", "CutoverDecision", "CutoverCoordinator"]
