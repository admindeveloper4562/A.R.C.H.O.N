# AUTO-013 Verification — Cloudflare monitor deployment

Status: `LOCAL_EVIDENCE_RECORDED / READY_FOR_INDEPENDENT_QC`

This verification candidate records the owner-executed deployment and bounded
read-only checks for AUTO-013. It does not expose or reproduce either Worker
secret. The deterministic Master remains the authority for task state,
receipts and completion.

## Identity and deployment evidence

| Field | Observed value |
| --- | --- |
| Task | `AUTO-013` |
| Execution mode | `verification` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration base SHA | `99ce2739f75b15657a33a9c0c133e3736e96fd3f` |
| Worker | `astra-one-monitor` |
| URL | `https://astra-one-monitor.admin-developer4562.workers.dev` |
| Deployment version | `e2adef30-cd8a-49ad-b3c1-a46bfb569317` |
| D1 database | `astra-one-monitor` / `e3d42451-9dfa-457d-abd0-b1b45609a0b4` |
| D1 schema | `_cf_KV`, `astra_events`, `astra_runs` |
| D1 writes during verification | `0` |
| Release approval reference | `owner-executed-deployment-command` |
| Deployment evidence SHA-256 | `2a8d5db901d2333b24037ebbcd406e750bbee23173eb695e67d28723e282bbc6` |

The owner-provided Wrangler transcript records successful secret installation,
deployment, the version ID above and the printed Worker URL. Secrets are not
included in this candidate or its evidence.

## Acceptance matrix

| Child | Result | Evidence and limitation |
| --- | --- | --- |
| `AUTO-013.S01` | PASS | The matrix binds version, URL, health, D1 schema, release reference and smoke checks to the source/base identities above. |
| `AUTO-013.S02` | PASS | Sanitized deployment metadata and deterministic local fixtures were used; no secrets or production records were copied. |
| `AUTO-013.S03` | PASS | Fresh local TypeScript typecheck, build, four-test Worker smoke suite, live `/api/health`, and read-only D1 schema query completed as recorded below. |
| `AUTO-013.S04` | PASS | Unauthenticated read and ingest requests were denied with HTTP 401; no safety boundary was bypassed. |
| `AUTO-013.S05` | PASS | This report records pass/limitation status, source/base SHAs, versioned deployment identity and bounded evidence hashes. |

## Executed checks

| Check | Exit/status | Result |
| --- | ---: | --- |
| `npx --yes --package typescript tsc --noEmit` | 0 | PASS |
| `npx --yes --package typescript tsc --noEmit false --outDir .test-output` | 0 | PASS |
| `node --test tests/worker.test.mjs` | 0 | 4 passed, 0 failed, 0 skipped |
| `GET /api/health` | HTTP 200 | `{"ok":true,"service":"astra-one-monitor"}` |
| `GET /api/runs` without a token | HTTP 401 | PASS: protected read API denied |
| `POST /api/events` without a token | HTTP 401 | PASS: protected ingest API denied |
| Wrangler D1 schema query with `--remote` | exit 0 | PASS; schema read-only and `rows_written=0` |

Bounded local source hashes:

```text
src/index.ts                  cdcc996bd3f7a3346c725404bbca6c59009e86789181ded01b5ace9cb42e328c
tests/worker.test.mjs          d03b69686f7d5061b937f6ae7add9360701f654e7b2dd244b5c432a0692750c7
metadata test digest           205946654c0dbfb1b1400855315d8ca2cf513c38aa75cb1a17fb0c9310b39e3f
```

## Limitations and safety boundaries

- The authenticated ingest path was not exercised because doing so would
  require handling the owner-held ingest secret. Its presence was verified by
  the successful Wrangler secret operation, not by copying the secret into the
  repository or chat.
- No production records were written. The remote D1 schema check reported
  zero writes.
- Hosted GitHub Actions were not dispatched under the repository quota policy.
- The deployment transcript is owner-provided terminal evidence; the Master
  must bind this report to the final candidate SHA and issue the independent QC
  and Merger receipts.

No application source, security policy, owner approval policy, protected
branch, production database or `main` ref was modified by this candidate.
