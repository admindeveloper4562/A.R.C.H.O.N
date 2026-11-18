# MIG-012 Verification — guarded owner gate

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This candidate records the authenticated owner-gate decision and the
reversible local checkpoint used for the guarded development workflow. It does
not perform native SDA cutover, production deployment, remote publication or
retire Astra One.

## Pinned identity

| Field | Value |
| --- | --- |
| Task | `MIG-012` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Candidate base / rollback SHA | `2ebb3ad294bf611bec22df5c3851532e25fe120a` |
| Candidate SHA | Bound by the Master after commit |
| Destination host | `reaper` local development host only |
| Integration checkout | `/home/r34p3r/.local/state/archon-astra/integration-reconciled-20261114` |
| Remote publication | Not attempted |
| Native SDA cutover | Not performed |

The candidate base is the last-known-good active controller checkpoint. If
this candidate is rejected or its integration is rolled back, the Merger and
trusted watchdog retain that checkpoint; no Git history rewrite is required.

## Owner decision evidence

The deterministic Master verified the signed receipt at:

`/home/r34p3r/.local/state/archon-astra/private/owner-approvals/MIG-012-v6/MIG-012.json`

Recorded receipt facts:

- Decision: `APPROVE`.
- Principal: `owner`.
- Task payload SHA: `72a107e2c943499e876624ba0d570438a3054e913b46bce88b119c4d7e3f68e2`.
- Source SHA: `43c8db7de8a5f0277a7db23379019d05f2edd2c6`.
- Approval-time integration SHA: `9f211667d137061701dc6d704bfaf351a205d2b9`.
- Receipt SHA-256: `d1d6add706f2748f5e0654dd8b6a39b4b69fd70dffef51695a77e2ac2402b8fa`.

The approval-time checkpoint is retained as provenance. The later controller
upgrade to `2ebb3ad294bf611bec22df5c3851532e25fe120a` was activated through
the independently tested trusted-watchdog upgrade path, with rollback to
`9f211667d137061701dc6d704bfaf351a205d2b9`; it is not represented as a
native-SDA production cutover.

## Gate checks

| Requirement | Evidence | Result |
| --- | --- | --- |
| One deterministic Master | Canonical SQLite ledger and one active integration checkpoint | PASS |
| Authenticated owner decision | SSH Ed25519 receipt verified by `approve-owner` | PASS |
| Candidate/rollback identity | Master base SHA and watchdog rollback checkpoint are recorded above | PASS |
| Destination boundary | Local `reaper` development checkout only | PASS |
| STOP/PAUSE/quota preservation | Trusted watchdog check: all clear; controls remain enforced | PASS |
| Reversible integration | Fast-forward-only Merger/watchdog path; previous checkpoint retained | PASS |
| Native SDA deployment | Not requested by this candidate; remains a later separately gated operation | NOT PERFORMED |

## Required verification

The independent QC lane must review the exact candidate commit, verify the
changed-file scope and rerun the relevant Astra tests. The serialized Merger
must record the final candidate and integration SHAs before this parent can
become `completed`.

No child is marked complete by this document alone. Child receipts remain the
Master's responsibility and must bind the final candidate SHA, test evidence,
QC receipt and resulting integration SHA.
