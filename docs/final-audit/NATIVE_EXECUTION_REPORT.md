# Native execution report

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Result: bounded Linux execution PASS; production operation CONDITIONAL.

## Verified operations

- Signed task admission verified the task identity, scope, approval, and trusted test key. Invalid/untrusted admission is rejected before it becomes executable.
- Capability enforcement permits only registered, explicitly scoped operations. Tested native operations include local model inference, read-only database inspection, and bounded allowlisted workspace effects.
- The clean container completed a bounded approved workspace write and denied an unauthorized write. A signed read-only task completed after fresh image load.
- Cancellation, idempotent result replay, queue recovery, restart persistence, failure receipts, and SQLite integrity have focused regression or container evidence.
- Native model inference uses only the configured loopback Ollama gateway. Replies persist in private conversations.sqlite3; queue receipts hold digests/metadata, and the result CLI retrieves content only after local authorization.
- Installed result retrieval passed from both wheel and sdist environments.
- NativeController enforces a lease at least gateway timeout plus a 15-second completion margin: 45 seconds requires 60; 120 requires 135. Regression cases cover both.
- The 36-task workload completed 18 signed model tasks and 18 read-only database inspections with no replay across three controller restarts.

## Boundaries and gaps

- No arbitrary or privileged shell operation was introduced. No unauthenticated network service was exposed.
- Finance and communications remain read-only/test-only; real transactions and messages were not enabled. External network destinations and non-loopback model routing were not used.
- The model and production owner key are not bundled. The acceptance harness used a disposable test-only Ed25519 signer; this is not a production delegation or trust anchor.
- This evidence does not qualify concurrent workers, the complete SMITH autonomous coding/QC/PR lifecycle, native SDA handoff, an independent AEGIS watchdog, or unattended rollback.
- The host service remains disabled. Exact runtime status and other outstanding gates are in AEGIS_RECOVERY_REPORT.md and FINAL_RELEASE_VERDICT.md.
