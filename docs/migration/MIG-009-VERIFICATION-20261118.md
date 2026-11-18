# MIG-009 Verification — fenced staging redeployment and rollback

Candidate base: `61045aa1d75dbd4ce98b64e4390c393c06e4bb06`.

Acceptance: **One writer fenced; canary, health and failed-release rollback
demonstrated.**

The verification uses the existing Guardian cutover/fencing, health, release,
rollback and external watchdog components. It uses disposable Git repositories
and SQLite fixtures from the tests. It does not switch a production route,
modify `main`, install a service, or deploy a live Guardian.

## Staging sequence

1. Build a candidate manifest with a SHA-256 artifact, candidate/base commit
   IDs, last-known-good digest, closed route gate and bounded evidence refs.
2. Inspect the candidate without changing the route. Missing evidence, changed
   artifacts and an active route are rejected.
3. Verify component/state schema compatibility, healthy readiness, rollback
   readiness and explicit capacity.
4. Acquire one writer lease and hand it to the standby. The generation change
   makes the old lease stale; a second writer cannot acquire authority.
5. Run the watchdog fast-forward activation fixture. It records the candidate
   and integration checkpoint only after the required checks and backup pass.
6. Inject a failed/unhealthy canary and select the last-known-good artifact.
   Restore is staged with the failed candidate and state checkpoint preserved.

The test harness is intentionally disposable. It proves the control decisions
and state transitions without claiming a real production deployment or native
device soak.

## Acceptance matrix

| Clause | Evidence | Result |
| --- | --- | --- |
| One writer fenced | `WriterFence` acquire/handoff tests and `CutoverCoordinator` tests reject stale leases and preserve one authority. | PASS |
| Candidate canary | `guardian.release.inspect_canary` checks artifact digest, Git IDs, evidence refs, closed route and last-known-good hash. | PASS |
| Health gate | `GuardianHealthEvaluator` and cutover tests require dependency-checked healthy readiness and explicit capacity. | PASS |
| Failed-release rollback | `select_last_known_good`/`restore_last_known_good` and watchdog rollback tests restore the healthy artifact, preserve state and retain the failed candidate. | PASS |
| Control markers | Fault-injection, standby and watchdog tests refuse recovery/activation while STOP, PAUSE or PAUSED_QUOTA is present. | PASS |
| No model self-authorization | Manifest inspection is read-only; owner/QC evidence remains an external Master gate and no route switch occurs in inspection. | PASS |

## Commands and results

- `PYTHONPATH=src python3 -m unittest discover -s tests -p
  'test_guardian_*.py'`: 66 passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p
  'test_astra_watchdog.py'`: 3 passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`:
  522 passed.
- `PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'` in
  `bootstrap/astra-one`: 141 passed.
- `python3 tools/verify_foundation.py`: passed — ten modules,
  ARCHON/AEGIS/ATLAS identities, independent monitor and Business excluded.
- `git diff --check`: passed.

## Failure and rollback evidence

- A dirty integration worktree, active control marker, missing backup, stale
  checkpoint, non-fast-forward candidate or active task prevents activation.
- A second writer acquisition fails while the first lease is live.
- After handoff, the former lease fails closed as stale.
- A healthy canary cannot trigger rollback.
- A changed last-known-good artifact or unsafe rollback path is rejected.
- The watchdog records a pending rollback before pointer movement and retains
  the failed candidate and database backup.

## Limits

This is a local, disposable staging qualification. It does not claim hosted
CI, production blue/green routing, physical-device acceptance, signed release
publication or native SDA cutover. Those gates remain separate and require
their own evidence and authorization.
