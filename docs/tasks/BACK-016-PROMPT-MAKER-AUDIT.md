# BACK-016 — Prompt maker and template reproducibility audit

**Task:** `BACK-016`  
**Execution mode:** `audit`  
**Candidate base:** `80e049bb26e054ce9673866b475fb3f0aab36576`  
**Scope:** bounded evidence and decision record only

## Decision

The existing Backend has the primitives needed for a small prompt-maker
implementation, but it does not currently provide template versioning or a
prompt audit record. This audit specifies the smallest compatible contract for
a later implementation task. It does not claim that the prompt maker is
implemented or that any rendered prompt was retained.

The implementation should render in memory from a version-pinned template and
bounded structured context, then retain only digests, references and audit
metadata. A provider, model, or fallback must not be part of the reproducible
template result.

## S01 — Evidence inventory

| Evidence | Observed fact | State |
|---|---|---|
| `src/jarvis_v2/backend/context.py` | `ContextPacker` canonicalizes JSON, bounds bytes/tokens, preserves requirements/policy/receipts, and rejects restricted field names. | Verified |
| `src/jarvis_v2/backend/conversation.py` | `ConversationStore` provides ordered, idempotent turns, but its content column is not an appropriate prompt-source audit store. | Verified |
| `src/jarvis_v2/backend/event_bus.py` | `EventBus` bounds payloads and records privacy scope, hashes and delivery receipts; it is not a template registry. | Verified |
| `src/jarvis_v2/backend/handoff.py` | `HandoffStore` preserves bounded provider-neutral context and effect metadata; it does not version prompt templates. | Verified |
| Backend package exports | Existing exports cover context, conversations, events, handoffs, routing and retrieval. No prompt-maker or template registry symbol exists at the candidate base. | Verified |
| Task packet | `BACK-016` is `execution_mode=audit`; S03 requires a versioned record and S04 requires an independent cross-check. | Verified |

No source content, private context, credentials or full database payload was
copied into this report.

## S02 — Findings matrix

| Acceptance clause | Finding | Required evidence | State |
|---|---|---|---|
| Prompts are reproducible | A template ID/version, template digest, canonical input digest and context digest are required inputs to one render. | Same inputs produce the same rendered-output digest. | Specified; not implemented |
| Sensitive raw sources are not stored | Existing `ContextPacker` can reject restricted fields, but `ConversationStore` can persist turn content and therefore must not be used for raw prompt retention. | Storage test proves only digests/references/metadata are persisted. | Gap identified |
| Template versioning | No current registry exists. Use an immutable `(template_id, version, template_sha256)` identity; a changed body is a new version. | Version conflict and changed-template tests. | Gap identified |
| Bounded execution | Reuse `ContextPacker` limits and add a prompt-specific output byte/token ceiling before rendering. | Oversize input/output is rejected without persistence. | Specified; not implemented |
| Auditability | Record task ID, template identity, source-reference digests, context digest, output digest, timestamp and result code; exclude rendered text. | Receipt shape and redaction test. | Specified; not implemented |

## S03 — Minimal implementation contract

The later implementation should add one Backend-owned component, without a
schema reset or provider dependency:

1. `PromptTemplate`: immutable ID, semantic version, body digest, bounded
   allowed-field names and a canonical rendering function.
2. `PromptBuildReceipt`: task ID, template ID/version/digest, input/context
   digests, output digest, estimated tokens, source-reference digests,
   timestamp and outcome. It must not contain rendered text or source bytes.
3. Canonicalization must use sorted, finite JSON with bounded UTF-8 size and
   the existing restricted-field policy. Timestamps and provider responses
   must not affect the output digest.
4. Replaying the same template and canonical inputs returns the same output
   digest. Reusing a template ID with a different body digest is rejected.
5. The component may use `ContextPacker` for the bounded context packet. It
   must not write raw prompt content to events, telemetry, task receipts or
   the persistent audit record.

Rejected alternatives: persisting complete rendered prompts for convenience,
using conversation history as an implicit template registry, silently
rewriting an existing template version, or routing a failed local render to a
different provider.

## S04 — Cross-check and test plan

The independent implementation/QC task must verify:

- identical inputs and a pinned template produce identical digests;
- template version or body changes produce a new identity;
- restricted fields, malformed values and size limits fail closed;
- no rendered text or source bytes occur in the stored receipt;
- source references are digest-bound and remain inspectable;
- replay is idempotent and does not duplicate a receipt; and
- the existing context, event, conversation, retrieval and handoff tests
  remain passing.

This audit report is the only candidate change for `BACK-016`. It records the
implementation boundary and evidence gaps; it does not mark the future
runtime behavior as complete.

**Handoff:** `BACK-016 | start_sha 80e049bb26e054ce9673866b475fb3f0aab36576 | candidate_sha pending | integration_sha pending | file docs/tasks/BACK-016-PROMPT-MAKER-AUDIT.md | independent_qc pending | merger pending | blocker none for bounded audit record`
