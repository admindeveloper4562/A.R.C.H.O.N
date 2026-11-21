# Native execution gap matrix

> Historical snapshot captured 2026-11-21 for source 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Current exact-source evidence for source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85 is summarized in NATIVE_EXECUTION_REPORT.md.

| Capability | Historical result | Historical evidence / remaining limit |
|---|---|---|
| Authenticated task admission | PASS for signed test admissions | Invalid or untrusted admissions were rejected; production owner delegation was absent. |
| Capability-scoped operations | PASS for tested operations | Explicit operations only; no unrestricted shell executor. |
| Model gateway call | PASS | Local loopback Ollama qwen3:4b through direct and signed native paths; optional in containers. |
| Private result retrieval | PASS | Conversation persisted privately; installed CLI passed from wheel and sdist. |
| Workspace effects | PASS for bounded test workspace | Approved write succeeded; unauthorized path/effect was denied. |
| Cancellation | PASS in contracts/container smoke | Host production service was not enabled. |
| Bounded lease and recovery | PASS for tested boundary | Minimum lease derived from gateway timeout plus 15 seconds; expired-lease and restart tests passed. |
| Idempotency and receipts | PASS for tested operations | Replay returned persisted result; event/queue receipts contained digests and status. |
| Container restart and interrupted effect | PASS in disposable container | Persistent volumes, restart, recovery reconciliation, and SQLite integrity passed. |
| Concurrent worker ownership | NOT QUALIFIED | The native controller workload was serial; no parallel worker coordination is claimed. |
| Native SDA handoff | NOT QUALIFIED | No one-writer cutover, separately protected watchdog, or owner authorization. |
| Trusted rollback application | NOT QUALIFIED | Planning and guard contracts exist; no signed production rollback/failback was applied. |
| External finance, communications, public network | DISABLED | No real transactions, messages, or external task effects were attempted. |
