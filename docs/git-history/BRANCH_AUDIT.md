# ARCHON branch audit

Source commit under audit: 4149c1d75eee24880bfacd819342f9c21d05d51a
Latest local evidence overlay: 0d6658b0aa2449c4071c0ca05ddda0aad3609bd2

Local branches: 1
Remote-tracking branches: 427
Tags: 0
Refs whose tips are ancestors of target: 118

No branch or object was deleted. The target has no configured upstream, and remote publication of the target SHA is unverified.

GitHub direct verification (2026-11-20): main is 5227b91d2725bf4be4336a5ad26189fdf1034704; develop and feature/astra-linux-integration-c799784769 are both 75582dbf48057e3d5b0e7cf4acfdba2386acfcff. The source candidate and local evidence overlays are not present on those refs. The source candidate is 36 commits ahead; the latest local evidence overlay is 38 commits ahead and 0 behind.

## Selected refs

| Ref | SHA | Subject | Relation to target |
| --- | --- | --- | --- |
| refs/heads/feature/astra-linux-integration-c799784769 | 0d6658b0aa2449c4071c0ca05ddda0aad3609bd2 | docs(audit): bind independent QC and native gaps | latest local evidence overlay |
| source commit under audit | 4149c1d75eee24880bfacd819342f9c21d05d51a | feat(native): qualify bounded probes and resumable inventory | source candidate |
| refs/remotes/origin/main | 5227b91d2725bf4be4336a5ad26189fdf1034704 | chore(repo): establish ARCHON foundation and Astra One [MIG-001] | ancestor |
| refs/remotes/origin/develop | 75582dbf48057e3d5b0e7cf4acfdba2386acfcff | fix(sda): complete integration tree synchronization | ancestor |
| refs/remotes/origin/feature/astra-linux-integration-c799784769 | 75582dbf48057e3d5b0e7cf4acfdba2386acfcff | fix(sda): complete integration tree synchronization | ancestor |

## Preservation notes

- The conflicted owner-approval-signatures worktree and all unique candidate refs remain preserved.
- The source clone contains 427 remote-tracking refs and 758 reachable commits. The local audit target is not present on the verified GitHub refs. The generated machine index intentionally snapshots the latest parent evidence commit; a later final binding commit may be described separately because a commit cannot contain its own post-commit SHA.
- No force-push, reset, reflog deletion, garbage collection, or history rewrite was performed.
