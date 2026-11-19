# REL-017 Verification — installation contract and operator runbooks

Status: `LINUX_SCOPE_EVIDENCE_RECORDED / WINDOWS_NEEDS_VERIFY / CANDIDATE_PENDING_QC`

This report is bound to the Main Codex builder receipt for REL-017. It records
the repository installation contract and local evidence only; it does not claim
a production deployment, a Cloudflare central command queue, native iOS/Xcode
installation, or TWS installation.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `REL-017` |
| Integration base SHA | `af32eee4664645a40f511781c23bb9d8a8e54ea4` |
| Builder branch | `feature/astra-rel-017-a2-99a6ac59` |
| Builder run | `99a6ac59-5be1-4ebc-abd1-6a6c7229fcad` |
| Candidate SHA | Exact REL-017 commit SHA is recorded in the bounded builder-submit receipt |
| Scope | `bootstrap/astra-one/`, `infra/`, `docs/operations/`, task amendment and task-specific `tests/` |
| Remote execution | Disabled; Cloudflare is metadata-monitor only |
| Windows host validation | `NEEDS_VERIFY` after the transfer ZIP and host review |
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
- The owner-authorized `REL-017-LINUX-FIRST-20261119` amendment keeps the
  existing implementation and documentation while deferring Windows host
  validation as `NEEDS_VERIFY`; it does not claim Windows execution.
- `bootstrap/astra-one/astra_one/linux_sda.py` validates the amendment and
  records the bounded deployment-packaging scope without enabling remote work.

## Local checks

| Check | Result |
| --- | --- |
| Existing source-bound root suite evidence | exit 0; 568 tests; `OK` retained from the already-tested implementation |
| `python3 infra/verify_installation.py --json` | exit 0; all five platform entries validated |
| REL-017 focused tests | exit 0; 7 tests; `OK` |
| PowerShell AST parse of `infra/windows/install.ps1` | `NEEDS_VERIFY`; PowerShell is unavailable on this Linux host |
| `git diff --check` | exit 0 |

The expected `unittest` diagnostic about `--json` being single-snapshot only
appears in the existing root suite and does not change its zero exit status.

## Acceptance matrix

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-017.S01` | PASS | Existing contracts, source, tests and migration boundaries were inspected at the pinned base SHA. |
| `REL-017.S02` | PASS | The installation manifest maps each supported platform to bounded artifacts and a runbook. |
| `REL-017.S03` | PASS | Linux units, bounded Windows/WSL artifacts, Cloudflare boundary documentation and verifier are implemented. |
| `REL-017.S04` | PASS | The verifier rejects path escapes, symlinks, incomplete platform declarations and unsafe execution policy; Windows host execution remains unclaimed. |
| `REL-017.S05` | PASS | Seven focused tests and retained source-bound suite evidence pass; Windows host validation remains NEEDS_VERIFY. |
| `REL-017.S06` | PASS | Candidate is committed on the isolated branch and the exact SHA/files are supplied in the bounded Astra builder receipt. |

## External boundaries

No `wrangler login`, remote D1 command, Cloudflare deploy, iOS/Xcode command,
Windows host command, Ollama performance claim, Git push, or database mutation
was performed for this candidate. Windows transfer/host validation remains
`NEEDS_VERIFY`; iOS/Xcode and TWS remain deferred. The optional Windows startup
task is designed to run local deterministic QC/Merger only; it is not proof of
automatic task pull from Cloudflare.

Required handoff line:

`REL-017 | start SHA af32eee4664645a40f511781c23bb9d8a8e54ea4 | branch feature/astra-rel-017-a2-99a6ac59 | candidate SHA is recorded in the bounded builder-submit receipt | changed files docs/tasks/REL-017-VERIFICATION-20261119.md | checks focused installation tests, manifest verifier, retained source-bound suite evidence, git diff --check | evidence this report and Astra builder receipt | state LINUX_SCOPE_EVIDENCE_RECORDED/WINDOWS_NEEDS_VERIFY/CANDIDATE_PENDING_QC | Windows transfer/host validation remains NEEDS_VERIFY; iOS/TWS remain deferred; live Cloudflare deployment remains owner-operated and monitor-only`
