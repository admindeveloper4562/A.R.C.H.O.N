# SDA-003 Verification — Codex model profiles

Task mode: `verification`
Source/integration base: `b488c7331628dfb20278658905a3e0218f9a5a84`
Observed at: `2026-11-15T17:23:43Z`
Independent QC and serialized Merger: pending for this candidate

## S01 — acceptance matrix

| Requirement | Observable check | Result |
| --- | --- | --- |
| Authenticated CLI | `codex --version` and `codex login status` succeed before model calls | PASS; `codex-cli 0.169.0` |
| Four profiles | Supervisor, worker, QC and Merger each receive the requested model and effort | PASS; four separate calls |
| Read-only smoke | Ephemeral call, `--sandbox read-only`, no tools, no source/task packet, no agents | PASS |
| Truthful success | JSONL completion event and exact bounded marker are both required | PASS |
| Unavailable alias | A denied model stops the sequence and does not fall back or run later roles | PASS; deterministic subprocess fixture |
| Safety controls | STOP, PAUSE, quota and lane markers stop before launching and remain untouched | PASS; deterministic tests |

## S02 — fixtures and scope

`tools/verify_codex_profiles.py` uses an empty temporary directory, explicit
OpenAI provider selection, the existing `codex_command()` contract, bounded
stdout/stderr capture and process-group termination. It does not open SQLite,
claim a task, create a worktree, write a candidate, or retain model text.

`tests/test_sda_003_profiles.py` uses bounded in-process fakes for success,
authentication denial, unavailable alias, quota, malformed events, tool
events, timeout and output-limit behavior. It contains no credentials or
private account data and is safe under the read-only Docker QC mount.

## S03 — execution evidence

Focused deterministic command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bootstrap/astra-one python3 -m unittest discover -s tests -p test_sda_003_profiles.py -v
```

Result: exit `0`, 7 tests passed.

Real authenticated smoke command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bootstrap/astra-one python3 tools/verify_codex_profiles.py --execute --home /home/r34p3r/.local/state/archon-astra --model gpt-5.6-luna --effort medium --timeout 120
```

Result: exit `0`, status `VERIFIED`. CLI `codex-cli 0.169.0`; authentication
was confirmed without retaining account output. Supervisor, worker, QC and
Merger each returned the required completion event and exact marker in
read-only mode. Per-call output hashes and event types are recorded in
`tools/SDA-003-EVIDENCE.json`.

## S04 — negative evidence

The focused suite rejects incomplete, duplicate and malformed JSONL, error and
tool events, wrong markers, unavailable aliases, quota errors, authentication
denial, active control markers, timeouts and bounded-output violations. The
unavailable-alias test proves the no-fallback rule and verifies that roles after
the denied role are not launched.

## S05 — result

The implementation satisfies the local and live CLI verification requirements.
It does not claim independent QC, Merger completion or parent completion;
those transitions remain owned by the canonical Master. The candidate must be
submitted with all five child evidence items, independently QC-tested, and
serialized through the Merger before SDA-003 can become verified complete.

The same candidate includes the tested `reopen_failed()` state transition: an
explicit reopen preserves the historical external case while restoring an
active batch member to `admitted`, preventing a resolved provider-quota failure
from being re-fenced by batch replenishment.
