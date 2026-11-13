# ADR-0001: Clean rebuild with external Astra One and staged code reuse

**Status:** Proposed, owner acceptance required.

**Decision:** create new private `jarvis-v2` repository with a normalized layout, new protected branches and fresh initial history. Keep legacy `personal-jarvis` immutable for reference. Import legacy code only as SHA-pinned candidates, then port behind clean module contracts. Build native v2 SDA via external Astra One in isolated worktrees; replace it only after independent Guardian watchdog verification, reversible cutover and owner approval.

**Why:** legacy branches include valuable runtime, Workhorse, TWS and Cloudflare code but divergent draft PRs and unverified native acceptance. Copying the entire repo would carry case-colliding files, generated artifacts, unresolved CI gates and conflicting process controllers.

**Alternatives rejected:** merge all legacy branches directly; let native SDA self-approve and restart itself; run two Masters simultaneously; create a single gigantic all-modules PR.

**Consequences:** additional migration tests and audits, but a more auditable long-term codebase with clean ownership and releasable artifacts.
