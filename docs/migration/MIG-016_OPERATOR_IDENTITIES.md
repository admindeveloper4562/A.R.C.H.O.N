# MIG-016 — operator identity overlay for migration intake

## Implementation contract

The legacy importer is an ATLAS-operated, reference-only intake boundary. Its
CLI description, preview, and provenance receipt identify **ATLAS** as the
deterministic migration operator. Imported source is still staged under
`migration/imported/` and remains unreviewed; it is never executed or promoted
by the importer.

The approved identity overlay is:

| Operator surface | Approved identity | Compatibility identifiers retained |
| --- | --- | --- |
| Migration intake and provenance | **ATLAS** | `jarvis-v2.legacy-import/1`, `jarvis-v2.legacy-provenance/1` |
| Main AI and runtime documentation | **ARCHON** | `jarvis_v2`, legacy `JARVIS` references |
| Guardian and recovery documentation | **AEGIS** | legacy `Guardian` references |
| Bootstrap/rescue development stack | **Astra One** | legacy `astra-one` paths and source provenance |

This is a display and operator contract, not a data migration. The ten stable
module IDs, task IDs, SQLite table names, source paths, Git refs, and provenance
records are not renamed. Deprecated names remain documented so old records and
source references can be interpreted without replacing them.

## Acceptance-to-test map

| Acceptance clause | Evidence |
| --- | --- |
| Ten module IDs remain unchanged | `tests/test_mig_016_identity.py` checks the existing module manifest and migration areas |
| CLI/provenance use approved operator identity | `tests/test_mig_016_identity.py` checks `ATLAS` in dry-run and applied receipts |
| Deprecated names remain compatibility-only | `tests/test_mig_016_identity.py` checks this contract and the unchanged legacy schemas |
| No database records are rewritten | The importer has no database writer; the test uses a SQLite fixture and verifies its digest |

## Safety and compatibility

The importer remains create-only, source-pinned, dry-run by default, and
collision-safe. `operator_identity` is additive metadata. Consumers that only
read the existing `entries` fields continue to work, while operators can
distinguish ATLAS intake receipts from legacy source naming.
