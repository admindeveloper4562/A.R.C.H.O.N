"""SDA transition readiness: advisory only. Actual fencing/migration is owner-gated."""
from __future__ import annotations
from dataclasses import dataclass, asdict

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
        failures=[name for name,val in evidence.items() if not val]
        return {"ready_for_controlled_cutover":not failures,"missing":failures,"actual_cutover_performed":False}
