# MIG-002 GitHub protection alternative

## Versioned plan amendment

The owner-authorized GitHub Free baseline is recorded in
[`MIG-002-GITHUB-FREE-AMENDMENT-v2.json`](MIG-002-GITHUB-FREE-AMENDMENT-v2.json).
The immutable original parent plan remains unchanged. The Master records both
the original plan SHA-256 and the amendment payload SHA-256, together with the
247-parent/1,359-child/446-edge graph binding, before re-admitting MIG-002.

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
does **not** provide GitHub server-side rejection of an unauthorized push. The
amended baseline therefore records hosted protection and hosted-only CI as
`DEFERRED_PLAN`, never as passed local evidence. MIG-002 may complete only after
the amended local acceptance matrix, independent QC and serialized integration
have passed.
