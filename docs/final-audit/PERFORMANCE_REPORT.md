# Linux performance evidence

> Historical snapshot captured 2026-11-21 for source 0ae26d563e5998a9390588feb58eb3d5c0081ffb. The current source-759 qualification contains no Ollama or extended-soak measurements; see SOAK_TEST.md.

Application source SHA: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. These prior measurements came from a bounded local qwen3:4b workload on the host available at that snapshot.
- 36 native serial tasks completed in 289.326 seconds: 18 inference and 18 read-only database inspections.
- Throughput: 0.124 completed tasks/second; maximum queue depth: 12.
- Model latency: 4.059–25.427 seconds; median 17.665 seconds.
- System CPU busy during model calls: mean 81.45%, range 72.46–87.61%.
- GPU memory after calls: 3,039–3,076 MiB; utilization after calls: 19–35%.
- Host available memory: 7,159 MiB before and 6,983 MiB after.
- Three controller restart boundaries and a final restart produced no task replay; SQLite integrity and runtime health passed.

These measurements remain historical and are not source-759 performance evidence or production guarantees.
