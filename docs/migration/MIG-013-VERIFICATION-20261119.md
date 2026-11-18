# MIG-013 Verification — isolated legacy provenance and guarded migration

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This candidate verifies the existing create-only migration staging and prepares
the next guarded handoff. It does **not** switch the active SDA, stop Astra
One, publish to GitHub, modify `main`, execute legacy code, or retire the
legacy rescue path.

## Pinned identities

| Field | Value |
| --- | --- |
| Task | `MIG-013` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Destination base SHA | `dc91a68bf51f90f27588d2bf27f3779740dad95c` |
| Integration checkout | `/home/r34p3r/.local/state/archon-astra/integration-reconciled-20261114` |
| Legacy source origin | `https://github.com/admindeveloper4562/personal-jarvis.git` |
| Legacy source checkout | `/home/r34p3r/Projects/personal-jarvis` |
| Legacy source HEAD | `b5168028433a448755a8fdb5d9cb1180f513250e` |
| Manifest SHA-256 | `ebb23c5a55c647ef62958e11a6eee5697f0a4e5f1520424bfd9fb857cdd4900f` |
| Provenance log SHA-256 | `5ab2f924a7edae5c114c6b0570454d43c2ed746db8db83e5ea37d1e15e835aef` |

The source checkout contained pre-existing uncommitted deletions. The
verification read only pinned remote-ref objects and did not alter that
checkout.

## Provenance inventory

The existing ATLAS provenance log contains 23 create-only entries:

| Area | Entries |
| --- | ---: |
| Core | 2 |
| Backend | 4 |
| Runtime | 5 |
| SDA | 3 |
| Guardian | 2 |
| TWS | 4 |
| Automation | 3 |

All five pinned source commits remain available as Git objects:

- `79a1a7b19630062bb6363244335beac2f585b262` — 12 entries.
- `14080d9a897494b17fad89dd6a02f942348d1fb2` — 3 entries.
- `4f37407ec177c30f9efaee2746c0b454a63931e2` — 1 entry.
- `351f713db748afa542806819e6ed27e4b715be22` — 4 entries.
- `8ba98707b2bffb3a04c49b3022db983239a267e6` — 3 entries.

The current `ARCHON-astra-source` checkout is not a valid legacy source for
this operation: its origin is the ARCHON repository. The importer rejected it
before reading any destination file. Using the preserved `personal-jarvis`
checkout passed the origin check.

## Dry-run and existing staging result

The create-only importer was run against the approved legacy origin. It
refused to apply because all requested target paths already exist in the
destination. This is the expected fail-closed result for an already-staged
candidate; no destination writes occurred.

The pinned-blob comparison then checked every provenance-log entry against its
recorded source commit and staged target:

- 23 source commits/blob records were present.
- 20 targets matched source bytes exactly.
- 3 targets differ only by line-ending normalization (legacy CRLF versus
  staged LF):
  `migration/imported/automation/cloudflare/src/index.ts`,
  `migration/imported/automation/cloudflare/schema.sql`, and
  `migration/imported/automation/windows/jarvis_queue_worker.py`.
- The provenance log's recorded source blob hashes match the pinned Git
  objects for all 23 entries.
- Writes performed: `0`.

The three normalized files are retained as existing historical staging; they
are not overwritten in this candidate because the importer is create-only.
Their source commit/blob identity and normalization are explicit review
evidence rather than a fabricated exact-byte match.

## Safety and rollback boundary

| Check | Result |
| --- | --- |
| One canonical Master / SQLite integrity | Verified by the Master; integrity `ok` |
| Active integration checkpoint | `dc91a68bf51f90f27588d2bf27f3779740dad95c` |
| Legacy source writes | None |
| Destination writes | None |
| Legacy execution | None |
| STOP/PAUSE/quota controls | Preserved; no marker is cleared |
| Active SDA switch | Not performed |
| Astra One rescue path | Preserved |
| Rollback target | Previous verified integration checkpoints remain available to the trusted watchdog |

The existing migration guardrail, compatibility, checkpoint and watchdog test
suites provide the disposable dry-run, collision, provenance, restore and
rollback checks. Independent QC must review this exact candidate and bind the
results to its final commit SHA before the Master can record child receipts.

## Remaining boundary

MIG-013 is a reversible migration candidate only. A future native-SDA
activation or Astra retirement remains a separate owner-authorized deployment
decision and is not implied by this report.
