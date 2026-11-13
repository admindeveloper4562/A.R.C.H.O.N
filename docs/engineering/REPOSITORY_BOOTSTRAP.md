# ARCHON empty-repository bootstrap — one clean main commit

Target: private `admindeveloper4562/A.R.C.H.O.N`, which must exist and have no Git heads. Run `bash tools/archon_bootstrap.sh` from a clean extracted combined foundation on Ubuntu.

The script verifies the bundled Astra One manifest and 23+49 local tests, verifies the pinned architecture and fetches the separately tracked JARVIS v2 task backlog; it then creates exactly **one root Git commit** on `main` with ARCHON/AEGIS/ATLAS foundation and `bootstrap/astra-one` source. `develop` starts from the same SHA, without a second commit. It does not rewrite the old personal-jarvis repository.

After bootstrapping, it creates a separate clean `develop` source clone, initializes an isolated Astra One state, approves the reviewed focused architecture and enqueues five explicit low-risk kickoff tasks. It validates authenticated Codex CLI and Docker, then starts a user-level systemd timer. No existing state, branch, repository or sensitive data will be overwritten.

See [managed service and safety controls](../operations/LINUX_ASTRA_SERVICE.md). GitHub branch protection/CI must be inspected after initial push; protected main should then be locked against direct automation.

If you have **already** initialized the GitHub repository, this one-root script intentionally refuses to push. Contact the operator to reconcile the existing history without `reset --hard` or force push. The legacy `tools/bootstrap_github.sh` is a no-op shim.

If a late post-push preflight (Codex, Docker, systemd user manager) fails, run `bash tools/archon_resume.sh` after addressing the dependency. Never force-rewrite an already-pushed main commit.
