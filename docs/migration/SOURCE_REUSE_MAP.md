# Legacy JARVIS → JARVIS v2 selective source migration

**Source:** private `admindeveloper4562/personal-jarvis` (old repo preserved unchanged). Import is a **reviewable candidate stage** only. The importer reads committed Git blobs with `git show`, never executes them and writes provenance (ref, commit SHA, source path, destination, SHA-256) to `migration/provenance/import-log.json`. It refuses to overwrite staged files.

| New subsystem | Existing legacy source to inspect | Approach / acceptance |
|---|---|---|
| Core tasks, dispatcher | `develop:jarvis/tasks.py`, `jarvis/worker.py` | Port durable states and typed tools behind Core v2 API; compare semantics via tests |
| Backend storage & permissions | `develop:jarvis/storage.py`, `jarvis/permissions.py`, `jarvis/router.py`, `jarvis/colibri.py` | Reuse behavior and tests, not DB schema blindly; preserve owner approvals and prompt boundaries |
| Runtime | `develop:jarvis/server.py`, `jarvis/voice.py`, `jarvis/inventory.py`, `jarvis/email.py`, `jarvis/calendar.py` | Review component-by-component; preserve strong local HTTP checks |
| SDA | `develop:scripts/codex_workhorse_v2.py`, `feature/jarvis-v2-expanded-architecture-20261113:scripts/sda_context_handoff.py` and `scripts/sda_module_integrity.py` | Reconcile external Astra Master with legacy Workhorse; avoid competing controllers |
| Context | `feature/workhorse-context-engine-4way-20261109:scripts/workhorse_context.py` | Re-benchmark four modes and adopt only passing ones |
| TWS | `feature/twelve-winged-m001:extensions/twelve-winged-system/` | Import complete relevant Python/iOS/3D sources in bounded batches; native device acceptance pending |
| Cloudflare | `feature/cloudflare-overnight-inference-coordinator-20261112:cloudflare/jarvis-coordinator/`, `scripts/jarvis_queue_worker.py` | Review live D1 schema and Worker IDs, avoid duplicate databases, no raw secrets |
| Guardian | `feature/jarvis-v2-expanded-architecture-20261113:scripts/sda_module_integrity.py`, `scripts/sda_recovery_triage.py` | Candidate diagnostics only; deploy trust control is new, independent policy code |
| Research | Existing `Video-Summary` repository requires separate authorized audit | New module integration via documented adapter, not guessed code paths |
| Finance | Mira source requires separate authorized repo audit | Read-only scoped contract, partner consent, paper-only trading |
| WIC | No verified implementation in this repo | New code with source/timestamp/correction contract |
| Business | Historical ideas only | **No active module** or tasks |

**Before promotion:** pinned commit SHA, licenses/copyright, dependency scan, import compatibility, targeted tests, security review, independent QC, serial merge and explicit integration approval. `migration/imported` must NEVER be installed as runtime executable code merely because it has been copied there.
