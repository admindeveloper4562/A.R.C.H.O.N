# Post-merge Linux qualification checkpoint

Observed: `2026-11-22T01:00:27Z`. This checkpoint supplements the earlier candidate-bound reports; it does not replace their historical evidence or change the release verdict.

## Git and candidate provenance

- Local `develop` and `origin/develop` were both `5363455c4da5b15d06463a8bb0f420f77ddae20c` at inspection. `origin/main` remained `5227b91d2725bf4be4336a5ad26189fdf1034704`.
- PR #10 merged the monitor receipt-coverage fix. Candidate `297a6aec62e078e88ac45558564e390ad1279f74` and integration commit `5363455c4da5b15d06463a8bb0f420f77ddae20c` have the same tree: `95e46a2aa7bb81d4a610b495ea84ec9eb8dff4fd`.
- Independent QC passed the exact candidate. At this checkpoint the `develop` branch-protection endpoint returned HTTP 404, repository rulesets count was zero, and PR #10 had zero formal GitHub reviews. The serial merger preserved the candidate as an integration parent.
- The repository is currently public. Its visibility was not changed during this checkpoint.

## Exact-candidate verification

The local release verifier ran on candidate `297a6aec62e078e88ac45558564e390ad1279f74`; the integrated tree is identical.

- Release verification: 42 checks completed with expected results; zero unexpected results.
- Root regression: 639 tests discovered; 637 passed, 2 skipped, 0 failed; 32.709 seconds.
- Coordination suite: 191/191 passed in 60.449 seconds.
- Focused monitor tests: 5/5 passed.
- `pip-audit` 2.10.1 reported zero known vulnerabilities.
- Wheel and source distribution version `0.0.3` built reproducibly, installed in disposable environments, and passed package/CLI checks. Clean-container acceptance covered fresh state, signed bounded admission, an allowlisted workspace effect, unauthorized-effect denial, cancellation, interrupted-effect recovery, persistence, restart, and SQLite integrity.

SHA-256 values from the candidate evidence bundle:

- Wheel: `be620dcb596d1abf1969387c7cb951792b6d58e5fde698f4c82cfb6f8bf73d77`
- Source distribution: `64e0ac7e5dce2136a2a02285648f1daeb960358f4fc73c269d28b2e0c56b9e43`
- Saved container image archive: `f796ead4e6d70a65ec34a577b83144f9c30a2eeb95c3578bf504311e7fdad566`

These results qualify the tested package and bounded runtime scenarios. They do not establish the full multi-module workflows or independent watchdog acceptance listed below.

## Privacy-pattern scan

A read-only regular-expression scan covered blobs reachable from the 15 current `origin/*` tracking refs: 4,038 objects and 1,543 blobs. Matched values were not printed or saved in this report.

- No matches: private-key headers, AWS access-key patterns, GitHub token patterns, Slack token patterns, Google API-key patterns, or quoted credential assignments.
- Historical ref matches: 273 Unix home-path indicators and 5,665 email-like strings.
- Current tracked tree: 9 Unix home-path indicators across 7 files; 792 email-like strings across 23 files, representing 27 unique addresses. Three unique addresses used placeholder domains and 24 used other domains.

The placeholder-domain count uses this exact allowlist: `example.com`, `example.org`, `example.net`, `test.com`, `test.local`, `localhost`, `users.noreply.github.com`, `noreply.github.com`, and `invalid`. “Other domain” does not imply that an address belongs to a person.

The owner previously stated that the identified project/account identifiers were safe to expose. The scan did not print the values and did not classify every email-like string as personal information. It is a bounded pattern scan, not proof that all sensitive data is absent. Dedicated `gitleaks`, `trufflehog`, and `detect-secrets` executables were unavailable. Untracked local files and unreachable Git objects were outside this scan.

The Codex Security diff-scan setup accepted the repository and exact range, but the scan launcher repeatedly rejected the local worktree with a resolvable-HEAD error. No tool-generated diff-scan result is claimed. The exact two-file diff was separately reviewed, and independent candidate QC passed.

## Read-only live state

The canonical SDA database was opened read-only; no database writes or backup were performed.

- SQLite integrity: `ok`; foreign-key violations: `0`.
- `ARCHON-JARVIS-V2`: 240 of 247 parents recorded completed; 7 archived. Of 1,359 children, 1,319 are recorded completed and 40 archived.
- Independent-QC coverage: 1,281 receipt rows cover 1,276 distinct children. 83 children have no qualifying receipt, including 43 recorded completed children.
- Pending, review, merge, and rebuild task queues were empty; the project queue had one pending row.
- Two recovery-coder lanes and one upgrade-auditor lane were recorded idle. Persisted lane/run records do not prove process liveness.
- `STOP`, `PAUSE`, `PAUSED_QUOTA`, `PAUSE_NORMAL`, and `PAUSE_RECOVERY` markers were absent in the checked state directory.
- The one-shot ATLAS monitor explicitly reported process liveness as unconfirmed. `systemctl --user` could not connect to the user bus, so the current native user-unit state remains unknown. This session did not activate the host service.

## Remaining mandatory gates

The overall verdict remains **CONDITIONAL**. These items remain unqualified:

- Real ALFRED-to-CORTEX/SAGE/HORIZON user workflows, full SMITH code-to-merge, and controlled-clock RELAY/ATLAS scenarios.
- Independently protected AEGIS survival, unattended recovery, trusted rollback application, and failback.
- Production owner-delegation/signature transport, native SDA cutover, and reconciliation of the 43 completed children without independent-QC receipts. No canonical task rows or receipts were edited.
- Multi-hour full-system soak and peak resource measurements.
- Hosted GitHub enforcement remains unavailable due billing; Windows and Apple validation remain deferred.

The host service remains gated on independent recovery acceptance. Finance and third-party communication effects remain disabled.
