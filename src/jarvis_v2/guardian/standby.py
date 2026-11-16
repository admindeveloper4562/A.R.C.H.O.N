"""Explicit-capacity, schema-compatible Guardian standby admission."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from .controller import Runner, TrustedControllerManager


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")


class StandbyError(ValueError):
    """Raised when a standby cannot be admitted or started."""


class StandbyLauncher:
    """Start one pinned standby only after explicit compatibility checks.

    Capacity is deliberately an input. This class never probes, reserves or
    assumes provider capacity, and it never changes routing or control markers.
    """

    def __init__(
        self,
        executable: str | Path,
        expected_sha256: str,
        *,
        trusted_root: str | Path,
        component_schema: str,
        state_schema: str,
        control_dir: str | Path | None = None,
        command: tuple[str, ...] | None = None,
        runner: Runner | None = None,
    ) -> None:
        if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
            raise StandbyError("invalid standby artifact digest")
        self.component_schema = _value(component_schema, "component schema")
        self.state_schema = _value(state_schema, "state schema")
        self._manager = TrustedControllerManager(
            executable,
            expected_sha256,
            trusted_root=trusted_root,
            control_dir=control_dir,
            command=command,
            runner=runner,
        )

    def inspect(
        self,
        *,
        component_schema: str,
        state_schema: str,
        capacity_available: bool,
    ) -> dict[str, Any]:
        """Return a bounded start decision without launching the standby."""
        if type(capacity_available) is not bool:
            raise StandbyError("capacity availability must be explicit")
        reasons: list[str] = []
        if component_schema != self.component_schema:
            reasons.append("component_schema_mismatch")
        if state_schema != self.state_schema:
            reasons.append("state_schema_mismatch")
        if not capacity_available:
            reasons.append("capacity_unavailable")
        verification = self._manager.verify() if not reasons else {
            "trusted": False,
            "reason": "compatibility_or_capacity_failed",
        }
        if not verification.get("trusted"):
            reasons.append(str(verification.get("reason", "standby_untrusted")))
        return {
            "eligible": not reasons,
            "reasons": reasons,
            "component_schema": self.component_schema,
            "state_schema": self.state_schema,
            "capacity_required": True,
            "automatic_capacity": False,
            "isolated": True,
            "started": False,
            "verification": verification,
        }

    def start(
        self,
        *,
        component_schema: str,
        state_schema: str,
        capacity_available: bool,
    ) -> dict[str, Any]:
        """Launch the verified standby through the existing trusted manager."""
        decision = self.inspect(
            component_schema=component_schema,
            state_schema=state_schema,
            capacity_available=capacity_available,
        )
        if not decision["eligible"]:
            raise StandbyError(",".join(decision["reasons"]))
        started = self._manager.restart()
        return {
            **started,
            "eligible": True,
            "isolated": True,
            "capacity_required": True,
            "automatic_capacity": False,
            "component_schema": self.component_schema,
            "state_schema": self.state_schema,
        }


def _value(value: str, label: str) -> str:
    if not isinstance(value, str) or not _VALUE.fullmatch(value):
        raise StandbyError(f"invalid {label}")
    return value


__all__ = ["StandbyError", "StandbyLauncher"]
