# Linux bounded normal-use soak

Candidate `2e24790c983bf3c8d2d0f99de7a086427355f172` has runtime `src/` tree SHA `5671f31b7340fae8a2979fe9d7b88d563f1e90a4`. The bounded local-inference/data workload used local Ollama `qwen3:4b` on source `2621056f64f3bee6f41b794913302d0fa36491b6`, whose `src/` subtree has that same SHA.

- 72 tasks: 36 local-model tasks and 36 read-only database tasks; no duplicate task replay.
- Duration: 491.427 seconds (0.1465 tasks/s); 12 controller restart cycles; maximum queue depth 6; final queue depth 0.
- Model-call latency across 36 calls: min 3.192 s, median 14.2895 s, mean 13.6003 s, max 24.545 s.
- Per-task CPU-busy samples across 72 calls: min 42.86%, median 53.135%, mean 52.359%, max 58.17%. These are sampled call-level values, not peak host or process CPU.
- Host available memory snapshots: 7,970 MiB before and 6,299 MiB after. GPU snapshots: 1,390 MiB used / 3% utilization before and 3,184 MiB / 31% after. Across 36 model-call samples, GPU memory used was 3,184 MiB; utilization median 25.5%, max 35%. These snapshots do not establish peak RAM/VRAM or process RSS.
- Receipt SHA-256: `20716944133572eb77f250f3ce6801ca785e494fd4841a2e531a8b4edaba8c83`.

This runtime-tree match allows the result to inform runtime capability, but it is not a run on the exact whole-source candidate. The workload is bounded and shorter than a multi-hour soak. Multi-hour model-backed operation, sustained resource/throughput behavior, and model-backed failure recovery remain unverified. Verdict stays CONDITIONAL.
