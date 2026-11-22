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

  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return response.json();
  }

  function stateName(value) {
    return String(value || "unreported").trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-");
  }

  function renderModules(modules) {
    const nav = byId("module-nav");
    const nodes = byId("module-nodes");
    const statusList = byId("module-status-list");
    nav.replaceChildren();
    nodes.replaceChildren();
    statusList.replaceChildren();
    const active = modules.filter((module) => activeStates.has(stateName(module.state))).length;
    byId("module-count").textContent = `${modules.length} registered`;
    byId("module-active-count").textContent = `${active}/${modules.length} active`;
    byId("metric-modules").textContent = `${active}/${modules.length}`;
    byId("metric-modules-note").textContent = `${modules.length} module definitions · ${active} reporting active`;

    modules.forEach((module, index) => {
      const key = String(module.key || `module-${index + 1}`);
      const name = String(module.name || key);
      const state = String(module.state || "unreported");
      const slug = stateName(state);
      const navLink = document.createElement("a");
      navLink.className = "nav-link";
      navLink.href = `#module-${encodeURIComponent(key)}`;
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
      node.id = `module-${key}`;
      node.href = "#execution";
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
  loadConversation();
  refreshTelemetry();
  window.setInterval(() => { if (!document.hidden) refreshTelemetry(); }, 15000);
})();
