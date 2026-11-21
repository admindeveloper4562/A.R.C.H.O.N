# Linux performance evidence

Application source SHA: 0ae26d563e5998a9390588feb58eb3d5c0081ffb. Workload evidence is from actual local Ollama qwen3:4b inference on the available NVIDIA GTX 980 with 4 GiB VRAM.

- 36 native serial tasks completed in 289.326 seconds: 18 inference and 18 read-only database inspections.
- Throughput: 0.124 completed tasks/second; maximum queue depth: 12.
- Model latency: 4.059–25.427 seconds; median 17.665 seconds.
- System CPU busy during model calls: mean 81.45%, range 72.46–87.61%.
- GPU memory after calls: 3,039–3,076 MiB; utilization after calls: 19–35%.
- Host available memory: 7,159 MiB before and 6,983 MiB after.
- Three controller restart boundaries and a final restart produced no task replay; SQLite integrity and runtime health passed.

These numbers describe the bounded test workload and host only. They are not a production throughput guarantee or Windows/Apple performance result.
