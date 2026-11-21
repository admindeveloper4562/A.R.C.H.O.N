# Linux bounded normal-use soak

Candidate application source: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Result: PASS for this bounded workload; multi-hour operation was not tested.

## Workload and outcome

- 36 signed tasks completed: 18 actual qwen3:4b local inference calls and 18 read-only conversation database inspections.
- One persistent native queue, maximum depth 12. Fresh signed approvals were issued at each of three 12-task batch boundaries.
- Three controller restarts between batches plus one final restart. Completed tasks were not replayed.
- Failures: 0. Runtime health: healthy. Atlas, runtime, and conversations SQLite integrity: ok.
- Duration: 289.326 seconds. Throughput: 0.124 completed tasks/second.
- Model latency: median 17.665 seconds; range 4.059–25.427 seconds.
- System CPU busy during model calls: mean 81.45%, range 72.46–87.61%.
- GTX 980, 4 GiB VRAM: observed use 3,039–3,076 MiB and utilization 19–35% after calls. Host available memory changed from 7,159 to 6,983 MiB.
- The earlier 12-task workload also passed.

The initial harness signed all 36 tasks once and returned no ready work after the test approval validity window elapsed. The corrected run renewed signatures per batch and passed; production approval policy was unchanged. Both attempt records are retained.

This is a bounded model/queue/database workload, not a multi-hour soak. It did not exercise parallel workers, live external feeds, a controlled-clock scheduled workflow, or an independent AEGIS process. No GPUs beyond the host GTX 980 or Windows/Apple devices were tested.
