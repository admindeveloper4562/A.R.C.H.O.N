# ARCHON · AEGIS · ATLAS — JARVIS v2 Foundation

**Identity:** ARCHON is the main AI; AEGIS is the independent Guardian; ATLAS is the infrastructure and orchestration layer. Astra One is legacy development infrastructure and is not required by the native package. See [Identity contract](docs/architecture/IDENTITIES.md).

**Status: Linux local scope audited, but final release is CONDITIONAL.** Native source, local regression, security, persistence, indexing, and host-inventory checks are documented under docs/final-audit. Source reuse from personal-jarvis is selective, traceable, tested and reviewed, not a bulk copy or direct PR merge.

**Modules:** 01 Core · 02 SDA · 03 Backend (includes Windows Ollama node) · 04 Runtime · 05 Research · 06 Quest/TWS · 07 World Information Center · 08 Finance (read-only Mira + paper trading) · 09 Guardian/Recovery · 10 Cloudflare Always-On Automation. Business remains archived/inactive.

## Independent terminal development monitor

ATLAS Monitor runs in a **second terminal**, reads an existing ARCHON/ATLAS SQLite state without writing, and never starts or controls a runner:

```bash
python3 tools/atlas_monitor.py --source auto --db ~/.local/state/archon/atlas.sqlite3 --watch --interval 2
# or atlas-monitor --source auto --db ~/.local/state/archon/atlas.sqlite3 --watch
```

See [ATLAS Monitor operations](docs/operations/ATLAS_TERMINAL_MONITOR.md).

## Native controller

The native controller owns one bounded queue cycle without Astra imports. Its built-in executor handles only read-only control-plane observations (`native_capabilities`, `module_health`, `runtime_health`, `inventory_digest`, `queue_status`, `database_inspect`, `sda_handoff_status`, and `guardian_readiness`); domain-effect operations fail closed until separately reviewed handlers are supplied:

```bash
PYTHONPATH=src python3 -m jarvis_v2.native_controller --once --state ~/.local/state/archon
```

The reviewed user-service candidate is `infra/systemd/archon.service`; it is not enabled by this audit.

## Bootstrap

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 -m jarvis_v2.cli modules
python3 -m jarvis_v2.cli health
python3 -m jarvis_v2.cli guardian-gate examples/release-candidate.example.json
```

Nothing starts in the background. No model requests, deployments, commits, pushes, database alterations, production or finance actions are performed by these commands. Test fixtures use temporary local paths.

To commit the complete foundation into the **existing empty private** GitHub repository, read [bootstrap instructions](docs/engineering/REPOSITORY_BOOTSTRAP.md), verify the downloaded package, and run `bash tools/archon_bootstrap.sh` locally with authenticated GitHub CLI. GitHub creation is not implied by this ZIP.

To inspect code reuse, run `python3 tools/import_legacy.py --repo "$HOME/Projects/personal-jarvis"` (dry-run); after reviewing, add `--apply`. Imported source goes only to `migration/imported/` and is NOT automatically executable, deployed or promoted. See [migration matrix](docs/migration/SOURCE_REUSE_MAP.md).


## Historical Astra bootstrap and Codex background service

The historical empty-repository bootstrap target was admindeveloper4562/A.R.C.H.O.N. The archived bootstrap source remains under bootstrap/astra-one/ for provenance and rescue recovery; it is not required for native runtime startup.

The historical owner bootstrap ran bash tools/archon_bootstrap.sh with authenticated GitHub and Codex tooling. It is retained as archival/recovery procedure, not as native runtime startup.

The historical service ran Astra One with bounded workers and serial local integration. Preserve it only as a separately controlled recovery path; do not treat its state as native runtime state.

Native runtime state is created under ~/.local/state/archon. Historical Astra state remains under ~/.local/state/archon-astra until the owner approves retirement. See docs/operations/ARCHON_NATIVE_RUNTIME.md for the native status boundary.

## Source of truth

- [ARCHON / AEGIS / ATLAS identities](docs/architecture/IDENTITIES.md)
- [ATLAS independent terminal monitor](docs/operations/ATLAS_TERMINAL_MONITOR.md)
- [Final architecture](docs/architecture/JARVIS_V2_CONSOLIDATED.md)
- [Agent constraints](AGENTS.md) and [Security](SECURITY.md)
- [Branch / commit rules](docs/engineering/BRANCH_COMMIT_POLICY.md)
- [Workspace directory ownership](docs/engineering/REPO_STRUCTURE.md)
- [First Astra Linux runbook](docs/tasks/ASTRA_LINUX_SETUP.md)
- [Handbook](CODING_HANDBOOK.md)
- [Source mapping](docs/migration/SOURCE_REUSE_MAP.md)
- [Astra One to native SDA handover](docs/migration/ASTRA_TO_NATIVE_SDA.md)
- [Guardian upgrade and rollback](docs/operations/GUARDIAN_RELEASE.md)

## Maturity

This seed implements the **first deterministic slice** only: module manifest, task/event state, non-preemptive Guardian scheduling policy, read-only deployment candidacy checks, and migration intake. The 247-task program remains in the [planning PR](https://github.com/admindeveloper4562/personal-jarvis/pull/18); task state is *not* carried forward as completed merely because a file exists on a draft branch.

**Interrupted install:** If GitHub main/develop were pushed but a later CLI, Docker or systemd check failed, use `bash tools/archon_resume.sh` after fixing the prerequisite; do not rerun the one-root-commit bootstrap.
