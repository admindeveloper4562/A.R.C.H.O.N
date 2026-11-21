# Coordination and end-to-end evidence

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb.

## Executed evidence

- Root regression suite: 626 passed, 0 failed, 0 skipped.
- Separate bootstrap/astra-one coordination suite: 191 passed, 0 failed, 0 skipped in 61.476 seconds. This is not proof of all ARCHON runtime orchestration or the retired multi-worker design.
- Clean container: all ten configured modules registered; signed read-only and bounded workspace tasks completed; unauthorized admission/effect rejected; cancellation and interrupted-effect reconciliation were exercised; persistent state survived restart.
- Native local workload: 36/36 serial tasks completed in one persistent queue, including 18 actual qwen3:4b inference calls and 18 read-only database inspections. Three controller restart boundaries and a final restart produced no replay; runtime health and all three SQLite integrity checks passed.
- Native result retrieval was exercised through separately installed wheel and sdist CLI entry points.

## Scenario matrix

| Scenario | Result | Evidence limit |
|---|---|---|
| A — ALFRED, CORTEX, SAGE, and HORIZON answer one personal-assistant goal | NOT RUN end to end | Component contracts passed, but no single request traversed the four modules and generated a persisted audited answer. |
| B — ARCHON-driven change through SMITH, independent QC, and merge | NOT RUN end to end | REL-016 local checks and independent source QC passed, but no runtime task autonomously changed a disposable repository and completed the full QC/PR/merge path. |
| C — Failure detection and recovery | PARTIAL | Container smoke reconciled an interrupted allowlisted workspace effect and preserved state across restart. A separate trusted Guardian process did not monitor and recover a crashed ARCHON process. |
| D — Scheduled automation through ATLAS, module execution, and restart | NOT RUN end to end | Scheduler contracts passed; controlled-clock dispatch and completed-work non-replay across the whole flow were not demonstrated. |
| E — Security rejection | PASS for tested boundaries | Invalid/untrusted admission, scope, replay/idempotency, forbidden workspace effects, and unauthorized container effects are covered by focused tests and smoke evidence. No real finance, communications, public network, or service-control effect was attempted. |
| F — Normal multitasking | PARTIAL | 36 signed tasks shared one persistent queue, but the native controller executed serially. Concurrent worker fairness and coordination are not claimed. |

The 36-task harness initially signed all tasks at once and later returned no ready work. Test admissions have a 300-second expiry. The corrected harness signs each 12-task batch immediately before execution; all 36 tasks then passed. This changes only the disposable test harness, not production policy. The first-attempt failure receipt is retained with the local evidence.

Reproduction: run tools/verify_release.sh for the root suite/container checks and the separate bootstrap/astra-one unittest suite for the 191 coordination checks. Native inference soak evidence is in the local release evidence bundle.
