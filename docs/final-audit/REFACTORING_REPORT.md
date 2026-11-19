# Refactoring and wrapper report

The audit was intentionally conservative. The generated catalog found 3,907 symbols across 347 source files: 903 functions, 2,436 methods, and 568 classes. Static analysis identified 227 single-call/pass-through patterns, but that pattern is not proof of an unnecessary wrapper.

## Actions completed

- Reused the existing FTS5 RepositoryIndex rather than introducing a second index abstraction.
- Changed native CLI health defaults from the historical Astra state path to ~/.local/state/archon.
- Changed native health reporting to inspect archon.service and archon.timer.
- Made the read-only monitor prefer the native ARCHON state path while retaining explicit Astra compatibility for historical databases.
- Added the bounded system-inventory API and four focused regression tests, including hardware/software/runtime-section and disk-capacity comparison.
- Added the bounded native control-plane executor with process fencing, durable control-marker admission, digest-only receipts, allowlisted read-only operations, and ten focused regression tests; domain-effect handlers remain explicitly unconfigured.
- Excluded only generated audit evidence and Serena cache directories from the bounded secret scanner; source, configuration, workflows, and deployment files remain scanned.

## Wrapper disposition

No wrapper was deleted. The 227 static candidates require caller and contract review; 551 symbols are in the legacy bootstrap and 481 are imported provenance. Public re-exports, authentication/authorization checks, error normalization, filesystem boundaries, migration ownership, and legacy compatibility were retained. Removing any of those without a separate compatibility receipt would reduce safety or provenance.

The remaining wrapper candidates are recorded in FUNCTION_CATALOG.json with callers, security signals, test references, and maintenance status. They are review candidates, not dead-code claims.

## Known compatibility boundary

The repository still contains the historical bootstrap and imported Astra source under bootstrap/astra-one and migration/imported. Those paths are preserved for provenance and rescue recovery; they are not imported by the native package when it is run with only PYTHONPATH=src. Full Astra retirement remains an approval-gated migration because the native unattended SDA/Guardian cutover has not been proven.
