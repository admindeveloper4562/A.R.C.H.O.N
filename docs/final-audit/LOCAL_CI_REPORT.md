# Local release verification report

Qualified application source SHA: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Package version: 0.0.3. Environment: Linux, Python 3.12.3.

## Result

- tools/verify_release.sh: PASS, 40/40 local workflow checks.
- Root unittest suite: 626 passed, 0 failed, 0 skipped in 43.560 seconds.
- Separate Astra coordination suite: 191 passed, 0 failed, 0 skipped in 61.476 seconds.
- Dependency scan, secret scan, source security scan: passed.
- pip-audit: 0 known vulnerabilities across three pinned runtime dependencies.
- Wheel and source distribution built, installed into separate disposable environments, checked with pip, exercised through installed CLI entry points, and uninstalled.
- Fresh source-built container acceptance and saved-image reload acceptance passed. Full logs, machine-readable reports, and the manifest remain in the local release evidence bundle.
- Hosted GitHub Actions: NOT RUN because billing was unavailable. Local verification does not replace hosted branch enforcement.

## Artifact checksums

| Artifact | SHA-256 |
|---|---|
| jarvis_v2-0.0.3-py3-none-any.whl | 674f83088441eeeaaac6718d8cc29ae53ed6ce482cc5b607608b1ce6a6155981 |
| jarvis_v2-0.0.3.tar.gz | 2ac610b9386e3907278d652aedc94829126b35affa566df5a4983a94cd88c45b |
| archon-local-image.tar | b7452422d6be305b2e5f803689c2956fcdf15f7074fc776eac0f0dc012ec1207 |

The Python artifacts have 116 wheel files, and the source distribution contains required module and identity configuration without runtime databases, credentials, or logs. The container image was saved and reloaded locally; no package or image registry publication occurred.
