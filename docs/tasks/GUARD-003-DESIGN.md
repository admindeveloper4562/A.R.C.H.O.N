# GUARD-003 — Recoverable component manifest and failure-domain graph

**Execution mode:** `design`
**Start SHA:** `557daff8e8c5b9746ffcce2f0b68f3c6d13e55de`
**Parent:** `GUARD-003`
**Acceptance:** Criticality, health, restart, state and owner-approval fields validated
**Scope:** versioned Guardian manifest contract, dependency graph, safety matrix and test plan
**Non-goal:** this document does not deploy a service, change SQLite, or authorize a restart.

## 1. Requirements and traceability

| Child | Requirement | Design evidence | Verification |
| --- | --- | --- | --- |
| S01 | Capture exact requirements, dependencies and non-goals | Sections 1–3 and the compatibility notes below | Review against the task packet, module contract and Guardian policy |
| S02 | Define versioned interfaces, ownership and transitions | Sections 2 and 4 | Schema fixtures, type/bound checks and graph validation |
| S03 | Define safety, privacy, failure, retry and rollback behavior | Section 3 | Negative fixtures and failure-injection tests; owner gates remain explicit |
| S04 | Map every acceptance clause to tests or a manual gate | Section 5 | Test matrix with expected result and evidence owner |
| S05 | Resolve architecture and security contradictions before coding | Section 6 | Supervisor review; implementation remains a later task |

### Dependencies and compatibility

`BACK-001` supplies the ten-module identifiers and typed manifest conventions;
`BACK-019` supplies honest health/readiness vocabulary; `GUARD-001` supplies
the local model and deterministic-stop boundary. This contract keeps Guardian
as module `guardian`, AEGIS as its identity, ATLAS as deterministic owner, and
the existing Git/SQLite task identifiers unchanged.

The manifest describes a component that may be recovered by a trusted,
independently managed controller. It is not a worker lease, a release
approval, a task record, or a replacement for the external watchdog.

## 2. Versioned component contract

The next implementation must accept only JSON objects with schema
`archon.guardian.component/1`. Unknown fields are rejected so a future
permission or restart behavior cannot be silently enabled by an older reader.

```json
{
  "schema": "archon.guardian.component/1",
  "component_id": "atlas-sda-master",
  "module": "sda",
  "instance_id": "atlas-sda-master-1",
  "version": "0.1.0",
  "artifact_sha256": "<64 lowercase hexadecimal characters>",
  "criticality": "critical",
  "health": {
    "liveness": {"kind": "process", "interval_seconds": 10, "timeout_seconds": 3},
    "readiness": {"kind": "checkpoint", "interval_seconds": 15, "timeout_seconds": 5}
  },
  "restart": {
    "enabled": true,
    "max_attempts": 3,
    "cooldown_seconds": 30,
    "deadline_seconds": 120
  },
  "state": {
    "schema_version": 1,
    "checkpoint_kind": "sqlite",
    "checkpoint_ref": "atlas-sda",
    "mirror_required": true
  },
  "dependencies": ["atlas-core"],
  "failure_domain": "linux-sda",
  "fencing_group": "atlas-sda-writer",
  "route_key": "sda.master",
  "owner_approval_class": "owner_review",
  "last_known_good_sha256": "<64 lowercase hexadecimal characters>"
}
```

### Field rules

| Field | Required validation |
| --- | --- |
| `schema` | Exact string `archon.guardian.component/1`. |
| `component_id`, `instance_id`, `failure_domain`, `fencing_group`, `route_key` | Non-empty ASCII identifiers, 1–128 characters, no path separators or control characters. IDs are unique within one manifest set. |
| `module` | One of the ten canonical module keys; `business` is rejected. |
| `version` | Unpadded semantic `X.Y.Z`; no build metadata is used as an authority. |
| `artifact_sha256`, `last_known_good_sha256` | Lowercase 64-character SHA-256 strings. The last-known-good value is mandatory for restartable components. |
| `criticality` | One of `critical`, `high`, `normal`, or `low`; criticality changes scheduling only, never permissions. |
| `health` | Exactly `liveness` and `readiness`; each probe has a non-shell `kind` from `process`, `checkpoint`, or `event`, and bounded integer interval/timeout values from 1–3600 seconds with timeout no greater than interval. |
| `restart` | `enabled` is boolean; `max_attempts` is 0–5; cooldown is 1–3600 seconds; deadline is 1–900 seconds. A disabled policy cannot request automatic restart. |
| `state` | Schema version is a positive integer at most 100; checkpoint kind is `sqlite`, `file`, or `memory`; checkpoint reference is an identifier; `mirror_required` is boolean. `memory` cannot be used when `mirror_required` is true. |
| `dependencies` | List of unique component IDs; no self-reference; every referenced node must exist before the set is admitted. |
| `owner_approval_class` | One of `none`, `owner_review`, or `owner_signed`. Promotion, policy changes and protected failover remain owner-gated even when restart is `none`. |

No field may contain credentials, raw prompts, model text, arbitrary shell
fragments, host paths, or unbounded log content. Health probes are declarative
signals; the validator must not turn a manifest into a generic command runner.

### Ownership and state transitions

ATLAS owns manifest admission, graph validation, leases and receipt state.
AEGIS may diagnose and propose recovery. The external trusted watchdog owns
the protected activation boundary. A manifest cannot authorize its own policy,
watchdog, approval, database or `main` branch change.

Allowed recorded component states are:

```text
declared -> healthy | degraded | quarantined | stopped
degraded -> restarting | quarantined | stopped
restarting -> healthy | degraded | quarantined
healthy -> degraded | quarantined | stopped
quarantined -> stopped | restarting
```

`restarting` requires a verified artifact digest, a clear STOP/PAUSE/quota
control, a valid checkpoint, an available restart budget and one fenced writer.
No transition clears a control marker, grants approval, or deletes a prior
artifact. Unknown or duplicate transitions fail closed and produce a bounded
diagnostic code.

## 3. Failure-domain and safety design

The dependency graph is a directed graph `component -> dependency`. Admission
requires unique nodes, existing references, no self-edge and no cycle. A
component may depend on another failure domain, but two critical writers may
not share a fencing group unless the manifest explicitly declares one lease
authority. A quarantined dependency makes dependents `degraded` or
`quarantined`; it does not authorize them to start a second writer.

| Failure or threat | Required behavior | Evidence |
| --- | --- | --- |
| Missing/invalid field | Reject the complete manifest before persistence or process effects | Validation error code and fixture |
| Unknown module or Business entry | Reject; preserve the previous manifest | Negative fixture |
| Duplicate ID, dependency or fencing writer | Reject; no lease or route change | Graph fixture |
| Cycle or missing dependency | Reject admission and report bounded node IDs only | Graph fixture |
| Artifact digest mismatch | Deny start/restart; retain last-known-good reference | Digest fixture |
| Failed liveness/readiness | Record degraded state, consume bounded retry budget, then quarantine | Failure-injection receipt |
| STOP, PAUSE or quota marker | Deny automatic restart and preserve marker | Control fixture |
| Missing checkpoint or incompatible state schema | Deny promotion; use last-known-good recovery path | State compatibility fixture |
| Owner approval class not satisfied | Keep `approval_required`; do not infer approval from tests or model output | Approval fixture |
| Health probe tries to execute a shell or expose data | Reject the manifest; no command or network effect | Probe-shape fixture |
| Repeated identical failure | Deduplicate by stable fingerprint and stop retry escalation | Fingerprint receipt |
| Watchdog or database unavailable | Enter safe degraded mode; do not self-authorize or switch pointers | Manual watchdog gate |

The restart budget is per component generation, not per process loop. Every
attempt records component ID, generation, artifact digest, reason code,
checkpoint reference and result digest. Raw output is not stored in the
manifest or monitor tables.

## 4. Interface and ownership notes

The implementation should expose a read-only validator and a graph builder
first. A later controller may consume its result through a narrow interface:

```text
validate_component(manifest) -> validated_manifest | bounded_error
validate_graph(manifests) -> graph_receipt | bounded_error
plan_recovery(component_id, observation) -> recovery_plan | bounded_error
```

`validate_component` and `validate_graph` have no process, network, Git or
SQLite side effects. Recovery planning may return a proposal only. The
deterministic Master/watchdog performs leases and activation through existing
authorized controls; no new queue or database is introduced by this design.

## 5. Acceptance and test matrix

| Acceptance clause | Deterministic test | Expected result | Evidence owner |
| --- | --- | --- | --- |
| Criticality is validated | Valid values plus empty, unknown and wrong-type fixtures | Only four declared values pass | Independent QC |
| Health fields are validated | Missing probes, shell probe, invalid kind, timeout/interval bounds | Invalid shapes reject without effects | Independent QC |
| Restart fields are validated | Attempts, cooldown, deadline and disabled-policy boundary fixtures | Bounds and disabled behavior are enforced | Independent QC |
| State fields are validated | Checkpoint kind/reference/schema and memory/mirror combinations | Incompatible state contract rejects | Independent QC |
| Owner-approval fields are validated | Each approval class, unknown class and missing approval receipt | Unknown/missing approval remains blocked | Master/QC |
| Dependency graph is valid | Missing node, duplicate node, self-edge and cycle fixtures | Graph rejects atomically | Independent QC |
| Failure domains are explicit | Critical writer collision and separate-domain fixtures | Unsafe writer topology rejects | Master/QC |
| STOP/PAUSE/quota survives recovery | Control-marker fixture with otherwise-valid component | No restart or marker mutation | Trusted watchdog/QC |
| Last-known-good is retained | Digest mismatch and unavailable checkpoint fixtures | Recovery denies activation and retains reference | Trusted watchdog |
| Privacy boundary holds | Unknown fields and oversized/raw payload fixtures | Reject; no sensitive payload is stored | Security QC |

Manual gates remain necessary for real host service ownership, a signed
release, hardware readiness, external watchdog identity and production
promotion. Local fixtures cannot satisfy those gates.

## 6. Review result and implementation boundary

This contract is consistent with `AGENTS.md`, `SECURITY.md`,
`docs/architecture/MODULE_CONTRACTS.md`, `docs/operations/GUARDIAN_RELEASE.md`
and the ten-module configuration. It preserves Business exclusion, existing
module IDs, owner STOP/PAUSE/quota controls, independent QC and the external
watchdog boundary.

The next implementation task may add a pure validator under
`src/jarvis_v2/guardian/` and focused tests under `tests/`. It must not add a
new queue, mutate the canonical database directly, install a systemd service,
or treat this design receipt as approval to deploy. A later host/service task
must separately handle installation and real watchdog qualification.
