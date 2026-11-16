# BACK-019 — Service inventory, status, metrics and health audit

**Task:** BACK-019
**Execution mode:** `audit`
**Parent objective:** Implement service inventory, status, metrics and health API
**Acceptance:** Each component reports honest readiness/liveness, version and resource use
**Audited baseline:** `50725ecc0878e0fe6fc47f1c0eac99e56834d7ca`
**Audit date:** 2026-11-17 (Asia/Bangkok)

## Scope and method

This is an evidence and decision record, not a runtime implementation. The
inspection was read-only and did not start a service, contact a health
endpoint, modify the canonical SQLite database, or change an inspected source.

Sources inspected at the pinned baseline:

| Source | Evidence |
| --- | --- |
| `src/jarvis_v2/cli.py` | `health` returns a fixed `seed_only` object; it does not inspect a process, database, dependency, version, or resource provider. |
| `src/jarvis_v2/__init__.py` | Package version is `0.0.3`. |
| `src/jarvis_v2/backend/module_manifest.py` | Ten stable module IDs, dependencies, health labels and module-local read/health scopes are validated without I/O. |
| `src/jarvis_v2/core/registry.py` | Module manifests are loaded and validated; the registry exposes identity and permission checks, not runtime health. |
| `config/modules.json` | SHA-256 `72691a65522d50751785f223611b3df51ad0f880b106f8705c129bc4c52ca306`; ten modules, Business excluded. |
| `config/identities.json` | SHA-256 `00045b6801d06c278a98a12e26c44f80490916fb8738c8f86de727b26f26bc79`; identity overlay and module ownership. |
| `src/jarvis_v2/monitor.py` | Read-only SQLite snapshot; records task/run state and explicitly labels liveness as unconfirmed. |
| `src/jarvis_v2/monitor_supervision.py` | Read-only persisted supervisor, failure and batch telemetry; it never probes services or starts workers. |
| `docs/operations/ATLAS_TERMINAL_MONITOR.md` | Monitor contract requires explicit persisted heartbeat evidence and forbids inference from missing observations. |

The live read-only ATLAS snapshot at audit time reported Astra schema
`Astra One Linux v0.3.0`, source SHA `43c8db7de8a5f0277a7db23379019d05f2edd2c6`,
integration SHA `50725ecc0878e0fe6fc47f1c0eac99e56834d7ca`, and no control
markers. Its counts include the currently leased audit task; project-specific
counts remain authoritative in the Master ledger. This snapshot is evidence of
recorded state, not proof that a component process is alive.

## Findings matrix

| Acceptance clause | Current evidence | Finding |
| --- | --- | --- |
| Service inventory | `ModuleRegistry` and `config/modules.json` identify ten modules and dependencies. | Identity inventory exists; no runtime instance inventory, endpoint, process identity or artifact digest is reported. |
| Honest readiness | `cli health` returns static `seed_only`; manifest validation is pure. | Not implemented. A static `deployed: false` response is honest for the seed, but cannot report deployed readiness. |
| Honest liveness | Monitor documentation says recorded rows are not process liveness; no persisted heartbeat contract was found. | Not implemented. Missing observations must remain `unknown`, not `healthy` or `idle`. |
| Version | `jarvis_v2.__version__ == 0.0.3`; Astra version is recorded in SQLite settings. | Package/controller version surfaces exist, but component instance versions are not bound to health observations. |
| Resource use | Monitor records run tool counts and elapsed time. | CPU, memory, disk, provider capacity and per-component resource samples are not exposed by the current health surface. |
| Security boundary | Module scopes permit only `<module>:read` and `<module>:health`; monitor is read-only. | Existing read boundaries are suitable. A future health reader must not gain administrative or cross-module write scope. |
| Failure honesty | Monitor exposes allow-listed failure codes and does not print raw findings. | Existing telemetry boundary should be reused; raw logs, prompts and sensitive values must remain excluded. |

## Decision

BACK-019 should not add an HTTP server, network probe, synthetic “healthy”
value, or resource guess. Those approaches would expand authority and would
make the acceptance claim stronger than the observed evidence.

The smallest compatible implementation boundary for a later implementation
task is:

1. Add a typed, bounded health snapshot record owned by the existing Backend
   boundary. It should contain module key, instance ID, artifact/package
   version, observed time, readiness, liveness, dependency summary, and
   optional resource samples.
2. Require a trusted producer or explicitly recorded heartbeat for `live`.
   Without one, return `unknown`; do not infer liveness from a task row or
   missing process record.
3. Reuse `ModuleRegistry` for stable identity and local health/read scopes.
4. Keep the ATLAS Monitor read-only and display only persisted snapshots,
   with an explicit `unknown` value when no trusted sample exists.
5. Bound and redact resource/error metadata. Store digests and codes rather
   than raw logs, prompts, credentials or private source content.
6. Add deterministic tests for stale heartbeat, missing dependency, version
   mismatch, unknown resource data, scope violations and restart recovery.

This task does not authorize external service discovery, Cloudflare writes,
Windows-host probing, deployment, or a production health endpoint. Those are
separate acceptance gates.

## Rejected alternatives

- Treating `cli health`'s static seed response as a deployed health API: it has
  no observation source and cannot satisfy readiness/liveness/resource use.
- Treating recorded SQLite task or run rows as process liveness: the monitor
  contract explicitly forbids that inference.
- Adding a generic network endpoint now: no approved transport, authentication
  contract, or deployment boundary exists in this audit task.
- Reporting zero resource use when no sample exists: absence of telemetry is
  `unknown`, not zero.

## Child evidence receipt

| Child | Evidence |
| --- | --- |
| `BACK-019.S01` | Pinned baseline, source list, configuration SHAs, package version, live monitor snapshot and unknowns recorded above. |
| `BACK-019.S02` | Each acceptance clause is mapped to observed evidence, a gap, or an explicitly labelled unknown. |
| `BACK-019.S03` | This versioned audit/decision record identifies the smallest implementation boundary and rejected alternatives. |
| `BACK-019.S04` | Source hashes, integration SHA, module count, Business exclusion, monitor controls and project-state distinction were cross-checked locally; independent QC must verify the exact candidate. |

## Next gate

Independent QC must verify this document against the BACK-019 candidate commit
produced from the audited baseline and confirm that the audit task did not
introduce runtime behavior or claim unavailable host evidence. A later
implementation task may consume this decision record.
