# Astra One bootstrap focus — owner review required (M0/M1 only)

**Scope:** external Astra One qualification and the clean repository migration foundations. Full architecture remains `docs/architecture/JARVIS_V2_CONSOLIDATED.md`; the `architecture_sha256` below pins this exact source. This text is a bounded implementation focus, **not** an override to security policies or permission requirements.

**Full architecture SHA-256:** `8d61e949302b70386d4e1d4a668cc4abe8b76be9966c5efe4575bdf2ca558d73`.

## Identity overlay
ARCHON = main AI for Core intelligent decisions and Runtime conversations. AEGIS = Guardian local AI and independent recovery, while ATLAS = infrastructure, persistent queues, SDK/backend coordination, Cloudflare and the separate read-only terminal progress monitor. Astra One remains external SDA until certified handover. These are role identities over the ten modules, not three extra modules.

## Goal
Build and qualify a new private JARVIS v2 repository from a clean modular foundation while reusing carefully reviewed, pinned code from the old `admindeveloper4562/personal-jarvis` branch families. Do not copy old history as production state or merge all old branches.

## Ten active modules
1 Core, 2 SDA, 3 Backend including Windows local Ollama agent, 4 Runtime, 5 Research, 6 Quest/TWS with Aurelia, 7 World Information Center, 8 Finance (read-only Mira and paper trading), 9 Guardian, 10 Cloudflare Always-On. Business excluded from active modules.

## External builder
Astra One Linux uses normal authenticated Codex CLI, preferred `gpt-5.6-luna` medium with five bounded coding slots. Master is deterministic, review is independent, and Merger is serialized. STOP, PAUSE, quota limits, owner approval and state/effect receipts must persist. Never launch duplicate Masters on the same branch or SQLite database.

## First tasks
1. Read and test this new seed; check branch/commit CI policies and module scaffolding.
2. Validate old source refs and source candidate importer without executing imported files.
3. Review the old Workhorse v2 and the standalone Astra One implementation, choose one canonical queue controller, and implement tested adapters incrementally.
4. Establish P0 safety and SDA gates A-I in an actual Linux environment before promoting the v2 SDA.
5. Produce independent QC, documented rollback, Guardian external-watchdog design, and blue/green staging acceptance prior to self-hosting SDA.

## Guardian rule
Local Guardian AI reserves the **next idle compatible** model slot. Current bounded generations complete first; deterministic emergency STOP may be used only under preauthorized policy. Guardian cannot approve its own deploy/change or manage its own immutable watchdog.

## Rebuild boundary
`main` contains only accepted releases. `develop` is the serial integration branch. Feature branches use `<kind>/<module>/<TASK-ID>-<kebab-slug>`, commits `<type>(<scope>): <imperative summary> [TASK-ID]`. First accepted release tag is proposed `v2.0.0`, not this seed. Keep old JARVIS repo intact; no Business module; no live financial trading; no automatic Cloudflare production changes; no unapproved personal file deletion.

## Evidence and permissions
Real model/Docker/CI/host tests, source SHA, reviewers, task IDs, failure categories and outcomes are required for completion. Do not equate a draft PR or passing mock test with released functionality. This focus packet must be specifically approved before Astra import and no tasks automatically launch.
