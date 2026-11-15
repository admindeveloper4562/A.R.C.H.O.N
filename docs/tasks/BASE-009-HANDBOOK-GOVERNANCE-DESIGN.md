# BASE-009 — Controlled `CODING_HANDBOOK.md` governance design

Status: design artifact; implementation and acceptance are **NOT_VERIFIED**.

Task: `BASE-009`
Execution mode: `design`
Allowed candidate scope: `docs/` only
Pinned source commit supplied by task: `173d4bdacb053e7301cee61e01c802faae6196d5`
Approved architecture SHA-256 supplied by task: `295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89`

This document is the sole candidate change for this design task. It does not
edit `CODING_HANDBOOK.md`, add enforcement code, change policy files, or claim
that approval controls already exist beyond the observed repository text.

## 1. Evidence and scope boundary

| Item | Observation | State |
|---|---|---|
| Existing handbook | Root `CODING_HANDBOOK.md` exists and states that coding workers are read-only. It assigns proposal/update authority to QC, Research, and Recovery/Guardian by section. | Observed |
| Architecture requirement | The consolidated architecture requires section-scoped handbook authority, versioned review/access controls, no worker self-approval, and owner approval for new constitutional/security rules. | Observed |
| Repository/security controls | `AGENTS.md` and `SECURITY.md` require independent QC, serialized merge, owner approval for protected changes, and preservation of STOP/PAUSE/quota controls. | Observed |
| Task dependency | The task plan lists `BASE-008` as a parent dependency. The supplied child packet separately lists S01 as having no child dependency. | Observed; dependency readiness not verified here |
| Runtime enforcement | No source, test, database, CODEOWNERS, branch-rule, or live approval evidence is asserted by this design. | Unknown |
| Host/remote/provider evidence | No host, remote, license, approval receipt, service, or execution evidence is asserted. | Not collected |

Non-goals: changing the handbook, implementing authorization, adding a
database schema, changing GitHub/branch policy, proving remote protection,
approving a candidate, or marking any child or parent complete.

## 2. S01 — Requirements-to-acceptance traceability

| Requirement / obligation | Design response | Acceptance evidence required | State |
|---|---|---|---|
| Handbook exists | Preserve root `CODING_HANDBOOK.md` as the governed document. Future implementation must resolve one canonical path and reject aliases/case-colliding copies. | Pinned-tree path/type check and content digest bound to the candidate. | Observed existence; canonical enforcement unknown |
| Edit approvals | Model edits as proposals with actor role, section, base handbook digest, candidate digest, reason, review receipt, and owner approval where required. | Independent QC receipt plus authorized review/owner receipt for the exact candidate digest. | Specified; not implemented |
| Read-only worker enforcement | Coding workers receive read capability only. Any attempted handbook write must be rejected before filesystem/Git side effects; workers cannot approve their own exception. | Negative authorization test for each worker role, including path alias and malformed request cases. | Specified; not implemented |
| Section ownership | Recovery/Guardian: bug-fixing entries; SDA QC: reviewed engineering/mistake rules; Research: development tips; owner: new constitutional/security rules. | Role × section allow/deny matrix tested against exact request shape. | Specified from observed policy |
| Independent review | QC must inspect the exact candidate and bind its receipt to the candidate digest before merge. | Candidate SHA, handbook base/candidate digests, test artifact hashes, QC decision, and Merger receipt. | Specified; no receipt present |
| Append/supersession history | Approved edits append an immutable entry and identify superseded entry IDs; no silent replacement or history rewrite. | Replay test shows deterministic history and supersession; rollback restores last-known-good pointer. | Specified; not implemented |
| Safety controls | STOP, PAUSE, quota, owner gates, and security failures block new edits and survive restart. | Control-state matrix and restart/rollback tests with no mutation during blocked state. | Specified from policy |
| Compatibility | Existing handbook readers continue to consume the canonical Markdown file; proposal metadata is additive and does not grant runtime permissions. | Read compatibility check and unknown-metadata/unknown-version rejection test. | Specified; not implemented |

Open decisions: the authoritative approval store and receipt format; whether
Git CODEOWNERS/branch rules or a local Master owns the final write; exact role
identity/authentication mechanism; handbook schema/version marker; retention
and archival location; and the owner-approved path for constitutional changes.

## 3. S02 — Contract and sequence specification

### 3.1 Typed proposal envelope

The following is a design contract, not an implemented API:

```text
HandbookEditProposalV1 {
  proposal_id: OpaqueId,
  handbook_path: CanonicalRelativePath,     // exactly CODING_HANDBOOK.md
  base_digest: Sha256,
  candidate_digest: Sha256,
  section: HandbookSection,                 // constitution | patterns |
                                            // mistakes | tips
  actor_role: HandbookActorRole,            // recovery | guardian | qc |
                                            // research | owner
  actor_id: AuthenticatedActorId,
  operation: AppendOrSupersede,
  entry_id: OpaqueId,
  supersedes: Optional<OpaqueId>,
  content_digest: Sha256,
  reason: BoundedText,
  regression_evidence: EvidenceRef,
  created_at_utc: Timestamp,
  schema_version: 1
}
```

`OpaqueId`, `Sha256`, `Timestamp`, and `EvidenceRef` are bounded validated
values. The content is never treated as permission, executable instructions,
or an approval receipt. Unknown schema versions, path aliases, digest shape,
missing actor identity, unrecognized sections, duplicate IDs, and oversized or
malformed fields fail closed before any write.

### 3.2 Authorization matrix

| Section | May propose | May approve/write | Owner approval |
|---|---|---|---|
| Constitution / security | Any actor may report a proposed change; no worker may authorize it | Independent reviewer plus authorized Merger/write owner | Required |
| Feature patterns | Relevant implementer may propose evidence; coding worker has no write grant | SDA QC, then serialized Merger | If safety/permission/deployment impact |
| Mistakes and fixes | Recovery/Guardian | SDA QC or separately authorized recovery reviewer, then Merger | If protected policy changes |
| Development tips | Research | Research-approved review path plus Merger | If safety/permission/deployment impact |

The existing handbook's stricter role statements remain the compatibility
floor. A proposal cannot broaden a role's authority, alter STOP/PAUSE/quota
behavior, or approve its own actor/receipt.

### 3.3 State transitions and ownership

```text
READ_ONLY
  -> PROPOSED          (authorized proposal, no handbook write)
  -> QC_PENDING        (immutable candidate and evidence pinned)
  -> APPROVED          (independent QC and required owner approval present)
  -> MERGE_QUEUED      (base/dependency freshness verified)
  -> APPLIED           (serialized Merger writes exact approved digest)
  -> VERIFIED          (post-write digest/history/rollback checks pass)

Any state -> REJECTED / BLOCKED on malformed input, missing approval,
             stale base, STOP/PAUSE/quota, duplicate effect, conflict,
             security finding, or failed verification.
```

Only the serialized Merger/write owner may perform the final write. The
canonical task ledger and approval state remain Master-owned; this document
does not authorize direct ledger updates. Replaying the same proposal ID and
base/candidate digest is idempotent; a conflicting reuse is rejected.

### 3.4 Compatibility behavior

Readers use the canonical root file and may ignore additive review metadata
that is not part of Markdown content. Writers must preserve existing sections,
append history, and retain supersession links. A missing or ambiguous canonical
path, stale base digest, or unknown policy/version is an unavailable/error
state, never an implicit allow.

## 4. S03 — Safety, failure, and rollback matrix

| Threat/failure | Prevention/detection | Required result |
|---|---|---|
| Coding worker self-edits handbook | Role/path authorization before write; negative test | Deny with no filesystem, Git, or ledger side effect |
| Worker self-approves | Separate actor and reviewer identities; receipt binding | Reject approval; preserve proposal |
| Path traversal or alias | Canonical relative path, exact filename, case-collision check | Fail closed |
| Malformed/oversized proposal | Typed validation and bounded fields before parsing/persistence | Reject without partial state |
| Stale base or concurrent edit | Compare base digest and Merger freshness under one writer | Reject/rebase through a new proposal; never overwrite |
| Duplicate replay | Stable proposal/entry IDs and applied-effect check | Return the original result or reject conflicting replay |
| Untrusted handbook text | Treat content as data; no execution or permission interpretation | Store only after review; no privilege expansion |
| Missing reviewer/owner receipt | Required approval matrix | `BLOCKED`, not applied |
| STOP/PAUSE/quota or unknown control | Check controls before proposal acceptance, before publication, and after staging | No new write; retain candidate for later reconciliation |
| QC or post-write failure | Candidate digest and last-known-good pointer | Roll back to prior verified digest; preserve failed artifact and evidence |
| Crash during apply | Atomic write/commit protocol and durable intent | Recovery resumes or rolls back; never report applied from process exit alone |
| Security or integrity anomaly | Isolate affected operation and preserve evidence | Stop affected lane; escalate to owner/Master |

Rollback is bounded to the last independently verified handbook digest and
must not delete proposal history. A rollback is not an approval and does not
clear STOP/PAUSE/quota markers.

## 5. S04 — Acceptance test matrix

These are planned commands/fixtures for the future implementation. They were
not run by this design task and therefore produce no pass claim.

| Acceptance clause | Test class | Fixture / expected output |
|---|---|---|
| Canonical handbook exists | Deterministic repository test | Pinned tree contains exactly one approved canonical path; output `HANDBOOK_PRESENT`; missing/duplicate/case-colliding path returns `HANDBOOK_UNAVAILABLE`. |
| Edit approvals are required | Unit + integration | Valid section proposal without required QC/owner receipt returns `BLOCKED_MISSING_APPROVAL`; complete receipts advance only through the defined states. |
| Workers are read-only | Negative authorization | Each coding-worker identity attempting create/replace/append/rename/path-alias write returns `DENIED_READ_ONLY` and leaves digest, Git status, and approval state unchanged. |
| Section ownership is enforced | Authorization matrix | Recovery/Guardian, QC, Research, and owner fixtures receive only their allowed proposal operations; unauthorized combinations return `DENIED_SECTION`. |
| Self-approval is impossible | Negative authorization | Same actor as proposer and approver returns `DENIED_SELF_APPROVAL`, including altered display names with same authenticated identity. |
| Validation is fail-closed | Unit/property tests | Bad IDs, hashes, timestamps, paths, versions, sections, duplicate IDs, oversized text, and unknown fields produce typed rejection with no side effect. |
| Append/supersession is deterministic | Integration/replay | Approved append preserves prior entry; approved supersession links exactly one prior ID; duplicate replay is idempotent; conflicting replay is rejected. |
| STOP/PAUSE/quota survive | Integration/restart | Each control blocks proposal/apply before side effect and remains blocked after restart; no marker is removed by the handbook path. |
| Rollback works | Integration/failure injection | Forced post-write verification failure restores the prior verified digest and retains failed candidate/evidence. |
| Compatibility is preserved | Read/upgrade test | Existing Markdown readers can read the canonical document; unknown schema version is rejected by writers and cannot grant access. |

Suggested future focused commands, once implementation exists:

```text
pytest -q tests/handbook_governance
python -m <approved_handbook_validator> --check-canonical
python -m <approved_handbook_validator> --negative-worker-writes
git diff --check
```

The module contract requires typed versioned envelopes and separate failure
domains. The test harness must therefore use an isolated test database and
temporary worktree; it must not touch the canonical SQLite database, live
services, remote refs, secrets, or production handbook.

## 6. S05 — Reviewed implementation plan and allowed paths

1. Confirm the `BASE-008` dependency and current Master/approval state from
   canonical read-only evidence; do not infer readiness from this document.
2. Have the Supervisor and independent QC review this design against
   `AGENTS.md`, `SECURITY.md`, the consolidated architecture, module contracts,
   and the existing handbook. Resolve the open decisions before coding.
3. Implement the smallest approved validator/authorization path in a later
   implementation task, with tests in an isolated test context. Preserve the
   root handbook as the canonical human-readable policy document.
4. Bind every approved candidate to base digest, candidate digest, actor,
   section, receipts, test evidence, and serialized Merger result.
5. Run the planned negative and rollback tests, then have independent QC test
   the exact candidate. Do not mark the parent complete until all child
   receipts and integration evidence exist.

Proposed paths for a later implementation task (not changed here):

| Path | Purpose | Approval needed |
|---|---|---|
| `CODING_HANDBOOK.md` | Canonical policy content/history | Independent review; owner for constitutional/security changes |
| `src/jarvis_v2/sda/` or the already-approved governance module path | Deterministic validation/authorization integration | Reviewed implementation scope |
| `tests/` | Unit, negative, replay, restart, and rollback fixtures | Independent QC |
| `docs/` | This design and later evidence receipts | Normal documentation review |

No implementation path above is authorized by this document; the current
candidate remains under `docs/` only as required by the task contract.

## 7. Child completion map and handoff

| Child | Deliverable in this artifact | Evidence state |
|---|---|---|
| BASE-009.S01 | Requirements-to-acceptance traceability table | Specified; source requirements observed; implementation unknown |
| BASE-009.S02 | Typed proposal, ownership, state, and compatibility contract | Specified; not implemented |
| BASE-009.S03 | Threat/failure matrix and rollback notes | Specified; not tested |
| BASE-009.S04 | Acceptance matrix, negative fixtures, and planned commands | Specified; commands not run |
| BASE-009.S05 | Reviewed-plan inputs, scope proposal, contradictions/open decisions | Proposed; Supervisor/QC approval not present |

Handoff receipt:

`BASE-009 | start SHA 173d4bdacb053e7301cee61e01c802faae6196d5 | changed file docs/tasks/BASE-009-HANDBOOK-GOVERNANCE-DESIGN.md | checks documentation-only scope review and git diff --check planned/not yet run | evidence this design and cited repository contracts | state NOT_VERIFIED | blocker runtime edit approvals and read-only worker enforcement are specified but not implemented or independently tested; BASE-008 readiness and open authorization-store decisions remain unresolved`
