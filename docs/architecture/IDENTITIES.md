# ARCHON · AEGIS · ATLAS — identity contract

**Authoritative naming overlay for the JARVIS v2 clean rebuild.** The existing ten functional modules remain intact; these are stable roles, not additional duplicate modules or silent renames of database tables.

| Identity | Owns | Meaning |
|---|---|---|
| **ARCHON** | Core's intelligent orchestration and Runtime's main assistant persona | Main AI responsible for interpreting goals, communicating, and requesting authorized task execution |
| **AEGIS** | Module 09 (Guardian/Recovery) | Local guardian intelligence, integrity diagnosis, security-event analysis, recovery proposals, priority reservation, controlled redeployment |
| **ATLAS** | Core's deterministic orchestrator, Backend, SDA infrastructure, Module 10 Cloudflare automation | Durable queues, dispatch, worker orchestration, event bus, model gateway, ASEL policy enforcement, capability/secret broker, security scanning and monitoring |
| **ASEL** | Cross-cutting subsystem owned by ATLAS/Backend | Deterministic Security Enforcement Layer: identity, policy, capability broker, scanner orchestration, runtime security events, containment and tamper-evident audit; not a separate functional module |
| **Astra One** | External bootstrap development stack (outside the new JARVIS runtime) | Builds and qualifies the native ATLAS SDA before a reversible, owner-approved handover |

**Authority:** ARCHON may request tasks, but does not bypass ATLAS/ASEL deterministic permissions and scheduling. AEGIS's local model receives **the next available compatible inference slot** once current bounded calls finish; it does not forcibly terminate healthy in-flight inference. AEGIS cannot approve its own deployment, change ASEL policy, suppress findings or replace the trusted watchdog. A separate immutable/policy-controlled watchdog remains the trust root for rollback and release approval.

**Design boundary:** Do not create a second archon/ replacement module for Core or a second atlas/ task queue. The platform still has ten modules and one task ledger owner. ASEL is cross-cutting, not module 11. In code, preserve jarvis_v2 package paths until separately reviewed migrations. The name change alone does not change GitHub repository name, task IDs, existing deployments, Cloudflare bindings or secrets.

The monitor is **ATLAS Monitor**, the independent terminal dashboard in tools/atlas_monitor.py / jarvis_v2.monitor. It attaches to an existing read-only Astra One or ATLAS database. It never starts Codex or controls the runner.
