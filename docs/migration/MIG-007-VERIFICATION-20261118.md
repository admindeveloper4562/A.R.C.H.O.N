# MIG-007 Verification — native SDA read-only shadow boundary

Candidate base: `5fa4eb63cf4abcbb69a8d9d49f8e4e3e623c1a7e`.

Parent acceptance: **Shadow consumes sanitized events; cannot claim/write real
tasks or protected refs.**

This qualification exercises the existing advisory handoff contract in
`src/jarvis_v2/sda/handoff.py`. It does not cut over native SDA, claim live
tasks, write the canonical queue, modify `develop`/`main`, or treat a model
report as an authorization.

## Sanitized shadow input

The qualification packet contains only bounded metadata:

```json
{
  "event_id": "shadow-mig-007-001",
  "event_type": "task_snapshot",
  "task_id": "MIG-007",
  "status": "observed",
  "source_sha": "5fa4eb63cf4abcbb69a8d9d49f8e4e3e623c1a7e",
  "payload_sha256": "not-retained-in-report"
}
```

No task description, credential, private prompt, raw model output or live
database content is copied into the shadow packet. The event is observation
input only; it is not an ownership lease or a write request.

## Acceptance matrix

| Clause | Evidence | Result |
| --- | --- | --- |
| Consume sanitized shadow observations | The existing handoff test exercises the bounded shadow report contract with no live task payload or write capability. | PASS |
| Cannot claim live task ownership | `HandoffEvidence.report()` hard-codes `claims_live_task_ownership: false`; the shadow test asserts it. | PASS |
| Cannot promote itself | The report hard-codes `self_promoted: false`; the shadow test asserts it. | PASS |
| Cannot perform cutover | The report hard-codes `actual_cutover_performed: false`; the shadow test asserts it. | PASS |
| Owner approval remains separate | All evidence flags still require `owner_approved`; the test asserts the missing owner gate prevents readiness. | PASS |
| Does not write protected refs or the live queue | The candidate changes only this verification document; no SDA runtime, SQLite ledger, Git ref, or protected policy file is modified. | PASS |

## Checks

- `PYTHONPATH=src python3 -m unittest discover -s tests -p
  'test_sda_shadow_handoff.py'`: 3 passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`:
  522 passed.
- `python3 tools/verify_foundation.py`: passed — ten modules,
  ARCHON/AEGIS/ATLAS identities, independent monitor, Business excluded.
- `git diff --check`: passed.
- The task worktree was created from the verified integration SHA above and
  the submitted candidate is a real Git commit.

## Negative and restart boundary

The shadow report is advisory and reconstructible: it contains no lease,
claim, queue-transition or promotion operation. Re-running the focused test
does not create a task row or change a Git ref. Existing Astra controls remain
the only authority for task ownership, QC, merging, STOP/PAUSE and approval
state.

## Remaining qualification limits

This is not the native SDA cutover or the later real five-worker acceptance.
Those remain separate tasks with their own requirements. Astra One remains the
external deterministic controller/rescue path. MIG-007 therefore records the
read-only shadow boundary without claiming native ownership, hosted CI, device
validation, or production deployment.
