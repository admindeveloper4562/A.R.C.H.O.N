# Security acceptance

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Result: local security checks PASS with external enforcement gaps.

## Checks passed

- Local dependency, secret, and source security scans passed.
- pip-audit found zero known vulnerabilities in the three pinned runtime dependencies at test time.
- Tracked candidate files contained no detected credential-token or private-key markers. Personal host-home prefixes were replaced with the generic $ARCHON_HOME placeholder in 92 current documentation occurrences. Git history was not rewritten.
- Container ran as UID/GID 10001, with read-only root, all capabilities dropped, no-new-privileges, and no network for the core smoke test.
- Unauthorized task admission was rejected before queue insertion. Unauthorized workspace effect was denied. Approval, capability scope, replay/idempotency, path boundary, and cancellation negative cases are covered by tests.
- Test signing identities and test runtime state were not included in wheel, sdist, container image, or source commit.

## Limits

- Test approvals used disposable Ed25519 identities. No production owner signing key or valid standing delegation was installed or inferred from chat authorization.
- The local Ollama gateway was loopback-only. No private task data was sent to an external provider.
- Hosted GitHub Actions was not run because billing was unavailable. Local verification is not equivalent to GitHub-hosted enforcement.
- At the remote policy inspection on 2026-11-21, develop protection and required checks were not enabled; the rulesets query was empty and branch-protection detail was unavailable. Recheck the actual remote before merge.
- Imported Astra verification/provenance records retain three absolute local-path occurrences; they are bound by the source manifest and were preserved to keep provenance intact. The current tracked audit documentation normalizes 92 personal-home prefixes; three historical Blender-manifest path fields are redacted while preserving asset hashes. Three occurrences remain in manifest-bound imported Astra provenance files and were preserved to keep source integrity. No history rewrite was performed.
- No real financial, communication, public-network, production-service, or external-system effect was attempted.
