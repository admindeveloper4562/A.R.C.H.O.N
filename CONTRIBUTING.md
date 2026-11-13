# Contribution / review workflow

1. Create an approved task with immutable ID and acceptance criteria; use a documented branch in an isolated worktree.
2. Make small focused commits following [commit policy](docs/engineering/BRANCH_COMMIT_POLICY.md).
3. Run `python3 -m unittest discover -s tests -v` and code/repo checks.
4. Open a PR into `develop` using the template; record imported source SHAs and license notes if applicable.
5. Pass independent QC, integration CI and a serial Merger gate. Human approval required for deployment and protected-branch promotion.

Draft work and skipped CI are never presented as merged or released.
