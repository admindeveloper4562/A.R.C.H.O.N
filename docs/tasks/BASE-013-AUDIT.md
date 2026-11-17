# BASE-013 — Cloudflare resource and authentication-boundary audit

Status: audit candidate

Audit base: `c0005bd44c169ddd71ab250d1b9ff29140d45a68`

The bounded read-only inventory was performed through the already-authorized
user-scoped Wrangler session. No mutating Wrangler command, SQL row query,
secret value read, deployment or credential change was performed.

## BASE-013.S01 — Inventory

The local restricted evidence artifact is identified by SHA-256:
`9785648345e14afd592a434e81dfff01d1ec900f6a30ef32850121558b2f2ed1`.

| Resource | Observed metadata |
|---|---|
| Account | Identifier retained only in the restricted local evidence artifact |
| D1 | `mira-finance`, ID `140fc8c8-c995-4cb7-b7d6-0649dc157e29` |
| D1 schema metadata | 13 tables reported; replication disabled; no rows read |
| Worker | `personal-management`, version `1f2dc83a-d844-4f39-bdda-e59300cb56e8`, deployed 100% |
| Worker binding | `DB`, type D1, bound to the Mira database ID above |
| Astra monitor | Not observed in the bounded Worker listing |
| Old coordinator | Not observed in the bounded Worker listing |
| Limits | Not exposed by the bounded read-only metadata commands |

The binding and version identifiers are resource metadata, not access
credentials. Secret/bearer values and full API responses were not retained.

## BASE-013.S02 — Authentication and boundary findings

- Authentication used the existing user-scoped Wrangler OAuth session.
- The session was used for identity, D1 metadata, Worker metadata, bindings
  and deployment metadata only.
- No write permission was used or required by the observed commands.
- The ARCHON boundary remains metadata-only and read-only; it does not use a
  shared D1 administrator capability.
- The account identifier is intentionally absent from this tracked report and
  remains in the restricted evidence artifact.

The bounded inventory does not establish that an Astra monitor or old
coordinator exists under another account, name or permission scope. That
remains an explicit unknown rather than a fabricated absence.

## BASE-013.S03 — Acceptance and remaining limits

| Acceptance item | Result |
|---|---|
| Existing D1 identity and metadata | Observed and source-bound |
| Worker identity, version and binding | Observed and source-bound |
| Authentication boundary | Observed; values redacted |
| Resource limits/quota | Unknown; endpoint did not expose them |
| Old coordinator and Astra monitor distinction | Unknown/not observed in bounded listing |
| Production change | None performed |

The available read-only authorization is sufficient for the bounded local
inventory and no further Linux coding retry is needed for this audit. Resource
limits and any differently named coordinator require a separately scoped
read-only query if they become necessary; this report does not infer them.

## BASE-013.S04 — Independent cross-check

- Candidate changed only this Markdown report under `docs/`.
- The report's resource values are limited to the restricted evidence
  artifact's sanitized metadata.
- The evidence SHA binds the report to the observed inventory without storing
  bearer values or raw responses.
- Unknown monitor/coordinator and quota fields are labelled as unknown.
- The current source and integration checkpoint were recorded before audit.

This audit does not deploy, rotate credentials, create databases, query user
rows or claim production readiness.
