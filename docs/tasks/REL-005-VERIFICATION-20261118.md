# REL-005 verification — Cloudflare pending jobs

This report is bound to the Main Codex candidate base `22f84df368b54c67b2c17044d8477d5e8a129faa` and the owner-operated Cloudflare deployment evidence recorded outside the repository. It contains metadata only; no job payloads, credentials, prompts or result contents are stored here.

## Acceptance matrix

| Acceptance clause | Observable check | Result |
| --- | --- | --- |
| Cloudflare stores jobs only | Worker API accepts bounded job metadata and rejects an unexpected `payload` field | PASS |
| Reconnect resumes safely | A 30-second lease expires, the job returns to `pending`, and another device claims it | PASS |
| Completion is trustworthy | A stale lease is rejected; the valid lease completes; an identical replay is idempotent and a conflicting digest is rejected | PASS |
| Age is reported | The pending-job listing returns the persisted creation/deadline timestamps needed to calculate age | PASS |
| Deployment is live | Authenticated create → claim → complete smoke test finished with state `completed` | PASS |

## Implementation and deployment identity

The reviewed pending-job implementation is preserved at source commit `4d6a5407443e0b0d8b7cff28724dcb9216386e0f`, with the REL branch-policy follow-up at `7a7718339ddd181d33091427a65859775d350466`. The owner-operated deployment is the `astra-one-monitor` Worker at:

`https://astra-one-monitor.admin-developer4562.workers.dev`

Deployment version: `15381dca-c6d0-44d9-9eaf-c7cc7b293e59`.

The additive D1 schema contains `_cf_KV`, `astra_events`, `astra_jobs` and `astra_runs`. The live smoke record is `rel005-smoke-1794997770`, and its final state is `completed`. The post-smoke D1 job-row count is 1. Only metadata and SHA-256 values are stored by this feature.

## Deterministic evidence

The reviewed worker test suite contains 7 tests and passed with `npm run typecheck && npm run smoke`. It covers authentication separation, malformed and payload-bearing requests, idempotent enqueue, lease expiry/reclaim, stale-lease rejection, completion idempotency and conflicting-result rejection.

The Wrangler deployment dry-run passed. The live health endpoint returned HTTP 200 for service `astra-one-monitor`. The authenticated live smoke used the owner-provided `ASTRA_JOB_TOKEN` interactively and produced `created=True claimed=leased completed=completed`; the token was not recorded.

The owner-private evidence packet is:

`~/.local/state/archon-astra/private/REL-005-external-evidence.json`

Its SHA-256 is `6f19bb40be6ab3a4ea5ad466fc44d230e58c387f1a3cca5ee5a880993dc32fca`. The deterministic Master accepted that packet and recorded a verified SQLite backup before re-admitting REL-005.

## Negative and boundary results

- Unauthenticated job reads are denied.
- Ingest/view/job tokens are separate.
- Requests containing an unapproved payload field are rejected.
- Duplicate job and idempotency-key submissions do not create a second job.
- Expired leases are requeued before reclaim.
- A stale or conflicting lease cannot complete another device's job.
- Repeating the same valid completion is idempotent.

No hosted GitHub Actions result is used. The evidence is local deterministic testing plus the real owner-operated Cloudflare smoke; hosted CI remains subject to the repository's quota policy.
