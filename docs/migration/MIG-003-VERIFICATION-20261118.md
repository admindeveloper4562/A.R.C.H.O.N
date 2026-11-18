# MIG-003 Verification — 2026-11-18

Candidate base: `bba514ed3d727e67b89f20fb65f6bf00d4902333`

The approved legacy checkout was read only. The importer was run first as a
dry-run and then with `--apply`; it performs create-only staging and does not
execute imported code or modify the legacy repository.

## Evidence

- Imported entries: 23.
- Provenance log: `migration/provenance/import-log.json`.
- Provenance-log SHA-256: `5ab2f924a7edae5c114c6b0570454d43c2ed746db8db83e5ea37d1e15e835aef`.
- Imported Python entries: 20; all parsed with `ast.parse` without execution.
- Non-Python imported entries remain staged data (Swift, TypeScript and SQL); no
  native Apple or production-service validation is claimed here.
- Source commits were pinned to the five approved legacy refs:
  `79a1a7b19630062bb6363244335beac2f585b262`,
  `14080d9a897494b17fad89dd6a02f942348d1fb2`,
  `4f37407ec177c30f9efaee2746c0b454a63931e2`,
  `351f713db748afa542806819e6ed27e4b715be22`, and
  `8ba98707b2bffb3a04c49b3022db983239a267e6`.

## Checks

- `python3 -m unittest discover -s tests -p 'test_importer.py'`: 2 passed.
- `python3 -m unittest discover -s tests -p 'test_migration_guardrails.py'`: 4 passed.
- Full project and Astra suites are run by the trusted upgrade controller and
  are bound to the candidate SHA before activation.

This document records migration evidence only. It does not claim production
deployment, native-device acceptance, hosted CI, or remote publication.
