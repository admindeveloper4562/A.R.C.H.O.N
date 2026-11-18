# MIG-005 Verification — Astra One / Workhorse Reconciliation

Candidate base: `bc3e9b4bb1655c8e7bea884f9e1b3e78011e2a4a`.

This is an audit of the historical Workhorse contract against the current
Astra One control plane. It does not revive the retired coding-worker model or
start a second Master.

## Pinned historical evidence

- Legacy repository: `admindeveloper4562/personal-jarvis`.
- Workhorse v2 source ref: `4f37407ec177c30f9efaee2746c0b454a63931e2`.
- `scripts/codex_workhorse_v2.py` blob SHA-1:
  `22437f72f618ac5eaba247bf824851d06014d1b8`.
- Workhorse context source blob SHA-1:
  `81c48a2356dab596e76afe359a22fd61e3336941`.
- SDA integrity source was inspected at the expanded-architecture ref
  `14080d9a897494b17fad89dd6a02f942348d1fb2`, blob
  `9bece2ea03bf021225445300fcb7bd9dda6c72e8`.
- The legacy checkout was read only; its pre-existing dirty/deleted build
  artifacts and session file were not changed.

The historical Workhorse declares five worker capacity, role-specific models,
durable task states, independent QC and a serialized merger. That is retained
as provenance, not as permission to launch legacy workers.

## Current Astra One reconciliation

| Requirement | Current evidence | Result |
|---|---|---|
| One authoritative queue/Master | Canonical SQLite plus `master.lock`; claims and transitions are fenced under the Master lock. | PASS |
| Isolated implementation worktrees | `builder-claim` creates one task worktree from the canonical integration SHA; `builder-submit` checks lease, base, candidate and exact changed-file manifest. | PASS |
| Independent QC | `process_candidate_queue` accepts Main Codex candidates only, requires the Docker image and performs deterministic validation before review. | PASS |
| Serialized Merger | Approved candidates enter the single merge path; MIG-003 and MIG-004 were independently QC-approved and integrated at `784a2a0d` and `bc3e9b4b`. | PASS |
| Five-worker historical compatibility | `run_concurrent` and the qualification tests retain the two-lane/worker-capacity compatibility surface. | PASS FOR COMPATIBILITY TESTS |
| Live ordinary coding dispatch | The `run` command refuses with `autonomous_coding_dispatch_disabled_use_builder_claim`; the batch service runs QC/Merger only. | PASS — intentionally disabled |

The current owner-approved authority model is one Main Codex builder. W1–W5
remain historical/logical capacity records; no claim is made that five
authenticated coding processes are currently running. This avoids silently
re-enabling the superseded Workhorse architecture.

## Verification

- ARCHON suite at this candidate: 522 tests passed.
- Astra One suite at this candidate: 177 tests passed.
- Current integration SHA is checked by the Master before QC/Merger work.
- STOP, PAUSE and quota controls remain enforced; the batch service does not
  clear markers or publish to remote `develop`.
- No legacy source was imported into the live Python package or executed.

## Decision

The current Astra One implementation preserves the important Workhorse
properties—durable ownership, isolated candidates, independent QC and one
serialized integrator—while deliberately replacing autonomous feature-code
dispatch with the owner-approved Main Codex handoff. Five-worker concurrent
execution remains a tested compatibility path, not an active authority.

No production deployment, remote publication, native SDA cutover or legacy
repository mutation is claimed.
