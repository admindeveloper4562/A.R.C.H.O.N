# MIG-014 Verification — external Astra rescue and guarded self-update

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This candidate qualifies the existing external watchdog path. It does not
retire Astra One, delete its state, start an unattended service, publish to a
remote branch or change `main`.

## Acceptance identity

| Field | Value |
| --- | --- |
| Task | `MIG-014` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration base SHA | `a01435995415a0baf4d0d6bf0addd6cc243f6636` |
| Active controller candidate | `2ebb3ad294bf611bec22df5c3851532e25fe120a` |
| Last-known-good rollback SHA | `9f211667d137061701dc6d704bfaf351a205d2b9` |
| Upgrade batch | `ARCHON-OWNER-GATE-CLAIM-20261118` |
| Activation journal | `~/.local/state/archon-astra/upgrade-activations/ARCHON-OWNER-GATE-CLAIM-20261118.json` |
| Watchdog backup SHA-256 | `7b9fdcc7eefa4f4252c2129b923d254b1ee67b00576f556062d0afd0fc09632c` |

The external Astra source checkout, canonical SQLite database, integration
worktree, rejected candidates and rollback backup remain present. The
user-level Astra service is currently inactive and the timer is enabled; this
candidate does not claim unattended service liveness.

## Verified behavior

| Requirement | Evidence | Result |
| --- | --- | --- |
| Independent watchdog | `tools/astra_watchdog.py` is a separate fail-closed control plane with no worker/model imports | PASS |
| Tested upgrade only | Activation requires TESTED, BACKUP, CANARY and HEALTH checks | PASS |
| One-writer fencing | Watchdog uses the canonical lock and rejects active task work | PASS |
| Fast-forward-only activation | Candidate ancestry and clean integration checkout are checked | PASS |
| Database protection | SQLite backup uses the backup API and passes integrity check before activation | PASS |
| Rescue checkpoint | Activation journal records previous SHA, candidate SHA, backup path and digest | PASS |
| Rollback safety | Rollback test records a durable pending rollback without moving the pointer | PASS |
| STOP/PAUSE/quota | Activation refuses control markers; live check reports all clear without clearing markers | PASS |
| Failed activation recovery | Activation restores the previous pointer and records a failed journal before returning failure | PASS |
| Astra rescue retained | Previous integration commit, source checkout, state and backup remain available | PASS |
| Native SDA retirement | Not performed | NOT PERFORMED |

## Reproducible checks

The bounded checks run on this candidate's base were:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_astra_watchdog.py' -q
  3 tests passed

PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_guardian_*.py' -q
  66 tests passed

PYTHONPATH=bootstrap/astra-one python3 -m unittest discover \
  -s bootstrap/astra-one/tests -p 'test_supervisor_v3.py' -q
  24 tests passed
```

The live trusted-watchdog check returned SQLite integrity `ok`, integration
SHA `a01435995415a0baf4d0d6bf0addd6cc243f6636`, configured pointer switching,
and `STOP=false`, `PAUSE=false`, `PAUSED_QUOTA=false`.

Independent QC must review the exact candidate commit and the serialized
Merger must bind its final integration SHA before this parent is complete.
