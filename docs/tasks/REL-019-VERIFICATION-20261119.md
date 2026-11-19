# REL-019 — in-scope licensing, provenance, threat model and release audit

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This audit is bound to the REL-019 candidate base and reviews the current
Linux-first, non-TWS release scope. It does not publish, deploy, modify
`main`, execute imported legacy source, or claim native Windows/macOS/iOS/TWS
qualification.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `REL-019` |
| Task payload SHA-256 | `cfc7d674be4979c273a49b8abddec7512563e7420d680c89028ac6d0fd77e30c` |
| Start/integration SHA | `5b22db874704534c2f616285e7ef235f62a04a75` |
| Candidate branch | `feature/astra-rel-019-a1-0f463256` |
| Scope amendment | `ARCHON-TWS-OUT-OF-SCOPE-20261119` |
| Scope amendment SHA-256 | `ec8eb9d28adb55828eb68aba94f1ef5b9137c0792a8c62a495d61bf754d3bef4` |
| Source SHA used by the integration checkout | `75582dbf48057e3d5b0e7cf4acfdba2386acfcff` |
| Protected branches | `main` was not checked out or modified |

## Findings matrix

| Acceptance area | Evidence | Result |
| --- | --- | --- |
| In-scope source provenance | `bootstrap/astra-one/MANIFEST.json` contains 48 SHA-bound runtime entries; `infra/installation_manifest.json` defines the supported release surfaces. | PASS — inventory is pinned for QC. |
| Runtime dependency surface | `pyproject.toml` declares no Python runtime dependencies. The Cloudflare monitor package is a private development/deployment project and is not vendored into the Python runtime. | PASS for the declared local runtime; package-manager license review remains outside this local receipt. |
| Legacy provenance boundary | `migration/provenance/SDA-001-astra-one-v0.2.0.json` binds the archive to ARCHON commit `5227b91d2725bf4be4336a5ad26189fdf1034704`, 32 manifest files and manifest SHA `7a9dff23d3bd9b93f53ddaf308c03db650b5ca91716d5a6f54bcb0af60f110f`. Its policy is `review_only_non_executable`; no runtime path or task state was changed. | PASS as provenance containment; `license_status=unclassified_requires_legal_review` remains explicitly open for the archive and is not converted into a license approval. |
| Legacy import safety | `migration/imported/sda/astra-one-v0.2.0/MANIFEST.json` matches the recorded 32-file archive. The source is not executed as part of this release audit. | PASS for containment and reproducibility. |
| Security/threat boundary | `SECURITY.md`, `bootstrap/astra-one/docs/SECURITY_BOUNDARIES.md`, `src/jarvis_v2/runtime/security.py` and `src/jarvis_v2/guardian/release.py` preserve least privilege, STOP/PAUSE, no self-approval, isolated execution and rollback boundaries. | PASS for static/local controls; no production certification claimed. |
| Deferred platform risk | The active scope amendment records TWS/iOS/device work as deferred and out of scope, with no native evidence claim. `infra/installation_manifest.json` records iOS as `deferred_unclaimed` and TWS as `out_of_scope`. | PASS — residual risk recorded, not waived silently. |
| Hosted controls | Hosted CI/remote branch protection are not used as local proof; hosted quota and unavailable remote enforcement remain deferred under existing policy. | NOT CLAIMED; no remote pass inferred. |

## Subtask evidence plan

| Child | Evidence | Result |
| --- | --- | --- |
| `REL-019.S01` | Pinned task/base/amendment SHAs; runtime and provenance manifests; security boundary files; current platform statuses. | PASS locally |
| `REL-019.S02` | Findings matrix above distinguishes release evidence, containment, open legal classification and deferred platform evidence. | PASS locally |
| `REL-019.S03` | This versioned decision record, with rejected alternative of treating review-only provenance as a license approval. | PASS locally |
| `REL-019.S04` | Independent QC must recheck the SHAs, paths, counts and residual-risk wording against the exact candidate. | PENDING QC |

## Reproducible checks

The following checks are run from this isolated worktree and are bound to the
candidate by the Master submission:

```text
git diff --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_acceptance_evidence.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_migration_guardrails.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_migration_compatibility.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_git_policy.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_guardian_release.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_ci_workflow.py' -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_mig_015_acceptance.py' -q
python3 tools/verify_foundation.py
python3 infra/verify_installation.py --json
```

The seven discovered suites ran 35 tests and all passed. The dotted-module
form is not used because this checkout's `tests/` directory is not a Python
package.

No hosted workflow, remote deployment, Cloudflare resource mutation, native
Apple validation, Windows-host validation or execution of review-only legacy
source is claimed by this record.

## Release decision

The in-scope release has no unreviewed *executable or published* third-party
artifact identified by this audit, and no critical local security finding was
introduced by the report-only candidate. The SDA-001 archive remains a
review-only, non-executable provenance record with an open legal-classification
note. That note must remain visible to QC and release review; it is not a
license grant and does not authorize redistribution or production use.

The deferred TWS/iOS scope is a documented residual risk under the owner-
authorized amendment, not a completion claim for those platforms.

## Handoff

`REL-019 | child_receipts pending Master registration | start_sha 5b22db874704534c2f616285e7ef235f62a04a75 | candidate_sha pending | integration_sha 5b22db874704534c2f616285e7ef235f62a04a75 | branch feature/astra-rel-019-a1-0f463256 | files docs/tasks/REL-019-VERIFICATION-20261119.md | test_evidence focused provenance/security/policy checks + foundation and installation validators | independent_qc pending | merger_result pending | runtime_lane main_builder | retries 0 | blockers review-only SDA-001 legal classification; deferred TWS/iOS/native platform evidence`
