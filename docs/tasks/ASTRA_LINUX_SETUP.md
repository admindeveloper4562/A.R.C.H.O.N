# External Astra One operator note

The integrated ARCHON foundation now includes the exact Astra One v0.2.0 bootstrap source under `bootstrap/astra-one/`. Do not install a second independent ZIP or run the legacy `jarvis-v2` repo-creation script.

From a fresh extraction, run `bash tools/archon_bootstrap.sh` once after checking its instructions and authenticated Codex/GitHub setup. It produces one clean main commit and a develop branch in the existing empty `A.R.C.H.O.N` repository, starts a bounded five-worker Codex background service, and leaves ATLAS Monitor separate.

For commands and safety caveats, see [ATLAS Linux Astra service](../operations/LINUX_ASTRA_SERVICE.md). The focused context remains [ASTRA_PHASE1_CONTEXT.md](ASTRA_PHASE1_CONTEXT.md); the full architecture remains [JARVIS_V2_CONSOLIDATED.md](../architecture/JARVIS_V2_CONSOLIDATED.md). Additional tasks require reviewed enqueue; do not authorize unbounded self-updating on the first start.
