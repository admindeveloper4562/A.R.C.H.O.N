# Module contracts — ten modules

Identities overlay the ten modules: **ARCHON** (main AI/Core + Runtime), **AEGIS** (Guardian), **ATLAS** (deterministic orchestration, Backend, SDA infrastructure, Cloudflare) and **ASEL** (cross-cutting security enforcement). See [IDENTITIES.md](IDENTITIES.md) and [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md).

| ID | Directory | Contract summary |
|---|---|---|
| 01 core | src/jarvis_v2/core/ | Global deterministic tasks/events, one logical session per task, separate event session, priority, scoped module handoff; all tool dispatches require ASEL authorization |
| 02 sda | src/jarvis_v2/sda/ | Five Codex workers, supervisor, deterministic Master, QC, serialized Merger, recoverable checkpoints; isolated sandboxes and commit-bound security scans |
| 03 backend | src/jarvis_v2/backend/ | SQLite, memory/RAG, model gateway, cross-device Windows Ollama node, capabilities; ASEL policy engine, identity, capability/secret broker, scanner orchestration, audit/event pipeline |
| 04 runtime | src/jarvis_v2/runtime/ | Voice/chat/dashboard/browser/desktop automation under permission broker; session isolation, safe URL handling and approval-bound side effects |
| 05 research | src/jarvis_v2/research/ | Source-backed YouTube/Instagram/GitHub knowledge, RAG and citations; retrieved content remains tainted and cannot authorize tools |
| 06 tws | src/jarvis_v2/tws/ | Twelve wings, quest/XP idempotency, Aurelia, iOS/3D; consent-scoped personal data and authenticated/revocable device pairing |
| 07 wic | src/jarvis_v2/wic/ | Dated world/Thai news, clustering, corrections, alerts; source sanitization, provenance and prompt-injection defenses |
| 08 finance | src/jarvis_v2/finance/ | Read-only scoped Mira analytics and segregated demo trading; per-person consent/row scope, no live broker-write capability |
| 09 guardian | src/jarvis_v2/guardian/ | Local AI next-slot priority, deterministic recovery, staged promotion/rollback; AEGIS advisory plus independent watchdog and security-event response |
| 10 automation | src/jarvis_v2/automation/ | Cloudflare queue, cron, metadata-only progress; authenticated device identity, rate limiting, WAF, replay protection and redacted telemetry |

## Cross-cutting ASEL contract

ASEL is not an eleventh module or a second task ledger. ATLAS/Backend owns deterministic identity, policy decisions, scoped capability issuance/revocation, secret brokering, active scanning, runtime security event collection, containment coordination and tamper-evident audit. Every module must expose a versioned security manifest: data classes, principals, capabilities, inbound/outbound interfaces, scan profile, telemetry health, containment action and recovery method.

No module may bypass the broker with direct shell, database, browser, network, filesystem, connector or Cloudflare access. A module-specific process may enforce its own boundary but must preserve central policy decisions and revocation. Security failure degrades safely: deny privileged work, preserve STOP/PAUSE and continue only independent low-risk work.

Guardian, SDA, browser, scanner, policy broker and privileged executor retain independent failure domains. Scanner adapters run least-privileged and cannot deploy fixes or suppress their own findings. Active scans are non-destructive and limited to inventoried owner-controlled assets.
