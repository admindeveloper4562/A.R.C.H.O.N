# ATLAS Monitor — separate read-only developer terminal

ATLAS Monitor is a standalone terminal UI, replacing the *status-viewing* workflow of the legacy Workhorse monitor. It **does not implement, import, stop, start or control the runner**. It does not create databases, edit task state, open Git repos, execute Codex, send network traffic, or deploy Cloudflare.

## Launch on Ubuntu

From the clean v2 repository:

```bash
# Native ARCHON/ATLAS queue status, refresh every two seconds
python3 tools/atlas_monitor.py --source atlas --watch --interval 2

# Or when installed: atlas-monitor --source atlas --watch

# One non-interactive snapshot (for diagnosis and local tooling)
python3 tools/atlas_monitor.py --source atlas --json

# Hide task descriptions on shared screens or in JSON logs
python3 tools/atlas_monitor.py --source atlas --watch --no-objectives

# Historical Astra status is explicit and read-only
python3 tools/atlas_monitor.py --source astra --watch --interval 2
```

For a customized Astra state directory, pass its exact database path:

```bash
python3 tools/atlas_monitor.py --source astra --db "$HOME/.local/state/astra-one-linux/sda.sqlite3" --watch
```

For the native ATLAS Core task DB:

```bash
python3 tools/atlas_monitor.py --source atlas --db "$HOME/.local/state/archon/atlas.sqlite3" --watch
```

`--source auto` prefers the native ATLAS database when it exists, then falls back to the native SDA-compatible path and finally to explicitly discoverable historical Astra databases. Native ATLAS records queued/leased/completed/failed tasks and a separate safe title; it does **not yet** track the full five-worker/review/merge pipeline. Do not mistake a blank five-worker panel for actual agent idleness when the runner does not persist that information.

## Astra One v3 supervisor and upgrade panels

On the existing ARCHON installation, `--source astra` now prefers
`~/.local/state/archon-astra/sda.sqlite3` and falls back to
`~/.local/state/astra-one-linux/sda.sqlite3` when necessary. Use `--db`
to select a nonstandard file explicitly.

The monitor now includes additive read-only panels:

- **Project ledger:** recorded parent and subtask status counts for `ARCHON-JARVIS-V2`, if available. Child statuses are explicitly labelled *bookkeeping, not independent acceptance proof*. A SQLite "completed" field is never treated as a QC receipt.
- **Five durable queues:** `project_queue`, `pending_queue`, `rebuild_queue`, `review_queue`, `merge_queue`. Missing tables are shown as `not recorded`, not zero.
- **Two supervisor recovery lanes and upgrade auditor:** `repair_1`, `repair_2`, `upgrade_auditor` when the optional `supervisor_lanes` table exists. No lane is fabricated from unrelated worker events.
- **Blocked task recovery:** categorized, dated case state from optional `supervisor_cases`. No raw failure reports, prompts or private source text are rendered.
- **Self-upgrade batch:** staged candidate and rollback SHA, recorded batch status from optional `upgrade_batches`. Does not claim an upgrade actually activated without an explicit persisted state.
- **Run/failure hotspots:** grouped run outcomes and redacted failure categories, never raw exception text or model review findings.

The proposed additive telemetry schema and control-plane upgrade phases are defined in
`docs/architecture/ASTRA_ONE_V3_CONTINUOUS_RECOVERY.md`.
The monitor **does not create those tables** or run migrations. Where runtime
instrumentation is not yet installed it reports **not instrumented**, rather
than interpreting missing observations as idle or healthy.

The monitor intentionally does not establish a live systemd process heartbeat,
time-to-merge estimate, or total token cost from database-only evidence.
Future versions must read explicit persisted lease, heartbeat and cost receipts
and label stale/unknown measurements separately.

### Full-build view

```bash
python3 tools/atlas_monitor.py --source astra \
  --db "$HOME/.local/state/archon-astra/sda.sqlite3" --watch --interval 2

# Machine-readable owner-private snapshot; do not combine --json and --watch
python3 tools/atlas_monitor.py --source astra \
  --db "$HOME/.local/state/archon-astra/sda.sqlite3" --json --no-objectives
```

## Data displayed

- Actual recorded queued, active, review, merge-ready, completed and blocked counts; completion percentage is **completed / observed tasks**, not an invented JARVIS v2 project-wide percentage.
- Active task IDs, bounded objective titles, area, status and last recorded step. Native ATLAS titles are distinct from private task payloads and are never inferred from untrusted tool arguments.
- Worker slot only if the **current run** emitted a `worker_N` or `repairer_N` event. Unknown slot is marked `unmapped`; events from a prior failed attempt cannot assign a misleading slot.
- Architecture approval status, integration branch/commit, STOP/PAUSE/PAUSED_QUOTA marker files.
- Review and merge-ready queues, up-next tasks, error classification and recent event stages.

The CLI reads SQLite via read-only URI (`mode=ro`) with `query_only` and a short busy timeout. It uses a single consistent read transaction per refresh, including WAL updates; it never issues inserts, updates, migrations or checkpoints. The task payload is never printed in JSON. Use `--no-objectives` to suppress task-title text. Treat the local monitor output as owner-private, particularly on remote terminals.

## Operational characteristics and failure handling

- **Two terminals:** start the approved native controller or the explicitly selected historical Astra source in one, and ATLAS Monitor in another. Closing ATLAS Monitor does **not** stop active work.
- When the DB is missing or unrecognized, the monitor prints a readable error and exits; it does not initialize a blank one.
- Press **Ctrl+C** to close the monitor safely; STOP/PAUSE must only be issued by the separate authorized SDA CLI.
- Terminal refresh uses ANSI clear only for interactive terminals. `--json` performs a single snapshot and exits, suitable for tests or operator reports.
- A database-only monitor cannot reliably infer live process identity if the runner has crashed and its last task status was not recovered. Old activity should be treated as possibly stale; check current process/heartbeat separately.
- Do not upload the JSON output to Cloudflare without a dedicated redaction/authorization layer.

## Options

```text
--source auto|astra|atlas        Schema selection (default auto)
--db PATH                      Explicit existing SQLite file
--watch                        Refresh until Ctrl+C
--interval 2                   Refresh period (0.5–3600 seconds)
--limit 10                     Max task entries per section
--events 8                     Latest event records
--json                         Single machine-readable snapshot
--no-objectives                Hide task descriptions
--no-color                     Disable ANSI heading
```
