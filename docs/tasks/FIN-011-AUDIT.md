# FIN-011 — Market research adapter audit

Status: audit candidate; implementation gap recorded

Audit base: `de5863e2036c1ad2f3382c0693bca5c93314f1e7`

This bounded report records repository evidence only. No live market service,
financial database, credential, or external row was accessed.

## Evidence inventory (FIN-011.S01)

| Area | Observed evidence | Result |
|---|---|---|
| Finance module | `src/jarvis_v2/finance/mira_audit.py` records source-bound Mira metadata and a GET-only policy | Reusable read-only boundary; no quote adapter |
| Research timestamps | `src/jarvis_v2/research/analysis.py`, `comparison.py`, `github.py` and `web.py` validate observation timestamps | Reusable timestamp conventions |
| WIC provenance | `src/jarvis_v2/wic/__init__.py` validates source, fetched, published and source-updated timestamps | Reusable provenance pattern |
| Existing finance tests | `tests/test_finance_mira_audit.py` covers metadata-only review and GET-only access | No market-price tests |
| Existing retrieval tests | `tests/test_backend_retrieval.py` covers source/timestamp/citation metadata | No exchange, quote delay or price uncertainty |
| Market adapter search | No finance symbol or fixture for price, exchange, quote delay or market uncertainty was found in the pinned worktree | Required implementation is absent |

The inspected source is unchanged. Existing timestamp and provenance helpers
are patterns, not proof that FIN-011's market acceptance is implemented.

## Findings matrix (FIN-011.S02)

| Acceptance clause | Evidence | Finding |
|---|---|---|
| Price value is represented | No finance quote model or adapter found | Gap |
| Source and provenance are represented | WIC/research patterns exist; finance adapter does not consume them | Partial |
| Delay is recorded | No delay field or source-specific delay contract found | Gap |
| Exchange is recorded | No exchange field or validation found | Gap |
| Uncertainty is recorded | Generic research confidence exists, but no market-quote uncertainty contract exists | Gap |
| Timestamp is recorded | Existing timezone-aware observation patterns are reusable | Available pattern |
| No guaranteed profit | Finance module is incomplete and contains no trading claim | Constraint preserved |
| Hosted CI evidence | Remote Actions are not used by this audit | Deferred; not a pass claim |

## Decision record (FIN-011.S03)

The smallest compatible future implementation is a read-only market adapter in
`src/jarvis_v2/finance/` with focused tests. Its immutable result should
contain at least:

```text
symbol, company, price, currency, exchange,
source_id, source_uri, observed_at, source_delay_seconds,
uncertainty, status
```

The adapter must reject naive timestamps, negative delay, invalid exchange or
uncertainty values, missing source provenance, and write operations. Unknown
delay must remain explicitly unknown rather than becoming zero. Results must
state the source timestamp/delay and must not imply guaranteed profit.

The adapter should reuse the existing source/timestamp validation style and
remain separate from Mira ingestion and the paper-trading ledger. A provider
or live market credential is not selected by this audit; that choice requires
a later implementation task and its own authorization/evidence.

## Independent cross-check (FIN-011.S04)

- The audit was performed against one isolated worktree and pinned base SHA.
- Only bounded path/symbol searches and source reads were used.
- No source file was modified; the candidate change is this report only.
- No price, credential, personal-finance row or live market result is present.
- The acceptance gaps above are intentionally retained and must not be
  reported as an implemented adapter.

## Outcome and next action

This candidate completes the audit/decision deliverable and preserves the
implementation gap. If the parent acceptance requires the adapter itself,
FIN-011 must remain unresolved after this audit and a separately admitted
implementation task must provide the code, deterministic fixtures, focused
tests and independent QC. This report is not a substitute for that evidence.
