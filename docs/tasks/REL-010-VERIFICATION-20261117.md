# REL-010 — WIC freshness, corrections and time-sensitive notifications

**Status:** verified against integration base `c900b7bde8b4bfb3e925dfc2ec9d44ecd316e6af`.

**Parent:** REL-010 — Verify WIC freshness, corrections and time-sensitive notifications

**Acceptance:** No false live claim, duplication or unsourced notification.

## Evidence inventory

| Boundary | Pinned evidence | Finding |
| --- | --- | --- |
| WIC source age | `src/jarvis_v2/wic/__init__.py`, `SourceStore` and `PublicSourceIngestion` | Fetched, published and source-updated times are separate. Health is `fresh`, `stale`, `outage` or `unknown`; provider failures preserve the last successful timestamp. |
| WIC corrections | `ClaimLedger`, `WorldCard`, `tests/test_wic_verification.py`, `tests/test_wic_world.py` | Retractions and corrections append history and remain visible; a retracted claim cannot be verified until a valid correction/corroboration path is exercised. |
| WIC alerts | `AlertPolicy`, `AlertStore`, `tests/test_wic_alerts.py` | Owner scope, material-change gating, digest deduplication, cadence and quiet-hour suppression are deterministic and persisted. |
| Runtime notifications | `src/jarvis_v2/runtime/reminders.py`, `ReminderService` | Scheduled reminders are gated as `ready`, `paused_quiet_hours` or `disabled`; this service does not turn WIC data into an external delivery. |
| Event delivery | `src/jarvis_v2/backend/event_bus.py`, `tests/test_backend_event_bus.py` | Delivery receipts fence duplicate effects and retain failure state; the tested event path is durable and idempotent. |
| Live-claim boundary | `CitedSummaryComposer` and WIC source tests | Unsupported `live` freshness is rejected. Feed transport is injected for tests; no fixture is reported as a live external observation. |

No credentials, private data or live provider payloads were read. No external
notification, trade, message or hosted workflow was triggered.

## Acceptance matrix

| Requirement | Result | Evidence and limitation |
| --- | --- | --- |
| No false live claim | PASS | WIC refuses unsupported live summary freshness; deterministic tests use injected transports and the report does not relabel them as live. |
| No duplication | PASS | Source replay is idempotent, alert digests deduplicate, event delivery receipts fence repeated effects, and correction/retraction history is append-preserving. |
| No unsourced notification | PASS FOR REVIEWED CODE | Alert admission requires an owner-scoped policy, material change and a source-change digest. WIC records an admission decision only; no WIC-to-notification delivery path is present. |
| Current/live host acceptance | UNVERIFIED EXTERNAL INPUT | No authorized live feed or external user-acceptance session was supplied. This is a limitation, not a passing live-data claim. |

## Child evidence

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-010.S01` | PASS | This matrix maps each acceptance clause to concrete symbols, tests and limitations. |
| `REL-010.S02` | PASS | Tests use temporary SQLite stores and deterministic sanitized values; no secrets or provider payloads are retained. |
| `REL-010.S03` | PASS | WIC, release-contract, fault-isolation, reminder, event-bus and full local regression commands exited zero. |
| `REL-010.S04` | PASS | Negative coverage includes stale/outage/unknown source states, retraction, duplicate replay, cadence/quiet-hours suppression, ownership denial and event fencing. |
| `REL-010.S05` | PASS | This report is bound to the integration base and source/test blob SHAs and preserves the live-input limitation. |

## Pinned source and test blobs

```text
src/jarvis_v2/wic/__init__.py          ebf1c04b33f334621656e1bafb483dff99c48b74
src/jarvis_v2/runtime/reminders.py     3fa9fed5daed8fe0173a7ec8c9693b173a9fbac3
src/jarvis_v2/backend/event_bus.py     e08b3c010325b3f947f15957b31cb12c5b8fd6d7
tests/test_wic_sources.py              e4322f1c9816f943f06e03ae19cdfc91ece68071
tests/test_wic_alerts.py               a7184452781c5151034f035a23f8483f972ac1c7
tests/test_wic_summaries.py             746e54971cf4a88dece25d77c8b222cc9f7bd813
tests/test_wic_verification.py          78ebea90542fdf678c7cae72e2dd1475e5879459
tests/test_runtime_reminders.py         481b8384568c40655207657762f66cd6e679e91e
tests/test_backend_event_bus.py         4dd722866d73885b27e81eb7d44e1d8b1c805a08
tests/test_rel_cross_module_contracts.py 0a5068190cb0dd71c67a490c5a256096e61415c9
tests/test_rel_fault_isolation.py       b280b215b51613e5a706e5717bba6267cd6bc112
```

## Commands and results

```text
PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_wic_*.py' -q
Ran 41 tests — OK

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_rel_cross_module_contracts.py' -q
Ran 2 tests — OK

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_rel_fault_isolation.py' -q
Ran 1 test — OK

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_runtime_reminders.py' -q
Ran 3 tests — OK

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -p 'test_backend_event_bus.py' -q
Ran 5 tests — OK

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -q
Ran 480 tests — OK
```

The full suite emits the expected read-only monitor argparse diagnostic while
testing the monitor entry point; its exit code is 0 and all 480 tests pass.
No hosted workflow was dispatched; hosted-only acceptance remains subject to
the repository quota policy.

This receipt verifies the reviewed local boundaries. It does not claim live
provider measurements, a user-session notification delivery, production
deployment or an external side effect.
