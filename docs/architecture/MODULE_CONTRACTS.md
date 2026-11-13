# Module contracts — ten modules

Identities overlay the ten modules: **ARCHON** (main AI/Core + Runtime), **AEGIS** (Guardian), **ATLAS** (deterministic orchestration, Backend, SDA infrastructure, Cloudflare). See [IDENTITIES.md](IDENTITIES.md).

| ID | Directory | Contract summary |
|---|---|---|
| 01 core | `src/jarvis_v2/core/` | Global deterministic tasks/events, one logical session per task, separate event session, priority, scoped module handoff |
| 02 sda | `src/jarvis_v2/sda/` | Five Codex workers, supervisor, deterministic Master, QC, serialized Merger, recoverable checkpoints |
| 03 backend | `src/jarvis_v2/backend/` | SQLite, memory/RAG, model gateway, cross-device Windows Ollama node, capabilities |
| 04 runtime | `src/jarvis_v2/runtime/` | Voice/chat/dashboard/browser/desktop automation under permission broker |
| 05 research | `src/jarvis_v2/research/` | Source-backed YouTube/Instagram/GitHub knowledge, RAG and citations |
| 06 tws | `src/jarvis_v2/tws/` | Twelve wings, quest/XP idempotency, Aurelia, iOS/3D |
| 07 wic | `src/jarvis_v2/wic/` | Dated world/Thai news, clustering, corrections, alerts |
| 08 finance | `src/jarvis_v2/finance/` | Read-only scoped Mira analytics and segregated demo trading |
| 09 guardian | `src/jarvis_v2/guardian/` | Local AI next-slot priority, deterministic recovery, staged promotion/rollback |
| 10 automation | `src/jarvis_v2/automation/` | Cloudflare queue, cron, metadata-only progress |

No Business module directory/service is instantiated. Modules use typed versioned API/event envelopes and separate persistence where appropriate; a single process is fine for low-risk services initially. Guardian, SDA, browser and privileged broker must retain independent failure domains.
