# FIN-002 — Read-only scopes and independent partner consent

Status: design candidate

This document is the bounded design deliverable for FIN-002.S01–S05. It
defines the authorization contract; it does not connect to Mira, read
financial rows, create credentials, or claim host/production evidence.

## Baseline and constraints

- Task: `FIN-002`
- Objective: define read-only scopes and independent partner consent
  enforcement.
- Acceptance: unauthorized cross-person rows are rejected server-side.
- Dependencies: `FIN-001`, `BACK-004`; both must be integrated before the
  implementation task that consumes this contract.
- Module: Finance; Business remains excluded.
- Design base: `721c02d91f40e8af220477dc0f64c3f13a10e3f6`
- Pinned source: `43c8db7de8a5f0277a7db23379019d05f2edd2c6`
- Non-goals: cookie scraping, shared D1 admin credentials, financial writes,
  trading, row export, or inference of consent from a single session.

## FIN-002.S01 — Requirements and traceability

| Requirement | Contract decision | Evidence planned |
|---|---|---|
| ARCHON access is read-only | Admit `GET` only; reject every write method before data access | Negative method test |
| A person may read their own rows | Self scope requires an exact requester/row-owner match | Self-row test |
| Shared partner access is explicit | Shared scope names one partner and requires two active consent records | Reciprocal-consent tests |
| Cross-person access is denied | A row owner must be the requester or named partner; a third owner is rejected | Third-owner test |
| Consent is independently revocable | Each direction is a separate record; either inactive record denies shared access | Revocation test |
| Existing Mira auth remains authoritative | ARCHON consumes bounded, already-authorized metadata and never assumes production DB access | Integration review |

The implementation must enforce the row predicate before selecting or
serializing a financial row. Filtering after retrieval is not sufficient.

## FIN-002.S02 — Versioned interface and data contract

Contract version: `mira-read-consent.v1`

The server-side authorization boundary receives this bounded request:

```text
ReadRequest {
  requester_id: opaque identifier,
  row_owner_id: opaque identifier,
  scope: "mira:read:self" | "mira:read:shared",
  partner_id: opaque identifier | absent,
  method: "GET"
}
```

The consent store exposes metadata only:

```text
PartnerConsent {
  subject_id: opaque identifier,
  partner_id: opaque identifier,
  scope: "mira:read:shared",
  active: boolean,
  version: monotonically increasing value,
  issued_at: timestamp
}
```

Admission sequence:

1. Validate identifiers, method and scope; fail closed on malformed input.
2. For self scope, require `requester_id == row_owner_id` and no partner
   expansion.
3. For shared scope, require a distinct named partner and require the row
   owner to be one of the two named identities.
4. Require active records for both `(requester, partner)` and
   `(partner, requester)` at the current consent version.
5. Only then execute or serialize the row query.

The decision is deterministic and returns either an allow result or one of
the bounded errors `finance_read_only`, `finance_scope_denied`, or
`finance_partner_consent_required`. It never returns row contents.

## FIN-002.S03 — Safety and failure matrix

| Condition | Required result | Recovery/rollback |
|---|---|---|
| Non-`GET` method | Deny with `finance_read_only` | No retry; audit the denied request |
| Self scope with another owner | Deny with `finance_scope_denied` | No fallback scope |
| Shared scope missing either direction | Deny with `finance_partner_consent_required` | Re-evaluate after a fresh consent event |
| Consent revoked or version stale | Deny closed | Revoke cached decision and require a new version |
| Third-party row owner | Deny with `finance_scope_denied` | Never broaden the partner set |
| Duplicate consent event | Idempotent same-version result; conflicting payload is rejected | Preserve the last valid record |
| Missing/unknown consent store | Deny closed | Surface dependency failure; do not read rows |
| STOP/PAUSE or security hold | Deny and preserve the control marker | Resume only through the controller |

No failure path authorizes access, retries a write, or falls back to a
shared administrator credential. Consent changes must be auditable and
revocable without changing historical receipts.

## FIN-002.S04 — Acceptance-to-test matrix

The implementation generation must add focused deterministic tests within the
finance/test scope. The required cases are:

| Case | Fixture | Expected result |
|---|---|---|
| Own row | Alice requests Alice, self scope | Allow |
| Cross-person self scope | Alice requests Bob, self scope | Deny before row access |
| One-way shared consent | Alice/Bob row, only Alice consent | Deny |
| Reciprocal shared consent | Alice/Bob row, both consents active | Allow |
| Third owner | Alice/Bob scope, Carol row | Deny |
| Revoked consent | Reciprocal pair with one inactive record | Deny |
| Write method | Any row with `POST`, `PATCH` or `DELETE` | Deny |
| Invalid/missing identity | Empty, malformed or missing identifiers | Deny |

The focused command is:

```text
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_finance_*.py'
```

Docker no-network QC must run the same focused tests against the exact
candidate SHA. Hosted CI is not substituted for local evidence.

## FIN-002.S05 — Reviewed implementation plan

The implementation is limited to the finance authorization boundary and its
deterministic tests. It must call the row-level guard before any Mira row is
returned, preserve the existing `MiraAuditSnapshot` metadata-only boundary,
and avoid changing the external Worker, D1 schema, credentials, or task
ledger. A future connector task may consume this contract but may not widen
it.

Review checklist:

- [x] Finance module contract and Business exclusion considered.
- [x] `SECURITY.md` least-privilege, fail-closed and no-secret rules applied.
- [x] `CODING_HANDBOOK.md` isolated candidate, focused tests and independent QC
  requirements applied.
- [x] Scope is limited to `src/jarvis_v2/finance/` and `tests/` for the
  implementation generation.
- [ ] Implementation, deterministic tests, independent QC and integration
  remain requirements of the subsequent implementation candidate.

This design does not claim that the implementation or production acceptance
has already been performed.
