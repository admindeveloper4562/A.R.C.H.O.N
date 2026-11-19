# Performance report

Measured local results:

- Full 590-test unittest run: 27.762 seconds at source `4149c1d75eee24880bfacd819342f9c21d05d51a`.
- Native import sweep: 106 modules, completed in under one second.
- FTS5 index: 552 files indexed from 553 cataloged files; representative search queries returned 1 to 5 results.
- Bounded host inventory: 10,000 metadata entries collected in approximately three seconds; the fresh scan persisted a 1,328-frame continuation cursor.
- Runtime capability inventory: Ollama model listing and NVIDIA GPU/driver probe completed successfully; VA-API, ROCm, and OpenCL probes were unavailable and recorded as such.
- Fresh SQLite database backup/restore: runtime.sqlite3 and atlas.sqlite3 passed.

These are development-host measurements, not production capacity claims. No sustained queue throughput, model latency, Blender performance, Windows Ollama benchmark, network-provider latency, or resource-soak test was run. The host has 12 logical CPUs, 15GiB RAM, and a critically full 110G home filesystem; disk pressure is a material performance and reliability limitation.
