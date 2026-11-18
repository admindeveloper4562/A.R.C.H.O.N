# REL-003 Acceptance Matrix

Task: `REL-003` — Verify Core-SDA project delegation and completion result.

This matrix is bound to the amended single-builder acceptance recorded by the
Master as `REL-003-SINGLE-BUILDER-20261119`. The original five-worker wording
is retained as provenance only; no retired Astra coding workers are started.

| Acceptance assertion | Observable check | Evidence |
| --- | --- | --- |
| Main Codex is the sole builder | Candidate is claimed through `builder-claim`; no Astra coding dispatch is used | Master run and candidate receipt |
| Core receives an SDA project delegation | `RuntimeService` creates a scoped `core:read` dispatch with project ID and source SHA | `test_single_builder_delegates_to_core_and_records_completion_event` |
| Completion reaches the Core event bus | Core publishes `core.project.completed` with correlation and causation IDs | Same test and event-bus SQLite outbox |
| Result is durable | Dispatch acknowledgement and completion event survive reopening the SQLite stores | `test_restart_preserves_result_and_delivery_is_idempotent` |
| Duplicate work is fenced | Duplicate delivery is a no-op and conflicting event idempotency is rejected | Restart and negative tests |
| Unauthorized work is denied | Foreign Core scope and wrong executor claim return 403/409 | `test_scope_claim_and_completion_idempotency_fail_closed` |
| QC and serial integration remain required | Candidate is submitted to Astra One independent QC and Merger; parent is not complete before both | Master submission/QC/merge receipts |

The test fixture uses temporary SQLite stores, the actual ARCHON registry,
authorization server, dispatch store, runtime service and event bus. It does
not mock the handoff or event persistence layers and contains no credentials.
