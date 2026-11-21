# ARCHON Security Architecture — ASEL 1.0

**Revision:** 2026-11-15  
**Status:** Accepted for rebuild planning; implementation and qualification are pending.  
**Scope:** All ten ARCHON modules, ATLAS infrastructure, AEGIS Guardian, Astra One bootstrap, Linux/Windows hosts and explicitly registered Cloudflare resources.  
**This is a cross-cutting subsystem, not an eleventh functional module.**

## 1. Security objective

ARCHON may become more capable without becoming more privileged. Model reasoning can propose actions, explain findings and request capabilities; deterministic enforcement code decides whether an action is permitted. No model, worker, retrieved document or module may grant itself authority, weaken policy, suppress a required scan or clear STOP/PAUSE/quota.

Security must provide prevention, detection, containment, recovery and independently verifiable evidence—not merely a one-time code scan.

## 2. Ownership and trust boundaries

- **ATLAS / Backend** owns ASEL's deterministic policy engine, identity and device registry, capability broker, secret broker, scanner orchestration, security event pipeline, audit ledger and security posture API.
- **ARCHON** requests actions and explains outcomes. It cannot mint capabilities, override denials or authorize itself.
- **AEGIS** analyzes alerts, correlates incidents and proposes recovery. Its model is advisory. It cannot disable sensors, edit its own trust policy, approve its release or clear STOP.
- **Independent watchdog** remains outside AEGIS, worker and normal ATLAS control. It verifies trust-anchored release identity, owner approvals, fencing, STOP and rollback.
- **SDA workers/QC/Merger** have distinct identities and isolated workspaces. Workers cannot approve their own code or policy changes.
- **Runtime/browser/device agents** receive only short-lived capabilities for specific resources and actions.
- **Cloudflare** receives minimum operational metadata. Raw prompts, source code, personal files, credentials and private financial records are not sent to public telemetry endpoints.

Trust boundaries are enforced in code and operating-system controls, not prompt wording.

## 3. ASEL subsystem components

### 3.1 Identity and device trust

Register the owner, service identities, worker identities and Linux/Windows devices independently. Authenticate every service-to-service request. Bind device credentials to a device record; support expiry, rotation, revocation and lost-device quarantine. Prefer mutually authenticated transport for peer connections and authenticated outbound HTTPS/VPN for remote devices. Never expose Ollama or internal admin endpoints publicly.

### 3.2 Deterministic policy engine

Implement policy-as-code outside every LLM. Default deny. Evaluate subject, device, task, audience, resource, action, scope, data classification, environment, expiry and risk. The engine must return allow, deny or approval-required with a machine-readable reason. A policy failure, unknown identity or unavailable policy service fails closed for privileged operations.

### 3.3 Capability broker and approvals

Issue short-lived, narrowly scoped, single-use capabilities bound to the exact task and action. Include a unique nonce and replay protection. An approval is bound to the exact operation, arguments, target resource, requesting identity and expiry; it cannot be reused for a different action. Support immediate revocation. Approval never overrides a hard STOP, legal restriction or disabled live-trading boundary.

### 3.4 Secrets broker

Keep credentials in OS-protected storage or a dedicated secret manager. Separate credentials by module, connector, environment and role. Expose a secret only to the authorized executor at the moment of use; never put secret values into model context, RAG, Git, issue comments, logs, crash dumps or Cloudflare telemetry. Scan for accidental exposure, rotate and revoke credentials, and preserve a redacted incident receipt.

### 3.5 Active Security Scanner

A scanner orchestrator maintains the asset inventory, scan policy, schedules, adapters, finding deduplication, severity, remediation status and evidence receipts.

Required scan families:

1. **SAST:** source analysis, unsafe APIs, injection patterns, path handling and authorization mistakes.
2. **SCA:** dependency vulnerability and license checks, lockfile validation and transitive dependency inventory.
3. **Secret scanning:** repository history, current diffs, build artifacts and approved local secret stores using test canaries; findings must redact values.
4. **SBOM and provenance:** generate a software bill of materials for release candidates; bind it to source and artifact hashes; verify build provenance and signatures.
5. **Container and IaC:** image, Dockerfile, deployment manifest, permissions, exposed ports, Cloudflare configuration and infrastructure policy scans.
6. **DAST/API:** authenticated, non-destructive checks of owner-controlled staging endpoints, API schemas, access control, session handling, rate limits, SSRF, CSRF and common web vulnerabilities.
7. **Host and endpoint posture:** registered Linux/Windows OS patch level, service exposure, firewall, endpoint protection, privilege changes and configuration drift.
8. **Runtime monitoring:** process, file-integrity, network-egress, authentication, privilege, service and policy-change events.
9. **LLM and retrieval evaluations:** adversarial prompt-injection fixtures for webpages, repositories, transcripts, documents, RAG and tool outputs.
10. **Recovery and integrity:** signed artifact identity, backup integrity, watchdog policy integrity, writer fencing and rollback target health.

Candidate open-source adapters may include Semgrep/CodeQL for SAST, OSV-Scanner or pip-audit for dependencies, Gitleaks for secrets, Syft plus Grype or Trivy for SBOM/image vulnerabilities, Checkov for IaC, and OWASP ZAP for staging DAST. These are candidates, not an assertion that they are installed or approved. Pin versions, verify provenance, run locally where practical and review each tool's permissions before adoption.

### 3.6 Runtime security sensors and event pipeline

Collect the minimum security metadata needed to detect suspicious behavior. Each event includes event ID, timestamp, source identity, device, module, task correlation, asset, event type, severity, policy version and evidence hash. Redact secrets and private payloads. Keep a tamper-evident, append-only audit stream separate from ordinary application logs. Missing, stale or tampered sensor telemetry must be visible as degraded security posture.

### 3.7 Active defence and containment controller

Deterministic controls—not an LLM—must be able to:
- deny new task claims and tool calls;
- STOP or pause the affected worker/module;
- revoke task, device and connector capabilities;
- quarantine a worker worktree or artifact;
- isolate a compromised process/module or device network path;
- fence writers to prevent split-brain;
- preserve logs, hashes, snapshots and incident evidence;
- route a repair proposal to SDA only after containment;
- restore only a verified, signed, compatible known-good artifact.

Contain the smallest affected boundary first. Do not shut down unrelated modules unless the threat crosses their trust boundary. Emergency STOP must work without a model, cloud connection or scanner availability.

## 4. Scan cadence and execution policy

| Trigger | Required activity |
| --- | --- |
| Every commit / pull request | SAST, SCA, secret scan, license checks, IaC/container checks where relevant, unit security tests and SBOM for release candidates |
| Nightly | Dependency re-scan, host posture, service exposure, configuration drift, credential age/revocation checks and scan-freshness review |
| Before staging promotion | Full relevant scanner set, authenticated non-destructive API/DAST, authorization regression, artifact provenance/signature and policy checks |
| Runtime | Event-driven process/file/network/authentication monitoring, abuse/rate-limit telemetry and security posture heartbeat |
| Weekly | Broader non-destructive scan of the registered owner-controlled asset inventory, with bounded concurrency and rate limits |
| Incident-triggered | Focused scan, forensic evidence capture, credential revocation and containment verification |

**Active scan authorization:** scanning is limited to repositories owned/authorized by the owner, registered local hosts, explicitly registered Cloudflare resources and staging endpoints. No scanning of arbitrary third-party hosts, credential spraying, destructive payloads, persistence attempts or exploit execution. Production DAST requires explicit owner authorization and a documented maintenance window. Scanner concurrency and network load must be bounded. A scan is not permission to exploit a finding.

Remote CI quota exhaustion must not be bypassed: run authorized local checks and mark remote-only checks deferred, never green.

## 5. Defensive hardening baseline

### SDA and build execution
- Use disposable, low-privilege rootless containers or dedicated VMs for untrusted code.
- Apply AppArmor/seccomp or equivalent OS confinement.
- No Docker socket, host home directory, SSH keys, production DBs or production secrets in worker sandboxes.
- Default-deny network egress; allow only exact task-scoped destinations when required.
- Separate worktrees, identities and caches; destroy ephemeral environments after preserving required evidence.
- Scan candidate source, dependencies, build outputs and artifacts before independent QC.

### Linux and Windows endpoints
- Minimize services and inbound ports; firewall deny-by-default.
- Keep OS security updates and endpoint protection active.
- Protect local secrets with OS-backed storage and filesystem ACLs.
- Monitor privilege changes, unexpected listeners, persistence locations and configuration drift.
- Keep Ollama bound to loopback; remote inference uses the authenticated device broker, not a public Ollama port.
- Device health failure or identity mismatch blocks job claims and triggers quarantine where warranted.

### Cloudflare and API surfaces
- Authenticate every service/device; use scoped service credentials and rotation.
- Apply WAF/rate limits, request-size/time bounds, strict schema validation, origin controls and replay protection.
- Keep private APIs private; separate public dashboard data from owner-only operational details.
- Redact prompts, source, credentials, personal records and financial data from logs/telemetry.
- Test authorization at the server, not only in the UI.

### Browser, research and LLM boundaries
- Isolate authenticated browser profiles and user sessions.
- Validate URLs, redirects, DNS/IP resolution, downloads and file paths to reduce SSRF/path traversal risk.
- Treat webpages, GitHub content, issue comments, transcripts, PDFs, tool output and RAG results as tainted data.
- Retrieved content may be quoted or summarized but cannot modify system policy, request secrets, authorize a tool or widen scope.
- Validate model tool arguments against typed schemas and re-check permissions at execution time.

### Personal and financial data
- Classify data and enforce per-module and per-person access at the backend.
- Encrypt sensitive data in transit and at rest where supported; define retention and deletion policies.
- Mira remains read-only with independent consent and server-side row scoping.
- Paper trading remains a separate ledger with no live broker-write capability.

## 6. Incident response lifecycle

1. **Detect:** scanner, sensor, user report or integrity monitor creates a correlated security event.
2. **Triage:** deterministic severity rules classify scope; AEGIS may analyze and recommend.
3. **Contain:** deny new work, STOP/quarantine the smallest affected module, revoke capabilities and isolate network/process access.
4. **Preserve:** capture redacted logs, hashes, relevant snapshots, source SHA, device identity and timeline in tamper-evident storage.
5. **Notify:** alert the owner with severity, impact, actions taken and outstanding decisions. External notifications require approval.
6. **Eradicate:** create a bounded SDA repair task from sanitized evidence; never let the compromised worker repair its own trust root.
7. **Recover:** restore a signed known-good artifact and compatible data snapshot under watchdog control; verify writer fencing.
8. **Verify:** re-scan, run negative tests, validate audit continuity and confirm STOP/approval state.
9. **Learn:** write a reviewed incident report and regression test. Do not silently weaken a policy to make a test pass.

## 7. Severity and response policy

- **Critical:** suspected credential exfiltration, confirmed sandbox escape, unauthorized privileged action, trust-root tampering, cross-person private-data exposure or production artifact compromise. Immediate deterministic containment and STOP of the affected trust domain; owner notification; release blocked.
- **High:** exploitable authorization bypass, exposed service, high-risk dependency reachable in the deployed path, repeated API abuse or missing critical sensor coverage. Contain or disable affected capability; release blocked by default.
- **Medium/Low:** create prioritized remediation with an owner and due date; monitor for escalation. Do not silently suppress.
- **Exceptions:** only a time-limited owner-signed exception with exact finding, affected SHA/asset, compensating controls, expiry and retest date may be considered for High findings. Critical findings are release blockers. Expired exceptions automatically re-block promotion.

Scanner failure, missing/stale evidence, unknown policy version or unavailable authorization service fails closed for privileged operations and release promotion.

## 8. Audit, metrics and dashboards

Keep append-only/tamper-evident event receipts with hash chaining or an equivalent integrity mechanism and a separately protected copy. Restrict audit read access and prohibit normal workers from deleting or rewriting records.

Track at minimum:
- registered asset and module scan coverage;
- scan freshness and failed/missing scanner runs;
- open findings by severity, age and affected artifact;
- secret exposure and revocation response;
- unauthorized action denials and replay attempts;
- runtime sensor health and configuration drift;
- time to detect, contain and recover;
- exception expiry and retest status;
- signed artifact/SBOM/provenance coverage.

Do not report a dashboard as secure merely because it is green; expose coverage gaps and stale evidence.

## 9. Security release gates

A release candidate cannot pass unless:
- every applicable scanner has a current result bound to the candidate SHA;
- all Critical findings are closed and High findings are closed or covered by a valid owner-signed exception;
- SBOM, provenance and artifact signature are verified;
- authorization, prompt-injection, sandbox, secret-leak, API and runtime negative tests pass;
- watchdog, STOP, capability revocation, incident containment and rollback drills pass;
- independent QC reviews the security evidence;
- owner approval is present for protected-branch promotion and production deployment.

## 10. Implementation mapping and task plan

ASEL is implemented as a cross-cutting platform subsystem owned by ATLAS/Backend, integrated with all ten existing modules. AEGIS remains the Guardian/Recovery module and independent watchdog remains the trust root. No eleventh module or duplicate task ledger is created.

The rebuild plan retains all 247 parent task IDs, their dependencies and existing runtime SQLite history. Every parent acceptance is enriched with the ASEL-1.0 baseline and module-specific controls. Twenty-two focused security child tasks are attached to existing parent tasks covering CI scans, threat modeling, sandbox isolation, signed supply chain, policy/capability enforcement, secret lifecycle, runtime sensors, connector revocation, scanner orchestration, Cloudflare/API hardening, Windows endpoint hardening, AEGIS/watchdog integration, containment, incident response, browser security, prompt-injection evaluations, mobile security, financial privacy and release red-teaming.

The JSON plans remain planning inputs; the canonical SQLite ledger is not duplicated or rewritten by this architecture amendment. Implementation status must be reported from actual host/test evidence, not from this specification.

## 11. References

- NIST SP 800-207 — Zero Trust Architecture.
- NIST SP 800-218 — Secure Software Development Framework.
- OWASP GenAI Security Project — LLM application threat guidance.
- OWASP ASVS and API Security Top 10 — application/API verification baseline.
