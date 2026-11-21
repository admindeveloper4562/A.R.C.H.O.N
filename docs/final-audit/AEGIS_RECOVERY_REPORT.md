# AEGIS and recovery report

Candidate application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`. Bounded container recovery evidence passed; independent Guardian recovery is not qualified.

## Verified recovery evidence

- A disposable runtime recovered a journaled interrupted workspace effect after container restart without losing the result.
- Container restart preserved task state; graceful shutdown and fresh saved-image reload passed.
- Container/runtime SQLite integrity passed after recovery.
- This qualifies ARCHON's bounded effect reconciliation. It does not qualify an independently protected AEGIS process or watchdog.

## Read-only canonical ledger snapshot

Snapshot time: `2026-11-21T22:41:47Z`. `sda.sqlite3` integrity check was `ok`, with zero foreign-key violations. The JARVIS V2 project declares 247 parents and 1,359 subtasks: 240 parents and 1,319 subtasks are recorded completed; 7 parents and 40 subtasks are archived. There are 1,281 child receipt rows covering 1,276 distinct children; 43 completed subtasks have no receipt. The project queue is pending; pending/review/merge/rebuild task queues are empty.

Three recorded supervisor lane rows are idle (two recovery-coder lanes and one upgrade-auditor lane). Run history contains one blocked worker run and 13 interrupted worker/repairer runs; these are persisted records, not proof of live processes. No service process or STOP/PAUSE/PAUSED_QUOTA marker was verified; the three queried user service units were inactive. No database mutation or backup was performed for this read-only snapshot.

## Not qualified

- Independent watchdog survival when ARCHON fails.
- Unattended restart after repeated crash or host reboot.
- Verified rollback application and trusted recovery approval.
- Canonical task-ledger receipt reconciliation and cohort completion.

The native host service remains inactive until these gates are independently accepted.
