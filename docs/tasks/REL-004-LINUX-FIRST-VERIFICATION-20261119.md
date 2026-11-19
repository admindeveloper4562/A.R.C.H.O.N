# REL-004 Linux-first verification

Status: `LINUX_SCOPE_VERIFIED / WINDOWS_MACOS_NEEDS_VERIFY`

This candidate reuses the provider handoff, bounded-context reconstruction,
idempotent tool-effect journal and local-agent implementation already present
in the reviewed Git integration. It does not claim a Windows host, a Windows
Ollama service, a macOS host, or native Apple tooling.

## Source binding

| Field | Value |
| --- | --- |
| Task | `REL-004` |
| Base SHA | `75582dbf48057e3d5b0e7cf4acfdba2386acfcff` |
| Implementation source | `7a521a1` (`feat(sda): sync Astra integration checkpoint 521304d [REL-004..REL-017]`) |
| Scope amendment | `REL-004-LINUX-FIRST-20261119` |
| Amendment SHA-256 | `db2112a87f3edf2256833b67518a767c7a7c584bdf3e870d930dd42d809605e5` |
| Candidate SHA | Recorded in the bound Astra Main Codex submission receipt |

## Locally verified Linux evidence

The following focused suites run against the reviewed implementation with
exit code 0:

```text
tests.test_backend_handoff
tests.test_backend_routing
tests.test_backend_windows_agent
tests.test_backend_acceptance
tests.test_backend_ollama_profile
tests.test_rel004_cross_device
```

The checks cover provider selection and explicit handoff, bounded context
reconstruction, permission-scoped tool effects, stale lease rejection,
idempotent job completion, duplicate-effect rejection and replay-safe receipts.
The independent QC receipt binds the exact candidate SHA, changed-file list,
test artifact and child evidence.

## Deferred verification

`NEEDS_VERIFY` after the future Windows transfer ZIP and native macOS evidence:

- Windows host/service/Ollama measurements and host-specific transport.
- macOS/native Apple tooling and device acceptance.
- Any cross-device claim that requires those environments.

The deferred checks remain visible and are not converted into Linux passes.
No credentials, private runtime state, prompts or raw model payloads are
included in this report.
