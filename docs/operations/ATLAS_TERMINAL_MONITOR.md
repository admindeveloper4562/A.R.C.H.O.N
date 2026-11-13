# ATLAS Monitor — separate read-only developer terminal

ATLAS Monitor is a standalone terminal UI, replacing the *status-viewing* workflow of the legacy Workhorse monitor. It **does not implement, import, stop, start or control the runner**. It does not create databases, edit task state, open Git repos, execute Codex, send network traffic, or deploy Cloudflare.

## Launch on Ubuntu

From the clean v2 repository:

```bash
# Real external Astra One Linux v0.2.0 SDA status, refresh every two seconds
python3 tools/atlas_monitor.py --source astra --watch --interval 2

# Or when installed: atlas-monitor --source astra --watch

# One non-interactive snapshot (for diagnosis and local tooling)
python3 tools/atlas_monitor.py --source astra --json

# Hide task descriptions on shared screens or in JSON logs
python3 tools/atlas_monitor.py --source astra --watch --no-objectives
```

For a customized Astra state directory, pass its exact database path:

```bash
python3 tools/atlas_monitor.py --source astra --db "$HOME/.local/state/astra-one-linux/sda.sqlite3" --watch
```

For the **future** native ATLAS Core task DB:

```bash
python3 tools/atlas_monitor.py --source atlas --db "$HOME/.local/state/archon/atlas.sqlite3" --watch
```

You can use `--source auto` with `--db` to detect a supported database schema, but native ATLAS's seed database only records queued/leased/completed/failed tasks and a separate safe title; it does **not yet** track the full five-worker/review/merge pipeline. Do not mistake a blank five-worker panel for actual agent idleness when the runner does not persist that information.

## Data displayed

- Actual recorded queued, active, review, merge-ready, completed and blocked counts; completion percentage is **completed / observed tasks**, not an invented JARVIS v2 project-wide percentage.
- Active task IDs, bounded objective titles, area, status and last recorded step. Native ATLAS titles are distinct from private task payloads and are never inferred from untrusted tool arguments.
- Worker slot only if the **current run** emitted a `worker_N` or `repairer_N` event. Unknown slot is marked `unmapped`; events from a prior failed attempt cannot assign a misleading slot.
- Architecture approval status, integration branch/commit, STOP/PAUSE/PAUSED_QUOTA marker files.
- Review and merge-ready queues, up-next tasks, error classification and recent event stages.

The CLI reads SQLite via read-only URI (`mode=ro`) with `query_only` and a short busy timeout. It uses a single consistent read transaction per refresh, including WAL updates; it never issues inserts, updates, migrations or checkpoints. The task payload is never printed in JSON. Use `--no-objectives` to suppress task-title text. Treat the local monitor output as owner-private, particularly on remote terminals.

## Operational characteristics and failure handling

- **Two terminals:** start Astra One in one, ATLAS Monitor in another. Closing ATLAS Monitor does **not** stop active SDA work.
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
