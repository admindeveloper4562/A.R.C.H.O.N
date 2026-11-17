# WIC-001 — World stories, events, sources, dates and confidence

**Status:** design artifact; implementation and acceptance are `NOT_VERIFIED`.

**Task:** `WIC-001`
**Execution mode:** `design`
**Base reviewed:** `66ce4002641865c9a6a50e2ce000faa7e62dfde6`
**Dependencies:** `BACK-001`, `CORE-014`
**Allowed candidate change:** this document under `docs/` only.

This document defines the smallest reviewed WIC contract needed by the task.
It does not add a runtime service, fetch live sources, alter SQLite, create a
dashboard, or claim that a later implementation already exists.

## 1. Requirements and traceability

| Requirement | Design response | Evidence required | State |
|---|---|---|---|
| Acceptance: published, fetched and event dates are independent | `SourceObservation` stores publication and fetch times; `StoryEvent` stores the event time and precision independently. Missing dates remain unknown. | Schema and negative tests prove that one date cannot overwrite another. | Specified; not implemented |
| Updates and corrections are independently stored | A new `StoryRevision` references its predecessor; `CorrectionRecord` and `RetractionRecord` preserve reason, effective time and source references. | Replay and correction tests prove history and current status both remain available. | Specified; not implemented |
| Source attribution survives clustering | Every story revision and event retains one or more observation IDs and canonical source references. Deduplication groups records but never erases attribution. | Two-outlet fixture with the same event retains both source records. | Specified; not implemented |
| Confidence is explicit and honest | Confidence is a bounded value or `unknown`, with a grading basis and observation references. No value is inferred when corroboration is absent or contradictory. | Confidence boundary and disagreement fixtures. | Specified; not implemented |
| WIC module contract | The design covers dated world/Thai news, clustering, corrections and alerts while keeping WIC ownership in `src/jarvis_v2/wic/`. | Contract review and later module tests. | Observed in base; implementation unknown |
| Pipeline behavior | Permitted observation -> normalization -> clustering -> corroboration -> summary -> snapshot/opt-in alert. A failed source leaves the feed stale and visible. | State-machine and failure-injection tests. | Specified; not implemented |
| Ten-module architecture | WIC remains module 07; Business is absent; Backend owns shared envelopes and WIC owns its domain records. | Existing manifest/contract validation. | Observed in base |

### Scope and non-goals

This task specifies typed records, ownership, transitions, safety and a later
test boundary. It does not implement a network fetcher, source allow-list,
summary model, alert transport, RAG index, financial action, Cloudflare job,
database migration, UI or deployment. It does not treat a headline as a trade
instruction and does not claim live or remote evidence.

Open implementation decisions are the concrete storage adapter, permitted
source registry, clustering algorithm, retention policy, alert transport and
the exact confidence calibration. Those decisions belong to the later
implementation tasks and must be reviewed against the inherited Backend/Core
contracts before activation.

## 2. Records, ownership and compatibility

The later implementation should use versioned, typed records. Values below
are contract fields, not a claim that the classes or tables already exist.

### 2.1 Source observation

```text
SourceObservationV1 {
  observation_id: OpaqueId,
  publisher_id: BoundedName,
  canonical_url: ApprovedReference,
  fetched_at: UTC timestamp,
  published_at: Optional UTC timestamp,
  source_updated_at: Optional UTC timestamp,
  title_digest: Sha256,
  content_digest: Sha256,
  language: BoundedName,
  provenance_ref: VersionedReference
}
```

`fetched_at`, `published_at` and `source_updated_at` are separate fields.
An absent or malformed date is retained as unknown with a stable diagnostic;
it is never replaced with the fetch time. The source reference is an approved
metadata reference, not an instruction or an authorization.

### 2.2 Story and event

```text
StoryV1 {
  story_id: OpaqueId,
  revision_id: OpaqueId,
  observation_ids: OrderedUniqueIds,
  canonical_key: BoundedDigest,
  status: active | corrected | retracted | stale,
  confidence: bounded score | unknown,
  confidence_basis: BoundedName | unknown,
  first_seen_at: UTC timestamp,
  last_updated_at: UTC timestamp
}

StoryEventV1 {
  event_id: OpaqueId,
  story_id: OpaqueId,
  event_at: Optional UTC timestamp,
  event_time_precision: exact | day | month | year | unknown,
  location_ref: Optional BoundedReference,
  observation_ids: OrderedUniqueIds,
  event_digest: Sha256
}
```

`event_at` is the date the described event occurred, not when the publisher
published it or when ARCHON fetched it. A story can have several events and a
revision can update the event record without mutating its prior revision.

### 2.3 Revision, correction and retraction

```text
StoryRevisionV1 {
  revision_id: OpaqueId,
  story_id: OpaqueId,
  predecessor_revision_id: Optional OpaqueId,
  observation_ids: OrderedUniqueIds,
  summary_ref: VersionedReference,
  created_at: UTC timestamp,
  effective_at: UTC timestamp,
  revision_reason: initial | update | correction | retraction,
  revision_digest: Sha256
}

CorrectionRecordV1 {
  correction_id: OpaqueId,
  story_id: OpaqueId,
  supersedes_revision_id: OpaqueId,
  replacement_revision_id: OpaqueId,
  reason_ref: VersionedReference,
  observation_ids: OrderedUniqueIds,
  recorded_at: UTC timestamp
}
```

A retraction is a revision state and a durable record; it is not deletion.
Conflict between sources preserves both observations and lowers confidence or
leaves it unknown. A correction cannot point to a missing predecessor, and a
replay with the same identity and digest is a no-op.

### 2.4 Ownership and API boundary

WIC owns source observations, stories, events, revisions, corrections and
derived dashboard snapshots. Backend validates shared versioned envelopes,
capabilities and durable receipts; Core owns task/event scheduling; Research
may provide cited findings through the approved envelope. No dependency grants
WIC write access to another module, and WIC cannot write finance, Guardian or
automation records directly.

Cross-module requests use the inherited `archon.request/1` envelope and a
module-local WIC scope. A dashboard or alert contains references to the
reviewed WIC revision and source observations, not unbounded source material.
Existing `jarvis_v2` paths and historical records remain compatible.

### 2.5 State and idempotency

```text
RECEIVED -> NORMALIZED -> CLUSTERED -> CORROBORATED -> PUBLISHED
                                      |              |
                                      +-> UNCERTAIN  +-> SNAPSHOTTED
                                      +-> QUARANTINED
```

Corrections and retractions append a revision and update the derived current
status. The idempotency key is `(publisher_id, canonical_url, content_digest,
source_updated_at)` when the publisher supplies an update time; otherwise the
stable source observation identity and content digest are used. Conflicting
bytes never silently replace an existing observation. All transitions carry a
bounded diagnostic and source/revision references.

## 3. Safety, failure and rollback matrix

| Failure or threat | Detection/prevention | Required result |
|---|---|---|
| Missing or invalid date | Typed parser and explicit precision | Preserve unknown; never substitute a current time |
| Duplicate observation | Stable source identity and content digest | Return the existing observation without a second effect |
| Same event from different outlets | Canonical clustering key plus source set | Group without deleting attribution |
| Source disagreement | Corroboration rules and bounded confidence | Keep both observations; mark uncertain or lower confidence |
| Correction or retraction | Predecessor/replacement references | Append history; update derived status; retain prior revision |
| Fetch failure or stale source | Per-source health and last-success timestamp | Keep a visibly stale feed; do not report it as live |
| Untrusted or malformed source data | Schema, size and reference validation before persistence | Reject or quarantine; no partial domain effect |
| Cross-module scope expansion | Backend capability and WIC-owner check | Deny before dispatch and record a bounded receipt |
| Duplicate opt-in alert | Alert idempotency key and consent scope | One alert effect at most; no implicit subscription |
| STOP, PAUSE or quota control | Check before fetch admission and non-idempotent effect | Retain queue state; never clear controls automatically |
| Migration or integration failure | Copied DB backup, integrity check and last-known-good pointer | Roll back the affected candidate without deleting history |

No design decision grants access to private records, production services or
financial execution. A later implementation must use the existing permission
broker and independent QC boundary.

## 4. Acceptance-to-test matrix

This is a plan for later implementation. No runtime tests or live fetches are
claimed by this design candidate.

| Acceptance clause | Test class | Planned fixture/evidence |
|---|---|---|
| Published, fetched and event dates are independent | Unit/negative | Construct a source with three different dates; verify each survives round-trip, then omit each field and verify `unknown`/precision behavior. |
| Updates and corrections are independently stored | Integration/replay | Insert an initial revision, update, correction and retraction; verify predecessor links, current status and complete history. |
| Source attribution survives deduplication | Integration | Two synthetic outlets describing one event produce one story with two observations and no lost source reference. |
| Confidence is not fabricated | Negative | Uncorroborated and contradictory observations remain `unknown` or use the bounded disagreement result; no score is guessed. |
| WIC pipeline is fail-closed | Failure injection | Malformed source, fetch timeout and invalid reference produce quarantine/stale state without a partial story effect. |
| Replay is idempotent | Crash/replay | Re-submit the same observation and correction before and after a simulated restart; verify one record/effect per identity. |
| Module ownership is enforced | Security/contract | Attempt a foreign-module write and an unscoped alert; both are rejected before persistence. |
| Controls and rollback survive restart | Control/restore | Apply a disposable control/restore scenario and verify no new effect while stopped and no history deletion after rollback. |
| Evidence is reviewable | QC/merge | Bind candidate SHA, changed document, source/base SHA, focused checks and independent child receipts. |

The later implementation should run focused WIC tests, relevant Backend/Core
regressions, local security checks and the approved no-network container QC.
Hosted CI, live publishers, hardware and production acceptance remain
external gates and cannot be certified by synthetic fixtures.

## 5. Reviewed implementation boundary

The design is checked against the current `AGENTS.md`, `SECURITY.md`,
`CODING_HANDBOOK.md`, `docs/architecture/MODULE_CONTRACTS.md` and the WIC
section of `JARVIS_V2_CONSOLIDATED.md`.

The subsequent implementation may be split into the smallest reviewed slices:

1. Add the WIC domain types and pure validation under
   `src/jarvis_v2/wic/`, reusing Backend/Core envelopes rather than creating a
   second control plane.
2. Add isolated unit, correction, deduplication, uncertainty and restart
   tests under `tests/`.
3. Add persistence only after the adapter and migration have a copied-database
   backup, integrity check and restore rehearsal.
4. Add source fetching and dashboard/alert adapters only with the required
   permission, provenance and opt-in checks.

The current candidate changes no source, test, configuration, policy,
database or tool file. It proposes no new module, privilege, owner gate or
external integration. S01 is addressed by §1; S02 by §2; S03 by §3; S04 by
§4; and S05 by this boundary and its explicit implementation prerequisites.

## 6. Design conclusion

The acceptance contract is satisfied at the design level: publication,
fetch and event dates are distinct; revisions, corrections and retractions
are append-only and source-attributed; deduplication preserves disagreement;
confidence can remain unknown; and stale/failure behavior is visible. Runtime
implementation, tests, QC, integration and any external authorization remain
unverified and are intentionally left to the dependent implementation tasks.
