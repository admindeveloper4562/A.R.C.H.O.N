# BASE-014 verification handoff

Assessment: **LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING**. Full host
gates A–O and milestones M0–M9 remain **NOT_VERIFIED**. Command exit codes
are observations, not independent certification or canonical completion.

Source/HEAD: `f482e846855285aa7eeefe595530156eb06f2e3f`.
Branch: `feature/astra-base-014-a6-e6fcd9da`.
Worktree: `base-014-e6fcd9da`; initial status was clean.
Candidate/integration SHA: null (uncommitted patch; integration not attempted).
Execution mode: verification. Scope: five additions under `docs/` and `tests/`.

## S01 — measurable acceptance

[PROJECT_ACCEPTANCE.md](../engineering/PROJECT_ACCEPTANCE.md) enumerates every
architecture §16 gate A–O and §17 milestone M0–M9. Each row defines test command
aliases, source S, accountable owner role, unique artifact label, observable
assertions and failure behavior. An authorized named owner and reviewed real
host command packet remain prerequisites for a full gate; support tests cannot
qualify a host or authorize an action.

| Parent acceptance field | Observable check | Local observation |
|---|---|---|
| Every gate | Exactly A–O once, followed by M0–M9 once | Matrix coverage assertions executed in command 01 |
| Test command | Every alias resolves to a literal unittest command; named support test files exist | Command references asserted in 01; execution subset in S03 |
| Source SHA | Every row uses S, defined as the full pinned SHA; future evidence must bind actual candidate/base/diff | Source binding asserted in 01; input hashes in evidence JSON |
| Owner | Every row has an accountable role; real identity/approval remains separately required | Populated field asserted in 01; actual host identities pending |
| Artifact | Every row has a distinct relative artifact label; actual manifests enumerate digests | Label shape/uniqueness asserted in 01; local output digests in evidence JSON |
| Failure behavior | Every row states a fail-closed action and preserves unresolved gates | Populated field asserted in 01; local denial/replay cases in S04 |

These are architecture milestone names, not a rewrite of the canonical task
plan. No gate, milestone, parent or child is marked complete by this patch.

## S02 — fixtures and environment

`tests/fixtures/base014.json` contains synthetic task/receipt/model canaries,
interleaved out-of-order sequences and invalid limits. Tests generate boundary
rows and module manifests in disposable local databases. Fixtures require no
secrets, imported legacy execution, network, model access or target hardware.

| Environment | Observed version/scope |
|---|---|
| Python | 3.12.3; project minimum >=3.11; no added dependencies |
| Platform | Linux, x86_64; local test process |
| SQLite | 3.45.1 |
| Environment overrides | `PYTHONPATH=src:.`, `PYTHONDONTWRITEBYTECODE=1` |
| Model/provider | NOT_INVOKED; availability, versions and quota not probed |
| Target devices | Windows, GPU, microphone, cloud and standby mirror NOT_EXERCISED |

The no-SQL-on-invalid-input check uses a disconnected mock connection only as
an access sentinel. Other queue checks use real isolated SQLite. Neither is a
Master crash, host/device, authenticated-model or end-to-end broker drill.

## S03 — execution observations

[BASE-014-EVIDENCE.json](BASE-014-EVIDENCE.json) records each exact argv,
environment overrides, UTC interval, case count, exit code, output artifact
location/hash and the three acceptance input hashes. Collection interval:
`2026-11-15T10:07:09.212192+00:00` through
`2026-11-15T10:07:10.414397+00:00`.

Every command below uses
`PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p PATTERN -v`.
No full-suite or Git-mutating test command was invoked.

| Command | PATTERN | Cases executed | Observed exit |
|---|---|---:|---:|
| 01 | `test_acceptance_evidence.py` | 9 | 0 |
| 02 | `test_atlas_core_events.py` | 3 | 0 |
| 03 | `test_backend_manifest.py` | 4 | 0 |
| 04 | `test_foundation.py` | 7 | 0 |
| 05 | `test_sda_shadow_handoff.py` | 3 | 0 |
| 06 | `test_monitor_supervision.py` | 3 | 0 |

There were 29 cases across six commands, with no repair/retry after execution.
Raw output files are retained internally under
`/tmp/base014-e6fcd9da-evidence/`. This temporary directory is not a durable
canonical evidence store; the checked-in JSON is a metadata record only. QC
must independently rerun commands and verify candidate bytes. Do not publish
raw logs, task payloads, receipts, leases, secrets or model output. Only fixed
status/reason enums, approved IDs, counts and digests belong in public progress.

Final scans and whitespace/scope observations belong to
`/tmp/base014-e6fcd9da-evidence/final-snapshot.json`, recorded after all five
files exist. That external manifest also hashes this report and the evidence
JSON, avoiding circular self-hashing. It is a local handoff artifact, not QC.

## S04 — negative cases and compatibility

| Stimulus | Required outcome / local assertion | Command |
|---|---|---|
| Out-of-order/interleaved events, limits 1–4, unknown/SQL-shaped task ID | Filter by exact task, order ascending unique seq, then oldest N; unknown empty; exact output keys `seq`, `task_id`, `kind` | 01, 02 |
| Default, 100, 101 and huge positive limits | Existing compatibility path caps at 100; does not return newest-first | 01 |
| Empty/non-string task ID; bool/null/string/fractional/nonfinite/collection, zero/negative limits | ValueError before SQL; disconnected connection records no execute | 01 |
| Stale lease and duplicate completion | Reject; no added event or changed history | 01, 02 |
| Close/reopen with active lease | No reissued lease; original lease completes once; this is not process-crash recovery | 01 |
| Private task, receipt, model and lease canaries | No canary in history projection; private CI/manifest fields rejected | 01 |
| Duplicate/missing CI checks, malformed shapes/fields, contradictory/bool/out-of-range exit codes | ValueError; caller check order retained on valid reversed input | 01 |
| Failed/cancelled/unavailable CI check | Status remains explicit; remote status DEFERRED_QUOTA; unavailable allowed only for policy | 01 |
| Typed and mapping manifests for all ten modules, reversed registry order | Same explicitly declared own read/health scopes; output stable by module ID | 01, 03 |
| Foreign read/health, write/process/execute/network/privilege/admin, wildcard and Business scopes | Reject for all ten modules in both typed and mapping paths; dependency grants no access | 01 |
| Missing/empty/inferred scope, duplicate scopes, malformed IDs/fields/collections, unknown private fields | ManifestValidationError; no effect authorized | 01, 03 |
| All shadow-handoff evidence set true | Remains advisory; no actual promotion or live ownership | 05 |

Runtime source, schema, imports/exports and public API signatures stay at S.
Existing positive-limit clamping and CI caller-order behavior are preserved.
These tests verify existing validators; they do not implement a production
permission broker or approve cross-module access. No acceptance test was weakened.

## S05 — remaining requirements and handoff

The supplied approved architecture SHA-256 is
`295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89`;
the observed file digest is
`8d61e949302b70386d4e1d4a668cc4abe8b76be9966c5efe4575bdf2ca558d73`.
Architecture-authority reconciliation is pending; neither digest is replaced.
BASE-008/BASE-011 live dependency acceptance and individual child receipts are
unverified. All five children have separate deliverables above, in S01–S05
order; independent acceptance receipts remain pending for each child.

Gates A–F still need actual Master/worker/model/QC/Merger/restart evidence;
G–K need real recovery, rollback, controls, fencing and resource priority
drills; L–M need the Windows and Cloudflare systems; N–O need authorized
handbook/consent/provenance/paper-trading workflow evidence. Complete host
harnesses and their approved commands are unavailable in this bounded packet.
Host/device work remains NOT_VERIFIED/WAITING_DEVICE. Hosted-only acceptance
remains DEFERRED_QUOTA. Unsupported commands are not replaced with fake harnesses.

Observed local `develop` and merge-base SHA:
`43c8db7de8a5f0277a7db23379019d05f2edd2c6`, an ancestor of S. The recorded
integration branch `feature/astra-linux-integration-c799784769` is at S.
This isolated branch is also at S. No local `main` ref was returned by the
targeted ref inventory. Remote refs/protection and future integration freshness
are unverified; the Merger must recheck against the actual integration target.
Worktree registration metadata was inspected read-only; no cleanup occurred.

Canonical SQLite integrity/backup, parent/child receipt counts, active leases
and workers, W/R/U concurrency, trial progress, STOP/PAUSE/quota controls, and
service/timer liveness are **unknown in this repair**. No canonical ledger,
control marker, service, Git ref or rejected worktree was changed. Historical
snapshots are not operational evidence. Their reconciliation remains with the
Master within its separate authorization.

Handoff: `BASE-014 | child_receipts=pending individually S01-S05 |
start_sha=f482e846855285aa7eeefe595530156eb06f2e3f | candidate_sha=null |
integration_sha=null | branch=feature/astra-base-014-a6-e6fcd9da |
files=5 docs/tests additions | test_evidence=BASE-014-EVIDENCE.json |
independent_qc=pending | merger_result=not_attempted |
runtime_lane=isolated_repair; canonical lane unknown | retries=0 in this run |
blockers=architecture/dependency/host evidence; independent QC and integration`.

Next safe action: independent QC reruns the focused checks on the exact candidate
and validates each child artifact. The Master reconciles prerequisites and
routes any approved candidate to the serialized Merger. This author cannot
self-approve, integrate, publish or qualify the full project.
