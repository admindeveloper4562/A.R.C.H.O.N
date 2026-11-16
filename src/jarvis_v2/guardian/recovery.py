"""Independent Guardian boot, bounded recovery and safe-mode decisions."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .controller import GuardianControllerError, TrustedControllerManager
from .restart import RestartBudget, RestartBudgetError


_CONTROL_MARKERS = ("STOP", "PAUSE", "PAUSED_QUOTA")


class RecoveryError(ValueError):
    """Raised when a recovery request is malformed."""


class GuardianRecoveryController:
    """Attempt one verified boot without clearing controls or self-retrying."""

    def __init__(
        self,
        manager: TrustedControllerManager,
        budget: RestartBudget,
        *,
        control_dir: str | Path | None = None,
    ) -> None:
        if not isinstance(manager, TrustedControllerManager):
            raise RecoveryError("trusted controller manager is required")
        if not isinstance(budget, RestartBudget):
            raise RecoveryError("restart budget is required")
        self.manager = manager
        self.budget = budget
        self.control_dir = None if control_dir is None else Path(control_dir)

    def boot(
        self,
        *,
        reason: str,
        evidence_ref: str = "",
        approval_required: bool = False,
    ) -> dict[str, Any]:
        """Perform at most one start attempt and return a redacted decision."""
        if not isinstance(reason, str) or not reason or len(reason) > 256:
            raise RecoveryError("recovery reason is invalid")
        if not isinstance(evidence_ref, str) or len(evidence_ref) > 128:
            raise RecoveryError("recovery evidence reference is invalid")
        if type(approval_required) is not bool:
            raise RecoveryError("approval state must be boolean")

        controls = self._controls()
        if controls or approval_required:
            return self._safe_mode(
                "owner_control_active" if controls else "approval_required",
                controls,
                approval_required,
            )

        try:
            decision = self.budget.request(reason=reason, evidence_ref=evidence_ref)
        except RestartBudgetError:
            return self._safe_mode("restart_budget_error", controls, approval_required)
        if not decision.allowed:
            return self._safe_mode(decision.reason, controls, approval_required)

        try:
            started = self.manager.restart()
        except GuardianControllerError:
            self.budget.record_outcome(
                decision.attempt, "failed", evidence_ref=evidence_ref
            )
            state = "safe_mode" if self.budget.snapshot().state == "escalated" else "degraded"
            return {
                "state": state,
                "started": False,
                "reason": "controller_start_failed",
                "attempt": decision.attempt,
                "control_markers": list(controls),
                "approval_required": approval_required,
            }

        self.budget.record_outcome(
            decision.attempt, "succeeded", evidence_ref=evidence_ref
        )
        return {
            "state": "running",
            "started": True,
            "reason": "controller_started",
            "attempt": decision.attempt,
            "controller": started,
            "control_markers": list(controls),
            "approval_required": approval_required,
        }

    def _controls(self) -> tuple[str, ...]:
        if self.control_dir is None:
            return ()
        return tuple(name for name in _CONTROL_MARKERS if (self.control_dir / name).exists())

    @staticmethod
    def _safe_mode(reason: str, controls: tuple[str, ...], approval: bool) -> dict[str, Any]:
        return {
            "state": "safe_mode",
            "started": False,
            "reason": reason,
            "control_markers": list(controls),
            "approval_required": approval,
        }


__all__ = ["RecoveryError", "GuardianRecoveryController"]
