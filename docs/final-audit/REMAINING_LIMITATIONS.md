# Remaining limitations

1. The canonical SHA is local-only; remote integration/develop is still 75582dbf and publication was not performed.
2. Native ARCHON imports and local contracts pass, but a complete native unattended SDA/AEGIS cutover with one-writer fencing, crash recovery, trusted watchdog activation, and rollback soak is not evidenced.
3. The legacy Astra timer remains enabled and the legacy monitor remains running; its latest transient service run exited 0 but logged incompatible `--json` and `--watch` arguments before completing. Retirement requires a controlled owner-approved transition.
4. Seven parent tasks remain archived/deferred. They are visible in the historical ledger and are not counted as completed.
5. pytest, hosted CI, the Codex Security diff-scan artifact, Windows hardware/Ollama, iOS/macOS, Blender execution, live feeds, external model providers, Cloudflare operations, real finance, and real communications were not run or verified.
6. The filesystem inventory is bounded and does not claim complete root visibility; permission-denied paths, virtual filesystems, mount boundaries, and truncation are recorded.
7. Cleanup is dry-run only. No old clone, worktree, backup, image, service, or database was removed.
8. The code catalog reports 6,800 unresolved static references and 1,733 suspected unused paths. These are heuristic and require caller-aware review; they are not defects by themselves.
9. Independent bounded QC covered the committed implementation/evidence tree but skipped the full suite and long scans; this final documentation-only refresh is not separately re-QC'd.
