# GUARD-010 — Policy-gated SDA repair proposal bridge

**Execution mode:** `design`
**Start SHA:** `c005b4c91fa39eb13551bb46d9530025ec39467d`
**Parent:** `GUARD-010`
**Dependencies:** `GUARD-009`, `SDA-021`
**Acceptance:** Reproducer, minimal scope, source SHA and acceptance stored; no auto privilege
**Scope:** A versioned, evidence-bound proposal contract and a deterministic handoff into the existing SDA rebuild path
**Non-goal:** This document does not create a queue, mutate SQLite, start a worker, grant privilege or approve a repair.

## 1. Requirements and traceability

| Child | Requirement | Design evidence | Verification |
| --- | --- | --- | --- |
| `GUARD-010.S01` | Capture requirements, dependencies, non-goals and open decisions | Sections 1–3 | Review against the task packet, SDA contract and Guardian policy |
| `GUARD-010.S02` | Define typed proposal fields, ownership and transitions | Sections 2 and 4 | Schema, bound, identity and transition fixtures |
| `GUARD-010.S03` | Define safety, privacy, retry, idempotency, rollback and STOP behavior | Section 3 | Negative policy and control-marker fixtures |
| `GUARD-010.S04` | Map every acceptance clause to evidence | Section 5 | Independent QC runs the listed deterministic tests |
| `GUARD-010.S05` | Resolve architecture and security contradictions before implementation | Section 6 | Supervisor review; runtime work remains a later implementation task |

The bridge connects Guardian evidence to the existing SDA Master. It does not
replace `project_queue`, `pending_queue`, `rebuild_queue`, `review_queue` or
`merge_queue`, and it does not introduce a second task ledger.

## 2. Versioned proposal contract

The later implementation should accept exactly one bounded JSON object with
schema `archon.guardian.repair-proposal/1`. Unknown fields must be rejected so
that a future proposal cannot silently add authority to an older reader.

```json
{
  "schema": "archon.guardian.repair-proposal/1",
  "proposal_id": "incident-<64-hex>-proposal-1",
  "task_id": "GUARD-009",
  "failure_fingerprint": "<64 lowercase hexadecimal characters>",
  "failure_category": "qc_rejection",
  "severity": "high",
  "source_sha": "<40 lowercase hexadecimal characters>",
  "reproduction_ref": "evidence-20261116-001",
  "scope_roots": ["src/jarvis_v2/guardian/"],
  "acceptance": ["Recurring same error yields one tracked incident and bounded alerts"],
  "evidence_refs": ["qc-receipt-001", "test-artifact-001"],
  "owner_approval_class": "none",
  "state": "proposed"
}
```

### Field rules

| Field | Required rule |
| --- | --- |
| `schema` | Exact schema string above. |
| `proposal_id`, `task_id`, `reproduction_ref`, `evidence_refs` | Bounded ASCII identifiers; no paths, control characters or raw diagnostic text. IDs are unique within one proposal set. |
| `failure_fingerprint` | Exactly 64 lowercase hexadecimal characters; derived from stable failure identity, not a model narrative. |
| `failure_category` | One of `code_defect`, `config_defect`, `test_defect`, `tooling_defect`, `queue_defect`, `state_defect`, `git_conflict`, `qc_rejection` or `unknown`. Dependency, owner, credential, device, quota and security waits are not coding proposals. |
| `severity` | One of `warning`, `high` or `critical`; severity changes review priority only and never grants permission. |
| `source_sha` | Exactly 40 lowercase hexadecimal characters and must resolve to the verified source/base commit for the task. |
| `scope_roots` | One to eight relative, normalized roots; no absolute path, `..`, symlink escape, hidden runtime state or protected branch control file. |
| `acceptance` | One to eight bounded clauses copied from the authoritative task packet; the proposal cannot weaken or replace them. |
| `owner_approval_class` | `none`, `owner_review` or `owner_signed`; a proposal cannot change the task’s recorded owner gate. |
| `state` | New proposals start at `proposed`; callers cannot submit `admitted`, `merged` or `completed` as an input. |

No proposal field may contain credentials, private prompts, raw model output,
shell fragments, host paths, arbitrary commands or unbounded logs. A
`reproduction_ref` points to existing bounded evidence; it is not an instruction
to execute external content.

## 3. Ownership, policy gate and failure behavior

AEGIS/Guardian may create a proposal from a verified `FailureAssessment` and
incident fingerprint. The Principal Supervisor reviews its root cause and
scope. ATLAS/SDA Master alone validates admission, owns SQLite transitions and
places an accepted repair into the existing `rebuild_queue`. Main Codex owns
implementation. Independent QC and the serialized Merger retain their current
roles.

The bridge must apply these checks inside one short Master transaction:

1. The task exists and its current source/base SHA matches `source_sha`.
2. The task is in an actionable failed, conflict or recovery state; dependency,
   owner, credential, device, quota and security holds are rejected as repair
   proposals.
3. The proposal fingerprint is new for that task/generation, or the exact
   proposal is returned idempotently without another queue row.
4. Scope roots are a subset of the task’s approved paths and do not include
   protected policy, approval, database, secret or branch-control files.
5. The acceptance clauses and evidence references are present and bounded.
6. A clear STOP/PAUSE/PAUSED_QUOTA state is required before admission; the
   bridge records the proposal but does not clear a control marker.

Proposed state transitions are:

```text
proposed -> rejected | validated
validated -> blocked | admitted
admitted -> implementation -> qc_pending
qc_pending -> rejected | approved
approved -> merge_pending -> merged | conflict
merged -> completed only after the ordinary parent/child receipt predicate
```

`rejected`, `blocked` and `conflict` retain the proposal, fingerprint, source
SHA and evidence references. A failed repair creates one bounded new generation
through the existing Master retry path; it never overwrites the prior
candidate, grants extra permissions or creates an untracked queue.

### Security and privacy matrix

| Condition | Required behavior | Evidence |
| --- | --- | --- |
| Missing or unknown field | Reject before persistence or process effects | Schema-negative fixture |
| Wrong source SHA or stale task | Reject as `state_defect`; preserve current task | Freshness fixture |
| Scope outside task allowance | Reject as `unsafe_changed_path`; no worktree or queue effect | Scope fixture |
| External prerequisite | Keep the task in its external wait; no coding proposal | Dependency/approval/device/quota fixtures |
| STOP, PAUSE or quota marker | Do not admit or dispatch; preserve marker | Control-marker fixture |
| Duplicate proposal | Return the original receipt; never duplicate queue membership | Idempotency fixture |
| Missing evidence or raw diagnostic payload | Reject; store only bounded IDs and digests | Payload-bound fixture |
| QC rejection or semantic merge conflict | Preserve candidate/history and return a bounded finding to Main Codex | QC/Merger fixture |
| Proposed privilege or policy change | Reject; owner/security workflow remains separate | Authorization-negative fixture |

The bridge has no shell, network, Git publication, database deletion,
service-manager, secret-reader or permission-granting operation. It cannot
approve its own proposal, clear a control, modify `main`, or authorize a
production/Guardian cutover.

## 4. Handoff and evidence contract

The implementation should expose a narrow deterministic boundary equivalent to:

```text
validate_repair_proposal(proposal, task_packet, controls) -> validated | bounded_error
admit_repair_proposal(validated) -> existing_master_receipt
```

Validation is pure. Admission is a Master-owned transaction that records the
proposal and existing `rebuild_queue` membership together. Neither operation
executes the reproducer or changes application source.

Every later implementation candidate must bind evidence to:

```text
task_id | proposal_id | generation | source_sha | candidate_sha
| reproduction_ref | scope_roots | acceptance | independent_qc
| integration_sha | merger_result
```

`candidate_sha` and `integration_sha` are absent until those stages genuinely
occur. A design or proposal receipt is not a completion receipt.

## 5. Acceptance and test matrix

| Acceptance clause | Test | Expected result | Evidence owner |
| --- | --- | --- | --- |
| Reproducer is stored | Valid proposal with bounded `reproduction_ref` | Accepted reference is retained; raw output is absent | Independent QC |
| Minimal scope is stored | In-scope, absolute, traversal, symlink and protected-root fixtures | Only task-allowed relative roots pass | Master/QC |
| Source SHA is bound | Current, stale, malformed and non-ancestor SHA fixtures | Only the verified task base passes | Master/QC |
| Acceptance is preserved | Empty, oversized and altered acceptance fixtures | Reject missing/changed authoritative criteria | Master/QC |
| Failure category is actionable | Actionable categories plus dependency/approval/device/quota/security categories | Only actionable categories can reach rebuild admission | Master |
| No automatic privilege | Proposal containing command, permission, control or publication fields | Schema/policy rejection; no side effect | Security QC |
| Duplicate incidents deduplicate | Same task/generation/fingerprint submitted repeatedly | One proposal and one rebuild row; repeat returns original receipt | Master |
| STOP/PAUSE/quota survives | Marker set before validation/admission | Proposal remains unadmitted and marker unchanged | Independent QC |
| QC/Merger remain independent | Accepted proposal through coding, QC and Merger fixtures | Completion requires exact candidate, QC, integration and child receipts | QC/Merger |
| Historical evidence remains | Rejected proposal and repair retry fixture | Prior proposal, run and candidate remain queryable | Master |

Manual gates remain for owner approvals, unavailable credentials/devices,
security policy changes, remote publication and production/native SDA cutover.
Local fixtures cannot satisfy those gates.

## 6. Supervisor review and implementation boundary

This design preserves the ten-module architecture, Business exclusion, the
existing five queues, the single deterministic Master, Main Codex builder
authority, independent QC, serial Merger, STOP/PAUSE/quota controls and
trusted-watchdog boundary. It does not add a second database or a new queue.

The later implementation may add a pure proposal validator and focused tests
under `src/jarvis_v2/guardian/` and `tests/`, plus the smallest Master adapter
under the existing Astra state code. It must not directly edit canonical
SQLite, start a coding worker, grant privilege or install a service. The
implementation and migration remain separate tasks with their own candidate,
QC, merge and child receipts.

No unresolved architecture or security contradiction is identified in this
design. The open implementation decisions are the exact Master API name and
the durable proposal receipt table/columns; both must reuse the current
`supervisor_cases`, `rebuild_queue` and receipt conventions rather than create
parallel state.

## Child evidence map

- `GUARD-010.S01`: Sections 1–3 capture requirements, dependencies, scope and
  non-goals.
- `GUARD-010.S02`: Sections 2 and 4 define the versioned proposal fields,
  ownership, handoff and state transitions.
- `GUARD-010.S03`: Section 3 defines policy, privacy, safety, idempotency,
  rollback and STOP behavior.
- `GUARD-010.S04`: Section 5 maps each acceptance clause to deterministic or
  manual evidence.
- `GUARD-010.S05`: Section 6 records the Supervisor review boundary and the
  allowed implementation paths.

## Handoff

`GUARD-010 | child_receipts pending until QC | start_sha c005b4c91fa39eb13551bb46d9530025ec39467d | candidate_sha pending | integration_sha c005b4c91fa39eb13551bb46d9530025ec39467d | files docs/tasks/GUARD-010-DESIGN.md | independent_qc pending | merger pending | no owner gate | no external blocker`
