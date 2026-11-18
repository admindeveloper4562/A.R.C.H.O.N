# REL-006 Acceptance Matrix

Task: Verify Guardian next-slot non-preemptive priority under live workload
Base source SHA: `68a38a973e9d0cb134cb96a03de6ddce0b8f3db4`
Candidate SHA: recorded by the Main Codex → Master submission receipt

| Child | Requirement | Observable evidence | Result |
| --- | --- | --- | --- |
| REL-006.S01 | Convert the acceptance into measurable assertions. | The test asserts active-slot preservation, Guardian reservation, worker wait, and release ordering. | PASS |
| REL-006.S02 | Use repeatable sanitized fixtures. | `ResourceBudget(2, slots=("slot-0", "slot-1"))` uses only deterministic in-memory state. | PASS |
| REL-006.S03 | Run the required local verification. | `tests/test_rel006_guardian_priority.py` runs against the real Core budget and Guardian priority classes. | PASS |
| REL-006.S04 | Cover the non-preemptive boundary. | The test proves active work remains held and a competing worker for the Guardian-compatible slot cannot bypass its reservation. | PASS |
| REL-006.S05 | Bind the result to source and artifact evidence. | The Master submission and independent QC receipts bind the candidate, test artifact and integration SHA. | PENDING QC |

This qualification verifies deterministic scheduling. It does not claim a live provider or hardware benchmark.
