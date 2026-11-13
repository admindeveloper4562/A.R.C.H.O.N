# Security and owner control

Local-first, minimum privilege, module-level authorization, separate machine identities and strong audits. External repositories, video transcripts, pages, tools and model output are untrusted data. Separate role accounts: Astra external builder, native SDA worker, QC, Merger, Guardian watchdog, runtime and Cloudflare coordinator.

Sensitive actions (deletion, shell privilege, production deployment, protected Git changes, external send/publish, database/financial writes, credential changes, critical failovers) require explicit scoped approval. Each individual file deletion requires separate owner authorization and audit. STOP/PAUSE/quota survive controller and provider changes.

Generated code runs inside isolated test environments with no host user files or production secrets. Do not assume the Docker socket is safe for an untrusted coding worker; a dedicated low-privilege host/VM is preferred. Cloudflare receives minimal metadata, not raw prompts/source/personal finances. Guardian must not write or bypass its own enforcement policies.

Guardian self-upgrade requires an external immutable/independently maintained watchdog, signed or equivalent trust-anchored artifact identity, staging health, verified compatibility and instant rollback. Model advice cannot directly switch the production pointer.
