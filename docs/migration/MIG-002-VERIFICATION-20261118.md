# MIG-002 verification — GitHub Free development-security baseline

This task record preserves the original acceptance and records the owner-
authorized versioned amendment. It does not claim GitHub-hosted branch
protection or hosted CI as passed.

## Identity

| Binding | Value |
| --- | --- |
| Original parent plan SHA-256 | `10cb1ed53eace6af1c5d052ef0ad0a85eaf9f535db5ae0be794cc7d12752b154` |
| Original MIG-002 payload SHA-256 | `cb42941bde888c64c1b888b6c15b28278624ac481956dfc41ca7079c7e238e93` |
| Amendment | `MIG-002-GITHUB-FREE-20261118` v2 |
| Amendment payload SHA-256 | `3dcd4e9c599ee30505b054da24252c85a1dbc7cb502ad610e0698b74451faf39` |
| Amendment artifact SHA-256 | `14906d45d95d6792a1af8f901bf8bba79ae98ba385be02d2f1cb0860853c4ba3` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration SHA | `43f7af8099ddfd0a4a8f239f1becd63ee1738736` |

## Acceptance matrix

| Original clause | Result under amended baseline | Evidence |
| --- | --- | --- |
| Server-enforced `main`/`develop` protection and rejected unauthorized push | Not available on the private GitHub Free plan; HTTP 403 was observed. Not claimed as passed. | Read-only GitHub API result; amendment residual-risk entry |
| Local policy and review gate | PASS | Local Git policy, SHA ancestry, signed-receipt support, independent QC and serialized Merger checks |
| Provenance and integration | PASS | Candidate/base/integration SHAs and watchdog activation receipt are recorded in Astra state |
| Hosted CI | `DEFERRED_PLAN` | Existing workflow/run metadata recorded; no hosted result is substituted by local tests |
| Safe publication | PASS for the local baseline | Fast-forward-only watchdog/Merger path; no force-push and no `main` modification |

The immutable plan remains the source of the original requirement. The Master
recorded the amendment transactionally in `task_plan_amendments`, after a
verified SQLite checkpoint, and then re-admitted MIG-002 through its external
resolution path. The stored graph binding remains 247 parents, 1,359 children
and 446 dependency edges with the hashes in the amendment JSON.

## Child evidence

- `MIG-002.S01`: repository visibility, GitHub protection response, workflow
  metadata, local policy and integration checkpoint inspected.
- `MIG-002.S02`: each original clause mapped to supported, deferred or
  residual-risk evidence; no local check was represented as remote enforcement.
- `MIG-002.S03`: this versioned decision record and the amendment JSON are the
  bounded deliverables.
- `MIG-002.S04`: independent QC must recheck the listed SHAs, path scope,
  amendment record and absence of secrets before merge.

## Explicit non-claims

The private repository was not made public, GitHub Pro was not purchased, no
unauthorized push was attempted against the real repository, hosted CI quota
was not consumed, and the original task-plan payload was not overwritten.
