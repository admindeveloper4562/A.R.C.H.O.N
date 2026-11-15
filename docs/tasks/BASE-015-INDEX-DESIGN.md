# BASE-015 — branch-specific symbol and FTS index design

Design version: `1.0.0`. Execution mode: `design`. Date: 2026-11-15.
State: `DRAFT / NOT_VERIFIED`; prepared for independent Supervisor/QC review.
This document specifies future behavior; it neither implements BACK-013 nor grants permissions.

## Evidence boundary and governing inputs

| Input | Evidence class | Observation or obligation |
|---|---|---|
| Supplied governing architecture SHA256 | Specified | `295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89` remains the approval binding; do not replace it with the observed digest. |
| Pinned source and current HEAD | Verified local metadata | Both are `7a8cb685baa1abf7d10d0bf1b35fd98024cb6f9f`. Initial `git status --short` produced no entries. |
| Current isolated branch | Verified local metadata | `feature/astra-base-015-a5-0b478688`; no integration freshness beyond this local HEAD is asserted. |
| Checked-in architecture | Verified digest; observed text | `docs/architecture/JARVIS_V2_CONSOLIDATED.md` hashes to `8d61e949302b70386d4e1d4a668cc4abe8b76be9966c5efe4575bdf2ca558d73`, which differs from the governing digest. Sections 3, 4, 12, 14–16 and 19 inform this provisional design, not approval of the mismatched bytes. |
| Local task plan | Observed | `docs/tasks/JARVIS_V2_TASK_PLAN.json` lists BASE-015 as NOT_VERIFIED and dependent on BASE-001. BACK-013 depends on BASE-015 and BACK-002. No full task payload is reproduced here. |
| Dependency audit | Observed report, not reverified host evidence | `docs/tasks/BASE-001-AUDIT-20261114.md` reports BLOCKED / NOT_VERIFIED. Its host, remote and sibling-worktree claims were not repeated in this task. |
| Repository rules | Observed | Read `AGENTS.md`, `CODING_HANDBOOK.md`, `SECURITY.md`, `docs/architecture/MODULE_CONTRACTS.md`, `docs/architecture/IDENTITIES.md`, and `docs/migration/ASTRA_TO_NATIVE_SDA.md`. |
| Existing compatibility surfaces | Observed source inspection | `src/jarvis_v2/backend/module_manifest.py`, `src/jarvis_v2/core/queue.py`, and `src/jarvis_v2/sda/handoff.py`; inspection is not execution evidence. The inspected Backend boundary has no index API. |
| Runtime behavior, license decisions, host qualification, approvals | Unknown / not performed | No index, database, scanner, parser, FTS query, fixture, runtime test, host drill, remote check or approval was exercised or obtained. |

Evidence labels below: **specified** means a proposed deterministic requirement;
**observed** means repository text inspected; **verified** is limited to checks
actually described above or in the final receipt; **unknown** is an unmet gate.
Acceptance wording that exclusions are “verified” requires future independent
execution evidence. This plan supplies auditable verification criteria only.

## S01 — requirements and acceptance traceability

| ID | Requirement / source | Design mapping | Future evidence / acceptance |
|---|---|---|---|
| R1 | BASE-015: branch-specific code symbols and FTS; architecture §4.3 | S02 repository/ref/snapshot identity, parser and FTS projections | T1, T8–T11: branches cannot mix; symbol and literal text lookup cite the same pinned blob. |
| R2 | Acceptance: generated-file exclusions verified | S02 admission rules, ordered path/header classification before persistence | T3: generated directories, suffixes, attributes and headers produce zero indexed tokens or symbols. |
| R3 | Acceptance: secret exclusions verified | S02 admission, S03 privacy and revocation | T4: synthetic canaries absent from all persistent and outward surfaces, including errors and failed refreshes. |
| R4 | Acceptance: license exclusions verified; architecture §§4.3, 6, 15 | S02 reviewed provenance manifest and deny-by-default decisions | T5: unknown, denied, conflicting or stale provenance is excluded; no inferred license approval. |
| R5 | Acceptance: refresh keyed by blob SHA | S02 parse key, branch bindings and atomic refresh | T8–T10: unchanged blobs reuse only compatible, admitted results; changed blobs reparse; no partial snapshot. |
| R6 | Repair: bounded read-only Git, root/ref/type validation | S02 Git boundary and budgets | T1, T2, T6: traversal, ref injection, special entries, malformed/large blobs and timeout fail closed. |
| R7 | Repair: strict query/limit and deterministic ordering | S02 search contract | T7, T11: reject invalid types/ranges/syntax; explicit stable order before limit, no payload exposure. |
| R8 | Security, STOP/PAUSE, idempotency, rollback | S03 failure matrix and S02 transitions | T9, T10, T12: retain last good snapshot; stop prevents publication; restart neither clears controls nor duplicates events. |
| R9 | Ten modules, existing interfaces and minimum scopes | S02 ownership; S05 compatibility review | T13 plus manual review: manifest, queues, handoff and monitor contracts unchanged. |
| D1 | BASE-001 is direct dependency | Gate P2 below | Independent current dependency evidence required; its existence in the tree is insufficient. |
| D2 | Governing architecture approval binding | Gate P1 below | Authorized matching architecture or explicit reconciled approval required. |
| D3 | BACK-013 is downstream; BACK-002 is its additional dependency | Gate P3 below | Backend storage/permissions contract and implementation packet required before runtime work. |
| D4 | S01 → S02 → S03 → S04 → S05; Supervisor scope approval | Sections in that order; S05 allowed-path proposal | Deliverables are present for review; S05 approval and child done states are not asserted. |

Non-goals: runtime implementation, schema migration, source ingestion, real
repository/license certification, embeddings, model calls, new module services,
remote fetch, submodule traversal, worktree-file indexing, task/receipt/session
indexing, public HTTP endpoints, cloud export, production changes, ref mutation,
deletion or native SDA cutover. Legacy source remains reference-only and untrusted.

Open decisions and prerequisites (all **unknown / pending**):

| Gate | Decision and owner | Safe behavior until resolved |
|---|---|---|
| P1 | Architecture authority reconciles supplied digest with actual approved bytes | Design may be reviewed; runtime authorization is blocked. |
| P2 | Supervisor/QC validates BASE-001 against the intended current base | No assumption that repository registration or host isolation is qualified. |
| P3 | Backend owner supplies BACK-002 storage contract and separately scoped, approved runtime execution packet | Existing read/health grants do not authorize index writes or Git child processes. |
| P4 | Owner/security reviewer approves repository/ref/path allowlists, isolated object-store access, scanner coverage, budgets and local storage retention | No repository is eligible for indexing by default. No scope strings are invented here. |
| P5 | Provenance reviewer approves per-path license decisions and permitted local indexing purpose; parser owner pins supported parser/tokenizer versions | Unknown provenance/language remains excluded; no fallback parser or copied legacy implementation. |
| P6 | Supervisor approves this bounded design scope; independent QC reviews S01–S05 evidence | Author cannot mark scope, design or acceptance approved. |

## S02 — typed contract, ownership and sequence specification

### Ownership and compatibility

Backend (03, ATLAS) owns only a derived, local code index and its private
snapshot/cache storage. It never owns SDA's authoritative tasks, locks, leases,
receipts or approvals. Core (01) requests authorized work; SDA (02) supplies a
pinned project context through its existing controller, not arbitrary shell text.
Runtime (04), Research (05), TWS (06), WIC (07) and Finance (08) receive no implicit
access to a foreign module's repository or index. Guardian (09, AEGIS) may observe
authorized health and request recovery; its model cannot promote a snapshot or
rewrite enforcement. Automation (10) receives no source-index content or events
under this version. Business remains absent. ARCHON/AEGIS/ATLAS are role overlays.

Observed manifest scopes are exactly each module's own read and health scopes.
Module manifests do not grant subprocess, filesystem write, network, privileged
or cross-module access. A caller's `sda:read` or `core:read` is not `backend:read`.
Even `backend:read` alone cannot authorize Git execution or refresh persistence.
Future index service operation needs a separately reviewed exact repository,
branch and storage grant from the deterministic broker; model text, dependency
edges and this plan confer no such authority. No manifest or policy change is
part of BASE-015.

Keep existing `jarvis_v2` paths, module IDs, dependency tuples and public APIs.
Do not reuse `TaskQueue.status()`, lease responses or task records as index
responses: their fields have different privacy boundaries. Preserve existing
bounded chronological `history()` behavior, including its current limit clamping;
the new index rejects excessive limits without changing that compatibility path.
Keep handoff evidence keys and advisory/shadow behavior intact. ATLAS Monitor
remains an independent read-only process, with no index dependency or worker-slot
reconstruction. Native SDA/Guardian scheduling and inference are unaffected.

### Versioned types and storage (specified, not created)

Closed records reject missing, extra, duplicated, coerced or wrongly typed fields.
`UInt` excludes booleans. `Label` is a broker-issued ASCII identifier, 1–64 bytes,
letters/digits/underscore/hyphen only; caller-supplied labels are never trusted
without exact registry lookup. Public labels must contain no path or private text.
`OID` is algorithm-tagged (`sha1` with 40 lower hex or `sha256` with 64 lower hex),
matching the registered repository format; abbreviations and mixed formats fail.
Use unpadded semantic versions. Incompatible versions are rejected, not downgraded.

| Record / interface | Exact fields and ownership |
|---|---|
| `SearchRequest/1.0.0` | `schema_version`, `repository_label: Label`, `branch_label: Label`, `snapshot_label: Label`, `mode: symbols|text`, `query: string`, `limit: UInt`; authentication and broker grant are trusted transport context, never caller claims. |
| `SearchResponse/1.0.0` | `schema_version`, `status: OK|UNAVAILABLE|INVALID_REQUEST|DENIED|BUSY`, `snapshot_label: Label|null`, `items: tuple[Hit]`, `has_more: bool`. Non-OK has null snapshot, empty items, false has_more. |
| `Hit/1.0.0` | `file_label: Label`, `symbol_label: Label|null`, `kind: function|class|method|import|test|text`, `line_start: UInt`, `line_end: UInt`, `blob_oid: OID`, `license_label: Label`; line numbers start at 1 and end ≥ start. Text hits have null symbol and equal start/end. |
| `RefreshRequest/1.0.0` | Internal only: `schema_version`, `repository_label`, `branch_label`, `expected_commit: OID`, `expected_generation: UInt`, `request_label: Label`. Actual root, exact ref and destination resolve from broker registry. No payload, path or command field. |
| `RefreshResult/1.0.0` | Internal fixed metadata: `schema_version`, `status: PUBLISHED|UNCHANGED|REJECTED|BUSY|PAUSED|STOPPED|FAILED`, `snapshot_label: Label|null`, `reason: NONE|SCOPE|REF|OBJECT|ADMISSION|BUDGET|CONTROL|CONFLICT|STORAGE|VERSION`. Never pass raw exceptions or Git stderr. |
| `BranchHead` | Backend-private primary key `(repository_id, exact_ref)`; active snapshot pointer, generation, monotonically increasing event sequence, current policy epoch and access-gate state. Branch deletion/recreation requires fresh registry identity. |
| `Snapshot` | Backend-private immutable `(snapshot_id, repository_id, exact_ref, commit_oid, policy_digest, parser_version, tokenizer_version, schema_version)`, admitted file count and manifest digest; one complete manifest, never partial. |
| `FileBinding` | Private key `(snapshot_id, repository-relative path bytes)`; regular mode, blob OID, admitted provenance/decision IDs, safe file label, parsed projection key. Paths exist only for admitted files and never enter responses/events. |
| `ParseProjection` | Private key `(repository_id, blob_oid, language, parser_version, tokenizer_version, schema_version, policy_digest)`; sanitized symbol/import/test metadata and FTS tokens/line references. No raw blob or source excerpt column. Admission is path-specific, not inferred from this cache. |
| `LicenseDecision` | Private reviewed manifest binds repository, path selector, applicable blob/tree/commit coverage, provenance identity, decision/version and permitted purpose. IDs and license labels are opaque; no author identities or private origin URLs in results. |
| `IndexEvent/1.0.0` | Optional local Backend publication payload exactly `snapshot_label`, `state: READY`, `reason: NONE`. No public/Cloudflare export or failed-build event. |

Response allowlists above are the entire proposed disclosure contract, subject
to P4 approval rather than a present disclosure grant: no symbol names,
relative/absolute paths, source snippets, raw FTS expressions, scores, diagnostic
messages, excluded-file identifiers/counts, task payloads, receipts, lease/session
IDs, prompts, model text, credentials or private host metadata. An opaque citation
does not authorize source retrieval; v1 provides no content-resolver API. All
outgoing metadata is checked for secret-shaped values and byte bounds before
serialization; a failing check emits only the fixed unavailable response.

Optional local events use the architecture §12 envelope through a future reviewed
adapter, with fixed producer `backend`, event type `backend.code_index.snapshot_changed`, schema version, opaque broker-generated
event/aggregate/correlation/causation IDs, UTC occurrence time, private scope and
payload hash. Task/session fields are null and cannot be populated from task
records; if the bus requires non-null values, integration is blocked pending a
reviewed adapter. Deduplicate by event ID; sequences increase per branch aggregate
only on committed pointer changes, including rollback. Rollback never rewinds the
sequence. Persist event intent with publication atomically; no task-queue writes.
Consumers reject unknown versions, scope, sequence regressions and duplicate
effects. Search reads and failed/no-op refreshes emit no publication event.

### Git boundary and finite budgets

All constants below are proposed maximums requiring P4 review, not observed host
capacity. Do not silently clamp over-budget inputs, truncate source or claim a
partial index complete.

| Resource | Bound / rejection behavior |
|---|---|
| Root/ref identity | Root comes only from registered handle; canonical root and approved Git/common directories must match registration, with no symlink component substitution. Full local `refs/heads/…` ref ≤240 ASCII bytes; exact allowlist and Git ref-format validation. No HEAD aliases, tags, remote refs, revisions, ranges, leading option, whitespace/control, reflog selectors or object/path expressions. |
| Paths/tree | NUL-delimited records; ≤10,000 entries, ≤4 MiB tree output, ≤240 UTF-8 bytes per path. Reject absolute paths, dot/dot-dot components, empty components, backslash/drive/UNC forms, controls, invalid UTF-8, non-NFC or casefold-colliding paths. Do not percent-decode paths. |
| Objects/text | Only tree-proven `blob` entries with mode `100644` or `100755`. Reject symlinks (`120000`), gitlinks (`160000`), trees as content, missing/corrupt objects and unsupported object format. Blob ≤1 MiB; aggregate inspected bytes ≤32 MiB. Strict UTF-8, no NUL, no decode replacement; empty file admits zero tokens. Binary, invalid or oversized eligible blobs reject refresh. |
| Processes/build | Fixed trusted Git executable; argument lists, `shell=False`; metadata commands ≤2 s each, tree/blob commands ≤5 s each; total refresh ≤60 s. Stream bounded stdout/stderr (stderr ≤4 KiB, discarded from outward errors), terminate the read-only child at cap/timeout, reap it. ≤2 child processes concurrently, 128 MiB worker budget; bounded parser time/memory; no source execution. |
| Derived output | ≤10,000 symbols and ≤100,000 tokens per admitted blob, ≤1,000,000 projection rows per snapshot and ≤64 MiB staged derived storage. Overflow rejects the entire candidate. One refresh per repository/ref, at most two per service; no unbounded pending queue. |
| Search | Query 1–256 ASCII bytes, 1–8 tokens, each 1–64 bytes; limit integer 1–50, default 20 only when omitted by a trusted adapter. Public closed request requires explicit limit. One snapshot, ≤1 s database execution, ≤16 KiB serialized response. Exceeding a work/response budget returns BUSY with zero items. |

Validation/read sequence is mandatory:

1. Authenticate, authorize exact operation/repository/ref, and check durable
   STOP/PAUSE/quota. Resolve registry handle; caller cannot supply a filesystem
   root. Validate canonical worktree and registered administrative directories
   before invoking Git. Hold a trusted registrar read lease preventing root/admin
   substitution throughout the operation; rechecking a pathname alone does not
   prevent a race. Reject if this protection cannot be established.
2. Use a trusted isolated Git configuration/environment: no inherited `GIT_DIR`,
   alternate object stores, arbitrary config injection, replacement/graft objects,
   fsmonitor, credential helpers, hooks, filters, textconv, paging or network.
   Reject unapproved alternates/promisor arrangements; disable lazy fetch and
   replacement objects. Do not inspect private OS configuration to discover grants.
   Repository control data must already be approved; indexer cannot repair it.
3. Bounded argv shapes (metavariables resolve only after validation) are
   `[git, -C, ROOT, rev-parse, --show-toplevel]`,
   `[git, check-ref-format, FULL_REF]`,
   `[git, -C, ROOT, show-ref, --verify, --hash, FULL_REF]`, and
   `[git, -C, ROOT, cat-file, -t, COMMIT_OID]`.
   Compare returned root/ref/commit to registration and expected commit;
   validate full OIDs, require commit type. Never interpolate a ref into a shell
   or build `ref:path` input from caller text. No checkout, fetch or update-ref.
4. Enumerate the pinned commit with bounded
   `[git, -C, ROOT, ls-tree, -r, -z, --full-tree, COMMIT_OID]`.
   Validate every record's syntax, path and type; tree metadata is not content.
   Path-denied entries do not cause content reads or retained exclusion records.
   Special entry modes fail closed. Resolve eligible entries to full tree-proven
   OIDs; use `[git, -C, ROOT, cat-file, -t, BLOB_OID]` and
   `[git, -C, ROOT, cat-file, -s, BLOB_OID]` before
   `[git, -C, ROOT, cat-file, blob, BLOB_OID]`.
   Check actual streamed length as well as advertised size; never call filters.
5. Re-resolve ref and check controls/grants/policy before publication. A moved ref,
   changed repository identity or missing approval rejects the candidate. Reads
   remain pinned to immutable objects throughout. No filesystem source fallback.

### Admission before any persistence

Order: authorize path → exclude secret/private paths → exclude generated/vendor
paths → require applicable approved provenance/license → validate object and
decode in bounded transient memory → generated-header and secret-content checks
→ non-executing pinned AST parse/tokenization → rescan derived fields → stage.
No raw blob is written to temporary files, logs, database, FTS shadow tables,
cache, traces, exception text or crash dumps. Disable core dumps for the future
isolated worker. Secret scanners are a defense, not proof that arbitrary source
is safe: only positively reviewed source-path scope is eligible.

| Gate | Deterministic specification |
|---|---|
| Path eligibility | Reviewed allowlist covers exact module source/test subtrees and file types; deny wins over allow. No automatic recursive repository-wide permission. Private task/session/receipt/prompt/model/log/export/database/backup trees, Git metadata and OS personal files are outside the allowlist. |
| Secret paths | Deny environment files including example variants by default, credential/private-key/certificate/token/secret stores and secret-bearing suffixes/components using versioned casefold rules. Scan all path text for canary/secret-shaped values before storage; a match rejects the build without persisting the path. Filename text is untrusted and never surfaced. |
| Generated paths/content | Deny build/dist/coverage/cache/vendor/dependency trees, minified files, source maps, lock/generated manifests and generated suffixes; positive reviewed manifest rules plus validated generated attributes and bounded header markers such as fixed generated-file labels. Attributes must come from the pinned reviewed admission manifest, never live worktree/global attributes. Never run repository generators or evaluate attributes as commands. Unreviewed attribute rules cannot expand scope. |
| License/provenance | Require applicable reviewed decision for each path at this snapshot and local indexing purpose. Unknown, denied, conflicting, expired/revoked or mismatched coverage is excluded, even for an otherwise allowed blob. License/notice/provenance documents themselves are metadata inputs only, excluded from symbol/FTS content. Third-party/vendor code is denied by default. SPDX-like text or presence of a license file does not constitute approval. |
| Content | Scan the complete bounded blob, not only a prefix: synthetic canary rules, key blocks, credential assignments, credential URLs and secret-shaped/high-entropy values, including comments/docstrings/identifiers. A match or scanner failure rejects refresh and closes access pending review; never persist the match, path, OID or excerpt in an exclusion log. Header-classified generated content is excluded entirely. |
| Projection | AST parser never imports or executes source. Initial proposal supports one pinned Python parser; unsupported languages are excluded explicitly by the reviewed admission manifest. No regex/model fallback. Persist only reviewed symbol/import/test lookup tokens and text tokens with line numbers, not reconstructed source; recheck tokens, identifiers and labels before staging. |

Path/license/generated exclusions are deterministic omissions in an otherwise
complete eligible manifest. Rejected eligible blobs, parsing/scanning failures
and unknown classifier state abort publication rather than silently omitting
errors. Exclusion decisions remain in the separately reviewed policy/provenance
inputs; the index retains no denied path, blob hash, token or per-file diagnostic.
No real license, generated-file or secret exclusion has been verified by this plan.

### Atomic refresh, idempotency and state transitions

`UNAVAILABLE → VALIDATING → BUILDING → READY_TO_PUBLISH → READY` describes an
initial build. For an existing READY snapshot, validation/build run beside its
immutable last-good pointer. Snapshot IDs are opaque; reproducible manifest
digests privately bind repository/ref/commit, admitted `(path, mode, blob_oid)`
entries and all policy/parser/tokenizer/schema versions. A blob's Git OID is the
content change key; mtime, working-tree bytes, file length and commit identity
alone cannot substitute for it.

1. Acquire Backend's per-ref writer lease/fence, not SDA's task lock. Pin expected
   generation and commit. Revalidate admission for every path, including cache
   hits. Only reuse ParseProjection for the full compatible key after all current
   path, license, generated and secret checks; cross-repository/branch visibility
   never follows from a common blob hash. Renames share parsing only when the new
   path is admitted; deletions disappear only from the new snapshot manifest.
2. Build immutable manifest, bindings, symbols and FTS rows in one inaccessible
   candidate. Isolation is by repository and snapshot; FTS joins always constrain
   both. Check symbol/FTS referential agreement, row/byte budgets and integrity.
   Candidate storage can contain admitted projections only. Partial candidates
   are never readable. Retention/cleanup needs separate approved policy; this
   task authorizes no file deletion or live database mutation.
3. Under a short transaction, recheck expected generation, writer fence, ref tip,
   current grants/policy, STOP/PAUSE/quota and complete candidate checks. Atomically
   publish all bindings/FTS visibility, head pointer, next generation and optional
   event intent, or publish nothing. Publication and STOP registration must share
   a deterministic fence: STOP committed first always prevents publication.
4. Same full desired manifest and policy yields UNCHANGED: no new generation or
   event. Replayed request labels bind to the same desired manifest; conflicting
   reuse is rejected. Crash before commit preserves old pointer; crash after
   commit is reconciled as already published. Unreferenced staged data stays
   inaccessible until separately authorized cleanup; no automatic deletion.
5. A refresh failure retains the physical last-good snapshot. Serve it only if
   current grants/policy still permit every admitted row and the caller explicitly
   requests that snapshot. Never silently answer a new commit request with old
   data. Unknown/revoked policy or suspected secret contamination closes the gate
   for all affected snapshots before returning anything; preservation is not
   permission to serve stale unsafe data.

Search pins one immutable snapshot in a read transaction. A pointer change during
the request cannot mix results. No implicit “latest” or cross-branch fallback.
Unknown snapshot and out-of-scope snapshot share the same outward DENIED shape
after request validation. Authorized but currently gated/unbuilt snapshot returns
UNAVAILABLE, without revealing a failed file or private execution state.

Query grammar is literal ASCII identifier terms `[A-Za-z0-9_]+` separated by single
ASCII spaces. Reject empty/whitespace-only strings, repeated/leading/trailing
spaces, NUL/control, Unicode, quotes, punctuation, wildcard/operator syntax and
secret-shaped values; never log query text. Operator-shaped words are ordinary
literal tokens, never interpreted as operators. Normalize to lowercase, deduplicate
and sort tokens. Text mode combines internally quoted tokens with fixed AND;
bind that expression and limit as SQL parameters. Callers never provide SQL,
MATCH syntax, column names, ORDER BY or parser options. Symbol mode requires all
terms in the same sanitized symbol/import/test projection. Use pinned tokenizer
semantics and exact token matches, with no prefix/fuzzy/ranking fallback.

Results sort globally **before** limiting by admitted relative-path UTF-8 bytes
(SQLite BINARY semantics), line start, line end, fixed kind order
`class,function,method,import,test,text`, private normalized symbol token, then
stable projection ordinal. Public labels never depend on iteration order or source
text. Text mode returns one hit per matching line; symbol mode deduplicates by
file/blob/kind/span/symbol identity. Deduplicate before ordering; fetch limit+1 to
set `has_more`, return the first limit only. No total count or cursor in v1.
Identical snapshot/query/limit yields identical ordered items. Exhausted search
budget returns BUSY, never an arbitrary prefix with `has_more=false`.

## S03 — threat/failure matrix, controls and rollback

All outcomes in this matrix are **specified**, not runtime observations.

| Threat / failure | Fail-closed response / recovery | Evidence plan |
|---|---|---|
| Root traversal, substituted worktree/admin directory, ref injection | Reject before content read; fixed SCOPE/REF reason; no root echo. No arbitrary process argv. | T1, T2 |
| Special entry, corrupt/missing object, bad encoding, false size, object-store escape | Reject candidate; bounded child termination and reap; no filesystem/network fallback. | T2, T6 |
| Generated or unlicensed data hidden behind rename or cache hit | Revalidate path/provenance/header for each snapshot binding before staging. | T3, T5, T8 |
| Secret in content, identifier, query, path or error | Entire blob/projection excluded; content suspicion closes affected read gate, rejects build; outward fixed labels only. Review required, no automatic retry. | T4 |
| SQL/FTS injection or excessive result request | Closed grammar and parameter binding; reject bool/float/string/null/negative/zero/over-limit; never clamp. | T7 |
| Concurrent refresh, ref advance, stale fence or generation | BUSY/CONFLICT, zero publication; discard visibility of stale candidate. No concurrent writers. | T9 |
| Disk full, schema mismatch, FTS corruption, parser/scanner error | FAILED, rollback transaction, preserve last good; incompatible/corrupt snapshots gated; no alternate engine or broad migration. | T6, T9, T10 |
| Timeout/resource pressure/backlog | Bounded execution; BUSY; no in-process unbounded queue. At most two controller retries for transient BUSY/storage-lock failures, with 250/500 ms delays within 60 s total budget, only while controls/grants remain valid. | T6, T12 |
| Deterministic validation/license/security failure | No retry; await corrected authorized input or independent decision. Never broaden scope, disable scanner or exceed budgets to recover. | T3–T7 |
| STOP/PAUSE/quota or unknown control state | Block new refresh and search dispatch; fence publication, stop read-only build at a bounded checkpoint, retain inactive staging and last good. Already pinned read completes only if controls still authorize final response; otherwise fixed UNAVAILABLE. | T12 |
| Crash/restart/event replay | Restore pointer, generation, fence and durable controls; replay committed event once by ID; do not infer missing approval or resume automatically through STOP. | T9, T12 |
| Foreign module, cloud export or private task/receipt join | DENIED; do not query domain tables. No generic event serialization of input records. Monitor remains independent. | T4, T13 |

STOP/PAUSE are enforced by the deterministic controller independently of any
model; no model call is part of indexing and no in-flight model generation is
interrupted. Durable controls are not cleared by refresh, restart or rollback.
Recovery observes the same scope, quota, authentication and backpressure limits.

Rollback: under the same approved Backend writer authority, durable control checks
and publication fence, select an
already complete compatible last-good snapshot, revalidate current grants,
policy/provenance and contamination status, then atomically switch the branch
pointer with a **new** generation and event sequence. Never roll back policy or
approvals to make old data readable. If no eligible snapshot exists, remain
UNAVAILABLE while preserving evidence physically; no source/database restoration
or deletion is implied. Incompatible schema requires a separately approved
migration plan; leave old data intact and use no destructive fallback. Retained
snapshots remain subject to revocation checks, not just the active pointer.

## S04 — acceptance tests and fixtures plan

No fixtures or tests are added or run by BASE-015. All following rows are
**planned / NOT_RUN**. Future BACK-013 work must create deterministic disposable
fixtures under `tests/`, with synthetic labels and fake canaries only, without
reading user files or contacting remotes. Record candidate SHA, exact command,
fixture digest, expected versus actual result and independent reviewer in the
future evidence receipt; retain no raw canary/source/payload in that receipt.

| Test | Kind and fixtures / stimulus | Expected output / invariant | Covers |
|---|---|---|---|
| T1 | Unit + local Git integration: two local branches, two registered roots, same path with different blobs; absent/detached/tag/remote/ref-selector/option-shaped/overlong ref | Exact registered branch only; pin expected commit; DENIED or REJECTED before blob read for invalid refs/roots; no branch/ref mutation. | R1, R6 |
| T2 | Negative: traversal/absolute/drive/backslash/control/non-NFC/case-collision paths; symlink/admin-directory swap, symlink blob, gitlink, missing/wrong-type OID, alternates/promisor/replacement setup | Zero content reads for rejected entries, no OS-file follow/network; previous pointer unchanged; errors contain fixed labels only. | R6 |
| T3 | Unit + integration: allowed source beside build/vendor/cache/minified/map/lock/generated fixtures, header-generated regular source and generated attributes, renamed cached blob | Generated files absent from bindings/symbols/FTS/cache; allowed control fixture remains searchable. Classifier uncertainty rejects build. | R2, R5 |
| T4 | Negative integration: fake canaries at start/middle/end, comments/identifiers/token output, fake credential URL, private record fields, rejected query and child stderr | No canary or secret-shaped value in staged/active/retained newly written rows, FTS shadow storage, logs/errors/events/results/temp files; access gate closes for suspected old contamination. Compare exact response keys and enums; no task/receipt/model fields. | R3, R7, R9 |
| T5 | Unit + integration: synthetic approved, unknown, denied, contradictory, revoked, expired and wrong-commit license decisions; license/notice text, renamed file and same blob under denied path | Only explicitly covered source admitted; license files never FTS content; stale cache cannot grant admission; revocation gates old snapshots. Reviewer uses fake decisions, never claims real license approval. | R4, R5 |
| T6 | Unit + integration: empty blob, exactly 1 MiB and one byte over; invalid UTF-8/NUL, corrupt object, advertised-size mismatch, 10,000/10,001 entries, output/token/row/memory/time limits, scanner/parser failure | Empty yields no hits; allowed boundaries succeed only with all other gates; overflow/malformed rejects atomically, child reaped, no truncation or raw error exposure. Host limits require T14 too. | R6, R8 |
| T7 | Unit + FTS integration: valid one/eight literal terms, 256/257 bytes, 64/65-byte token, 8/9 tokens; quotes/operators/punctuation/Unicode/escapes/NUL/spaces; every invalid limit type/range including bool and 51 | Fixed INVALID_REQUEST, empty items for invalid input; no SQL/FTS expression execution from caller syntax. Limits 1 and 50 honored; normalization exact; no query echo. | R7 |
| T8 | Integration: identical length changed blob, unchanged blob in new commit, allowed/disallowed rename, removed file, parser/tokenizer/policy/schema changes | Blob OID change reparses; same compatible key reuses projection only after fresh admission; removed/denied paths absent from new snapshot; old explicitly pinned snapshot follows current gates. | R1, R5 |
| T9 | Integration fault injection: crash before stage/after stage/before commit/after commit; competing fence/generation, branch movement, disk full and event replay | One complete active snapshot; no mixed FTS/symbol data; old pointer survives failure; post-commit retry reconciles; one logical event per pointer change, monotonic sequence. | R5, R8 |
| T10 | Integration: idempotent repeat, conflicting request-label replay, eligible rollback, incompatible/revoked rollback and no eligible last good | UNCHANGED causes no generation/event; conflicting replay rejects; valid rollback advances generation/sequence while restoring prior manifest; unsafe rollback remains UNAVAILABLE. | R5, R8 |
| T11 | Unit + integration: shuffled tree/parser insertion order, same spans/names/kinds, >50 matches, ties at limit, duplicate projections, concurrent snapshot publication | Expected exact globally sorted first N after dedupe; `has_more` true only for extra eligible hit; byte-identical repeated response and no snapshot mixing; no snippets/path/name/score extras. | R1, R7 |
| T12 | Integration + host: STOP/PAUSE/quota/unknown control before start, during build, racing commit and after restart; transient retry saturation | No new dispatch/publication once control fence wins; persistent controls intact, at most prescribed retries, bounded pending work; no recovery privilege expansion. | R8 |
| T13 | Compatibility + negative authorization: existing manifest/Core history/handoff suites and public export comparisons; own/foreign read/health plus write/process/network/admin/inferred grants | Existing behavior unchanged; foreign or unapproved operation denied even with Backend read; no task-table access, monitor import/start or cloud export dependency. | R9 |
| T14 | Manual independent Linux gate: approved disposable repository/storage sandbox, real Git/SQLite FTS5/parser/scanner, denied network and host files, resource/timeout/crash/restart/rollback drills | Record actual environment/artifact identity and bounded side effects; prove no host file escape or hidden write, no private bytes in persisted artifacts; no claim from mocks alone. | R2–R9, P2–P5 |
| T15 | Unit + integration: missing/extra/coerced fields, unknown schema/mode, malformed labels/OIDs, mismatched repository/branch/snapshot, event duplicate/stale/unknown version and mandatory task/session bus fields | Closed request/response keys, fixed errors; no private echo; unavailable bus adapter blocks integration instead of filling fields from task records. Literal operator words behave as tokens; no downgrade or sequence rollback. | R1, R7, R9 |

Future command plan, **not executed and not yet present**: use
`python3 -m unittest discover -s tests -p 'test_backend_code_index*.py'` for
T1–T12 and T15 implementation suites (future naming proposal), then
`python3 -m unittest discover -s tests` for repository regression including T13.
Host T14 uses a separately reviewed runbook against disposable local objects and
isolated storage; no command in this plan grants host/process/write authority.
Expected suite output is nonzero failures until implemented; zero discovered
tests or mocked Git/scanner results are not acceptance. Independent QC must check
discovery counts, deterministic assertions and real negative-path evidence.

## S05 — design cross-check and allowed-path proposal

This is an author cross-check awaiting independent review, not a Supervisor
approval or QC receipt. No known rule conflict is silently resolved by widening
permissions; architecture equivalence, dependency qualification and approvals
remain explicit prerequisites P1–P6.

| Contract | Cross-check / resolution | Gate state |
|---|---|---|
| Architecture supplied digest versus checked-in architecture | Governing hash retained; observed mismatch recorded, no substitute approval. | P1 unmet |
| Ten-module contract and identity overlay | Backend owns derived index only; domains retain data; no new services/Business; Core/SDA/Guardian boundaries retained. | Specified; runtime T13 pending |
| AGENTS and handbook | One design artifact; no source/tests/policy/ledger/ref changes, no self-approval, no source execution; separate QC/Merger remain authoritative. | Candidate scope check below; P6 unmet |
| SECURITY minimum privilege and privacy | No implied subprocess/write/cross-module scope, reviewed local-only broker gate, admission before persistence, closed metadata outputs and revocation behavior. | P3–P5 and runtime evidence pending |
| Existing Backend/Core/handoff APIs | Additive future index contract only; no existing schema/API changes or reliance on private task responses; preserve public behavior and shadow status. | Inspected; T13 NOT_RUN |
| ATLAS Monitor read-only contract | No dependency, mutation, runner invocation or fabricated slots. | Documentation-only; future T13 pending |
| BASE-001 and BACK-013 boundary | Dependency report is not independently accepted; BACK-013/BACK-002 runtime work excluded from BASE-015. | P2/P3 unmet |
| Ordered child completion | S01 traceability precedes S02 contracts, S03 safety, S04 tests and this S05 review. These sections supply design evidence, not execution or approval evidence. | Supervisor/QC decisions pending |

Allowed-path proposal and this candidate's complete scope:
`docs/tasks/BASE-015-INDEX-DESIGN.md` only, add/modify documentation.
No source, tests, fixture, configuration, policy, database or tool changes; no
deletion, rename, commit, push, fetch, ref change, deployment, external message or
subagent. A future BACK-013 allowed-path proposal must be separately prepared
against its then-current integration base and approved after P1–P6; this design
does not preauthorize runtime paths or mutate task status.

Review order: Supervisor verifies S01 dependencies and scope, Backend/security
reviewers resolve P1–P5 and versioned contracts, independent QC evaluates the
design and future acceptance plan, then authorized controller records review
state. Implementation may start only under a new bounded runtime packet. Recheck
base/dependency freshness and patch compatibility at that point; no remote or
integration-branch freshness was established by this task.

## Candidate check record and handoff

Performed: read-only local status/HEAD/branch inspection; architecture SHA256;
bounded repository document and interface inspection; task/dependency metadata
inspection. Working-tree scope check observed only this untracked Markdown file
and no tracked changes. Explicit no-index diff check emitted no diagnostics
(exit 1 denotes the new-file difference); direct document inspection found no
trailing whitespace or conflict markers and confirmed S01–S05 section order.
No runtime tests were run, and none are claimed to pass.
The design contains only fixed labels, public contract paths and bounded
metadata; private paths, source snippets and full execution records are omitted.

`BASE-015 | start SHA 7a8cb685baa1abf7d10d0bf1b35fd98024cb6f9f | branch feature/astra-base-015-a5-0b478688 | changed files docs/tasks/BASE-015-INDEX-DESIGN.md | checks local metadata/digest/document/interface inspection, documentation scope/whitespace/conflict-marker checks; no runtime tests | evidence this design and local check outputs | state DRAFT/NOT_VERIFIED | blocker architecture digest mismatch, BASE-001 qualification, runtime contracts/grants/provenance and Supervisor/QC approval pending`
