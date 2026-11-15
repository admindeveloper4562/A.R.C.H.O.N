# MIG-001 — clean private repository design

**Status:** design proposal; no runtime or repository-policy implementation is included.

**Authority:** pinned source `b9cf9d82a2ce2496ab2e763521c0d69e7d34eb54`; approved architecture digest `295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89`.

## 1. Requirements and acceptance traceability

| Requirement | Design decision | Acceptance/evidence | State |
|---|---|---|---|
| Fresh seed contains ten active modules | Seed maps modules `01` through `10` to Core, SDA, Backend, Runtime, Research, TWS, WIC, Finance, Guardian and Automation. | Fresh-seed inventory has exactly those ten module roots. | specified; implementation unknown |
| No Business module | Business is excluded from the module registry, tree, ownership map and seed generator. Historical references remain documentation-only. | Negative test rejects a Business root or registry entry. | specified; implementation unknown |
| Versioned documentation | Design, contract, provenance and migration records use stable document/schema version fields; incompatible changes require a new major version. | Fixture check validates required version fields and rejects unsupported versions. | specified; implementation unknown |
| Branch and commit lint | Worker branches follow `docs/engineering/BRANCH_COMMIT_POLICY.md`; commits use the documented Conventional Commit form and task suffix. | Policy lint accepts valid examples and rejects invalid module/task/path forms. | observed policy; lint implementation status unknown |
| Private repository structure | Source, migration candidates, provenance, documentation and ownership have separate roots; imported candidates are never runtime imports. | Tree and import-boundary checks; no production package points at `migration/imported`. | specified; implementation unknown |
| Source provenance and compatibility | Imported material retains source ref/commit/blob/path/digest and is reviewed before porting. | Provenance fixture and importer guardrails remain green. | observed in existing importer/tests; fresh run not performed |

Dependencies are the ten-module contract, consolidated architecture, identities, security boundaries, coding handbook, migration provenance rules and branch/commit policy. Non-goals are runtime implementation, source import, database migration, CODEOWNERS activation, deployment, remote publication, and Business design.

Open decisions: the repository host's exact private visibility and required review count; the final CODEOWNERS identities; the authoritative CI provider; and whether schema compatibility uses JSON Schema, typed Python models, or both. These choices must be owner-reviewed before implementation.

## 2. Proposed seed and ownership layout

```text
docs/
  architecture/          # authoritative system and module contracts
  engineering/           # branch, commit, release and review policy
  migration/             # migration plans, provenance maps and this design
migration/
  imported/               # immutable, staged, non-executable candidates
  provenance/             # source and digest records
src/jarvis_v2/
  core/ sda/ backend/ runtime/ research/
  tws/ wic/ finance/ guardian/ automation/
tests/
tools/
.github/CODEOWNERS        # proposed ownership policy; implementation deferred
```

The ten module roots are the only active architecture roots. Shared protocol definitions may live under a separately owned `contracts/` package, but module data remains owned by its module. `migration/imported` is evidence/source material, not an installable package. No Business directory, namespace, service, or owner rule is created.

Proposed CODEOWNERS rules, to be materialized only after identity approval:

```text
/src/jarvis_v2/core/       @archon-core
/src/jarvis_v2/sda/        @atlas-sda
/src/jarvis_v2/backend/    @atlas-backend
/src/jarvis_v2/runtime/    @archon-runtime
/src/jarvis_v2/research/   @archon-research
/src/jarvis_v2/tws/        @archon-tws
/src/jarvis_v2/wic/        @archon-wic
/src/jarvis_v2/finance/    @archon-finance
/src/jarvis_v2/guardian/   @aegis-guardian
/src/jarvis_v2/automation/ @atlas-automation
/docs/architecture/        @architecture-reviewers
/docs/migration/           @migration-reviewers
/migration/                @migration-reviewers
```

These handles are placeholders, not verified repository identities. Protected files such as security, CI and ownership policy require the separately authorized platform/security owners; this task does not edit them.

## 3. Versioned interfaces and ownership

All cross-module records use an envelope with these required fields: `event_id`, `event_type`, `schema_version`, `producer`, `aggregate_id`, `sequence`, `occurred_at`, `causation_id`, `correlation_id`, `privacy_scope`, `payload_hash`, and `payload`. Consumers reject unknown major versions, stale sequence numbers and duplicate IDs; minor additions are tolerated only when the consumer contract says so.

Task records additionally carry `task_id`, `parent_id`, `project_id`, `module`, `dependencies`, `acceptance`, `permission_scopes`, `attempt`, `lease`, `state`, `result_refs` and `tool_effect_receipts`. The deterministic SDA Master owns task state, leases, fencing and transitions. Modules own domain data. Backend owns identity, scoped metadata and indexes; it does not become owner of module-private records.

The lifecycle is:

```text
ELIGIBLE -> LEASED -> PREFLIGHT -> CODING -> DETERMINISTIC_TESTS
  -> INDEPENDENT_QC -> APPROVED -> MERGE_QUEUE -> SERIAL_MERGER
  -> VERIFIED_COMPLETE
```

Failure, pause, quota and external waits are explicit states and never imply completion. Events are append-only facts; projections may be rebuilt. A compatibility adapter may read an older minor version, but a major-version migration must preserve the old reader or provide a reversible migration and a pinned rollback target.

## 4. Safety, privacy and rollback matrix

| Risk/failure | Required behavior | Recovery evidence |
|---|---|---|
| Untrusted imported code | Read committed blobs only; stage as non-executable; never execute on host. | Provenance digest and negative execution/import-boundary test. |
| Duplicate import or path collision | Create-only writes; reject exact, case-only and symlink collisions before writing. | Existing importer guardrail tests and collision fixtures. |
| Duplicate event/job | Deduplicate by stable event/operation ID and acknowledge only one effect. | Replay test with one effect receipt. |
| Unknown schema or incompatible producer | Fail closed with a typed incompatibility error; do not guess fields. | Unsupported-major negative fixture. |
| Lease loss or two writers | Fence the stale generation; only the Master may transition ownership. | Disposable recovery test with one accepted writer. |
| STOP/PAUSE/quota | Preserve the marker and stop affected non-idempotent work; do not clear it automatically. | Restart/marker restoration test or explicit manual gate. |
| Secret/private data exposure | Enforce scoped permissions and metadata-only public progress; never place secrets in migration artifacts. | Secret scan and payload-scope review. |
| Failed migration or seed update | Keep the previous version, verify backup/integrity, and roll back atomically; never delete source evidence. | Restore rehearsal and checksum comparison. |

No new privilege, network access, external write, deployment, database mutation or approval is implied by this design. Missing owner identity, host, credential, quota or device evidence remains an external/manual gate.

## 5. Acceptance test matrix

| Acceptance clause | Test type | Planned command/fixture | Expected result |
|---|---|---|---|
| Ten modules in a fresh seed | unit/integration | Seed in a temporary directory; enumerate active module roots | Exact set of ten named modules; no extras |
| No Business | negative | Attempt Business root, registry entry and owner rule | Each is rejected or absent |
| Versioned docs | unit/fixture | Validate representative architecture, contract and provenance records | Required version fields present; unsupported major rejected |
| Branch lint | unit/negative | `python3 tools/check_git_policy.py --branch <name>` or the repository's equivalent | Policy examples pass; malformed/Business names fail |
| Commit lint | unit/negative | `python3 tools/check_git_policy.py --commit <message>` or equivalent | Conventional Commit with task suffix passes; malformed messages fail |
| Import safety | integration/negative | Existing `tests/test_migration_guardrails.py` against temporary repositories | Pin, provenance, collision and create-only rules hold |
| Ownership and boundary review | manual | Review CODEOWNERS proposal against approved identities and protected paths | No placeholder identity is activated without approval |

The exact command names for seed validation and CODEOWNERS validation are **unknown** until implementation exists. Existing importer and policy tests are observed in the worktree; they were not run in this design-only repair.

## 6. Ordered child deliverables

- **S01 requirements:** this document's traceability table, dependencies, non-goals and open decisions.
- **S02 contract:** the seed layout, envelope fields, ownership rules, lifecycle and version compatibility in sections 2–3.
- **S03 safety:** the threat/failure, privacy, idempotency and rollback matrix in section 4.
- **S04 test plan:** the clause-to-test matrix, fixtures and manual gates in section 5.
- **S05 review design:** the implementation boundary below, with contradictions called out as open decisions rather than silently resolved.

## 7. Reviewed implementation boundary

The eventual implementation proposal is limited to `tools/import_legacy.py`, `migration/`, `docs/migration/`, and `tests/` as supplied by the task contract. This candidate intentionally narrows its own changes to `docs/migration/` because execution mode is `design`; it does not create source modules, tests, fixtures, configuration, policy, database files, or tools. A later implementation task must independently review the security and handbook requirements, obtain the unresolved owner decisions, add tests before behavior, and preserve the pinned source/provenance model.

**Evidence classification:** architecture and policy wording above is specified/observed from repository documents; current implementation of the proposed fresh seed, CODEOWNERS, lint integration and version validators is unknown; no runtime, host, remote, approval, test-pass or deployment evidence is claimed.
