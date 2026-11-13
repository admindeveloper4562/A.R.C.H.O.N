# Astra One → Native JARVIS v2 SDA: phased handover

## Non-negotiable two-controller rule

The external Astra One builder remains independently operable while it develops the v2 SDA. Two Masters must never execute against the same integration branch or SQLite queue simultaneously. SDA cannot approve its own transition. Guardian never serves as a free-for-all self-modification authority.

## Steps
1. **External bootstrap:** run Astra One from a separate trusted install, with a clean source checkout of the new v2 repo. Review and pin the architecture, STOP/PAUSE controls, model entitlement, quotas, and sandbox.
2. **Source migration:** stage old code as non-executable candidates using `tools/import_legacy.py`, verify SHA/provenance, independently review and port one module at a time.
3. **Shadow native SDA:** implement v2 SDA queue, task session, five workers, independent QC, serialized Merger, code indexing and reliable state. Read actual events from Astra via scoped sanitized export but **do not claim jobs or write the live integration branch**.
4. **Qualification:** demonstrate real five-worker Codex run, independent QC, crash/lease recovery, duplicate action prevention, quota pause, failure report, rollback and protected-branch policy on a disposable project. Existing mock Astra tests are not sufficient.
5. **Standby candidate:** build a reproducible immutable SDA release artifact with digest/provenance, human-reviewed QC receipt, rollback target and compatibility statement. Do not ship secrets in the artifact.
6. **Drain and fence:** owner approves cutover; pause external Astra task intake, let current work finish or checkpoint, persist state, revoke Astra's write lease for target, verify exactly one writer. If state import fails, keep Astra active and native in shadow.
7. **Guardian deploy gate:** independent Guardian/watchdog stages v2 SDA on standby and validates health, task replay, locked paths and STOP state; atomically switches only the authorized route after all gates pass. Preserve external Astra and previous SDA version for rollback.
8. **Post-cutover soak:** observe real project cycle and crash drills. If failure, Guardian's deterministic watchdog reverts the routing to the last-known-good and fences the failed writer.
9. **Retire external builder:** *only after owner approval and stability evidence* may Astra One stop handling new work. Preserve recovery artifact, source and logs; do not delete without separate file approvals.

Astra One may continue to maintain native SDA as an **external rescue builder**. Native v2 SDA updates itself only by creating candidates that independent QC and privileged Guardian deployment policy validate.

## Approval gates (all mandatory)
- Real developer host verified and CI jobs actually executed.
- Candidate SHA, tests, independent reviewer and security checks recorded.
- STOP/PAUSE, quota and approval state restore correctly after restart.
- No two live writers. Queue/task checkpoint migration is reversible and tested.
- Guardian out-of-process watcher functional and rollback artifact verified.
- Human owner authorizes the production cutover. Guardian model cannot approve this gate.

## Architecture context size
The full consolidated architecture may exceed Astra One's 30K-character Supervisor prompt limit. Keep the full SHA256 as authoritative; use separately reviewed focused task packets per milestone. Do not silently truncate requirements or disable context checks.

## Identity and monitoring boundary

- **ARCHON** is the main conversational/orchestrating intelligence; it requests work through **ATLAS** deterministic policy/queue infrastructure.
- **AEGIS** is the independent Guardian AI; a separate trusted watchdog authorizes staged recovery/deployment and must remain outside the self-updated component.
- `python3 tools/atlas_monitor.py --source astra --watch` is a **separate, read-only** status process. Never make it a scheduler or a cutover gate and never treat stale task states as proof a runner is alive.
