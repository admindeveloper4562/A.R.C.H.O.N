# BASE-014 acceptance evidence and milestone checklist

This is a verification contract, not a qualification or an authorization to run
host drills. Owners below are accountable roles; the Master must bind an actual
authorized identity before a host run. Independent QC reviews the exact candidate;
only the authorized Merger integrates it. No checklist changes canonical state.

Every row below uses source **S =
`f482e846855285aa7eeefe595530156eb06f2e3f`** for this baseline. On a future run,
record the actual full candidate SHA, base SHA, integration SHA (or null), diff
SHA-256 and environment snapshot. Never reuse this baseline as evidence for a
different candidate. An uncommitted patch is identified by its file hashes and
diff hash, not by pretending S contains it.

The supplied approval digest is
`295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89`;
the checked-in architecture digest is
`8d61e949302b70386d4e1d4a668cc4abe8b76be9966c5efe4575bdf2ca558d73`.
Reconciliation by the architecture authority is pending. The definitions below
trace the observed architecture §§16–17; they do not approve its bytes.
BASE-008 and BASE-011 dependency acceptance remains unverified here.

Repair scope: this matrix, synthetic fixtures, focused verification tests and
their report. Public runtime APIs, schema, exports, dependencies and policies
remain at S. Hazards under review are ambiguous ordering, private metadata
exposure, malformed evidence and inferred/foreign permissions. No model or
test result may authorize an effect. Actual owner identity, current approval,
run/generation and candidate binding are required separately by the Master.

## Reproduction and evidence rules

Run from the assigned worktree with Python >=3.11 and `PYTHONPATH=src:.`.
Use only a fresh temporary SQLite database, no network, models, Docker socket,
credentials or imported legacy execution. `tests/fixtures/base014.json` is fully
synthetic. Its out-of-order, interleaved event rows distinguish chronological
ordering from insertion order and task filtering. Invalid limits include bool,
zero, negative, null, string and fractional values. The boundary drill generates
more than 100 synthetic rows locally. Canaries are test strings, never real data.
Manifests enumerate the ten existing module IDs; only explicitly declared
`<own-module>:read` and `<own-module>:health` are allowed. Dependency on Core
does not grant Core read permission. Missing/empty permission lists, foreign
module scopes, wildcards, write/process/network/privilege scopes and unknown
fields reject before any effect. Typed manifests and mappings follow the same
contract; this is validation evidence, not a deployed permission broker.

Command aliases below expand literally as follows. Each command is a **local
support check**, not a complete real-host gate. A missing command, prerequisite,
or host harness is pending, never a success. Do not create a fake executable for
an unavailable host drill. Required host observations are specified per row;
their executable commands must be reviewed in a separate authorized host packet.

| Alias | Exact local test command |
|---|---|
| V | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_acceptance_evidence.py -v` |
| F | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_foundation.py -v` |
| Q | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_sda_shadow_handoff.py -v` |
| B | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_backend_manifest.py -v` |
| P | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_git_policy.py -v` |
| W | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_astra_watchdog.py -v` |
| T | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_monitor_supervision.py -v` |
| C | `PYTHONPATH=src:. python3 -m unittest discover -s tests -p test_ci_workflow.py -v` |
| R | `PYTHONPATH=src:. python3 -m unittest discover -s tests -v` |

P, W and R can create Git objects/refs in disposable test repositories; they
are definitions for future authorized checks, not part of this repair's run.
Record argv, cwd label, exit code, UTC interval, environment digest and artifact
SHA-256 for each actual invocation. Capture only sanitized outputs in a local
access-controlled evidence directory; store private debugging material separately.
Do not publish raw logs, task payloads, receipts, secrets or model text. Public
progress uses only approved IDs, fixed status/reason enums, counts and digests.
An evidence receipt reference is an opaque internal identifier, not its contents.

Each gate artifact is a directory of metadata plus sanitized observations,
identified below by a relative label. Its manifest must enumerate file digests;
QC independently verifies both bytes and the candidate binding. A digest alone
does not attest that a test ran, an owner approved, or a host is qualified.
Missing, duplicate, stale, corrupt or contradictory evidence is rejected, with
no task transition. A failed local command is FAIL; a missing prerequisite is
BLOCKED. Host/device work not executed is NOT_VERIFIED or WAITING_DEVICE;
hosted-only checks remain DEFERRED_QUOTA. Exit zero on support checks cannot
override those states. No hosted workflow rerun is authorized here.

## Gate matrix: observable assertion, owner, artifact and safe failure

The source column is S for **every** row. Current observed outcome for every
full gate A–O is **NOT_VERIFIED**; local support observations are recorded in
the BASE-014 report, separately from these full assertions.

| Gate / source | Expected observation, including required host evidence | Local command | Accountable owner | Artifact label | Failure behavior |
|---|---|---|---|---|---|
| A / S | Exact acceptance/dependency DAG admits only eligible tasks; missing dependency and cyclic fixture rejected; preserve 247 parent and 1,359 child IDs. Real Master admission evidence required. | V, F | SDA planner + independent QC | `A/admission` | Block affected admission; retain original graph. |
| B / S | Real authenticated coder creates required diff in its isolated worktree; source refs unchanged; scope escape/no-op rejected. | Q, P | SDA worker + QC | `B/worktree` | Reject candidate; preserve worktree, no merge. |
| C / S | Real router records provider/model/context/privacy/quota decision and durable per-task session; denied/unavailable provider never silently substituted. | B, V | Backend gateway + QC | `C/routing` | WAITING_OWNER or PAUSED_QUOTA; no dispatch. |
| D / S | Independent reviewer runs regression/security checks on exact candidate; author identity differs; reproducible rejection binds violated clause and bounded repair advice. | C, R | Independent QC | `D/review` | Return actionable rejection; no approval or queue entry. |
| E / S | Real serialized Merger verifies fresh parent/candidate, one integration writer and post-conflict checks; stale and semantic-conflict cases rejected. | P, Q | Serialized Merger + QC | `E/integration` | Stop affected merge; semantic repair returns to coder. |
| F / S | Real Master kill/restart preserves leases, approvals, candidate commits and idempotent effects; single writer retained. V proves only seed SQLite close/reopen behavior. | V, Q | SDA Master + independent QC | `F/restart` | Fence uncertain owner, reconcile without duplicate effects. |
| G / S | Real integrity finding is deduplicated into a scoped repair, independently tested and integrated; repeat fingerprint does not spawn competing ownership. | W, T | Guardian + recovery QC | `G/repair` | Preserve finding and open Supervisor case; bounded recovery only. |
| H / S | Authorized canary fault triggers independently verified last-good rollback; backup restores with intact task/child ledger and controls. | W, F | Trusted watchdog + QC | `H/rollback` | Halt activation; preserve backup and rescue path. |
| I / S | Real STOP, global/lane PAUSE, quota and approvals survive crash, provider handoff and Guardian replay; no prohibited claim or effect. | Q, W | SDA Master + trusted watchdog | `I/controls` | Honor active control; never clear marker as repair. |
| J / S | Actual mirror sync/fencing denies stale standby and two writers before critical live promotion; measure checkpoint compatibility and recovery. | Q, W | Trusted watchdog + owner | `J/mirror` | Deny promotion; retain safe active writer or degrade. |
| K / S | On real shared model resource, current generation finishes/checkpoints; waiting Guardian gets next eligible slot before ordinary work, within budgets. | F | Guardian scheduler + QC | `K/priority` | Block lower-priority dispatch; never interrupt unknown tool effects. |
| L / S | Real Windows host disconnect/reconnect queues work once, maintains fenced leases and authenticated link; Ollama has no public listener. Record actual device/model versions. | B, Q | Windows host owner + QC | `L/windows` | WAITING_DEVICE; keep queue, deny untrusted link. |
| M / S | Actual Cloudflare hosts-offline event remains queued and is consumed once on authorized reconnect; exported progress contains approved metadata only. | T, V | Automation owner + QC | `M/offline` | Mark offline/stale; preserve queue, no invented execution. |
| N / S | Real authorized handbook proposal workflow limits Recovery/QC/Research to allowed sections, independently rejects self-approval and protected policy edits. | P, Q | Handbook reviewer + owner for protected edits | `N/handbook` | Reject unauthorized write; original handbook retained. |
| O / S | Real consent-scoped Mira read-only access denies partner data; Research/WIC claims retain provenance; paper broker denies every live order/credential path. | B, V | Finance/Research/WIC owners + privacy QC | `O/privacy` | Deny access/order; mark missing provenance, no financial effect. |

These commands intentionally expose current coverage gaps. For example B and V
cannot certify Mira, a Windows host or Cloudflare, and W does not prove an actual
production rollback. Their absence of a complete host harness remains an open
acceptance gap, not a waived test.

## Milestone checklists

These are architecture §17 milestones, not renamed canonical task-plan IDs or
state transitions. Every row uses source S. Before checking any box, independently
verify the row's exit evidence and every listed gate. All boxes start unchecked.
Cross-cutting N/O apply where handbook, provenance or private data is involved;
M9 requires all A–O. Gates may overlap milestones without authorizing execution.

| Checklist / source | Required exit observations | Local command | Accountable owner | Artifact label | Failure behavior |
|---|---|---|---|---|---|
| [ ] M0 / S | Approved architecture digest reconciled; legacy/source preserved; host/model inventory and exact task/DAG baseline reviewed (A). | V, F | Architecture owner + QC | `M0/baseline` | WAITING_OWNER/dependency; no approval inferred. |
| [ ] M1 / S | A–F on actual Linux with five authenticated workers, separate QC/Merger, resource/quota measurements. | R | SDA Supervisor + QC | `M1/linux` | Keep external builder; quota/device blockers explicit. |
| [ ] M2 / S | Core/Backend round trip, priority/FIFO, durable session/event restart and scoped gateway (A, C, F, I). | V, F, B | Core/Backend + QC | `M2/roundtrip` | Stop affected dispatch; preserve checkpoint. |
| [ ] M3 / S | Local Guardian, next-slot priority, immutable watchdog and G–K; unsafe operations denied. | W, F, Q | Guardian + trusted watchdog | `M3/recovery` | Deny activation/promotion; retain rollback. |
| [ ] M4 / S | Actual Windows and Cloudflare offline/online tests L–M; accurate private-safe dashboard. | B, T, V | Device/Automation + QC | `M4/devices` | WAITING_DEVICE; offline work remains queued. |
| [ ] M5 / S | Owner-approved clean repo, stable contracts, reviewed licensed migration, CI and rollback evidence (B, D, E, H, N). | P, C, Q | Owner + Merger + provenance QC | `M5/migration` | No repo creation/migration/release without authorization. |
| [ ] M6 / S | Runtime chat/voice/browser/desktop user acceptance and Research source provenance, scoped effects (C, I, O). | B, V | Runtime/Research + owner | `M6/user` | Deny unapproved effects; retain source uncertainty. |
| [ ] M7 / S | Quest reward replay grants once; WIC dated sources/corrections accepted; original Aurelia preserved (F, O). | V | TWS/WIC + QC | `M7/quest-world` | Reject duplicate rewards/unproven claims; preserve original work. |
| [ ] M8 / S | Real read-only consent, partner denial, exact money arithmetic and separate paper ledger; zero live broker-write permission (O). | B, V | Finance + privacy QC | `M8/finance` | Deny access/write; no real funds moved. |
| [ ] M9 / S | All A–O on intended hosts, full regression, canary/rollback and explicit owner release approval for exact candidate. | R | Owner + independent QC + Merger | `M9/release` | No production release/cutover; preserve Astra rescue path. |

## BASE-014 child evidence order

S01 matrix precedes S02 fixtures/environment, then S03 execution, S04 negative
cases and S05 report. Each child requires its own independent evidence receipt;
neither this ordering nor a parent merge completes children automatically.
Local event history returns the **oldest matching events in ascending unique seq
order, then applies limit**; positive integers above 100 clamp to 100, invalid
types/zero/negative reject, unknown task returns empty. It is a metadata projection
of exactly `seq`, `task_id`, `kind`; lease/status APIs remain unchanged and are
not safe substitutes. CI reports preserve caller order and are not event history.
CI's `unavailable` policy check and DEFERRED_QUOTA remote status never prove the
corresponding gate. Child receipts and private diagnostic content stay internal.
