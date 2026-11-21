# ARCHON Linux full-system qualification

Assessment date: 2026-11-22. Verdict: CONDITIONAL. Root release evidence below is bound to source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85; a follow-up runbook/test change is not yet fully verified.

## Qualified source

- Application source SHA: 759e78dc04c61ed7f01a4b714d35ab8c999d2a85.
- Source tree: 7472b26bbc24538851a920ff89ac9a65206050a8.
- Package version: 0.0.3; declared Python requirement: >=3.11.
- Release build and verification environment: Linux, Python 3.12.3. Python 3.11 installation was not evidenced for this exact candidate.
- Qualification addendum: QUALIFICATION_ADDENDUM_759E78D.json, SHA-256 d207ae3841092a77e231fb7cda821c2f564bc27c52dc884a226c9272994736ee. It binds the root evidence to the 759e source only.

## Results

- Exact-source release verifier: PASS, exit 0. Regression suite: 635/635 passed, 0 failed, 0 skipped; unittest time 47.793 seconds and verifier wall time 48.243 seconds.
- Local CI equivalent on source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85: PASS, 42 checks. Forty commands returned 0. Two expected negative checks returned 2 for rejecting caller trust-store input and 1 for confirming an uninstalled package is absent.
- Follow-up runbook marker-preservation regression: focused command passed 1/1 by executing both documented Python snippets in disposable directories and asserting NativeController safe_mode with STOP, PAUSE, and PAUSED_QUOTA preserved. The full verifier has not yet run on the follow-up candidate.
- Coordination suite: PASS, 191/191 in 62.389 seconds.
- Dependency, secret, and source security scans passed. pip-audit 2.10.1 reported zero known vulnerabilities.
- Hosted GitHub Actions was not run because billing was unavailable.
- Independent QC passed for the root evidence source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. The docs/test follow-up candidate still needs exact-source full verification and QC; do not transfer the base receipt to that child candidate.

## Package and container

- Wheel and source distribution remain version 0.0.3. Duplicate builds produced matching hashes. Fresh package install, CLI, and pip checks passed in the recorded Linux Python 3.12.3 environment.
- Wheel: 303,942 bytes, SHA-256 66d6ac2e977c65f7d48321852d7021383ab3c38540f2299612a56d93dd15f879.
- Source distribution: 346,655 bytes, SHA-256 9f585df16ac92b14d088a69fb20fa24a3573029ecefc873a526b8f982af70aeb.
- Exact-candidate container smoke ran 47 commands and exited 0 with fresh state. It used network mode none, UID/GID 10001, a read-only root filesystem, all capabilities dropped, and no-new-privileges. SQLite integrity passed for atlas, effects, and runtime databases.
- Container receipts covered read-only work, one approved workspace write, unauthorized admission and workspace-effect rejection, cancellation, interrupted-effect recovery, restart, and persistence.
- Saved image archive reload passed with healthy status and SQLite integrity. Archive SHA-256: 4a6d21a613c9611c63c94c2a2410b1817c53c574ed49d5e537d86dbc9a258709. All ten module states in the reload report were planned.

## Current canonical host state

Read-only snapshot at 2026-11-22 03:03:40 +07; the canonical database was not modified. PRAGMA integrity_check and quick_check returned ok; foreign_key_check found zero violations. ARCHON-JARVIS-V2 had 247 parents (240 completed, 7 archived) and 1,359 subtasks (1,319 completed, 40 archived). There were 1,281 receipt rows covering 1,276 distinct children; 43 completed children lacked receipts, with archived children excluded from that missing-receipt count. The project queue had one item and zero pending/review/merge items; no active, blocked, or queued controller task was present. Three recorded supervisor lanes were idle; process liveness was unknown. No STOP/PAUSE/PAUSED_QUOTA markers were present. The host user service and Astra runner/timer were inactive.

All ten module names registered, but every reported module state was planned. Local inference/extended Ollama soak was not rerun for this exact candidate. Full ALFRED/SAGE/HORIZON assistant flow, SMITH autonomous change through QC/PR/merge, controlled-clock RELAY/ATLAS, independent AEGIS watchdog and rollback, production owner signing/native SDA cutover, multi-hour operation, Windows, Apple, hardware-specific, and live external-provider validation remain unverified or deferred. No native service was activated by this qualification.
