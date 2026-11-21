# Native execution gap matrix

Application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb.

| Capability | Result | Evidence / remaining limit |
|---|---|---|
| Authenticated task admission | PASS for signed test admissions | Invalid or untrusted admissions are rejected; production owner delegation is absent. |
| Capability-scoped operations | PASS for tested operations | Explicit operations only; no unrestricted shell executor. |
| Model gateway call | PASS | Local loopback Ollama qwen3:4b through direct and signed native paths; optional in containers. |
| Private result retrieval | PASS | Conversation persisted privately; installed CLI passed from wheel and sdist. |
| Workspace effects | PASS for bounded test workspace | Approved write succeeds; unauthorized path/effect is denied. |
| Cancellation | PASS in contracts/container smoke | Host production service not enabled. |
| Bounded lease and recovery | PASS for tested boundary | Minimum lease derives from gateway timeout plus 15 seconds; expired-lease and restart tests pass. |
| Idempotency and receipts | PASS for tested operations | Replay returns persisted result; event/queue receipts contain digests and status. |
| Container restart and interrupted effect | PASS in disposable container | Persistent volumes, restart, recovery reconciliation, and SQLite integrity passed. |
| Concurrent worker ownership | NOT QUALIFIED | The native controller workload was serial; no parallel worker coordination is claimed. |
| Native SDA handoff | NOT QUALIFIED | No one-writer cutover, separately protected watchdog, or owner authorization. |
| Trusted rollback application | NOT QUALIFIED | Planning and guard contracts exist; no signed production rollback/failback was applied. |
| External finance, communications, public network | DISABLED | No real transactions, messages, or external task effects were attempted. |
