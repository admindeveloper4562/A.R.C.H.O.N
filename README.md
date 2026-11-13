# ARCHON · AEGIS · ATLAS — JARVIS v2 Foundation

**Identity:** ARCHON is the main AI; AEGIS is the independent Guardian; ATLAS is the infrastructure, orchestration, five-worker SDA control plane and progress monitor. Astra One remains the external bootstrap builder. See [Identity contract](docs/architecture/IDENTITIES.md).

**Status: foundation seed, NOT a deployed/qualified v2 release.** This is the clean rebuild repository scaffold for the owner's ten-module JARVIS v2 architecture. Its external bootstrap builder is Astra One. Source reuse from [`personal-jarvis`](https://github.com/admindeveloper4562/personal-jarvis) is **selective, traceable, tested and reviewed**, not a bulk copy or direct PR merge.

**Modules:** 01 Core · 02 SDA · 03 Backend (includes Windows Ollama node) · 04 Runtime · 05 Research · 06 Quest/TWS · 07 World Information Center · 08 Finance (read-only Mira + paper trading) · 09 Guardian/Recovery · 10 Cloudflare Always-On Automation. Business remains archived/inactive.

## Independent terminal development monitor

ATLAS Monitor runs in a **second terminal**, reads actual Astra One or ATLAS SQLite state without writing, and never starts/controls the runner:

```bash
python3 tools/atlas_monitor.py --source astra --watch --interval 2
# or atlas-monitor --source astra --watch
```

See [ATLAS Monitor operations](docs/operations/ATLAS_TERMINAL_MONITOR.md).

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


## First private GitHub bootstrap and Codex background service

The empty repository target is `admindeveloper4562/A.R.C.H.O.N`. The all-in-one bootstrap source is included in `bootstrap/astra-one/` alongside the ARCHON/AEGIS/ATLAS foundation.

The owner runs `bash tools/archon_bootstrap.sh` **once** from a fresh extraction on Ubuntu after authenticating `gh` and `codex`. It checks the empty remote, verifies both test suites, creates one root commit on `main`, creates `develop` at the same SHA, clones a separate clean source checkout, imports and approves the SHA-pinned first-milestone architecture, enqueues exactly five bounded kickoff coding tasks, and enables a user-level `archon-astra.timer`/service.

The service runs Astra One with five Codex Luna Medium workers, network-disabled Docker QC, independent AI review and serial local integration. **It only pushes locally verified, fast-forward integration commits to `develop`**; it never pushes `main` or performs deployment. On conflict it refuses the push and sets `PAUSE`. No development happens when STOP/PAUSE/PAUSED_QUOTA exists. Subsequent work requires additional reviewed task batches or a separately qualified backlog scheduler; this first bootstrap does not silently enqueue all 247 tasks.

Observe a separate terminal using `python3 tools/atlas_monitor.py --source astra --db ~/.local/state/archon-astra/sda.sqlite3 --watch`. See `docs/operations/LINUX_ASTRA_SERVICE.md` for status, logs and stop procedures.

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
