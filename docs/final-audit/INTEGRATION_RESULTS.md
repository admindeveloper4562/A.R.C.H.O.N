# Integration results

Source under test: /home/r34p3r/dev/A.R.C.H.O.N at tested local tree 239e10154e1c81b4ff463cdd796e04f0dbc68407; implementation commit eef1e3c8d1bfd3ea6a3dc7e1b06ac2daa3e21767.

| Check | Command/evidence | Result |
| --- | --- | --- |
| Native import sweep | PYTHONPATH=src; import all 106 jarvis_v2 modules | PASS |
| Module and identity CLI | python3 -m jarvis_v2.cli modules/identities | PASS |
| Native monitor | tools/atlas_monitor.py --source atlas against fresh atlas.sqlite3 | PASS; empty queue |
| Default monitor boundary | tools/atlas_monitor.py --json with both native and historical state present | PASS; selects native ATLAS; Astra requires explicit `--source astra` |
| Fresh storage | StorageManager migration into runtime.sqlite3 | PASS |
| Fresh queue | TaskQueue schema into atlas.sqlite3 | PASS |
| Fresh restore | SQLite backup API plus integrity/foreign-key checks | PASS |
| FTS5 index | 549 files indexed from 550 cataloged files, including systemd and Windows deployment files; four representative queries returned results | PASS |
| Astra unavailable native import | PYTHONPATH=src without bootstrap path | PASS for native imports |
| Native controller | Fresh one-shot, lock fencing, control-marker admission, executor success/failure receipts, terminate/restart, and systemd unit verification | PASS; unit not installed and executor unconfigured |
| Native health | `jarvis_v2.cli health` against fresh runtime/ATLAS state; historical ledger explicitly not loaded | PASS |
| Host capability inventory | Bounded root metadata scan plus Ollama model listing and NVIDIA acceleration probe | PASS; scan truncated by bound |
| Full regression | 579 unittest cases | PASS |
| Security/dependency checks | local dependency, secret, and security scans | PASS |

This is a controlled Linux integration result, not proof of complete release operation. The fresh native state intentionally has no task ledger, credentials, personal records, or external accounts.
