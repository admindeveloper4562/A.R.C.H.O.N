# REL-022 verification — private GitHub Free release baseline

REL-022 originally required protected-branch CI, tag provenance and deployment
receipts. The private repository remains on GitHub Free. A read-only request to
the branch-protection and ruleset endpoints returned HTTP 403 stating that the
feature requires GitHub Pro or public visibility. No public-visibility change,
Pro purchase, unauthorized push, `main` change, or release tag was attempted.

## Amendment binding

| Binding | Value |
| --- | --- |
| Original parent plan SHA-256 | `10cb1ed53eace6af1c5d052ef0ad0a85eaf9f535db5ae0be794cc7d12752b154` |
| Original REL-022 payload SHA-256 | `127a27a11353ec291835bb9789274ce35639b2932668758d4db1bc81a2ed38e1` |
| Amendment | `REL-022-GITHUB-FREE-20261119` v2 |
| Amendment payload SHA-256 | `ad84a6e8bb351e1f40f8382fc3dd7361e9a21cba336c7ced0827d3ad3fcab10b` |
| Amendment artifact SHA-256 | `50e4f0c4f8610a993b89226136869f34d96b202e31877ef1982f1a9d1bca43d6` |
| Current integration base | `a6826ee43d7c0520c43cd4aa75d085a4940a4ec8` |
| Current source reference | `75582dbf48057e3d5b0e7cf4acfdba2386acfcff` |
| Current graph binding | 247 parents, 1,359 children, 443 dependency edges |

The Master validated the amendment against the live plan and payload, created a
verified checkpoint, recorded the amendment transactionally, resolved the
`remote_policy_unavailable` case, and re-admitted REL-022. The original
acceptance remains historical provenance; the amended acceptance is the active
task contract.

## Acceptance matrix

| Requirement | Result | Evidence boundary |
| --- | --- | --- |
| Server-enforced protected-branch CI and rejected unauthorized push | `DEFERRED_PLAN` | GitHub Free HTTP 403; no remote rejection is claimed |
| Local source policy and provenance | PASS | SHA-bound source/base/integration records, local policy checks and serialized Merger controls |
| Independent review and integration | PASS when this candidate is accepted | Candidate-bound deterministic QC and one-writer Merger receipt are required |
| Hosted CI evidence | `DEFERRED_PLAN` | Local checks are not represented as hosted CI |
| Tag provenance and deployment receipts | PASS for the local development baseline | Immutable SHA records and existing release receipts are checked; no release tag or production deployment is performed |
| Publication | Not performed | Owner-authorized, fast-forward-only publication remains a separate operation |

## Child evidence map

| Child | Evidence |
| --- | --- |
| REL-022.S01 | Current integration/source refs, task amendment and read-only GitHub capability result inspected |
| REL-022.S02 | Original-to-amended acceptance and residual-risk contract recorded in the amendment artifact |
| REL-022.S03 | Local-policy release baseline reuses the existing Merger, ancestry and receipt mechanisms; no protected ref is written |
| REL-022.S04 | Negative remote-capability result and no-publication boundary are recorded |
| REL-022.S05 | Focused acceptance, CI-workflow and Git-policy tests are run against this candidate |
| REL-022.S06 | Candidate SHA, changed path, test results and independent QC receipt are recorded by the Master |

## Local verification commands

```text
git diff --check
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_acceptance_evidence.py' -q
python3 -m unittest discover -s tests -p 'test_ci_workflow.py' -q
python3 -m unittest discover -s tests -p 'test_git_policy.py' -q
```

The GitHub-hosted branch-protection and CI properties unavailable on the private
Free plan remain explicitly unclaimed. This task does not authorize a release,
production deployment, protected-branch modification, or remote tag creation.
