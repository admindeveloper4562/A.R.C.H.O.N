# MIG-002 GitHub protection alternative

Status: **remote GitHub acceptance remains blocked; local development can continue
without weakening the repository or making it public.**

## Observed limitation

On 2026-11-18, the private repository
`admindeveloper4562/A.R.C.H.O.N` returned the GitHub plan limitation below for
both protected branches and repository rulesets:

```text
HTTP 403: Upgrade to GitHub Pro or make this repository public to enable this feature.
```

This is a hosting-plan capability boundary, not a repository defect. There is no
safe bypass. Making the repository public would expose private ARCHON source and
is outside this task's authorization.

## Safe local alternative

Until a paid GitHub plan or an owner-approved private Git forge is available:

1. Keep `main` unchanged and treat `develop` as a local serial-Merger target.
2. Require the deterministic Master to own the integration checkpoint.
3. Run the repository branch/commit policy and local test suite before each
   candidate is accepted.
4. Keep hosted-only branch-protection and CI clauses explicitly `DEFERRED_PLAN`;
   local tests do not substitute for remote enforcement.
5. Publish only after an owner-authorized, fast-forward-only operation; do not
   force-push or claim remote protection.

Representative local checks:

```sh
python3 tools/check_git_policy.py \
  --branch fix/release/REL-005-pending-jobs \
  --commit "$(git log -1 --format=%s)"
python3 -m unittest discover -s tests
```

The local alternative preserves development safety and evidence integrity, but it
does **not** satisfy MIG-002's required GitHub-hosted protection/rejected-push or
executed-hosted-CI evidence. MIG-002 must remain blocked until those remote
requirements are available or the owner approves a task-plan amendment.
