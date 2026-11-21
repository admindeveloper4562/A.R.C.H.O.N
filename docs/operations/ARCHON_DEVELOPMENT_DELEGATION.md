# ARCHON development delegation — owner signature required

**Policy:** `config/autonomy-policy.json`, schema `archon.autonomy-policy/v1`, revision 1

**Status:** `PENDING_OWNER_SIGNATURE_AND_RUNTIME_ENFORCEMENT`

**Activation:** disabled; this proposal grants no machine capability.

## Proposed scope

The policy limits autonomous development to the existing public repository
`admindeveloper4562/A.R.C.H.O.N`, task-scoped branches, local tests, disposable
unprivileged test state, and the listed network destinations. It permits a
develop merge only after exact-candidate testing, independent QC, and any
GitHub-enforced requirements. It denies changes to `main`, force-pushes,
visibility or access changes, credential export, production writes/deploys,
real finance or communications, trust-root changes, and emergency-stop
clearing.

The policy uses the repository-scoped GitHub connection already configured by
the owner. It contains no credential material and creates no new GitHub token
or signing identity. The existing owner-approval ledger remains the trust
source.

## Why it is not active

The existing `AuthorizationServer` grants short-lived module scopes and checks
digest-bound `OwnerApproval` values; it is not a repository-operation policy
loader and does not itself verify an Ed25519 delegation. The native executor's
signed approval path is separate. No policy loader, policy-bound delegation
receipt, or production owner signature for this scope has been verified.
Consequently this file is a signing-ready specification only. Do not infer
authority from its presence or from conversational text.

## Owner signing mandate

To activate this delegation, the owner must review the complete JSON policy and
authorize its exact SHA-256 in the existing authoritative approval ledger.
The Master must verify the receipt using the already trusted owner identity,
record an explicit `issued_at` and `expires_at` no more than 90 days apart, and
bind the receipt to policy ID `ARCHON-DEVELOPMENT-DELEGATION`, revision 1, and
the policy digest. No signing key or signature is to be added to Git.

The authorization is limited to the listed repository-development operations.
It does not alter protected-branch rules, owner gates, STOP/PAUSE, ASEL, the
Guardian trust root, or the exclusions in `SECURITY.md`. A signed policy alone
is insufficient for use: a reviewed loader/enforcer and negative tests must
reject expired, revoked, malformed, wrong-repository, wrong-branch, and
out-of-scope requests. The owner may revoke it through the approval ledger;
STOP immediately denies new work and cannot be cleared by the agent.

This draft should enter its own review and integration decision. The builder
does not approve or activate its own policy.
