# FIN-015 Verification Report

**Task:** FIN-015 — Run leakage/consent/financial precision/adversarial tests  
**Run:** `f40051ab-d1ae-446f-889f-7e777c55996d`  
**Attempt:** 1  
**Base/integration SHA:** `1bf3f66967c6adccc459ce8b268532ba56019953`  
**Source SHA:** `43c8db7de8a5f0277a7db23379019d05f2edd2c6`  
**Environment:** Python 3.12.3, Linux, no live Mira, broker, or Cloudflare calls

## Acceptance matrix

| Requirement | Observable check | Result |
| --- | --- | --- |
| Other-person data is denied | Finance reads are keyed by `(source_id, scope_id)`; the scope-isolation test writes two person scopes and verifies that a read for the other scope is empty | PASS |
| Mira is read-only to ARCHON | `authorize_mira_method` accepts `GET` only; `POST`, `PUT`, `PATCH`, and `DELETE` are rejected | PASS |
| Mira capability is consent- and identity-scoped | Connector tests reject a foreign identity and `mira:write`, and verify immediate revocation and bounded TTL | PASS |
| Paper trading cannot touch real finance state | Paper-ledger tests use a separate database and verify real-account state remains unchanged | PASS |
| Precision and adverse cases are covered | Finance tests cover exact satang values, duplicate orders, insufficient cash, invalid sells, closed market hours, and liquidity limits | PASS |
| No real write endpoint is exposed by this ARCHON surface | Source and tests contain no Mira/broker write client; the only ARCHON Mira method authorization is `GET`, and paper orders remain local hypothetical state | PASS |

## Child evidence

- `FIN-015.S01` — acceptance clauses converted to the matrix above; every clause has an observable assertion.
- `FIN-015.S02` — deterministic in-memory/temp-directory fixtures; no credentials or financial rows are included.
- `FIN-015.S03` — all runnable focused checks below completed with exit code 0.
- `FIN-015.S04` — denial, identity mismatch, revocation, duplicate, precision, insufficient-cash, market-hours, and liquidity cases completed with exit code 0.
- `FIN-015.S05` — this report is bound to the base SHA and candidate report commit.

## Test evidence

All commands ran from the candidate worktree with `PYTHONPATH=src:bootstrap/astra-one`.

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_finance*.py' -q` | PASS — 43 tests |
| `python3 -m unittest discover -s tests -p 'test_backend_connectors.py' -q` | PASS — 4 tests |
| `python3 -m unittest discover -s tests -p 'test_backend_authorization.py' -q` | PASS — 4 tests |
| `python3 -m unittest discover -s tests -p 'test_backend_secrets.py' -q` | PASS — 4 tests |

No hosted workflow was invoked. No external credentials, private key material, Mira rows, broker account, or live endpoint was accessed.

## Source and test artifact hashes

The report was prepared against base `1bf3f66967c6adccc459ce8b268532ba56019953`.

```text
c7ed7e8069aab8b4195b5d09bd40f29661c70021f9561cb0e2534e907b536427  src/jarvis_v2/finance/mira_audit.py
7cbfa916deacafbcc25b55db6c66567e7804f389305a96a526647eb768848f27  src/jarvis_v2/finance/mira_connector.py
72222ca10d348aa4aa486f929037a10c5a4520867af14d3b99555f59beafb6f4  src/jarvis_v2/finance/paper.py
1409988f39d7dc96886f9bb5cbe82c634985c4fea0f5c654113dc72df4a947d6  tests/test_finance_mira_audit.py
d95732484867b97b55718b78f87e8642143989c710ef5f29c8bceb80d6a909c4  tests/test_finance_mira_connector.py
1f27cdd0a1a6c42a2e3094889ad5d275f395c19cac6def476f0307028ee6ebe6  tests/test_finance_paper.py
7b62df629df278a7a1f4e6d7296b376f46685460bba3fe23f6610a2f42161993  tests/test_finance_alerts.py
b6b4d3b9004d733db23b4c86fa5c27a9a358425d86d7a40bdc22e28b656da5f8  tests/test_finance_advice.py
```

## Conclusion

The local, deterministic acceptance evidence passes. This verification does not claim live Mira or broker testing; the implementation is intentionally limited to read-only Mira authorization and isolated paper state. The candidate changes only this bounded verification report.
