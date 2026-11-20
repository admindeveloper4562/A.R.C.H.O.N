# Native execution gap matrix

The native controller and queue provide a safe single-writer control plane. The built-in executor intentionally does not claim domain execution authority. The following is the complete current boundary, based on the SDA, ATLAS, AEGIS, authorization, effect-journal, and rollback contracts.

| Required operation | Current evidence | Status | Missing acceptance evidence or implementation |
| --- | --- | --- | --- |
| Capability discovery and module health | Eight allowlisted probes; all ten module manifests validate | PASS | None for read-only discovery |
| Durable task identity and admission | `CoordinatorQueue` task IDs, dependency-ready leasing, control markers, process lock | PASS local | No authenticated external admission endpoint in the native service |
| Persistent leases and fencing | Lease expiry/requeue, owner lease token, controller lock, stale completion rejection | PASS local | Native unattended SDA ownership and out-of-process Guardian qualification |
| Idempotent completion and audit receipt | Digest-only success/failure receipts and durable queue events | PASS local | Domain-specific result/receipt binding for real effects |
| Safe cancellation | Queue schema has a cancelled state, but no native public cancellation operation | BLOCKED | Owner-authenticated cancellation API, exact approval binding, audit receipt, and tests |
| Controlled retry | Event failure/retry primitives exist in Core | PARTIAL | Native task retry ceiling, retry identity, quarantine policy, and restart acceptance |
| Task submission | Owner-intent admission exists in Core | PARTIAL | Native transport must verify a signed owner approval for sensitive actions; current approval objects are digest-bound but not signed transport |
| Filesystem or artifact writes | No built-in handler; capability is rejected | BLOCKED by policy | Reviewed bounded handler, path allowlist, effect journal, approval, rollback and fault-injection tests |
| Service start/stop or route switch | No built-in handler; service control is rejected | BLOCKED by policy | Separately protected trusted watchdog identity, unit qualification, fencing and rollback soak |
| Network/provider/model calls | No built-in handler; network/provider/model operations are rejected | BLOCKED by policy | Module connector contracts, secret isolation, rate limits, approval and external test fixtures |
| Finance and communications | No built-in handler; real effects are rejected | BLOCKED by policy | Paper/sandbox handlers plus owner-approved connector and no-real-side-effect acceptance |
| SDA handoff | Shadow `HandoffEvidence` report only; no route or ownership change | BLOCKED | All handoff evidence keys, independent QC, checkpoint, one-writer, Guardian and owner gates |
| AEGIS restart/recovery | Readiness probe only; Guardian manager/recovery contracts are separately tested | PARTIAL | External watchdog activation, failure handling, health soak and verified failback |
| Rollback application | Read-only rollback planning exists; native executor rejects apply | BLOCKED by policy | Trusted watchdog gate, signed release evidence, last-known-good restore test and state-preservation proof |
| Unified native audit ledger | Queue events, effect journal, sessions, and approval contracts exist separately | PARTIAL | One native execution receipt schema spanning task, grant, effect, retry, recovery and rollback |

No missing operation is enabled by this audit merely to make the release appear complete. The safe next implementation boundary is the owner-authenticated, signed-approval control plane and its disposable-fixture tests; domain handlers remain disabled until that boundary and the trusted watchdog are independently qualified.
