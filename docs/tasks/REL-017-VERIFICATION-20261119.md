# REL-017 Verification — installation contract and operator runbooks

Status: `LOCAL_EVIDENCE_RECORDED / CANDIDATE_PENDING_QC`

This report is bound to the Main Codex builder receipt for REL-017. It records
the repository installation contract and local evidence only; it does not claim
a production deployment, a Cloudflare central command queue, native iOS/Xcode
installation, or TWS installation.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `REL-017` |
| Integration base SHA | `a5e152c1019b6868718dd7014c66760c01b1776d` |
| Builder branch | `feature/astra-rel-017-a2-287d8858` |
| Builder run | `287d8858-0c25-403a-9640-ddc274d367b7` |
| Candidate SHA | Exact REL-017 commit SHA is recorded in the bounded builder-submit receipt |
| Scope | `bootstrap/astra-one/`, `infra/`, `docs/operations/`, task amendment and task-specific `tests/` |
| Remote execution | Disabled; Cloudflare is metadata-monitor only |
| Native iOS | `deferred_unclaimed` |
| TWS | `out_of_scope` by owner-requested amendment |

## Implementation

- `infra/installation_manifest.json` declares the Linux, Windows/WSL,
  Cloudflare, iOS and TWS status, required tools, artifacts and state boundary.
- `infra/verify_installation.py` performs a read-only path, artifact, platform
  and secret-name validation. It never installs packages or invokes a remote
  service.
- `infra/systemd/archon-astra.service` and `.timer` provide a hardened,
  user-level QC/Merger timer. They do not launch a coding worker or claim a
  remote queue item.
- `infra/windows/install.ps1` checks local WSL prerequisites and, only with an
  explicit owner-selected mode, registers a local QC/Merger startup task.
- `infra/cloudflare/README.md` binds deployment to the existing Astra monitor
  package and names only the two secure secret names, never their values.
- `docs/operations/INSTALLATION_RUNBOOK.md` documents reproducible commands,
  stop conditions, and all deferred evidence boundaries.
- The owner-authorized `REL-017-DEPLOYMENT-ARTIFACT-SCOPE-20261119` amendment
  binds the repository installation contract to the controller path allowlist;
  `.service`, `.timer` and `.ps1` are the only newly allowlisted suffixes.
- `bootstrap/astra-one/astra_one/linux_sda.py` validates the amendment and
  records the bounded deployment-packaging scope without enabling remote work.

## Local checks

| Check | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -q` | exit 0; 568 tests; `OK` |
| Same root suite in Python 3.11 Docker | exit 0; 568 tests; network `none`, read-only source, dropped capabilities |
| `python3 infra/verify_installation.py --json` | exit 0; all five platform entries validated |
| REL-017 focused tests | exit 0; 7 tests; `OK` |
| PowerShell AST parse of `infra/windows/install.ps1` | exit 0; parse OK |
| `git diff --check` | exit 0 |

The expected `unittest` diagnostic about `--json` being single-snapshot only
appears in the existing root suite and does not change its zero exit status.

## Acceptance matrix

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-017.S01` | PASS | Existing contracts, source, tests and migration boundaries were inspected at the pinned base SHA. |
| `REL-017.S02` | PASS | The installation manifest maps each supported platform to bounded artifacts and a runbook. |
| `REL-017.S03` | PASS | Linux units, Windows/WSL check/registration script, Cloudflare boundary documentation and verifier are implemented. |
| `REL-017.S04` | PASS | The verifier rejects path escapes, symlinks, incomplete platform declarations and unsafe execution policy; the controller allowlist covers the three checked-in deployment manifest types. |
| `REL-017.S05` | PASS | Seven focused tests plus the full root suite pass; no sensitive values or remote command channel are introduced. |
| `REL-017.S06` | PASS | Candidate is committed on the isolated branch and the exact SHA/files are supplied in the bounded Astra builder receipt. |

## External boundaries

No `wrangler login`, remote D1 command, Cloudflare deploy, iOS/Xcode command,
Windows hardware benchmark, Ollama performance claim, Git push, or database
mutation was performed for this candidate. Those actions remain owner- or
device-dependent external gates. The optional Windows startup task is designed
to run local deterministic QC/Merger only; it is not proof of automatic task
pull from Cloudflare.

Required handoff line:

`REL-017 | start SHA a5e152c1019b6868718dd7014c66760c01b1776d | branch feature/astra-rel-017-a2-287d8858 | candidate SHA is recorded in the bounded builder-submit receipt | changed files bootstrap/astra-one/MANIFEST.json bootstrap/astra-one/astra_one/linux_runtime.py bootstrap/astra-one/astra_one/linux_sda.py docs/operations/INSTALLATION_RUNBOOK.md docs/tasks/REL-017-VERIFICATION-20261119.md docs/tasks/amendments/REL-017-DEPLOYMENT-ARTIFACT-SCOPE-20261119.json infra/cloudflare/README.md infra/installation_manifest.json infra/systemd/archon-astra.service infra/systemd/archon-astra.timer infra/verify_installation.py infra/windows/README.md infra/windows/install.ps1 tests/test_rel017_installation.py | checks full Python 3.12/3.11 suites, focused installation tests, manifest verifier, PowerShell parse, verifier, git diff --check | evidence this report and Astra builder receipt | state LOCAL_EVIDENCE_RECORDED/CANDIDATE_PENDING_QC | blockers native iOS/Xcode and TWS remain explicitly deferred; live Cloudflare deployment remains owner-operated and monitor-only`
