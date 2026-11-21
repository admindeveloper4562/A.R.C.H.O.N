# Security and owner control

This file is the mandatory policy entry point. The detailed threat model, active scanner, defences, incident lifecycle and release gates are defined in docs/architecture/SECURITY_ARCHITECTURE.md (ASEL-1.0).

## Non-negotiable rules

- Local-first, default-deny, least privilege, module-level authorization, separate machine/device identities and tamper-evident audit.
- ASEL is deterministic enforcement owned by ATLAS/Backend, not an LLM and not an eleventh functional module. Every tool/data operation is re-authorized at execution time.
- External repositories, video transcripts, pages, documents, tool outputs and model output are untrusted data; they cannot authorize tools or change policy.
- Short-lived, single-use capabilities are bound to subject, device, task, audience, resource, action, scope, expiry and nonce. Support immediate revocation and replay denial.
- Sensitive actions (deletion, shell privilege, production deployment, protected Git changes, external send/publish, database/financial writes, credential changes, critical failovers) require explicit scoped approval. Each individual file deletion requires separate owner authorization and audit.
- STOP/PAUSE/quota survive controller/provider changes. Emergency STOP and capability revocation work without a model or cloud service.
- Generated code runs in disposable low-privilege sandbox/VM environments with no host user files, SSH keys, production secrets/DBs, Docker socket or network by default. A Git worktree alone is not a sandbox.
- Active scans are non-destructive, bounded and limited to inventoried owner-controlled repositories, registered hosts, Cloudflare resources and staging endpoints. No third-party scanning, credential spraying or exploit execution. Production DAST requires explicit owner authorization.
- Required SAST, SCA, secret, license, SBOM/provenance, IaC/container, API/DAST and runtime checks must produce commit/asset-bound evidence. Scanner failure or missing/stale evidence fails closed.
- Critical findings block release. High findings block by default; only a time-limited owner-signed exception with compensating controls and retest may be considered.
- Cloudflare receives minimum operational metadata, not raw prompts/source/personal finances. Mira stays read-only; paper trading has no live broker-write capability.
- AEGIS is advisory. It cannot alter ASEL policy, disable sensors, approve its own release or replace the independent external watchdog. The watchdog verifies signed/trust-anchored artifacts, STOP, fencing and rollback.
- Preserve redacted evidence, source provenance, revocation receipts and per-file deletion audits in DELETE-LOGS.md. Never claim a mock or skipped scan passed.

## Incident response

Detect -> triage -> contain (STOP/quarantine/revoke/isolate) -> preserve evidence -> notify owner -> bounded reviewed repair -> signed known-good recovery -> re-scan -> verify -> post-incident regression.

## Security release gate

Independent QC must verify current scan evidence bound to the candidate SHA, SBOM/provenance/signature, authorization and prompt-injection tests, sandbox isolation, secrets redaction, API/runtime defences, containment/revocation, rollback and all required owner approvals. Unresolved Critical findings block release; High findings block unless the defined exception policy is satisfied.
