# Final Linux release verdict

## Verdict: CONDITIONAL

This update adds targeted native-model, unsupported-operation, cancellation, and contract-fixture evidence for source `fb499facad4447cb6eff7a29071364506ba100f7` (tree `35705fe52a47af4dac43526d2627af024905d9bf`). A full release verifier and artifact rebuild were not rerun on that exact HEAD. The broader `2e24790c983bf3c8d2d0f99de7a086427355f172` qualification below is retained as historical evidence and is not used as exact-HEAD evidence.

The current exact-source runs were: a process-level source-module CLI flow passed fresh initialization, signed test-fixture admission, forged-signature rejection, one-shot native execution with real local Ollama inference, and persisted result readback in 6.709 seconds; a separate signed request for unsupported `shell` was recorded `failed` without creating its confined sentinel in 1.156 seconds; a signed-cancellation CLI scenario left its task `cancelled`, the controller idle, and model turns at zero in 1.460 seconds; two manifest/permission/event-contract fixture tests passed in 0.287 seconds. The CLI flows used temporary state and an ephemeral public-key fixture, not an installed-wheel CLI or production owner delegation. The unsupported-operation and cancellation checks are narrow, not comprehensive effect-security qualification. These results do not establish module-operation E2E. A complete autonomous ARCHON system is not established; the release verdict remains **CONDITIONAL**.

The earlier post-merge checkpoint contains its own develop provenance, privacy scan, and read-only live-state snapshot: [POSTMERGE_CHECKPOINT_5363455.md](POSTMERGE_CHECKPOINT_5363455.md). This targeted update did not refresh that checkpoint or repeat its scans.

## Inherited source/test/config-tree evidence

Git tree comparison confirms that `fb499facad4447cb6eff7a29071364506ba100f7` and fully verified candidate `297a6aec62e078e88ac45558564e390ad1279f74` have identical `src` (`77d8be604cc372f7bc04a9bf43c5bf64a7f0f3c2`), `tests` (`13c1804a70efcd2fc7c2097962eb173c4d5f71d1`), and `config` (`3557f481f1e9de7983e814396534bd2a39b3914c`) trees. The Git comparison shows only three final-audit documents differ between those commits.

The post-merge checkpoint records independent QC and 42 local checks on candidate `297a6aec`: 639 tests discovered, 637 passed, 2 skipped, 0 failed; coordination 191/191; monitor tests 5/5; pip-audit reported zero known vulnerabilities; wheel, sdist, and container qualification passed with artifact hashes recorded there. This is inherited evidence for the identical source/test/config trees. It is not a full verifier run or package/image rebuild bound to exact HEAD `fb499fac`; exact-HEAD release artifact verification remains open.

## Historical full-release candidate and Git snapshot

- Qualified application code SHA: `2e24790c983bf3c8d2d0f99de7a086427355f172`.
- Source tree: `5dc151512b5df78ecf5e911a93222ad2a44fb94b`.
- Package version: `0.0.3`; declared Python `>=3.11`.
- Candidate branch: `feat/release/REL-025-linux-release-final`, based on `origin/develop` `41dab1ad003c7526d80e3caaa46e63a6da1b6496`.
- Release publication: PR [#7](https://github.com/admindeveloper4562/A.R.C.H.O.N/pull/7) merged into `develop` at `67e8689da898fb62026fdfbd1875bc9bbf64f783`; candidate `bd66b6411c8de4cd4e6709b1cefbc60d57865c06` is included. The last post-merge check found `origin/develop` at that integration SHA and `origin/main` unchanged at `5227b91d2725bf4be4336a5ad26189fdf1034704`.
- GitHub Actions remains unavailable due billing; hosted CI is deferred, not passed.

## Historical acceptance snapshot for source 2e24790 (not rerun on fb499)

- Python 3.12.3 regression: 637 passed, 0 failed, 0 skipped; local CI: 42 expected checks; coordination: 191/191.
- Python 3.11.18 wheel/sdist installation, installed CLI/resource checks, and root regression: 637 passed, 0 failed, 0 skipped.
- Local inference: the exact-candidate root suite ran with Ollama opt-in integration enabled; `qwen3:4b` completed the separately recorded bounded workload on the identical runtime source subtree. Container networking remains disabled by default.
- pip-audit: zero known vulnerabilities. Container: UID 10001, network none, read-only root, all caps dropped; bounded task effects, denial, restart, recovery, and SQLite integrity passed.
- Independent QC: two complete exact-source runs passed with color forcing on/off; package hashes matched the root build.
- Runtime-tree soak: 72 bounded tasks over 491.427 seconds (0.1465 tasks/s), with 12 restarts, on an identical `src/` subtree but not the exact whole-source candidate. Across 36 model calls, latency median was 14.2895 s (3.192–24.545 s); 72 per-task CPU-busy samples had a 53.135% median (42.86–58.17%). Host available-memory snapshots were 7,970/6,299 MiB before/after; GPU snapshots were 1,390 MiB/3% before and 3,184 MiB/31% after. These do not establish peak usage; no multi-hour run or peak process RSS was captured.
- The released image-only Compose manifest passed startup, health, ten-key registration, non-root identity, workspace persistence across restart, and SQLite integrity; receipt SHA-256 `b5bce93865595ada53e76f28e59f49f58067582eecbfb1dcac4485b89e27d501`.

## Release gates still open after this targeted update

1. Complete exact-HEAD release artifact verification and reconcile independent QC for `fb499facad4447cb6eff7a29071364506ba100f7`; inherited source/test/config-tree evidence is available, but no package or image rebuild was bound to this exact HEAD. This update contains four targeted invocations, one of which runs the two-test contract suite.
2. Full operation for ALFRED, SMITH, SAGE, HORIZON, LUMEN, CROWN, RELAY, and cross-module flows.
3. Independently protected AEGIS/watchdog, unattended recovery, and verified rollback.
4. Production owner delegation/signature transport and native SDA cutover.
5. Multi-hour soak and live performance/resource qualification.
6. Resolve outstanding repository privacy-pattern review based on the latest exact-source scan; this task did not repeat it.
7. Hosted CI remains deferred by billing; Windows and Apple-native validation remain deferred.

The exact evidence and hashes for the historical 2e candidate are in [QUALIFICATION_ADDENDUM_2E24790.json](QUALIFICATION_ADDENDUM_2E24790.json). The current targeted native test used temporary state and did not activate a service. Do not interpret this CONDITIONAL result as approval for live finance, communication, public network exposure, or unattended privileged recovery.
