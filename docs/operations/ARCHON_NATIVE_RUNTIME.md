# Native ARCHON runtime

The canonical source checkout is $ARCHON_HOME/dev/A.R.C.H.O.N. Native runtime state is kept under ~/.local/state/archon:

- runtime.sqlite3: empty module-owned Backend storage after migrations
- atlas.sqlite3: empty native queue schema
- code_index.sqlite3: provenance-bound FTS5 index
- host_inventory.json: private metadata-only host inventory
- logs, cache, run: empty ARCHON-owned directories

The native package can import and run its local contracts with only the repository src directory on PYTHONPATH. The health CLI defaults to this state root, and the read-only ATLAS monitor prefers its database before historical Astra paths.
The native deterministic controller is available as `PYTHONPATH=src python3 -m jarvis_v2.native_controller --once` or `archon-native-controller --watch`. It owns a process-level lock under `~/.local/state/archon/run/`, honors STOP/PAUSE/PAUSED_QUOTA markers and durable queue controls, and uses a built-in read-only control-plane executor for `native_capabilities`, `module_health`, `runtime_health`, `inventory_digest`, `queue_status`, `database_inspect`, `sda_handoff_status`, and `guardian_readiness`. Database inspection is restricted to named native databases and query-only access. SDA and Guardian probes report readiness without claiming ownership or switching routes. Domain-effect operations remain unsupported and fail closed until separately reviewed handlers, exact owner approval transport, and the independent trusted watchdog are supplied.

The historical ~/.local/state/archon-astra state is not copied into native runtime. Its timer and monitor remain separate until a verified native SDA/AEGIS cutover, watchdog soak, rollback test, and explicit owner-approved retirement transition are complete.

Safe local checks:

    PYTHONPATH=src python3 -m jarvis_v2.cli modules
    PYTHONPATH=src python3 -m jarvis_v2.cli identities
    PYTHONPATH=src python3 tools/atlas_monitor.py --source atlas --db ~/.local/state/archon/atlas.sqlite3 --json

`infra/systemd/archon.service` is a reviewed native unit candidate. It is not installed or enabled by this audit; service activation remains gated on native recovery/watchdog qualification and owner-approved Astra retirement.
