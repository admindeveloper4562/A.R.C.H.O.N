(() => {
  "use strict";
  const byId = (id) => document.getElementById(id);
  const conversationKey = "archon.local.conversation";
  let conversationId = sessionStorage.getItem(conversationKey);
  if (!conversationId) {
    conversationId = crypto.randomUUID();
    sessionStorage.setItem(conversationKey, conversationId);
  }
  const activeStates = new Set(["active", "online", "ready", "running"]);
  let currentModules = [];
  const legacyModuleRoutes = Object.freeze({
    "/calendar": "automation", "/email": "runtime", "/actions": "sda",
    "/files": "backend", "/system": "core", "/projects": "backend",
    "/voice": "runtime", "/activity": "core", "/world": "wic",
    "/world/timeline": "wic"
  });

  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return response.json();
  }

  function stateName(value) {
    return String(value || "unreported").trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-");
  }

  function renderModules(modules) {
    currentModules = modules;
    const nav = byId("module-nav");
    const nodes = byId("module-nodes");
    const statusList = byId("module-status-list");
    nav.replaceChildren();
    nodes.replaceChildren();
    statusList.replaceChildren();
    const active = modules.filter((module) => module.runtime_status === "online").length;
    const partial = modules.filter((module) => module.runtime_status === "partial").length;
    byId("module-count").textContent = `${modules.length} registered`;
    byId("module-active-count").textContent = `${active}/${modules.length} online`;
    byId("metric-modules").textContent = `${active}/${modules.length}`;
    byId("metric-modules-note").textContent = `${partial} partial · ${modules.length - active - partial} waiting`;

    modules.forEach((module, index) => {
      const key = String(module.key || `module-${index + 1}`);
      const name = String(module.name || key);
      const state = String(module.runtime_status || module.state || "unreported");
      const slug = stateName(state);
      const navLink = document.createElement("a");
      navLink.className = "nav-link";
      navLink.href = `#module/${encodeURIComponent(key)}`;
      const mark = document.createElement("span");
      mark.className = "nav-icon";
      mark.textContent = key.slice(0, 3).toUpperCase();
      const label = document.createElement("span");
      label.textContent = name;
      const navState = document.createElement("small");
      navState.className = "module-nav-state";
      navState.textContent = state;
      navLink.append(mark, label, navState);
      nav.append(navLink);

      const node = document.createElement("a");
      node.id = `module-node-${key}`;
      node.href = `#module/${encodeURIComponent(key)}`;
      node.className = `module-node state-${slug}`;
      node.style.setProperty("--angle", `${index * (360 / Math.max(modules.length, 1))}deg`);
      node.style.animationDelay = `${Math.min(index * 45, 450)}ms`;
      const nodeMark = document.createElement("span");
      nodeMark.className = "module-node-mark";
      nodeMark.textContent = key.slice(0, 3).toUpperCase();
      const nodeCopy = document.createElement("span");
      nodeCopy.className = "module-node-copy";
      const nodeName = document.createElement("strong");
      nodeName.textContent = name;
      const nodeState = document.createElement("small");
      nodeState.textContent = state;
      nodeCopy.append(nodeName, nodeState);
      node.append(nodeMark, nodeCopy);
      nodes.append(node);

      const row = document.createElement("div");
      row.className = "module-status-row";
      const dot = document.createElement("span");
      dot.className = `telemetry-dot${activeStates.has(slug) ? "" : " pending"}`;
      dot.setAttribute("aria-hidden", "true");
      const rowName = document.createElement("span");
      rowName.className = "module-name";
      rowName.textContent = name;
      const rowState = document.createElement("span");
      rowState.className = `module-state${activeStates.has(slug) ? " online" : ""}`;
      rowState.textContent = state;
      row.append(dot, rowName, rowState);
      statusList.append(row);
    });
    if (!modules.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No modules are registered.";
      nodes.append(empty);
      statusList.append(empty.cloneNode(true));
    }
    if (location.hash.startsWith("#module/") || legacyModuleRoutes[location.pathname]) updatePage();
  }

  function renderModuleDashboard(key) {
    const module = currentModules.find((item) => item.key === key);
    const title = byId("module-page-title");
    const statusChip = byId("module-page-status");
    const metrics = byId("module-page-metrics");
    const checks = byId("module-page-checks");
    if (!module) {
      title.textContent = "Module unavailable";
      byId("module-page-summary").textContent = "This module is not present in the live registry.";
      statusChip.className = "module-status-chip state-blocked";
      statusChip.textContent = "UNKNOWN";
      metrics.replaceChildren();
      checks.replaceChildren();
      renderWorldTimeline([], false);
      return;
    }
    const status = String(module.runtime_status || "unknown");
    byId("module-page-kicker").textContent = `MODULE ${String(module.id).padStart(2, "0")} / ${String(module.key).toUpperCase()}`;
    title.textContent = module.name || module.key;
    byId("module-page-summary").textContent = module.summary || "No runtime summary is available.";
    statusChip.className = `module-status-chip state-${stateName(status)}`;
    statusChip.textContent = status.toUpperCase();
    metrics.replaceChildren();
    (module.metrics || []).forEach((metric, index) => {
      const card = document.createElement("article");
      card.className = "module-page-metric";
      card.style.animationDelay = `${index * 55}ms`;
      const label = document.createElement("span");
      label.textContent = metric.label || "STATUS";
      const value = document.createElement("strong");
      value.textContent = metric.value || "UNKNOWN";
      card.append(label, value);
      metrics.append(card);
    });
    checks.replaceChildren();
    const moduleChecks = module.checks || [];
    const readyCount = moduleChecks.filter((check) => check.state === "ready").length;
    byId("module-check-count").textContent = `${readyCount}/${moduleChecks.length} ready`;
    moduleChecks.forEach((check) => {
      const row = document.createElement("div");
      row.className = "module-check-row";
      const dot = document.createElement("span");
      dot.className = `telemetry-dot ${stateName(check.state)}`;
      dot.setAttribute("aria-hidden", "true");
      const detail = document.createElement("span");
      detail.className = "module-check-copy";
      const name = document.createElement("strong");
      name.textContent = check.label || "Check";
      const note = document.createElement("small");
      note.textContent = check.detail || "No details supplied";
      const state = document.createElement("span");
      state.className = `module-check-state ${stateName(check.state)}`;
      state.textContent = String(check.state || "unknown").toUpperCase();
      detail.append(name, note);
      row.append(dot, detail, state);
      checks.append(row);
    });
    renderWorldTimeline(module.world_cards, module.key === "wic");
    document.title = `ARCHON — ${module.name || module.key}`;
    byId("module-page-next-step").textContent = module.next_step || "No next-step guidance is available.";
    byId("module-page-declared-state").textContent = `Manifest declaration: ${module.declared_state || module.state || "unreported"}. Runtime state is measured separately.`;
  }

  function renderWorldTimeline(cards, visible) {
    const panel = byId("world-overview");
    panel.hidden = !visible;
    if (!visible) return;
    const empty = byId("world-empty");
    const timeline = byId("world-timeline");
    timeline.replaceChildren();
    (Array.isArray(cards) ? cards.slice(0, 32) : []).forEach((card) => {
      if (!card || typeof card !== "object" || typeof card.title !== "string" || !Array.isArray(card.source_urls)) return;
      const sources = card.source_urls.filter((source) => {
        if (typeof source !== "string") return false;
        try {
          const url = new URL(source);
          return url.protocol === "https:" && !url.username && !url.password;
        } catch { return false; }
      }).slice(0, 32);
      if (!sources.length) return;
      const item = document.createElement("li");
      item.className = "world-card";
      const heading = document.createElement("h3");
      heading.textContent = card.title;
      item.append(heading);
      const dates = document.createElement("dl");
      [["Source/published date", card.published_at], ["Fetched date", card.fetched_at],
        ["Event date", card.event_at], ["Correction", card.correction]].forEach(([label, value]) => {
        const term = document.createElement("dt");
        term.textContent = label;
        const detail = document.createElement("dd");
        detail.textContent = typeof value === "string" && value ? value : (label === "Correction" ? "None reported" : "Unknown");
        dates.append(term, detail);
      });
      item.append(dates);
      const links = document.createElement("p");
      links.className = "world-card-sources";
      sources.forEach((source) => {
        const link = document.createElement("a");
        link.href = source;
        link.textContent = "Source";
        link.rel = "noreferrer";
        links.append(link);
      });
      item.append(links);
      timeline.append(item);
    });
    const hasStories = timeline.childElementCount > 0;
    empty.hidden = hasStories;
    timeline.hidden = !hasStories;
  }

  function updatePage() {
    const match = location.hash.match(/^#module\/([a-z0-9_-]+)$/i);
    const moduleKey = match ? match[1].toLowerCase() : (!location.hash ? legacyModuleRoutes[location.pathname] || null : null);
    const settingsPage = !location.hash && location.pathname === "/settings";
    const modulePage = Boolean(moduleKey);
    document.querySelectorAll(".overview-only").forEach((element) => element.classList.toggle("view-hidden", modulePage || settingsPage));
    byId("module-dashboard").classList.toggle("view-hidden", !modulePage);
    byId("world-dashboard").classList.toggle("view-hidden", moduleKey !== "wic");
    byId("settings-dashboard").classList.toggle("view-hidden", !settingsPage);
    document.querySelectorAll(".primary-nav .nav-link").forEach((link) => link.classList.toggle("active", settingsPage ? link.getAttribute("href") === "/settings" : (!modulePage && link.getAttribute("href") === "#overview")));
    document.querySelectorAll(".module-nav .nav-link").forEach((link) => link.classList.toggle("active", modulePage && link.getAttribute("href") === `#module/${moduleKey}`));
    if (settingsPage) document.title = "ARCHON — Settings";
    if (moduleKey) renderModuleDashboard(moduleKey);
  }

  function renderTasks(tasks) {
    const list = byId("task-list");
    list.replaceChildren();
    if (!tasks.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No tasks in the durable queue.";
      list.append(empty);
      return;
    }
    tasks.slice(0, 20).forEach((task) => {
      const row = document.createElement("div");
      row.className = "task-row";
      const id = document.createElement("span");
      id.className = "task-id";
      id.textContent = task.id || "task";
      const state = document.createElement("span");
      state.className = "task-state";
      state.textContent = task.state || "unknown";
      const meta = document.createElement("span");
      meta.className = "task-meta";
      meta.textContent = `${task.module || "module"} / ${task.priority || "normal"}`;
      row.append(id, state, meta);
      list.append(row);
    });
  }

  function renderCapabilities(data) {
    const list = byId("capability-list");
    list.replaceChildren();
    byId("auth-state").textContent = data.owner_key_store === "configured" ? "SIGNED GATE" : "OWNER KEY MISSING";
    const add = (name, state, reason = "") => {
      const row = document.createElement("div");
      row.className = "capability-row";
      const label = document.createElement("span");
      label.className = "capability-name";
      label.textContent = name.replaceAll("_", " ");
      const value = document.createElement("span");
      value.className = `capability-state${reason ? " blocked" : ""}`;
      value.textContent = state;
      row.append(label, value);
      if (reason) {
        const detail = document.createElement("span");
        detail.className = "capability-reason";
        detail.textContent = reason;
        row.append(detail);
      }
      list.append(row);
    };
    data.operations.forEach((operation) => add(operation, "QUEUE-GATED"));
    Object.entries(data.blocked).forEach(([name, reason]) => add(name, "LOCKED", reason));
    const controller = data.controller || {};
    byId("telemetry-controller").textContent = controller.process === "running" ? "RUNNING" : String(controller.process || "UNKNOWN").toUpperCase();
    byId("controller-dot").classList.toggle("offline", controller.process !== "running");
  }

  function addTurn(turn) {
    const history = byId("chat-history");
    const item = document.createElement("li");
    item.className = turn.role === "assistant" ? "turn-assistant" : "turn-user";
    const role = document.createElement("strong");
    role.textContent = turn.role === "assistant" ? "ARCHON / LOCAL" : "YOU";
    const content = document.createElement("p");
    content.textContent = turn.content || "";
    item.append(role, content);
    history.append(item);
    item.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }

  async function loadConversation() {
    try {
      const result = await getJson(`/api/chat?conversation_id=${encodeURIComponent(conversationId)}`);
      (result.turns || []).forEach(addTurn);
    } catch {
      byId("chat-status").textContent = "Conversation history is not available yet.";
    }
  }

  function setDot(id, state) {
    const element = byId(id);
    element.classList.toggle("offline", state === "offline");
    element.classList.toggle("pending", state === "pending");
  }

  async function refreshTelemetry() {
    const button = byId("refresh-runtime");
    button?.setAttribute("aria-busy", "true");
    try {
      const [healthResult, tasksResult, modulesResult, modelsResult, capabilitiesResult] = await Promise.allSettled([
        getJson("/api/health"), getJson("/api/tasks"), getJson("/api/modules"),
        getJson("/api/models"), getJson("/api/capabilities")
      ]);
      if (healthResult.status === "rejected") throw healthResult.reason;
      const health = healthResult.value;
      const healthy = health.status === "healthy";
      const controller = health.controller || {};
      const queue = health.queue || {};
      const controllerState = String(controller.process || "unknown").toLowerCase();
      const controlState = String(queue.control?.state || "unknown");
      byId("metric-runtime").textContent = healthy ? "HEALTHY" : String(health.status || "UNKNOWN").toUpperCase();
      byId("metric-runtime-note").textContent = `SQLite integrity ${Object.values(health.sqlite || {}).every((item) => item.integrity === "ok") ? "OK" : "CHECK"} · ${String(health.git?.checkout_sha || "").slice(0, 8)}`;
      byId("header-state").textContent = healthy ? "ARCHON ONLINE" : "DEGRADED";
      byId("header-led").classList.toggle("offline", !healthy);
      byId("core-state").textContent = healthy ? "LOCAL RUNTIME HEALTHY" : "CHECK RUNTIME";
      byId("telemetry-runtime").textContent = String(health.status || "UNKNOWN").toUpperCase();
      setDot("runtime-dot", healthy ? "online" : "offline");
      byId("telemetry-controller").textContent = controllerState.toUpperCase();
      setDot("controller-dot", controllerState === "running" ? "online" : "offline");
      byId("telemetry-queue").textContent = controlState.toUpperCase();
      setDot("queue-dot", controlState === "running" ? "online" : "pending");
      byId("metric-queue").textContent = String(queue.total ?? 0);
      byId("metric-queue-note").textContent = `Durable records · control ${controlState}`;

      if (tasksResult.status === "fulfilled") renderTasks(tasksResult.value.tasks || []);
      if (modulesResult.status === "fulfilled") renderModules(modulesResult.value.modules || []);
      if (modelsResult.status === "fulfilled") {
        const models = modelsResult.value;
        const ready = Boolean(models.configured_available);
        const installed = (models.models || []).length;
        byId("metric-model").textContent = models.configured || "LOCAL MODEL";
        byId("metric-model-note").textContent = ready ? `${installed} installed · inference ready` : "Configured model is unavailable";
        byId("chat-model-chip").textContent = ready ? `${models.configured} / LOCAL` : "MODEL OFFLINE";
        byId("assistant-model-chip").textContent = ready ? `${models.configured} / LOCAL` : "MODEL OFFLINE";
        byId("telemetry-model").textContent = ready ? "READY" : "OFFLINE";
        setDot("model-dot", ready ? "online" : "offline");
      } else {
        byId("metric-model-note").textContent = "Ollama status unavailable";
        byId("telemetry-model").textContent = "UNKNOWN";
        setDot("model-dot", "offline");
      }
      if (capabilitiesResult.status === "fulfilled") renderCapabilities(capabilitiesResult.value);
      byId("telemetry-updated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
      byId("last-refresh").textContent = `TELEMETRY ${new Date().toLocaleTimeString()}`;
    } catch {
      byId("header-state").textContent = "NODE UNAVAILABLE";
      byId("header-led").classList.add("offline");
      byId("metric-runtime").textContent = "OFFLINE";
      byId("metric-runtime-note").textContent = "Runtime health endpoint unavailable";
      byId("core-state").textContent = "NO SIGNAL";
      setDot("runtime-dot", "offline");
      byId("telemetry-updated").textContent = "Telemetry unavailable";
    } finally {
      button?.removeAttribute("aria-busy");
    }
  }

  byId("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = byId("chat-message");
    const button = byId("chat-send");
    const panel = document.querySelector(".assistant-panel");
    const text = message.value.trim();
    if (!text) return;
    button.disabled = true;
    panel.setAttribute("aria-busy", "true");
    byId("chat-status").textContent = "Local model is thinking…";
    try {
      const response = await fetch("/api/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation_id: conversationId, message: text })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "local chat failed");
      addTurn({ role: "user", content: text });
      addTurn({ role: "assistant", content: result.response });
      message.value = "";
      byId("chat-status").textContent = result.saved ? `Answered by ${result.model}; saved locally.` : "Response returned; persistence not confirmed.";
    } catch {
      byId("chat-status").textContent = "Local chat failed; no completed response was saved.";
    } finally {
      panel.removeAttribute("aria-busy");
      button.disabled = false;
      message.focus();
      refreshTelemetry();
    }
  });

  byId("refresh-runtime").addEventListener("click", refreshTelemetry);
  byId("chat-message").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) byId("chat-form").requestSubmit();
  });
  window.addEventListener("hashchange", updatePage);
  updatePage();
  loadConversation();
  refreshTelemetry();
  window.setInterval(() => { if (!document.hidden) refreshTelemetry(); }, 15000);
})();
