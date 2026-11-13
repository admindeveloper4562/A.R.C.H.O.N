# Directory ownership and naming

```text
.github/             Actions CI, PR templates, CODEOWNERS, issue forms
apps/                Owner-facing web/desktop/iOS frontends (not active yet)
agents/              Agent role definitions and prompt manifests (reviewed)
config/              Versioned, non-secret module manifests and import allowlist
docs/                Architecture, ADRs, engineering rules, tasks, operations
infra/               Cloudflare Worker, systemd and Windows host deployment manifests
migration/imported/   Review-only pinned legacy code candidates, not executable
migration/provenance/ SHA and license/candidate audit trail
packages/            Shared reusable packages (when implemented)
services/            Independently deployable processes / control planes
src/jarvis_v2/       Canonical Python package, one directory per active module
tests/               Unit, regression, integration and safety checks
tools/               Repo bootstrap, migration, developer validation and standalone ATLAS monitor
```

Use Python `snake_case` for modules/functions, `PascalCase` for classes, `kebab-case` for Git branches and Markdown documentation groupings, and unpadded semver. No `business/` package or service should be created unless scope changes. The `apps`, `agents`, `packages` and `services` areas are reserved for accepted implementations rather than duplicated placeholders presented as working systems.
