# REL-007 — Runtime verification on Ubuntu

**Result:** `PARTIAL_WITH_EXTERNAL_HOST_GATES`

This report records the runnable Runtime, browser-route, permission and audio
observations for the exact source checkpoint below. It does not turn static
route tests or device enumeration into real Firefox or voice acceptance.

## Pinned execution

| Item | Observed value |
| --- | --- |
| Task | `REL-007` / attempt 1 |
| Start and candidate source | `86ab29532e3a463c9e249c34cfc947dacc60835b` |
| Branch | `feature/astra-rel-007-a1-3d9acc3a` |
| Host | Ubuntu 24.04 / x86_64, sanitized local label `archon-local` |
| Firefox | `firefox --version` available, exit 0; reported version is retained only in the private evidence manifest |
| Audio | 3 ALSA capture devices and 3 PipeWire source rows enumerated |
| Raw host output | Not retained in the report or manifest |

## Acceptance matrix

| Requirement | Evidence | Result / limitation |
| --- | --- | --- |
| Real Firefox dashboard | All 10 static dashboard routes returned HTTP 200, including `/voice`; the bounded Firefox headless render exceeded 45 seconds and was terminated | **BLOCKED** — owner-session interactive Firefox E2E and refresh/navigation smoke remain unverified |
| Voice device | `arecord -l`, `pactl list short sources` and `wpctl status` completed; 3 ALSA devices and 3 PipeWire source rows were observed | **PARTIAL** — enumeration is not microphone-to-STT-to-TTS evidence; no audio was recorded or transmitted |
| Typed browser actions | Browser profile, human handoff, allowlist, confirmation, idempotency and sensitive-field denial tests passed | **PASS for deterministic service tests; host UI actions not claimed** |
| Runtime denial/security boundary | Runtime security focused tests passed; no unauthenticated effect was accepted by the tested service boundary | **PASS for local tests; live browser session boundary remains unverified** |
| Full local regression | 329 tests passed, exit 0 | **PASS** — local evidence only |

## Commands and artifacts

The following commands ran in the isolated REL-007 worktree with
`PYTHONPATH=src:.`; each exit code was 0 unless stated otherwise.

| Command | Tests | Artifact SHA-256 |
| --- | ---: | --- |
| `python3 -m unittest discover -s tests -p 'test_runtime_*.py'` | 50 | `30912fe9cce128c7787f9435dea6af1281f0176748deb95a4512f3bf860becd4` |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 329 | `e33723c488e2f307f084428cb933ea49e47d827675a738528f3ee197ac2e5244` |
| `python3 -m unittest discover -s tests -p 'test_runtime_security.py'` | 3 | `d1dcabf85406e8e8e688c7ae1c6af8541eb9c9c5fdfbefc2fae110de020f25e4` |
| `python3 -m unittest discover -s tests -p 'test_runtime_browser.py'` | 3 | `a00c56ed23a61e7ccbb27adee0f0ca75a582ee6aec7741ee44f0e5499fffde60` |
| `python3 -m unittest discover -s tests -p 'test_runtime_speech.py'` | 4 | `62ebc837b03527c2fd383822817aa4bdc5835004f695c77ce4d5f17e91fc18e0` |
| `python3 -m unittest discover -s tests -p 'test_runtime_dashboard.py'` | 3 | `b0e8179eaee5395c5b3ba2106b0d600ff82e798252791ca92f9ac8f8716ff9a4` |
| `python3 -m unittest discover -s tests -p 'test_runtime_file_actions.py'` | 4 | `38fefd930311d885aa158f74805c29dd78dfa3283e513198e32bbac824dcfbfd` |

The complete sanitized evidence manifest is outside the Git worktree at:

`$ARCHON_HOME/.local/state/archon-astra/private/candidates/REL-007/REL-007-evidence-manifest.json`

Manifest SHA-256:
`3ae7067eaf92273f27e2187a2aadb2869cef19eeafbc0849435e7c713a60245b`

## Child evidence

| Child | Result | Evidence |
| --- | --- | --- |
| `REL-007.S01` | PASS | The matrix above maps the parent clauses to observable checks and explicit host limitations. |
| `REL-007.S02` | PASS | Tests use isolated deterministic fixtures; the host manifest retains only sanitized versions, counts, exit codes and hashes. |
| `REL-007.S03` | PASS | 50 Runtime tests and 329 full local tests passed; all ten static routes returned HTTP 200; host probes were recorded. |
| `REL-007.S04` | PASS | Security, browser allowlist, confirmation, idempotency, invalid-field and file-action denial tests passed; no audio or external action was performed. |
| `REL-007.S05` | PASS | This report is bound to the integration source SHA and artifact hashes; Firefox interactive and functional voice gates remain explicitly blocked. |

## Required follow-up

Run the owner-session Firefox smoke with the existing browser process preserved,
then perform an explicit local microphone-to-response-to-speaker qualification
on the target device. These are real-host gates and cannot be replaced by
headless timeout results, ALSA/PipeWire enumeration or mocks.

`REL-007 | start SHA 86ab29532e3a463c9e249c34cfc947dacc60835b | branch feature/astra-rel-007-a1-3d9acc3a | changed file docs/tasks/REL-007-VERIFICATION.md | local 329-test regression and sanitized host/device evidence | state PARTIAL_WITH_EXTERNAL_HOST_GATES`
