# REL-012 — Security adversarial matrix

**Status:** locally verified against integration base `eecc5a70ce7b06b4ec19cb8d622846ba7ba8cbb9`.

**Parent:** REL-012 — Run full security adversarial matrix against each module

**Acceptance:** Injection, authentication, path, CSRF, XSS, secrets and prompt boundary tests pass.

This is a verification-only candidate. No application source, security policy,
owner approval, credential, device, production service or hosted workflow was
modified or accessed.

## Acceptance matrix

| Boundary | Result | Evidence and limitation |
| --- | --- | --- |
| Injection and failure handling | PASS | Core, Guardian and REL fault-injection tests pass; the full local suite passes. No source-backed injection sink was identified in the reviewed authorization, context, runtime or file-action boundaries. |
| Authentication and authorization | PASS | Module-scoped grants, exact owner-approved cross-module grants, identity conflicts, expiry and revocation fail closed in `test_backend_authorization.py`; connector revocation is covered by backend acceptance tests. |
| Path safety | PASS | File actions enforce allowed roots, protected paths, per-file approval, identity re-checks and recoverable trash. Browser operations are typed and do not expose a generic operation. |
| CSRF and browser response boundaries | PASS | Runtime mutations require the matching owner session, host/origin and CSRF token. Invalid host, origin, identity and token values fail closed. Responses set `X-Frame-Options: DENY` and a `frame-ancestors 'none'` CSP and do not emit wildcard CORS. |
| XSS/instruction boundary | PASS FOR REVIEWED CODE | Browser adapter output is explicitly marked untrusted page data; sensitive form fields and untyped browser execution are rejected. No HTML-rendering or live browser surface was exercised. |
| Secret handling | PASS FOR REVIEWED CODE | Secret values are allowlisted, size-bounded, redacted from representations and telemetry, and missing/unallowlisted values fail closed. The bounded credential-shaped scan found no private-key or common provider-token matches under `src/`, `tests/`, `config/` or `docs/`. |
| Prompt/context boundary | PASS | Context packing rejects restricted raw-prompt fields, preserves requirements/policy/receipts under history reduction, and fails closed when protected content cannot fit. Browser page instructions remain untrusted data. |

## Source-backed controls reviewed

- `src/jarvis_v2/backend/authorization.py`: identity, module scope, exact
  approval binding, TTL, revocation and fail-closed authorization.
- `src/jarvis_v2/backend/connectors.py`: connector allowlists, bounded grants,
  revocation and redacted grant metadata.
- `src/jarvis_v2/backend/secrets.py`: allowlisted retrieval, bounded values,
  redacted `SecretValue` representations and safe metadata.
- `src/jarvis_v2/backend/context.py`: protected context fields, bounded
  history and deterministic protected-content digest.
- `src/jarvis_v2/runtime/security.py` and `service.py`: host/origin/session/
  CSRF checks and hardened response headers.
- `src/jarvis_v2/runtime/file_actions.py`: allowed-root and protected-path
  checks, per-file approval, identity fencing, trash recovery and redacted
  audit records.
- `src/jarvis_v2/runtime/browser.py`: typed browser operations, confirmation
  for side effects, sensitive-field rejection, bounded adapter output and
  untrusted page-data marking.
- `src/jarvis_v2/core/session.py` and `src/jarvis_v2/monitor.py`: bounded,
  redacted context/monitor boundaries.

## Child evidence

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-012.S01` | PASS | Matrix above maps each required security boundary to implementation controls and deterministic tests. |
| `REL-012.S02` | PASS | Tests use temporary SQLite/filesystem fixtures, synthetic values and no live credentials or provider payloads. |
| `REL-012.S03` | PASS | Focused security matrix and the complete local regression suite exited zero. |
| `REL-012.S04` | PASS | Negative coverage exercises invalid identity/origin/CSRF, expired/revoked grants, protected/outside paths, changed-file identity, sensitive browser fields, raw prompt retention and fault-injection paths. |
| `REL-012.S05` | PASS | This report is bound to the candidate base and records external/hosted limitations without converting them into passes. |

## Commands and results

```text
PYTHONPATH=tests:src:bootstrap/astra-one python3 -m unittest -q \
  test_backend_authorization test_backend_secrets test_core_event_guard \
  test_core_model_policy test_runtime_security test_runtime_file_actions \
  test_runtime_browser_tools test_rel_cross_module_contracts \
  test_rel_fault_isolation
Ran 28 tests — OK (exit 0)

PYTHONPATH=tests:src:bootstrap/astra-one python3 -m unittest -q \
  test_core_fault_injection test_guardian_fault_injection
Ran 8 tests — OK (exit 0)

PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s tests -q
Ran 516 tests — OK (exit 0)

credential-shaped source scan using the installed local `rg`
No credential-shaped matches in src/, tests/, config/ or docs/
```

The full suite emits the expected read-only monitor argparse diagnostic while
testing the monitor entry point; the suite still exits zero. No GitHub Actions
workflow was dispatched. Hosted-only evidence remains deferred under the
repository quota policy. No live browser, external provider, Windows device,
production service or user financial data was accessed.

## Independent scan limitation

A separate Codex Security standard scan was started for this exact base and
scope. Its preflight completed, but the delegated read-only baseline and
architecture review did not return a usable artifact within the bounded review
window; therefore that plugin scan is not represented as a passing result here.
This receipt relies on the source-backed review and deterministic local tests
listed above and does not claim coverage outside them.
