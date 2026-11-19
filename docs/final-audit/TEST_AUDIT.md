# Test audit

## Executed evidence

- Evidence was run against tested local tree 239e10154e1c81b4ff463cdd796e04f0dbc68407; implementation commit eef1e3c8d1bfd3ea6a3dc7e1b06ac2daa3e21767 is not published to GitHub.
- Full standard-library discovery: 579 tests, 579 passed, 0 failed, 27.720 seconds.
- Final post-commit suite output is retained at docs/final-audit/evidence/unittest-postcommit.log.
- Native package import sweep: 106 jarvis_v2 modules, 0 import errors.
- Native controller checks: fresh one-shot, process-lock fencing, control-marker admission, executor success/failure receipts, terminate/restart, and systemd unit verification all passed; the unit is not installed and the default executor is intentionally unconfigured.
- Native health check: fresh runtime and ATLAS databases reported healthy read-only state; historical ledger loading was explicitly false.
- Host inventory capability check: Ollama model listing and NVIDIA acceleration probe were captured; unavailable accelerator tools were recorded without failure.
- Local dependency_scan, secret_scan, and security_scan: all passed.
- Fresh runtime database migration, integrity, foreign-key, backup, and restore checks: passed for runtime.sqlite3 and atlas.sqlite3.
- pytest is not installed on this host. No hosted workflow was manually rerun.

## Coverage reviewed

The suite includes core state transitions, duplicate events, leases, retry/failure handling, authorization, path boundaries, command restrictions, secret redaction, migrations/rollback, provider adapters, runtime services, guardian recovery, automation leases, research safety, finance paper/read-only flows, TWS persistence, WIC provenance, CI policy, and installation contracts.

Fixtures use temporary directories and disposable SQLite files. The full suite does not transact, send communications, or modify production services.

## Gaps

- No coverage tool is installed, so executable line/branch coverage is not claimed.
- Tests with Astra, Windows, iOS, Blender, Cloudflare, or external providers validate contracts and fixtures; they do not prove those external environments on this Linux host.
- Flakiness and order dependence were not statistically profiled across repeated runs.
- Hosted CI acceptance remains unverified in this run.
- Independent bounded QC validated the committed tree's JSON, native one-shot/health, ledger envelope, diff cleanliness, remote divergence, and Astra boundary; it skipped the full suite and long scans by design. See INDEPENDENT_QC.md.
