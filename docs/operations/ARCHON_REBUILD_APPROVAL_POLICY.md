# ARCHON rebuild repository approval policy

**Task:** BASE-016
**Status:** Owner-approved policy; implementation remains subject to independent QC and serial integration.

## Decision

The canonical ARCHON rebuild repository is the existing
`admindeveloper4562/A.R.C.H.O.N` repository. This decision does not create a
new repository and does not authorize a release or deployment.

The historical `admindeveloper4562/personal-jarvis` repository remains an
immutable reference source. It is not a write target and is not installed as
runtime code.

## Authorized migration scope

Only reviewed, SHA-pinned material may be integrated:

- source code and tests;
- architecture and module contracts;
- compatible configuration;
- documentation and migration provenance.

The migration excludes runtime databases, secrets, private checkpoints, raw
model conversations, credentials and personal data. Imported legacy material
remains a reviewable candidate until deterministic checks, independent QC and
serialized integration have passed.

## Branch and promotion policy

- `develop` is the only serial integration target.
- `main` remains release-protected and unchanged by this task.
- Candidates use isolated task worktrees and immutable base SHAs.
- Independent QC reviews the exact candidate commit.
- Only the serialized Merger may integrate an approved candidate.
- No force-push, history rewrite, automatic release, production deployment or
  native SDA cutover is permitted.
- A later promotion requires its own exact candidate digest and owner gate.

## Required sequence

```text
owner decision -> bounded candidate -> deterministic tests
-> independent QC -> serialized Merger -> develop checkpoint
```

No repository creation, source migration or protected-branch promotion may
occur before the applicable gate and evidence exist. An owner decision never
waives technical prerequisites, provenance review, security checks or QC.

## Recorded owner decision

The deterministic Master records the following digest-bound decision for this
task:

| Field | Value |
|---|---|
| Decision | `APPROVE` |
| Owner identity | `owner` |
| Decision time | `2026-11-16T14:49:55.266798Z` |
| Task payload SHA-256 | `1d50cea718ce37804864a81aa33577a6a223b56db51a8af564512743dd2c59a9` |
| Approved architecture SHA-256 | `295e0ec823e8a26635cd0d818be0fc5af12953589d2ada83f27314216c65db89` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration SHA | `b25949dd1390a75148026639a70214678a82dc15` |
| Owner receipt SHA-256 | `439d0f6a8b790f115903aeb94b088dcf17dc82f6477ae3a4a0b4cf92f1d292dd` |

The private signed receipt and its trust-anchor verification remain in the
authoritative owner-approval ledger, not in Git. The candidate submission and
Merger receipt must separately bind the final candidate SHA, changed-file
digest, test evidence and resulting integration SHA.
