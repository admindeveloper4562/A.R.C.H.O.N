# Current security status

Qualified application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb.

- Local dependency, secret, and source security scans passed; pip-audit reported zero known vulnerabilities in three pinned runtime dependencies at test time.
- Container test used UID/GID 10001, read-only root, all capabilities dropped, no-new-privileges, and no network for the core smoke.
- Invalid admission and unauthorized effects were rejected. Test keys were ephemeral and are not a production trust root.
- The local model path was loopback-only. No private data was sent to an external model service.
- GitHub-hosted Actions was unavailable and not run. Develop protection was not enabled at the prior remote inspection; refresh remote policy before merging.
- Current audit docs normalize 92 personal-home prefixes; the Blender test manifest paths are redacted. Three absolute path occurrences remain in manifest-bound imported Astra provenance records. Public history was not rewritten.
- Finance, communication, public-network, and production service effects remain disabled.

See SECURITY_ACCEPTANCE.md for complete evidence and limits.
