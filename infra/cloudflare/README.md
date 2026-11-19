# Cloudflare monitor installation contract

The supported Cloudflare artifact is the metadata-only monitor at
`bootstrap/astra-one/cloudflare/astra-one-monitor`. Its package manifest,
Worker source, D1 schema and Wrangler example are the source of truth. This
directory documents the repository-level deployment boundary; it is not a
second Worker implementation.

## Local verification

From the monitor directory, install the package-declared development tools and
run the offline checks:

```powershell
npm install
npm run typecheck
npm run smoke
```

`wrangler.toml` is ignored and must be created locally from
`wrangler.toml.example`. Replace only the D1 UUID in that private file. Use an
owner-authenticated Wrangler session for any remote D1 schema or deployment
operation.

The only accepted secret names are `ASTRA_INGEST_TOKEN` and
`ASTRA_VIEW_TOKEN`; their values must be entered through Wrangler's secure
prompt and must never be committed, printed, or placed in task receipts.

The Worker is a monitor, not a command channel: it does not run Codex, claim a
task, access the host, or pull executable work from a central queue. Remote
deployment and live D1 evidence are owner-operated external gates.
