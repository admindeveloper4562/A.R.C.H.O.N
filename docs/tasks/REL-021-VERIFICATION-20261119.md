# REL-021 — owner release-gate decision record

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This record verifies the authenticated owner decision for the frozen in-scope
release candidate. It does not promote `main`, create a tag, deploy production,
or perform a native SDA cutover.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `REL-021` |
| Run | `e2f1f82e-8dde-4ec1-8080-65c5c06e6cff` |
| Task payload SHA-256 | `f56ac3a005adbcd054eccc5dd70c306f7ab44ec39dbe67aec264a18edbd0990e` |
| Frozen release candidate SHA | `8b526c4031deab215674fef40d8c5457e2b7424b` |
| Candidate base SHA | `8b526c4031deab215674fef40d8c5457e2b7424b` |
| Rollback target | `29c11f860bcb203e388b6956bbac28462de81fcf` |
| Source SHA | `75582dbf48057e3d5b0e7cf4acfdba2386acfcff` |
| Owner receipt ID | `d3d31079-710e-41bd-a1c3-1e7d603b4e81` |
| Owner receipt SHA-256 | `3b389f1680239f814e74fdb8050facf76b0b8c28fe41fbe611fd55024bdac04e` |
| Owner identity | `owner` |
| Candidate branch | `feature/astra-rel-021-a1-e2f1f82e` |

The owner receipt was verified and registered by the deterministic Master
before this generation was claimed. Its signed payload is bound to the exact
REL-021 task payload, architecture digest and frozen integration SHA above.

## Acceptance matrix

| Child | Evidence | Result |
| --- | --- | --- |
| `REL-021.S01` | Decision packet binds the release candidate SHA, source SHA, scope, rollback target and exact owner decision. | PASS locally |
| `REL-021.S02` | REL-020 is completed; the frozen candidate is the current integration SHA; the rollback target is its verified ancestor; no protected branch was changed. | PASS locally |
| `REL-021.S03` | Authenticated owner receipt was verified through `approve-owner` and recorded in SQLite. | PASS — owner decision registered |

## Safety boundary

The approval authorizes the release-gate decision record only. The serialized
Merger must still verify this candidate and the project must not promote
`main`, tag a release, deploy production, or cut over native SDA without the
separate applicable workflow and controls. Windows/macOS/iOS/TWS evidence
remains deferred and is not inferred from this approval.

## Reproducible checks

```text
SQLite PRAGMA integrity_check: ok
REL-020: completed at 8b526c4031deab215674fef40d8c5457e2b7424b
Rollback ancestry: 29c11f860bcb203e388b6956bbac28462de81fcf is an ancestor
of 8b526c4031deab215674fef40d8c5457e2b7424b
Owner receipt: verified and registered before claim
```

The local owner-approval and scope-boundary test suites are run against this
isolated worktree before submission. No remote workflow or production effect
is used as evidence.

## Handoff

`REL-021 | child_receipts pending Master registration | start_sha 8b526c4031deab215674fef40d8c5457e2b7424b | candidate_sha pending | integration_sha 8b526c4031deab215674fef40d8c5457e2b7424b | branch feature/astra-rel-021-a1-e2f1f82e | files docs/tasks/REL-021-VERIFICATION-20261119.md | test_evidence owner-approval, rollback-ancestry and SQLite checks | independent_qc pending | merger_result pending | runtime_lane main_builder | retries 0 | blockers no automatic main promotion or production deployment`
