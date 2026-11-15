# MIG-015 — ATLAS Monitor and identity manifest

## Implementation contract

`tools/atlas_monitor.py` is a standalone, read-only view over an existing
SQLite snapshot. It may inspect Astra One (`--source astra`) or the native
Core queue (`--source atlas`); `--source auto` detects either supported
schema. The monitor must not create a database, import the runner, invoke
Codex, execute Git commands, or write task state.

The monitor exposes recorded task counts and bounded task entries. Astra One
snapshots may additionally expose the current run's worker/repairer slot,
review and merge-ready states, recent events, and optional supervisor
telemetry. A slot is shown only when an event belongs to the task's current
run. Missing native telemetry is reported as unavailable, never inferred as
idle or healthy.

Task descriptions are hidden by default and all untrusted text is bounded and
redacted before rendering. The JSON snapshot is therefore an operational
view, not a copy of private task prompts or acceptance criteria.

## Identity contract

The approved display identities are role overlays on the existing ten module
IDs and database records:

- **ARCHON** — main AI and user-facing orchestration/runtime role.
- **AEGIS** — independent Guardian and recovery role.
- **ATLAS** — deterministic queue, backend, SDA infrastructure, automation,
  and read-only monitor role.
- **Astra One** — external bootstrap/rescue development stack.

`config/identities.json` is the machine-readable manifest. The names do not
rename `jarvis_v2`, task IDs, SQLite tables, or module IDs.

## Acceptance-to-test map

| Acceptance clause | Evidence |
| --- | --- |
| Astra snapshot renders task, worker, review, and merge state | `tests/test_monitor.py` Astra fixture and render assertions |
| Native Core snapshot is readable without runner control | `tests/test_monitor.py` native queue/CLI coverage |
| Monitor does not mutate the database | `tests/test_mig_015_acceptance.py` before/after database digest |
| ARCHON/AEGIS/ATLAS roles are present in config and operator docs | `tests/test_mig_015_acceptance.py` manifest and documentation assertions |

Live-host, process-heartbeat, and hardware evidence are outside this local
repository test contract and remain external verification gates.
