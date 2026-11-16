# BACK-001 — Shared versioned API, event envelope and module manifests

**Status:** design artifact; implementation and acceptance are `NOT_VERIFIED`.

**Task:** `BACK-001`
**Execution mode:** `design`
**Base reviewed:** `400581ba13a82f332de7dbaecd13563da0e70e74`
**Dependencies:** `SDA-028`, `CORE-001`
**Allowed candidate change:** this document under `docs/` only.

This document defines the bounded Backend contract required by the task. It
does not add runtime APIs, alter the SQLite schema, create a new event bus,
change module ownership, or claim that any proposed behavior is implemented.

## 1. Requirements and traceability

| Requirement | Design response | Evidence required | State |
|---|---|---|---|
| Versioned schemas | Every cross-module envelope and manifest declares a stable schema name and major version; incompatible majors fail closed. | Validator tests for supported, unknown and malformed versions. | Specified; not implemented |
| Stable IDs and ordering | Events use an opaque event ID, aggregate ID, correlation ID and strictly increasing sequence within the owning stream. | Replay, duplicate and out-of-order fixtures in an isolated database. | Specified; not implemented |
| Privacy boundaries | Payloads carry a bounded privacy class and only approved references; private content is not copied into progress, telemetry or cross-module metadata. | Negative scope tests, sanitized receipt inspection and independent QC. | Specified; not implemented |
| Idempotency | Effectful consumers require an idempotency key and durable effect receipt before acknowledging an event. | Replayed delivery produces one effect and one receipt. | Specified; not implemented |
| Ten-module architecture | Manifest IDs and keys remain the existing 1–10 set from `config/modules.json`; Business is absent. | Existing manifest validator plus exact-set regression test. | Observed in base; implementation partly exists |
| Domain ownership | Backend owns shared metadata and protocol validation; domain modules retain their own authoritative application data. | Boundary review and negative cross-domain write tests. | Specified; not implemented |
| Existing Core compatibility | The design maps to the existing Core queue, event session, dispatch and timeline primitives rather than replacing them. | Focused adapter and restart tests in a later implementation task. | Observed; adapter unknown |
| Safe operations | STOP, PAUSE, quota, owner gates and security failures prevent new non-idempotent effects and survive restart. | Control-state and crash/restart tests. | Specified from policy; not implemented |

### Scope and non-goals

The task is limited to shared contracts and a reviewed implementation boundary.
It does not implement a gateway, RAG store, Windows connector, Cloudflare
integration, migration, deployment, owner approval, or production event
transport. It does not create an eleventh module or convert Business into an
active module. The existing `jarvis_v2` package paths and historical records
remain compatible.

Open implementation decisions are the authoritative storage location for
cross-module receipts, the transport selected for durable delivery, the exact
retention policy, and the adapter boundary between Core's current SQLite
event/session tables and a later Backend service. These decisions require
review in the implementation task; this design does not silently choose them.

## 2. Module manifest contract

The canonical manifest set is the ten entries already represented by
`config/modules.json` and `src/jarvis_v2/backend/module_manifest.py`:

| ID | Key | Dependencies | Owner/domain |
|---:|---|---|---|
| 1 | `core` | none | ARCHON / ATLAS Core |
| 2 | `sda` | `core` | ATLAS SDA |
| 3 | `backend` | `core` | ATLAS Backend |
| 4 | `runtime` | `backend`, `core` | ARCHON Runtime |
| 5 | `research` | `backend` | Research |
| 6 | `tws` | `backend` | Twelve-Winged System |
| 7 | `wic` | `backend` | World Information Center |
| 8 | `finance` | `backend` | Financial Intelligence |
| 9 | `guardian` | `backend` | AEGIS Guardian |
| 10 | `automation` | `backend`, `core` | ATLAS Automation |

The manifest validator must continue to require the exact stable ID/key pair,
declared dependencies, a health label equal to the key, and only module-local
read/health scopes. A dependency does not grant write access to the dependency.
Unknown keys, duplicate IDs, Business, wildcard scopes, foreign scopes and
unknown fields fail before any effect.

A versioned manifest envelope for a later implementation is:

```json
{
  "schema": "archon.module-manifest/1",
  "module_id": 3,
  "key": "backend",
  "version": "1.0.0",
  "dependencies": ["core"],
  "health_endpoint_label": "backend",
  "permission_scopes": ["backend:health", "backend:read"],
  "artifact_sha256": "<sha256>",
  "owner": "ATLAS"
}
```

`artifact_sha256` binds the reviewed artifact; it is not an authorization by
itself. The exact allowed fields and version policy belong to the later typed
validator and must remain backward-compatible with the current pure validator.

## 3. Versioned event and API envelope

The shared envelope is a transport-neutral contract. Producers own event
creation; the deterministic dispatcher and Backend validation layer own
admission, ordering, deduplication and receipt rules.

```text
ArchonEventV1 {
  schema: "archon.event/1",
  event_id: OpaqueId,
  event_type: BoundedName,
  producer_module: StableModuleKey,
  aggregate_type: BoundedName,
  aggregate_id: OpaqueId,
  sequence: PositiveInteger,
  occurred_at: UTC timestamp,
  correlation_id: OpaqueId,
  causation_id: Optional[OpaqueId],
  idempotency_key: Optional[OpaqueId],
  privacy_class: "public_metadata" | "internal_metadata" | "scoped_private",
  payload_schema: BoundedSchemaName,
  payload_sha256: Sha256,
  payload: VersionedData
}
```

The payload is bounded, typed data or an approved reference. It must not be
interpreted as executable instructions or permission. Receivers reject an
unknown major schema, invalid module identity, duplicate event with conflicting
bytes, sequence regression, missing required correlation, invalid digest or
privacy class. Minor additions are accepted only when the consumer contract
explicitly permits them.

The minimum API/request envelope follows the same identity rules:

```text
ArchonRequestV1 {
  schema: "archon.request/1",
  request_id: OpaqueId,
  operation: BoundedName,
  caller_module: StableModuleKey,
  target_module: StableModuleKey,
  correlation_id: OpaqueId,
  permission_scope: ModuleLocalScope,
  idempotency_key: OpaqueId,
  input_ref: VersionedDataOrApprovedReference
}
```

The target module remains the owner of domain data. Backend may validate and
index shared metadata, but a request cannot use the shared envelope to grant a
foreign module scope or perform an unreviewed cross-domain write.

### Delivery and idempotency sequence

```text
CREATED -> ADMITTED -> DELIVERED -> EFFECT_RECORDED -> ACKNOWLEDGED
                         |                         |
                         +-> RETRYABLE_FAILURE    +-> DUPLICATE_NOOP
                         +-> QUARANTINED
```

Admission validates schema, identity, authorization, sequence and digest.
Delivery may be retried with the same idempotency key. A consumer records the
effect receipt before acknowledgement; a duplicate returns the existing
receipt without repeating the effect. A sequence conflict, privacy violation,
unknown schema, lost lease or active STOP/PAUSE/quota state is not a successful
delivery. Retryable failures use bounded backoff and eventually enter a
quarantine/dead-letter state with a diagnostic code and digest-only reference.

## 4. Safety, privacy, failure and rollback matrix

| Failure or threat | Detection/prevention | Required result |
|---|---|---|
| Unknown schema or malformed envelope | Typed validation before persistence/effect | Reject with stable failure code; no partial effect |
| Duplicate or conflicting replay | Event/idempotency key plus payload digest | Return prior receipt for identical replay; reject conflicting replay |
| Sequence gap or regression | Per-stream sequence check and durable cursor | Hold/retry or quarantine; never silently reorder |
| Cross-module scope expansion | Module-local permission matrix and target-owner check | Deny before dispatch; preserve evidence |
| Private data in metadata | Privacy-class validation, bounded references and sanitized telemetry | Reject or redact; never publish raw content |
| Consumer crash after effect | Durable effect receipt before acknowledgement | Replay is a no-op and returns the receipt |
| Consumer crash before effect | Lease and idempotency fencing | Retry the same operation once ownership is valid |
| Retry storm/backpressure | Per-correlation pending limit, bounded attempts and quarantine | Stop admitting new work for the affected stream; keep unrelated streams available |
| Lost or stale lease | Master fencing generation | Reject stale acknowledgement/effect; preserve current owner |
| STOP, PAUSE or quota marker | Check before admission and before non-idempotent effect | Retain queue state; do not clear a marker automatically |
| Integration or schema migration failure | Verified backup, atomic migration and last-known-good pointer | Roll back the affected change; retain candidate and receipts |
| Untrusted payload content | Treat payload as data, never as policy or executable input | Validate, store and route only under the caller's fixed permissions |

Rollback is bounded to the last independently verified contract/runtime
checkpoint. It does not delete event history, clear controls, or mark an
unverified effect successful. Any future database migration must use a copied
test database, SQLite integrity checks and a restore rehearsal before the live
Master considers activation.

## 5. Acceptance-to-test matrix

This is a plan for a later implementation task. The current design candidate
does not claim that these commands were run.

| Acceptance clause | Test class | Planned evidence |
|---|---|---|
| Versioned schemas are explicit | Unit/negative | Validate supported `archon.event/1`, `archon.request/1`, and `archon.module-manifest/1`; reject unknown major, missing version and unknown fields. |
| Stable IDs and sequence are enforced | Integration/replay | Insert synthetic events in and out of order; accept the next sequence, reject regression/gap according to the selected policy, and preserve correlation. |
| Privacy and scoped ownership hold | Negative/security | Attempt foreign scope, wildcard scope, unapproved metadata and unbounded payload; each is rejected with no effect. |
| Idempotency is durable | Crash/replay | Deliver the same request twice and inject a crash before/after receipt; exactly one effect receipt remains. |
| Ten manifests remain compatible | Regression | Run `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_backend_manifest.py'`; exact IDs 1–10 pass and Business is rejected. |
| Existing Core behavior remains compatible | Regression/integration | Run the Core queue/event/dispatch/timeline tests against an isolated SQLite database; compare stable event and receipt metadata. |
| Backpressure and retry are bounded | Failure injection | Exceed the per-correlation limit and force retryable failures; verify quarantine and unrelated-stream progress. |
| STOP/PAUSE/quota are honored | Restart/control | Set each control in a disposable state store, restart the controller, and verify no new non-idempotent admission or effect occurs. |
| Rollback preserves state | Migration/restore | Apply a disposable schema or contract change, force verification failure, restore the last-known-good copy, and compare integrity/checksums. |
| Evidence is independently reviewable | QC/merge | Bind test artifact hashes, candidate SHA, base SHA, changed paths and Merger result; reject missing or stale evidence. |

Required host, provider, hardware and remote-service acceptance remains a
manual or external gate. Local synthetic tests cannot certify Windows Ollama,
Cloudflare, hosted CI, production deployment or a provider quota state.

## 6. Child deliverables and reviewed implementation boundary

| Child | Deliverable in this design | Evidence state |
|---|---|---|
| `BACK-001.S01` | Requirements, dependencies, non-goals and compatibility obligations in §1. | Specified; not independently tested |
| `BACK-001.S02` | Manifest, event/request envelope, ownership and lifecycle in §§2–3. | Specified; not implemented |
| `BACK-001.S03` | Privacy, failure, idempotency, backpressure, rollback and STOP matrix in §4. | Specified; not tested |
| `BACK-001.S04` | Acceptance-to-test matrix and external/manual boundaries in §5. | Planned; commands not run by this candidate |
| `BACK-001.S05` | Scope, compatibility constraints and open implementation decisions in this section. | Proposed; Supervisor/QC review pending |

The later implementation should be split into the smallest reviewed changes:

1. Extend or adapt the existing pure manifest validator only where the
   versioned contract requires it, preserving its exact-set and local-scope
   checks.
2. Reuse Core's existing event/session, dispatch and receipt primitives before
   introducing new storage or transport.
3. Add isolated unit, negative, replay, failure-injection and restart tests.
4. Bind candidate, base, diff, test artifacts, independent QC and Merger
   evidence before any parent completion transition.

Potential implementation paths are `src/jarvis_v2/backend/`, existing Core
contract modules under `src/jarvis_v2/core/`, and focused `tests/` fixtures.
This design task intentionally changes none of them because its execution mode
requires documentation only. No owner approval, production access, database
migration or remote CI run is implied.

## 7. Design conclusion

The proposed contract satisfies the BACK-001 acceptance shape: versioned
schemas, stable IDs, sequence, privacy and idempotency are defined against the
existing ten-module architecture and current Core primitives. Implementation,
test execution, independent QC, serialized integration and child receipts are
still required before this parent can be considered complete.
