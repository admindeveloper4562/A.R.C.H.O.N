# Local release verification report

Qualified application source: `2e24790c983bf3c8d2d0f99de7a086427355f172`; tree `5dc151512b5df78ecf5e911a93222ad2a44fb94b`; package `0.0.3`; Linux, Python 3.12.3.

## Result

- Full release verifier: PASS, exit 0; 637 tests passed, 0 failed, 0 skipped; unittest 49.232 seconds, verifier wall 49.671 seconds.
- Local CI equivalent: PASS, 42 checks; 40 expected success codes and two expected-negative results (return codes 2 and 1).
- Coordination suite: PASS, 191/191 in 60.584 seconds.
- pip-audit 2.10.1: zero known vulnerabilities. Dependency, secret, and security scans passed.
- Wheel and source distribution built twice with matching hashes; exact artifacts installed and checked on Python 3.12.3 and 3.11.18. Python 3.11.18 root suite passed 637/637 with zero skips.
- The exact-candidate verifier ran with the local Ollama integration opt-ins enabled. The separate qwen3:4b workload and its source-tree caveat are in SOAK_TEST.md. The default container has network mode none and does not connect to a host Ollama service.
- Container smoke and fresh saved-image reload passed. The saved archive hash and reload evidence are in the addendum.
- Two independent QC verifier runs reproduced the wheel/sdist hashes and passed their container smoke.
- The packaged image-only Compose manifest passed a fresh-volume start/restart, health, ten-module registration, non-root UID/GID, and SQLite integrity check; receipt SHA-256 `b5bce93865595ada53e76f28e59f49f58067582eecbfb1dcac4485b89e27d501`; manifest SHA-256 `746dbb8db950e28f4693eab45b55e56722ae71cc3413cf616e70984304b04dff`.
- GitHub Actions was not run because billing is unavailable. Local CI is not hosted CI enforcement; hosted status is `DEFERRED_QUOTA`.

## Artifact checksums

- Wheel: `jarvis_v2-0.0.3-py3-none-any.whl`, 303,942 bytes, SHA-256 `5f04940e72466a83835a527530dc6ca3acdfb6452f0d62da8b7c9c751304ec75`.
- Source distribution: `jarvis_v2-0.0.3.tar.gz`, 347,780 bytes, SHA-256 `fb289c4aef7061acf998502e6e6b06bfef9d8e93058c56ac99246d4e0f4f5826`.
- OCI image archive: `archon-local-image.tar`, 50,039,296 bytes, SHA-256 `b62e2645aef0437ab715a864f05926a3fd97273ec03d6a9c9cbd1f2768473a26`.
- Root release manifest SHA-256: `1919d0f4072f91b632d0e3c9317ecfb10f0f5e5ef2788340fe11fd4934b42e3a`.

See [QUALIFICATION_ADDENDUM_2E24790.json](QUALIFICATION_ADDENDUM_2E24790.json) for exact report hashes and boundaries.
