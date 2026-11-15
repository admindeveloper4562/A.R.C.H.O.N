# Astra One v0.1.0 — local foundation release evidence

## Implemented and offline-verified

- Deterministic task state/attempt ledger in local SQLite, WAL, explicit architecture SHA-256 approval and local text retention.
- Bounded optional Ollama task planner that proposes JSON only; no auto-enqueue; focused headings for oversized architecture.
- One serialized Codex coding task with structured JSON telemetry, new Git feature worktree, pinned integration SHA and runtime bound.
- STOP/PAUSE, explicit retry, interrupted-run marking (does not kill stale workers), durable local event outbox and authenticated HTTPS-only Cloudflare sync.
- Static syntax/Git checks, human review approval, explicit local-only serial integration branch, next task base advances from integrated commits.
- Cloudflare Worker + D1 dashboard with separate bearer tokens, scoped event ingest and view operations, read-only browser, idempotent event replay, status timeline, counts and task progress.

## Test evidence in this artifact-build environment

- `python -m unittest discover -s tests -p 'test_*.py' -q`: **31 passed**, including actual local Git integration into a disposable branch.
- `tsc --noEmit` (Cloudflare Worker TypeScript): **passed**.
- `tsc --noEmit false --outDir .test-output && node --test tests/worker.test.mjs`: **4 passed** (authentication, idempotency, replay ordering, read routes, safe JS syntax).
- In-memory SQLite parsing of Cloudflare D1 schema: **passed**.

## Not claimed

- No on-device Windows runtime/real Codex task was run during this packaging session; final owner-side tests still required.
- No Cloudflare resources were deployed or tokens configured on the owner's account.
- No actual final JARVIS v2 architecture was imported yet; engine remains stopped.
- Independent behavioral QC isolation (VM/container), full autonomous self-healing, high-impact approvals, systemd/Windows service watchdog, remote GitHub pushes, production deployment, live JARVIS data integration and full product modules **not implemented** in this foundation release.
- Codex Windows workspace sandbox may be weaker than a VM. Do not provide a privileged Windows account or personal secrets to experimental generated code.
