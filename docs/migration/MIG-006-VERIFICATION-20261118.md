# MIG-006 Verification — TWS/Aurelia and Cloudflare/Windows staging

Candidate base: `024181b8aaf8f406d62c366bb7cd1fc7170a084e`.

This is a bounded provenance and acceptance-gap audit. It does not execute
imported legacy code, deploy Cloudflare resources, claim Windows hardware
evidence, or claim Apple-native validation.

## Provenance

- Import log: `migration/provenance/import-log.json`.
- Import-log SHA-256:
  `5ab2f924a7edae5c114c6b0570454d43c2ed746db8db83e5ea37d1e15e835aef`.
- Selected entries: 7 — four TWS/Aurelia entries and three
  Cloudflare/Windows automation entries.
- TWS source ref/commit:
  `feature/twelve-winged-m001` /
  `351f713db748afa542806819e6ed27e4b715be22`.
- Automation source ref/commit:
  `feature/cloudflare-overnight-inference-coordinator-20261112` /
  `8ba98707b2bffb3a04c49b3022db983239a267e6`.
- The source checkout was read-only. No imported source was executed.

## Staged-file verification

The four TWS files match their pinned source bytes and logged SHA-256 values.
The three automation files have the same text content and differ only in
terminal line endings: the source uses CRLF and the staged copy uses LF. That
normalization is recorded here and is not treated as byte identity.

| Area | Staged target | Source SHA-256 | Staged SHA-256 | Result |
| --- | --- | --- | --- | --- |
| TWS | `migration/imported/tws/engine.py` | `8b09c63d80c25b384852ff70c95f1c8c9392ece6b9c24d661856cc41f31e5091` | same | PASS |
| TWS | `migration/imported/tws/evidence.py` | `55c299cae45142785fd12f41f2f78d19881d003b91d53383b7609c15041f5c08` | same | PASS |
| TWS | `migration/imported/tws/aurelia3d/build_portable.py` | `75d33780a99c936dbf3709fa6e10443e14c6791a8dd5ec15b024f29ae276d4ad` | same | PASS |
| TWS | `migration/imported/tws/ios/Aurelia3DSceneView.swift` | `33f164c1eb5480b096bf1ffe964d422b2f73f5551bc098d55d9e9a34e81f5ceb` | same | PASS |
| Automation | `migration/imported/automation/cloudflare/src/index.ts` | `21ebe06be2009718189198efa8f34fb713b30d67c7a507cda5c1a9bded1aa901` | `17a1bf034348e6498cb57a86b34c8bb13c6ee84b1f8dde39ffe046f993541459` | LF-normalized |
| Automation | `migration/imported/automation/cloudflare/schema.sql` | `bc4db8ca145a70d9706e8e4526c943a576beea63b4d9120bb42957846c248ac8` | `167b85746543cc68b3df14193023eff620722568dea4e46873ea30420c9a4c27` | LF-normalized |
| Automation | `migration/imported/automation/windows/jarvis_queue_worker.py` | `e8d5d310e08f8d5998eb196d5a9dd106e27015f95b87bf70fd4c19dc4cffe16d` | `dd0175815108a387d8c19728d89a7861a1b74b04720ef1be01465227ae596961` | LF-normalized |

All three normalized files compare equal after newline normalization. The
source SHA and source blob recorded in the import log remain the provenance
authority.

## Acceptance and dependency gaps

| Area | Verified evidence | Remaining gate |
| --- | --- | --- |
| TWS-011 | Blender 5.3.0 generated and reopened the editable `.blend`; the accepted candidate contains 8 meshes, 1 armature and 8 modifiers. USDZ SHA-256 is `30b3e13de9b42091c4ce432c63e51a1fe893bc86da3d5c2fe23ff8124012633d`. | No Apple SceneKit/Xcode/device claim is made. The current Master records TWS-011 completed only for its accepted evidence packet. |
| TWS-012 | Visual QA evidence has 24 views; manifest SHA-256 `5f18d0e3a18c2cfbab8cacbe01f9a4349775c9a8b85addf5e0df8a0bfa6e9cf6`; `motion_present=false`; artist review not run. | `artist_review_required`; remains blocked. Linux output cannot satisfy artist/device acceptance. |
| TWS-013–016 | Dependency states are preserved in SQLite and no native macOS/iOS run is fabricated. | Dependency-propagated blocked state; no eligible implementation claim. |
| TWS-019–020 | No physical iPhone or Apple-native release evidence was found. | Device/native acceptance remains unavailable; no retry is consumed. |
| Cloudflare automation | The configured monitor has a verified D1 binding and its existing REL-005 smoke test passed. No token value is stored in this report. | No additional production deployment or secret inspection is part of MIG-006. |
| Windows automation | `jarvis_queue_worker.py` is staged and parses with `ast.parse` without execution. | WIN-002 remains `device_unavailable`; Linux cannot replace Windows/Ollama measurements. |

## Deterministic checks

- The seven selected staged files were checked against the import log; all
  sizes and hashes matched exactly or were classified as newline-normalized.
- All imported Python files in the selected set parsed with `ast.parse`; no
  Python module was imported or executed.
- Existing importer and migration guardrail tests remain the governing checks;
  the candidate is submitted for the full independent QC/Merger pipeline.
- The source and integration worktrees remain separate and the legacy source
  checkout remains unmodified.

## Decision

MIG-006 records the provenance, staged-file identity and actual TWS,
Cloudflare and Windows acceptance gaps. It does not waive TWS-012 artist
review, Apple/iOS/device requirements, or WIN-002 Windows/Ollama evidence.
Those tasks must remain truthfully blocked until their real prerequisites are
available. No additional TWS retry or Cloudflare deployment is justified by
this audit.
