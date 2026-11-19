# Regression coverage

| Area | Evidence | Result | Remaining gap |
| --- | --- | --- | --- |
| Core queue, dispatch, sessions, controls | 20 core test files in the 579-test suite, including native controller fencing, marker admission, and native health | PASS | No sustained load benchmark |
| Backend storage, migration, event bus, routing, secrets | Backend test files and fresh SQLite restore | PASS | No external provider calls |
| Runtime, security, browser, chat, speech, service | Runtime test files and native import sweep | PASS | No real desktop/browser/device run |
| Guardian, fencing, rollback, restart | Guardian tests and fault-injection fixtures | PASS locally | Trusted out-of-process cutover not proven |
| Automation, leases, scheduler, recovery | Automation test files | PASS locally | No live external-action execution |
| Research and RAG | Research safety, retrieval, reranking, and media tests | PASS locally | No live provider freshness evidence |
| Finance | Paper/read-only finance tests | PASS locally | Real accounts and transactions intentionally not initialized |
| TWS | Model, lifecycle, storage, CI, and visual-QA fixtures | PASS locally | Blender/device execution not run here |
| WIC | Source, verification, alerts, watchlists, and world tests | PASS locally | Live feed access not run unattended |
| Build/release/security | CI policy, secret scan, security scan, dependency scan | PASS locally | Hosted CI unavailable |
| Host inventory | Four API regression tests, including section/capacity comparison, and one bounded Linux scan | PASS | Scan was bounded/truncated by design |

No production data was used by regression tests. No test result is promoted to external acceptance without the missing environment evidence.
