# Test audit

## Executed evidence

- Evidence was run against the base integration SHA a2df24261d5ea19e9260f7f6c270b26ea9abdb03 plus the uncommitted audit changes in the canonical working tree.
- Full standard-library discovery: 579 tests, 579 passed, 0 failed, 27.243 seconds.
- Final suite output is retained at docs/final-audit/evidence/unittest-final.log.
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
