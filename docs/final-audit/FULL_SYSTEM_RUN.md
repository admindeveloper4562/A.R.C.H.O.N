# ARCHON Linux full-system qualification

Assessment date: 2026-11-22. Verdict: **CONDITIONAL**.

## Qualified source

- Application code candidate: `2e24790c983bf3c8d2d0f99de7a086427355f172`; source tree `5dc151512b5df78ecf5e911a93222ad2a44fb94b`.
- Package: `0.0.3`, Python `>=3.11`.
- Exact-candidate evidence index: [QUALIFICATION_ADDENDUM_2E24790.json](QUALIFICATION_ADDENDUM_2E24790.json), SHA-256 `c4385f8027dacb724cea2cccd1604ea92d717c78470d88d57156cab0bc9e0497`. This identifies the code candidate separately from the later audit-document commit.

## Results

- Python 3.12.3 release verifier: **637 passed, 0 failed, 0 skipped**; unittest 49.232 s, verifier wall 49.671 s.
- Local CI equivalent: **42 checks**, 40 success exits and two expected-negative checks; dependency, secret, and security scans passed; pip-audit 2.10.1 reported zero known vulnerabilities.
- Astra/ATLAS coordination suite: **191/191 passed** in 60.584 s.
- Python 3.11.18: wheel and sdist installed independently; package checks, imports/resources, and installed CLI checks passed; root suite **637/637**, 0 failures, 0 skips.
- Local inference: exact-candidate root suite ran with Ollama opt-in integration enabled; the bounded `qwen3:4b` 72-task workload is recorded separately with the identical runtime source subtree caveat.
- Container smoke: 47 command records, fresh state, signed bounded task admission, authorized workspace effect, forbidden effect rejection, cancellation, interrupted-effect recovery, persistence, restart, SQLite integrity, and graceful shutdown passed. The released image-only Compose manifest also passed fresh start, health, ten-key registration, workspace persistence across restart, and non-root policy checks.
- Saved-image archive reload: passed on a fresh container; health was healthy, ten module keys registered, two database integrity checks passed, and the process exited cleanly.
- Two independent exact-source verifier runs passed, one with `FORCE_COLOR=1` and one without color. Wheel and sdist hashes matched the root builds.

## Operational boundary

A successful package/container release does not establish every ARCHON module as operational. The image reports all ten registered module states as `planned`. Full assistant orchestration, autonomous SMITH code-to-merge, controlled-clock RELAY/ATLAS execution, independent AEGIS watchdog/rollback, production owner delegation, and multi-hour operation remain unqualified. See [FINAL_RELEASE_VERDICT.md](FINAL_RELEASE_VERDICT.md).
