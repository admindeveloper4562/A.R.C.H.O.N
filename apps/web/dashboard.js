(() => {
  "use strict";
  const byId = (id) => document.getElementById(id);
  const conversationKey = "archon.local.conversation";
  let conversationId = sessionStorage.getItem(conversationKey);
  if (!conversationId) {
    conversationId = crypto.randomUUID();
    sessionStorage.setItem(conversationKey, conversationId);
  }

  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return response.json();
  }

  function renderModules(modules) {
    const grid = byId("module-grid");
    grid.replaceChildren();
    byId("module-count").textContent = `${modules.length} manifest entries`;
    modules.forEach((module) => {
      const card = document.createElement("article");
      card.className = "module-card";
      const head = document.createElement("div");
      head.className = "module-head";
      const key = document.createElement("span");
      key.className = "module-key";
      key.textContent = module.key || "unknown";
      const state = document.createElement("span");
      state.className = "module-state";
      state.textContent = module.state || "unreported";
      head.append(key, state);
      const name = document.createElement("p");
      name.className = "module-name";
      name.textContent = module.name || module.key || "Unnamed module";
      card.append(head, name);
      grid.append(card);
    });
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
      byId("metric-runtime").textContent = healthy ? "HEALTHY" : String(health.status || "UNKNOWN").toUpperCase();
      byId("metric-runtime-note").textContent = `SQLite integrity OK · ${String(health.git.checkout_sha).slice(0, 8)}`;
      byId("header-state").textContent = healthy ? "NODE ONLINE" : "DEGRADED";
      byId("header-led").classList.toggle("offline", !healthy);
      byId("visual-health").textContent = healthy ? "SYSTEM HEALTHY" : "CHECK RUNTIME";
      byId("metric-controller").textContent = String(health.controller.process || "unknown").toUpperCase();
      byId("metric-controller-note").textContent = `Writer lease · systemd ${health.controller.service}`;
      byId("metric-queue").textContent = String(health.queue.total);
      byId("metric-queue-note").textContent = `Durable records · control ${health.queue.control.state}`;
      if (tasksResult.status === "fulfilled") renderTasks(tasksResult.value.tasks || []);
      if (modulesResult.status === "fulfilled") renderModules(modulesResult.value.modules || []);
      if (modelsResult.status === "fulfilled") {
        const models = modelsResult.value;
        const ready = models.configured_available;
        byId("metric-model").textContent = models.configured || "LOCAL MODEL";
        byId("metric-model-note").textContent = ready ? `${(models.models || []).length} installed · inference ready` : "Configured model is unavailable";
        byId("chat-model-chip").textContent = ready ? `${models.configured} / LOCAL` : "MODEL OFFLINE";
      }
      if (capabilitiesResult.status === "fulfilled") renderCapabilities(capabilitiesResult.value);
      byId("last-refresh").textContent = `TELEMETRY ${new Date().toLocaleTimeString()}`;
    } catch {
      byId("header-state").textContent = "NODE UNAVAILABLE";
      byId("header-led").classList.add("offline");
      byId("metric-runtime").textContent = "OFFLINE";
      byId("metric-runtime-note").textContent = "Runtime health endpoint unavailable";
      byId("visual-health").textContent = "NO SIGNAL";
    } finally {
      button?.removeAttribute("aria-busy");
    }
  }

  byId("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = byId("chat-message");
    const button = byId("chat-send");
    const text = message.value.trim();
    if (!text) return;
    button.disabled = true;
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
      byId("chat-status").textContent = result.saved ? `Answered by ${result.model}; saved to local memory.` : "Response returned; persistence not confirmed.";
    } catch {
      byId("chat-status").textContent = "Local chat failed; no completed response was saved.";
    } finally {
      button.disabled = false;
      message.focus();
      refreshTelemetry();
    }
  });

  byId("refresh-runtime").addEventListener("click", refreshTelemetry);
  byId("chat-message").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) byId("chat-form").requestSubmit();
  });
  loadConversation();
  refreshTelemetry();
  window.setInterval(() => { if (!document.hidden) refreshTelemetry(); }, 15000);
})();
