# ARCHON Linux full-system qualification

Assessment date: 2026-11-21 UTC. Verdict: CONDITIONAL.

## Qualified source

- Application source SHA: 0ae26d563e5998a9390588feb58eb3d5c0081ffb.
- Candidate branch: feature/linux-release-integrated-20261121.
- Package version: 0.0.3 on Linux, Python 3.12.3.
- origin/develop at qualification start: 41dab1ad003c7526d80e3caaa46e63a6da1b6496. origin/main: 5227b91d2725bf4be4336a5ad26189fdf1034704.
- The tested package, image, and evidence bind to the application source SHA above. GitHub-hosted Actions was unavailable and was not run. Three absolute local-path occurrences remain in manifest-bound imported Astra provenance files; they were preserved to keep source integrity. Current audit documentation and the Blender test manifest were normalized without rewriting public history.

## Results

- Local release verifier: PASS. The exact-source unittest suite passed 626/626, with zero failures and zero skips. Runtime was 43.560 seconds; verifier wall time was 44.092 seconds.
- Separate Astra coordination suite: PASS, 191/191 in 61.476 seconds. This is coordination-tooling evidence, not full ARCHON module orchestration.
- Local CI report: PASS, 40/40 workflow checks. Dependency, secret, and security scans passed; pip-audit reported zero known vulnerabilities across three pinned runtime dependencies.
- Independent read-only source QC: PASS for 0ae26d563e5998a9390588feb58eb3d5c0081ffb. The reviewer did not run tests; the local verifier supplies test evidence.
- The clean source-built container registered all ten configured modules, initialized fresh state, completed signed bounded tasks, rejected unauthorized admission/effects, recovered an interrupted workspace effect, restarted with persistent state, and passed SQLite integrity checks.
- A saved image archive was loaded afresh and started under the same non-root, read-only, no-network security profile. One signed read-only task completed and remained completed after restart; ten modules were registered and SQLite integrity was ok.
- Wheel and sdist were independently installed into disposable environments. Installed CLI help, controller, health, admission fixture, result retrieval, pip checks, and uninstall passed.

## Native Linux inference and workload

- Local Ollama qwen3:4b inference ran through both the direct runtime gateway and the signed native task executor. Native inference results persisted in private conversation state and were retrieved through the installed CLI.
- The 36-task bounded workload completed 36/36 tasks: 18 signed inference tasks and 18 signed read-only conversation database inspections. It used one persistent serial queue, three between-batch controller restarts plus a final restart, no completed-task replay, zero failures, healthy runtime, and three intact SQLite databases.
- Workload duration was 289.326 seconds; throughput was 0.124 tasks/second; maximum queue depth was 12. The 12-task earlier workload also passed.
- This bounded workload does not demonstrate multi-hour operation, parallel workers, or all requested cross-module assistant/SDA scenarios.

## Release artifacts

- Wheel SHA-256: 674f83088441eeeaaac6718d8cc29ae53ed6ce482cc5b607608b1ce6a6155981.
- Source distribution SHA-256: 2ac610b9386e3907278d652aedc94829126b35affa566df5a4983a94cd88c45b.
- Saved container archive SHA-256: b7452422d6be305b2e5f803689c2956fcdf15f7074fc776eac0f0dc012ec1207.
- Artifact files and full logs are retained in the local evidence bundle and were not pushed to a package or image registry.

## Current runtime and ledger

- Canonical SQLite backup and restore-copy integrity checks passed; source database was not modified. Backup SHA-256: 6a37810719d1e93a9ecca14cc6aebd2e992f721be17ab5dc722ea1d39e947fc0.
- Project ledger: 240 completed and 7 archived parents out of 247; 1,319 completed and 40 archived children out of 1,359. A completed child without an independent receipt is not counted as verified.
- No live workers or active leases were observed; the three recorded supervisor lanes were idle. The project queue has one pending item. Process liveness is unknown without trusted heartbeats.
- STOP, PAUSE, and PAUSED_QUOTA markers were absent at the read-only snapshot. ARCHON/Astra user services and timers were inactive or absent. They were not enabled.
- Main was not modified. GitHub publication and the resulting develop SHA are recorded separately after merge.

## Material gaps

Trusted owner delegation/signing for production, independent AEGIS watchdog activation and rollback, native SDA cutover, complete ALFRED/SAGE/HORIZON and SMITH/QC/merge workflows, controlled-clock RELAY-to-ATLAS execution, multi-hour soak, hosted Actions, and Windows/Apple/device validation remain open. See FINAL_RELEASE_VERDICT.md and the module, coordination, native-execution, and AEGIS reports.
