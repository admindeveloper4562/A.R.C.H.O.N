# WIC-012 — Source ranking and primary-evidence labels

**Status:** design candidate; implementation remains a later bounded slice.

**Parent:** WIC-012 — Implement source ranking policy and primary evidence labels

**Base reviewed:** `81c2574a171c5c4643dc9db0fc8bed80ee5ed013`

**Dependency:** WIC-004

**Acceptance:** Original versus secondary sources and disagreement are shown.

## 1. Requirements and constraints

WIC must show where a claim came from without treating a source rank as proof
of truth. The implementation must:

1. Preserve every source observation and citation through clustering and
   summary projection.
2. Label a source as `primary`, `secondary` or `unknown` only from an
   explicit, reviewed source policy.
3. Show disagreement as disagreement; it must not be resolved by rank or by
   an inferred confidence value.
4. Keep publication, fetch and event times independent and retain corrections
   and retractions.
5. Keep WIC storage in WIC and use the existing Research finding boundary;
   there is no direct Finance write or trade/action effect.

Non-goals are live source discovery, an automatic trust score, silent source
promotion, changing the existing task ledger, a new module, a new network
capability or financial execution.

## 2. Versioned data contract

The implementation should add the smallest WIC-owned value object needed by
the existing `SourceObservation`, `StoryCluster`, `ClaimRecord`,
`SummarySegment` and `WorldCard` records:

```text
EvidenceLabelV1 {
  source_id: BoundedId,
  observation_id: BoundedId,
  citation_url: ApprovedHttpsUrl,
  source_class: primary | secondary | unknown,
  rank: OptionalInteger,       // lower is preferred; null for unknown
  policy_ref: BoundedReference,
  labelled_at: UTC timestamp
}
```

The policy input is an existing Research `SourcePolicy` plus an explicit,
versioned WIC classification record. `SourcePolicy` allowlisting proves only
that an HTTPS host and public scope are permitted; it does not make the source
primary. A source without a matching classification remains `unknown`.

An evidence-bearing claim retains an ordered set of labels and all original
citations. A `ResearchFinding` maps source IDs, citations and evidence refs
without dropping contradictory assertions. A `WorldCard` renders the labels,
dates, source links and correction state; it never renders a rank as a fact
confidence value.

## 3. Ranking policy

The policy is deterministic and reviewable:

| Class | Meaning | Example boundary | Rank |
| --- | --- | --- | --- |
| `primary` | Direct record or statement from the responsible first-party authority | Official publication, filing, court record or named organization statement | Explicit policy value |
| `secondary` | Reporting or analysis that cites or describes an event but is not the first-party record | Authorized news or research publisher | Explicit policy value |
| `unknown` | Source identity, provenance or classification is incomplete | Unclassified or conflicting metadata | `null` |

The policy never derives class from URL text, headline wording or model
output. It never changes a claim's `verified`, `supported` or `uncertain`
state. When primary and secondary claims disagree, both labels and both
assertions remain visible, the finding is uncertain, and confidence remains
unknown unless an independent corroboration rule supplies it.

## 4. Ownership and sequence

```text
authorized observation
  -> SourcePolicy validation
  -> EvidenceLabelV1 assignment
  -> cluster while retaining every observation
  -> Research comparison/corroboration
  -> claim revision and correction history
  -> cited summary / WorldCard
  -> read-only dashboard projection
```

ATLAS/Backend validates the shared envelope and capabilities. Research owns
source comparison and cited findings. WIC owns labels attached to WIC
observations, claims and dashboard records. Finance remains a separate module;
no ranking path may call a trade or order operation. A label assignment is
idempotent on `(source_id, observation_id, policy_ref)` and a changed policy
creates a new revision rather than rewriting history.

## 5. Safety and failure matrix

| Condition | Required result |
| --- | --- |
| Missing policy classification | Store/display `unknown`; do not infer `secondary` or publish an unlabelled primary claim. |
| Unallowlisted or non-HTTPS citation | Reject before persistence. |
| Duplicate label assignment | Return the existing revision without a second effect. |
| Primary and secondary disagreement | Preserve both observations and assertions; display the disagreement and use unknown confidence. |
| Source correction or retraction | Append a revision, retain the prior label and expose the correction/retraction reason. |
| Source fetch outage | Keep the last dated record with stale state; do not claim current truth. |
| STOP, PAUSE or quota | Retain state and do not create a new fetch or non-idempotent effect. |
| Cross-module or finance action request | Deny at the capability boundary; labels have no action authority. |

No source content is executed. No private records, secrets or raw model
conversations are stored in the label. The policy is not a permission grant.

## 6. Acceptance-to-test matrix

| Acceptance clause | Test | Expected evidence |
| --- | --- | --- |
| Original source is labelled primary | Unit | An explicitly classified first-party source round-trips with `primary`, policy reference and citation. |
| Secondary source is labelled secondary | Unit | An explicitly classified reporting source round-trips with `secondary`; rank remains metadata, not confidence. |
| Missing classification is visible | Negative | Unknown source is retained as `unknown` and cannot be silently promoted. |
| Disagreement is shown | Integration | Primary and secondary assertions for one cluster preserve both labels, citations and contradictory text. |
| Provenance survives projection | Integration/replay | Label, observation, claim and correction references survive store reopen and dashboard serialization. |
| No direct trade effect | Security/contract | Attempted finance/action callback is absent or denied; WIC projection remains read-only. |
| Replay is idempotent | Crash/replay | Re-submit the same identity and policy reference; exactly one label revision is retained. |

Focused WIC and Research tests, relevant Backend authorization tests, local
security checks and the approved no-network container QC are required for the
implementation candidate. Hosted workflows, live publishers and real Finance
data remain external evidence and cannot be replaced by fixtures.

## 7. Implementation boundary and decision

The smallest implementation is a WIC-local label value object, a bounded
policy table/adapter and read-only projection fields. It should reuse the
existing SQLite ownership conventions and avoid a second source registry. No
code, database migration or external authorization is required for this
design candidate. The implementation must not mark unknown or contradictory
evidence as primary, verified or actionable.
