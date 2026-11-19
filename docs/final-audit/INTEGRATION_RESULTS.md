# Integration results

Source under test: `/home/r34p3r/dev/A.R.C.H.O.N` at implementation candidate `4149c1d75eee24880bfacd819342f9c21d05d51a`; latest evidence overlay `0d6658b0aa2449c4071c0ca05ddda0aad3609bd2` contains no production-code changes.

| Check | Command/evidence | Result |
| --- | --- | --- |
| Native import sweep | PYTHONPATH=src; import all 106 jarvis_v2 modules | PASS |
| Module and identity CLI | python3 -m jarvis_v2.cli modules/identities | PASS |
| Native monitor | tools/atlas_monitor.py --source atlas against fresh atlas.sqlite3 | PASS; empty queue |
| Default monitor boundary | tools/atlas_monitor.py --json with both native and historical state present | PASS; selects native ATLAS; Astra requires explicit `--source astra` |
| Fresh storage | StorageManager migration into runtime.sqlite3 | PASS |
| Fresh queue | TaskQueue schema into atlas.sqlite3 | PASS |
| Fresh restore | SQLite backup API plus integrity/foreign-key checks | PASS |
| FTS5 index | 552 files indexed from 553 cataloged files, including systemd and Windows deployment files; four representative queries returned results | PASS |
| Astra unavailable native import | PYTHONPATH=src without bootstrap path | PASS for native imports |
| Native controller | Fresh one-shot, lock fencing, control-marker admission, executor success/failure receipts, eight bounded read-only probes, resumable inventory cursor, terminate/restart, and systemd unit verification | PASS for bounded read-only operations; unit not installed and domain-effect handlers not configured |
| Native health | `jarvis_v2.cli health` against fresh runtime/ATLAS state; historical ledger explicitly not loaded | PASS |
| Host capability inventory | Bounded root metadata scan plus Ollama model listing, NVIDIA acceleration probe, and private continuation cursor | PASS; 10,000 entries, 1,328 pending frames, scan truncated by bound |
| Full regression | 590 unittest cases at 4149c1d | PASS; 27.762 seconds, exit 0 |
| Independent focused QC | Current overlay 1c27e22; native executor 8/8 and inventory 6/6 | PASS; full suite was not rerun independently |
| Security/dependency checks | local dependency, secret, and security scans | PASS |

This is a controlled Linux integration result, not proof of complete release operation. The fresh native state intentionally has no task ledger, credentials, personal records, or external accounts.
