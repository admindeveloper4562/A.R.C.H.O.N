"""SDA transition readiness: advisory only. Actual fencing/migration is owner-gated."""
from __future__ import annotations
from dataclasses import dataclass, asdict


# These keys are part of the handoff evidence contract.  Keep them stable so
# callers can persist and compare reports without relying on display text.
EVIDENCE_KEYS = (
    "external_astra_healthy",
    "native_sda_real_test_passed",
    "qc_independent",
    "queue_checkpoint_verified",
    "one_writer_fencing_tested",
    "guardian_out_of_process_verified",
    "rollback_drill_passed",
    "owner_approved",
)


@dataclass(frozen=True)
class HandoffEvidence:
    external_astra_healthy: bool = False
    native_sda_real_test_passed: bool = False
    qc_independent: bool = False
    queue_checkpoint_verified: bool = False
    one_writer_fencing_tested: bool = False
    guardian_out_of_process_verified: bool = False
    rollback_drill_passed: bool = False
    owner_approved: bool = False

    def report(self) -> dict:
        evidence=asdict(self)
        missing_evidence_keys = [
            key for key in EVIDENCE_KEYS if not evidence[key]
        ]
        return {
            "ready_for_controlled_cutover": not missing_evidence_keys,
            "missing": missing_evidence_keys,
            "missing_evidence_keys": missing_evidence_keys,
            "evidence": {key: evidence[key] for key in EVIDENCE_KEYS},
            "owner_approval_required": True,
            # Native SDA is advisory in shadow mode.  These are deliberately
            # constants: evidence cannot grant it live ownership or promotion.
            "shadow_mode": True,
            "claims_live_task_ownership": False,
            "self_promoted": False,
            "actual_cutover_performed": False,
        }
