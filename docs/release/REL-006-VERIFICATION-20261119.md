# REL-006 Verification

## Scope

REL-006 verifies that Guardian priority is non-preemptive: an active inference
continues to its normal completion boundary, Guardian reserves the next
compatible free slot, and ordinary new inference waits until that reservation
is released.

## Evidence

- Source/base SHA: `68a38a973e9d0cb134cb96a03de6ddce0b8f3db4`
- Candidate SHA: Master-bound in the builder submission receipt.
- Test: `tests/test_rel006_guardian_priority.py`
- Test result: PASS locally; independent Docker QC pending.
- External provider/device evidence: not required for this deterministic queue contract.

## Result

The test uses the production `ResourceBudget` and `SlotPriority` implementation,
not a replacement scheduler. It records that the active Core holder is not
preempted, the Guardian obtains the next compatible slot, and a competing
worker cannot claim that slot while Guardian owns it. The next compatible
worker is admitted only after Guardian finishes. Independent, non-overlapping
slots remain governed by the normal budget.
