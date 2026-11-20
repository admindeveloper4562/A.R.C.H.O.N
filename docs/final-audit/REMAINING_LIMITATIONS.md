# Remaining limitations

1. The final canonical feature SHA `2fec1e3` is published and matches its remote feature ref; `main` remains unchanged and remote `develop` remains at `75582db`.
2. Native ARCHON imports and local contracts pass, but a complete native unattended SDA/AEGIS cutover with one-writer fencing, crash recovery, trusted watchdog activation, and rollback soak is not evidenced.
3. The legacy Astra timer/service are disabled or absent and no Astra process remains. Historical state/worktrees are retained; native unattended recovery, trusted watchdog activation, and rollback soak remain unproven.
4. Seven parent tasks remain archived/deferred. They are visible in the historical ledger and are not counted as completed.
5. pytest, hosted CI, the Codex Security diff-scan artifact, Windows hardware/Ollama, iOS/macOS, Blender execution, live feeds, external model providers, Cloudflare operations, real finance, and real communications were not run or verified.
6. The filesystem inventory is bounded and does not claim complete root visibility; permission-denied paths, virtual filesystems, mount boundaries, and truncation are recorded.
7. The exact owner-approved cleanup batch reclaimed 2,838,614,016 bytes. Old clones, unique worktrees, the historical database, final-audit checkpoint, and native reset quarantine remain because they were not individually proven disposable.
8. The code catalog reports 6,800 unresolved static references and 1,733 suspected unused paths. These are heuristic and require caller-aware review; they are not defects by themselves.
9. Independent bounded QC covers documentation-only ancestor `1c27e22` and implementation ancestor `4149c1d` with focused native/inventory checks; the exact final checkout passed 590 tests, but no separate independent receipt was generated for the docs-only final SHA and no cutover was approved.
