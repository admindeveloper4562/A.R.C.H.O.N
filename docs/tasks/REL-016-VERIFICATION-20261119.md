# REL-016 Verification — local CI evidence and bounded blockers

Status: `RESUMED / LOCAL_EVIDENCE_RECORDED / CANDIDATE_PENDING`

This report records the exact local evidence for the amended REL-016 task. It
does not claim hosted Python, Windows, native iOS, or TWS evidence.

## Identity and scope

| Field | Observed value |
| --- | --- |
| Task | `REL-016` |
| Task payload SHA | `208023536a34d1641582305d7a81cc4f810d2fa927bc22ace9dd0c84240d7ca0` |
| Amended plan SHA | `ec8eb9d28adb55828eb68aba94f1ef5b9137c0792a8c62a495d61bf754d3bef4` |
| REL-016 packaging amendment | `REL-016-PACKAGING-SCOPE-20261119` |
| Packaging amendment SHA | `3e36632c38d3d13a044d3d48786789f4ca0f3b9d9b6e42742cdecb2d12660546` |
| Integration base SHA | `60c731229a2cafed8f3c6d2ab49ca3a68f414635` |
| Candidate branch | `feature/astra-rel-016-a1-b5175fa3` |
| Candidate worktree | `$ARCHON_HOME/.local/state/archon-astra/worktrees/rel-016-b5175fa3` |
| Candidate source SHA | `60c731229a2cafed8f3c6d2ab49ca3a68f414635` |
| Workflow SHA-256 | `dbcc492abf3ca6c6e3cdcf49900616d09891b343027c63ba9b55dfe46df8ec79` |
| Execution mode | `ci_local_only` |
| Remote Actions | Not triggered; `DEFERRED_QUOTA` per task instruction |
| Native iOS | Explicitly deferred and unclaimed |
| TWS | Explicitly out of scope and unclaimed |

The owner-authorized packaging amendment expands this task's roots to include
`bootstrap/astra-one/` for the manifest repair and local runner validation.
Hosted quota and native iOS evidence remain deferred and unclaimed.

## Workflow inspection

`.github/workflows/ci.yml` declares an Ubuntu matrix for Python 3.11 and 3.12,
an Ubuntu preflight, an Ubuntu test job, a macOS scaffold-test job, and a
fallback receipt job. The bootstrap step runs
`bootstrap/astra-one/scripts/verify_manifest.py` before the Astra test suite.
The workflow contains no Windows runner job. The macOS job runs only scaffold
tests; it is not native Xcode/device acceptance.

## Local replay

| Check | Result |
| --- | --- |
| `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -q` | exit 0; 561 tests; `OK` |
| `PYTHONPATH=src:bootstrap/astra-one python3 -m unittest discover -s bootstrap/astra-one/tests -p 'test_*.py' -q` | exit 0; 191 tests; `OK` |
| `PYTHONPATH=src python3 -m unittest tests.test_ci_workflow -q` | exit 0; 8 tests; `OK` |
| `python3 -m unittest discover -s apps/ios/tests -p 'test_*.py' -q` | exit 0; 1 scaffold test; `OK` |
| `PYTHONPATH=src python3 tools/verify_foundation.py` | exit 0; validation passed |
| `python3 tools/ci_checks.py dependency_scan` | exit 0 |
| `python3 tools/ci_checks.py secret_scan` | exit 0 |
| `python3 tools/ci_checks.py security_scan` | exit 0 |
| `python3 bootstrap/astra-one/scripts/verify_manifest.py` | exit 0; 48 files; integrity passed |
| `python3 bootstrap/astra-one/scripts/verify_package.py` with disposable TypeScript/Wrangler tools | exit 0; 191 Astra tests, TypeScript, and 4 monitor smoke tests passed |
| Python 3.11 Docker root suite, no network/read-only source | exit 0; 561 tests; `OK` |
| Python 3.11 Docker bootstrap manifest | exit 0; 48 files; integrity passed |
| Python 3.11 Docker Astra suite, no network/read-only source | exit 0; 191 tests; `OK` |

The manifest was stale across six existing hashes and four unlisted package
files. The owner-authorized amendment records the repair and expands the
REL-016 scope only for `bootstrap/astra-one/`; verification now passes for all
48 package files.

The local WSL image has Python `3.12.3`; `python3.11` is unavailable. No
hosted runner was invoked to substitute for that missing declared matrix
version, and no Windows or native iOS evidence is claimed.

## Disposition

The external blocker was resolved through the Master-applied packaging
amendment and REL-016 was requeued for a fresh builder generation. The
candidate must still pass independent QC and serialized Merger integration;
hosted quota and native iOS evidence remain explicitly deferred. No main
branch or production state was changed.
