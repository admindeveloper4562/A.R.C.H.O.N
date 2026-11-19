# REL-004 verification — Windows/Linux model routing and context handoff

Status: `LOCAL_EVIDENCE_RECORDED / INDEPENDENT_QC_PENDING`

This verification is bound to the canonical integration checkpoint and keeps
the Windows Ollama service loopback-only. It records sanitized counters and
hashes only; no prompt, response, credential, token, private key or raw
runtime payload is retained.

## Acceptance identity

| Field | Value |
| --- | --- |
| Task | `REL-004` |
| Source SHA | `43c8db7de8a5f0277a7db23379019d05f2edd2c6` |
| Integration SHA | `d5adb408d6491d69e0c75b099a3c750527673287` |
| Controller upgrade | `ARCHON-REL004-EVIDENCE-20261119` |
| Controller candidate | `d5adb408d6491d69e0c75b099a3c750527673287` |
| Windows model | `qwen3:8b` |
| Windows model digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Ollama | `0.40.16` |
| Listener | `127.0.0.1:11434` |
| Profile | `num_ctx=16384`, `q8_0`, Flash Attention, `num_parallel=1` |

## Measured Windows evidence

The live loopback probe performed one warmup and three bounded requests. Only
numeric counters were retained:

| Run | eval_count | eval_duration_ns | prompt_eval_count | tokens/s |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 64 | 1,618,476,000 | 19 | 39.543 |
| 2 | 64 | 1,704,115,000 | 19 | 37.556 |
| 3 | 64 | 1,832,705,000 | 19 | 34.921 |

The persistent user profile was observed as `OLLAMA_HOST=127.0.0.1:11434`,
`OLLAMA_CONTEXT_LENGTH=16384`, `OLLAMA_FLASH_ATTENTION=1`,
`OLLAMA_KV_CACHE_TYPE=q8_0` and `OLLAMA_NUM_PARALLEL=1`. The test did not
expose Ollama beyond loopback.

## Linux and cross-device checks

All five focused suites ran on the active integration worktree with exit code
0. The private manifest is
`/home/archon/.local/state/archon-astra/private/rel-004/linux-tests.json`
with SHA-256
`d9a0e5cea5f2a990c6f23378c0b905bc4d5667a94e648d982f6b81639d1ebf1b`.

| Check | Tests | Result |
| --- | ---: | --- |
| `test_backend_handoff.py` | 3 | PASS |
| `test_backend_routing.py` | 5 | PASS |
| `test_backend_windows_agent.py` | 5 | PASS |
| `test_backend_acceptance.py` | 5 | PASS |
| `test_backend_ollama_profile.py` | 5 | PASS |
| `test_rel004_cross_device.py` | 2 | PASS |

The checks cover provider handoff, task/permission/tool receipt recovery,
sticky-provider handoff, quota admission, Windows capability routing, stale
lease rejection, idempotent job completion and exactly-once effect replay.

## Negative and boundary evidence

| Boundary | Observed result |
| --- | --- |
| Replayed handoff identity | Same receipt returned; conflicting tool effect rejected |
| Replayed tool effect | Execution permission denied; original result preserved |
| Explicit provider switch | Sticky route stayed on Codex until explicit Ollama handoff |
| Windows job replay | Same completed receipt returned; duplicate execution not admitted |
| Listener exposure | Loopback-only profile accepted; non-loopback evidence rejected by the controller |
| Raw payload retention | Not recorded; private manifest contains counters and output digests only |

## Remaining boundary

This closes the Windows/Linux verification gate for this host and leaves the
candidate in `INDEPENDENT_QC_PENDING` until the independent QC lane reviews
the exact candidate and the serialized Merger records the final integration
receipt. Native macOS/iOS acceptance remains separately blocked by the
unavailable Apple toolchain/device and is not substituted by this result.
