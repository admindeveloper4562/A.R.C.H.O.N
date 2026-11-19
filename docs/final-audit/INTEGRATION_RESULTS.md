# Integration results

Source under test: /home/r34p3r/dev/A.R.C.H.O.N at a2df24261d5ea19e9260f7f6c270b26ea9abdb03.

| Check | Command/evidence | Result |
| --- | --- | --- |
| Native import sweep | PYTHONPATH=src; import all 106 jarvis_v2 modules | PASS |
| Module and identity CLI | python3 -m jarvis_v2.cli modules/identities | PASS |
| Native monitor | tools/atlas_monitor.py --source atlas against fresh atlas.sqlite3 | PASS; empty queue |
| Fresh storage | StorageManager migration into runtime.sqlite3 | PASS |
| Fresh queue | TaskQueue schema into atlas.sqlite3 | PASS |
| Fresh restore | SQLite backup API plus integrity/foreign-key checks | PASS |
| FTS5 index | 546 files indexed from 547 cataloged files, including systemd and Windows deployment files; four representative queries returned results | PASS |
| Astra unavailable native import | PYTHONPATH=src without bootstrap path | PASS for native imports |
| Native controller | Fresh one-shot, lock fencing, control-marker admission, executor success/failure receipts, terminate/restart, and systemd unit verification | PASS; unit not installed and executor unconfigured |
| Native health | `jarvis_v2.cli health` against fresh runtime/ATLAS state; historical ledger explicitly not loaded | PASS |
| Host capability inventory | Bounded root metadata scan plus Ollama model listing and NVIDIA acceleration probe | PASS; scan truncated by bound |
| Full regression | 579 unittest cases | PASS |
| Security/dependency checks | local dependency, secret, and security scans | PASS |

This is a controlled Linux integration result, not proof of complete release operation. The fresh native state intentionally has no task ledger, credentials, personal records, or external accounts.
