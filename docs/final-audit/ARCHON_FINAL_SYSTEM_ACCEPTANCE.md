# ARCHON Final System Acceptance

**Date:** 2026-11-22

**Verdict:** **CONDITIONAL**

The Linux package and clean-container candidate passed the local release verifier on the exact application source SHA below. ARCHON is not accepted as a fully autonomous Linux system: native SDA approval separation, independent AEGIS recovery, full module-to-module workflows, and a current-source soak remain unverified.

## Candidate and Git state

- **Qualified application source:** `ae07aeb405bb4a1dcf71b2a0255639b30db17b62`
- **Package:** `jarvis-v2` version `0.0.3`; Python metadata requires `>=3.11`. This run used Python 3.12.3.
- **Qualification base:** remote `develop` was `4a83fd07a91bc9e1e47e67fb05e463fedfe3e4c6`; remote `main` was `5227b91d2725bf4be4336a5ad26189fdf1034704`.
- **Local integration:** `develop` was a fast-forward descendant of remote `develop`, four commits ahead at qualification. The four application commits are `6d08fff` (OCI archive identity), `d33818a` (daily reminder replay), `99ea3ee` (Docker context privacy), and `ae07aeb` (archive handoff verification).
- **Publication:** no remote push was made. The workflow runs on pushes to `develop`, while hosted Actions are unavailable for billing reasons; this run used local verification. The separate reviewer sessions were stopped as requested, so no independent reviewer approved the exact final candidate. Remote `develop` therefore remains the base SHA above; `main` was not modified.
- **Other work:** unmerged AEGIS (11 changed entries), IRIS (7), and integration (1 untracked report) worktrees remain preserved. The clean SMITH candidate `4c65112c5be7821f10d6d87d681b1aa7e27f5811` was not integrated. Open PR #1 still has an unresolved local-path disclosure; draft PR #5 remains open. Repository visibility was not changed.

## Changes integrated locally

1. Container images use source-SHA-specific tags. OCI archive verification selects the exact source-tagged image, distinguishes the image index digest from config digests, and verifies the embedded source SHA before and after reload.
2. Daily reminder acknowledgements now require the expected due occurrence. Stale acknowledgements are idempotent and cannot advance the next due date again; SQL updates are conditional on the observed occurrence.
3. `.dockerignore` excludes local `codex-session*.md` files. A regression test checks that these transcripts are not sent in the Docker build context; the files themselves were preserved.
4. The release verifier now reads the archive name from the smoke report, validates the report source SHA and result, rejects path escapes and symlinks, checks the archive digest, and records that archive in the manifest and checksum list.

The first full release run exposed the verifier's obsolete fixed archive filename after the container smoke had passed. The verifier handoff was fixed, focused tests passed, and the complete release verification then passed on `ae07aeb`.

## Exact-source qualification

The authoritative command was `python3 tools/verify_release.py --output-dir …`, run from a clean detached worktree at the exact source SHA with the shared heavyweight-operation lock.

| Check | Result |
| --- | --- |
| Release verifier | Passed; 42 subprocess records |
| Regression suite | 654 discovered in 32.585 seconds; 652 passed, 2 opt-in tests skipped in the default run; no failures |
| Opt-in local inference tests | Both skipped tests were then run and passed: local Ollama runtime and signed native model-task round trip |
| Static, dependency, and secret scans | All three local scans passed |
| `pip-audit==2.10.1` | Passed; zero known vulnerabilities in the locked dependencies |
| Python wheel and source distribution | Built, installed in disposable environments, CLI/package checks passed, and repeat builds matched |
| Clean container | Passed fresh startup, health, ten-module registration, task and effect checks, restart recovery, SQLite integrity, and graceful stop |

The private-data check covered the current source tree and release inputs; it did not scan Git object history. Exact-source package execution was tested on Python 3.12.3; Python 3.11 was not rerun locally.

The two opt-in tests used the local `qwen3:4b` model. The runtime test returned its expected marker and persisted two conversation turns; its measured inference time was 14.733 seconds on the first run and 1.077 seconds on the subsequent combined run. No throughput figure is claimed.

### Release artifacts and evidence

Artifacts and full logs are retained locally in `/var/tmp/archon-final-qualification-ae07aeb/`; they are not included in the public source tree.

| Artifact | SHA-256 |
| --- | --- |
| Wheel `jarvis_v2-0.0.3-py3-none-any.whl` | `6234073e278b20f269415eeb3d2cfec867e45dceed9ed952171f4f85ba0a3259` |
| Source distribution `jarvis_v2-0.0.3.tar.gz` | `dc1b3eea9a0a40997c4593c8803009f827f01d70beb167bdd8b73c8fb6b03f2a` |
| Container archive | `218d6bbbd92c9a4a48f5f4450b8d0c1492a08603a79c0783ec62a2973ce9c611` |
| Release manifest | `213fddee50cc558ad0d5988ddc53bfc2665a6b383c3c952b89e9f625d0311010` |
| Full regression log | `5758358ad48bd7a81323415e940ff239c4cd8f70afa0d3b5f3e71aa1ac34ec0e` |
| Security report | `b8604a9be55a6fd3dc7fca6168526aaea4a9fa51645e1ad846c84be174f0b767` |
| Container smoke report | `c22e865d8cb56810bfa779e2fd8b40d6aebfcadfa10fe2b6cfbebd6112d7810d` |
| Local inference and native-task log | `2fe3b2cfe9055a5632d001b00ca7ac0777efca338389632486503ac4449d19b8` |

The wheel is 304,726 bytes and the source distribution is 352,925 bytes. The saved container image is tagged `archon-release:ae07aeb405bb4a1dcf71b2a0255639b30db17b62`, with image ID / OCI index descriptor digest `sha256:6c140efcc78588b4898901760929d3ba444208cd73d444b29e19b4f626c6bade`. The source-SHA-specific archive was loaded and the exact reloaded image was selected before the smoke test.

The full verifier's first attempt on `99ea3ee` did not complete because of the fixed-name handoff defect; its failure report and container evidence are retained separately. The successful run is the `ae07aeb` evidence listed above.

## Module status

The container registered all ten module keys: core, SDA, backend, runtime, research, TWS, WIC, finance, guardian, and automation. Registration is not proof of every module's full operational contract.

| Module | Status | Exact boundary |
| --- | --- | --- |
| ALFRED / Core | Partial | Fresh task admission, read-only operation, bounded effects, cancellation, and recovery passed. A complete user-goal route through other modules was not run. |
| SMITH / SDA | Not qualified | A disposable native-SDA candidate passed its focused tests, but its QC flow can accept an approval signed by the coding owner's key. It was withheld; independent approval-role separation and the full native development-to-merge path remain open. |
| CORTEX / Backend | Pass for tested persistence scope | Fresh runtime, ATLAS, and effect databases passed integrity checks; migrations, persistence, package, and backend tests passed. A production corpus restore was not tested. |
| IRIS / Runtime | Partial; local inference passed | `qwen3:4b` completed runtime and native task tests on this source. Browser, desktop, and hardware adapters were not qualified. |
| SAGE / Research | Partial | Local research/RAG tests ran; no live research-provider workflow with stored, cited results was exercised. |
| LUMEN / TWS | Partial | Local package and module tests ran; no Blender or device workflow was tested. |
| HORIZON / WIC | Partial | Local provenance and information tests ran; no live feed/reconnect workflow was exercised. |
| CROWN / Finance | Pass for paper/read-only scope | Paper and read-only tests ran. Live financial actions remain disabled. |
| PALADIN / Guardian | Partial | Local Guardian tests ran. An independently protected AEGIS watchdog, unattended recovery, and controlled rollback were not qualified. |
| RELAY / Automation | Partial | Daily acknowledgement replay was fixed and covered by current tests. Clock-controlled dispatch through ATLAS and restart reconciliation were not run end to end. |

## Native execution and container evidence

On the exact source, the local native-controller test completed a signed model task through Ollama and persisted the response. The clean container used an ephemeral test-only Ed25519 key, not a production owner delegation. It verified:

- Fresh task admission and rejection of unsigned/unauthorized admission without a queue entry.
- A read-only operation and an approved workspace write with observable file contents.
- Rejection of an unauthorized workspace effect without creating the target file.
- Durable cancellation, restart persistence, and reconciliation of an interrupted journaled effect without duplicate output.
- Health, module registration, and integrity of runtime, ATLAS, and effect SQLite databases.
- Runtime UID/GID `10001:10001`, read-only root filesystem, all Linux capabilities dropped, network mode `none`, and `no-new-privileges`.
- Graceful container exit with code zero.

The resulting task ledger recorded three completed test tasks, one expected failed unauthorized effect, and one cancelled task. The final test container and its two disposable volumes were removed after preserving the reports; the release image and archive were retained.

## Guardian, ledger, service, and soak

- **AEGIS:** The watchdog candidate remains uncommitted in its preserved worktree. No separately protected watchdog process, signed owner rollback authorization, repeated-crash recovery, host-reboot recovery, or applied rollback was demonstrated. Unattended privileged recovery remains disabled.
- **Canonical task ledger:** Read-only `PRAGMA integrity_check` returned `ok`. The saved SQLite backup also returned `ok`; its logical dump matches the canonical database (logical SHA-256 `c693ee9857aed1eba01866ba654a07fbbaf455defad634f542a4fc4308f4e723`).
- **Ledger reconciliation:** 252 parent rows exist (245 completed, 7 archived), five above the 247-parent contract. There are 1,359 child rows (1,319 completed, 40 archived). There are 1,281 child-receipt rows covering 1,276 distinct children; 43 completed children and 40 archived children have no receipt, and five children have duplicate receipt groups. These historical records were not modified. Pending, rebuild, review, and merge queues were empty; all three recorded supervisor lanes were idle.
- **Controls and service:** No STOP/PAUSE marker was found in the canonical state directory, and no ARCHON/Astra runtime process was detected. The user systemd bus was unavailable in this session, so unit state could not be queried. No native user service was activated.
- **Soak:** No four-hour soak ran on this exact source. A prior 72-task, 491.427-second model/data soak belongs to an older runtime tree and is historical evidence only.

## Remaining acceptance gates

1. Obtain independent review of the exact candidate; do not self-approve the coordinator-authored verifier fix.
2. Resolve SMITH's coding/QC identity separation and demonstrate full disposable-repository coding, independent QC, repair, authorized Git integration, receipt, and interruption recovery.
3. Complete independent AEGIS watchdog, trust, crash/restart, rollback, and STOP/revocation qualification before enabling unattended recovery or the native service.
4. Run ALFRED cross-module assistant and research workflows, controlled-clock RELAY dispatch/recovery, and multi-task coordination with observable module outputs.
5. Run the required sustained soak on the final integrated source and record resource, throughput, retry, and recovery metrics.
6. Reconcile the five extra parent rows and missing/duplicate legacy child receipts through the authorized Master workflow; do not edit the ledger directly.
7. Review or sanitize the disclosure in open PR #1 before merging it. Do not change repository visibility as part of this acceptance.
8. Reconcile GitHub publication after independent QC and the hosted Actions billing gate. Run the exact candidate on Python 3.11. Windows and Apple validation remain deferred; live financial and communications actions remain disabled.

**Final decision:** CONDITIONAL. The Python package and Linux container candidate work on the tested source, but mandatory autonomy, recovery, coordination, ledger, independent-review, and soak criteria remain open.
