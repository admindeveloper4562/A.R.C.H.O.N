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
  let moduleDataRequest = 0;
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
      byId("module-live-controls").replaceChildren();
      byId("module-live-metrics").replaceChildren();
      byId("module-live-sections").replaceChildren();
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
    loadModuleData(key);
  }

  function prepareModuleControls(key) {
    const controls = byId("module-live-controls");
    if (controls.dataset.moduleKey === key) return;
    controls.dataset.moduleKey = key;
    controls.replaceChildren();
    if (key === "research") {
      const form = document.createElement("form");
      form.className = "module-research-form";
      const label = document.createElement("label");
      label.htmlFor = "module-research-query";
      label.textContent = "Search tracked local source";
      const input = document.createElement("input");
      input.id = "module-research-query";
      input.type = "search";
      input.maxLength = 512;
      input.placeholder = "Try: owner approval, event bus, or scheduler";
      const button = document.createElement("button");
      button.type = "submit";
      button.className = "send-button";
      button.textContent = "Search local source";
      form.append(label, input, button);
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        loadModuleData(key, input.value.trim());
      });
      controls.append(form);
      return;
    }
    const forms = {
      tws: [
        ["add_wing", "Add a local wing", [{ name: "wing_id", label: "Wing ID" }, { name: "name", label: "Name" }]],
        ["create_quest", "Create a local quest", [{ name: "quest_id", label: "Quest ID" }, { name: "wing_id", label: "Wing ID" }, { name: "title", label: "Title" }, { name: "kind", label: "Kind", value: "skill" }, { name: "cadence", label: "Cadence", value: "once" }]]
      ],
      finance: [
        ["open_paper_account", "Open paper account", [{ name: "account_id", label: "Account ID" }, { name: "scope_id", label: "Scope ID", value: "local-paper" }, { name: "currency", label: "Currency", value: "THB" }, { name: "cash_satang", label: "Initial cash (satang)", type: "number", min: "0" }]],
        ["place_paper_order", "Place paper order", [{ name: "order_id", label: "Order ID" }, { name: "account_id", label: "Paper account ID" }, { name: "symbol", label: "Symbol" }, { name: "side", label: "Side", type: "select", options: ["buy", "sell"] }, { name: "quantity", label: "Quantity", type: "number", min: "1" }, { name: "price_satang", label: "Limit price (satang)", type: "number", min: "1" }]],
        ["fill_paper_order", "Simulate paper fill", [{ name: "order_id", label: "Order ID" }]]
      ],
      automation: [
        ["schedule_once", "Schedule local reminder", [{ name: "schedule_id", label: "Schedule ID" }, { name: "message", label: "Reminder", type: "textarea" }, { name: "due_at", label: "Due time (your local time)", type: "datetime-local" }]]
      ]
    };
    (forms[key] || []).forEach(([action, title, fields]) => {
      controls.append(createModuleActionForm(key, action, title, fields));
    });
  }

  function createModuleActionForm(module, action, title, fields) {
    const form = document.createElement("form");
    form.className = "module-action-form";
    const heading = document.createElement("h3");
    heading.textContent = title;
    form.append(heading);
    fields.forEach((field) => {
      const label = document.createElement("label");
      const id = `module-${module}-${action}-${field.name}`;
      label.htmlFor = id;
      label.textContent = field.label;
      let input;
      if (field.type === "textarea") input = document.createElement("textarea");
      else if (field.type === "select") {
        input = document.createElement("select");
        field.options.forEach((option) => {
          const item = document.createElement("option");
          item.value = option;
          item.textContent = option;
          input.append(item);
        });
      } else input = document.createElement("input");
      input.id = id;
      input.name = field.name;
      if (field.type !== "textarea" && field.type !== "select") input.type = field.type || "text";
      if (field.value) input.value = field.value;
      if (field.min) input.min = field.min;
      input.required = true;
      form.append(label, input);
    });
    const button = document.createElement("button");
    button.type = "submit";
    button.className = "send-button";
    button.textContent = title;
    form.append(button);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      try {
        for (const name of ["cash_satang", "quantity", "price_satang"]) {
          if (name in payload) {
            const value = Number(payload[name]);
            if (!Number.isSafeInteger(value)) throw new Error(`${name} must be a whole number`);
            payload[name] = value;
          }
        }
        if (action === "schedule_once") {
          const due = new Date(payload.due_at);
          if (!Number.isFinite(due.valueOf())) throw new Error("due time is invalid");
          payload.due_at = due.toISOString();
          payload.timezone_name = "UTC";
        }
        await submitModuleAction(module, action, payload);
        form.reset();
      } catch (error) {
        byId("module-live-status").textContent = String(error.message || "Module action failed.");
      }
    });
    return form;
  }

  async function submitModuleAction(module, action, payload) {
    byId("module-live-status").textContent = "Saving local module data…";
    const response = await fetch("/api/module-action", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module, action, payload })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "module_action_failed");
    byId("module-live-status").textContent = `${action.replaceAll("_", " ")} saved in ${result.mode} state.`;
    await loadModuleData(module);
  }

  function renderModuleLiveData(data) {
    byId("module-live-mode").textContent = String(data.mode || "LOCAL").replaceAll("_", " ").toUpperCase();
    byId("module-live-summary").textContent = data.summary || "No live module data is available.";
    const metrics = byId("module-live-metrics");
    metrics.replaceChildren();
    (Array.isArray(data.metrics) ? data.metrics : []).slice(0, 8).forEach((metric, index) => {
      const card = document.createElement("article");
      card.className = "module-live-metric";
      card.style.animationDelay = `${index * 45}ms`;
      const label = document.createElement("span");
      label.textContent = String(metric.label || "STATUS");
      const value = document.createElement("strong");
      value.textContent = String(metric.value ?? "UNKNOWN");
      card.append(label, value);
      metrics.append(card);
    });
    const sections = byId("module-live-sections");
    sections.replaceChildren();
    (Array.isArray(data.sections) ? data.sections : []).slice(0, 12).forEach((section) => {
      const panel = document.createElement("section");
      panel.className = "module-live-section";
      const heading = document.createElement("h3");
      heading.textContent = String(section.title || "Module data");
      panel.append(heading);
      const items = Array.isArray(section.items) ? section.items.slice(0, 40) : [];
      if (!items.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = section.empty || "No entries recorded.";
        panel.append(empty);
      } else {
        const list = document.createElement("ul");
        list.className = "module-live-list";
        items.forEach((value) => {
          const item = document.createElement("li");
          item.className = "module-live-item";
          const title = document.createElement("strong");
          title.textContent = String(value.title || "Entry");
          const details = document.createElement("small");
          details.textContent = String(value.details || "");
          item.append(title, details);
          if (typeof value.url === "string") {
            try {
              const url = new URL(value.url);
              if (url.protocol === "https:" && !url.username && !url.password) {
                const link = document.createElement("a");
                link.href = url.href;
                link.textContent = "Open source";
                link.rel = "noreferrer";
                item.append(link);
              }
            } catch { /* invalid source links stay plain text */ }
          }
          if (data.module === "automation" && typeof value.schedule_id === "string" && value.schedule_id) {
            const cancel = document.createElement("button");
            cancel.type = "button";
            cancel.className = "module-action-button";
            cancel.textContent = "Cancel reminder";
            cancel.addEventListener("click", async () => {
              try {
                await submitModuleAction("automation", "cancel_schedule", { schedule_id: value.schedule_id });
              } catch (error) {
                byId("module-live-status").textContent = String(error.message || "Reminder cancellation failed.");
              }
            });
            item.append(cancel);
          }
          list.append(item);
        });
        panel.append(list);
      }
      sections.append(panel);
    });
  }

  async function loadModuleData(key, requestedQuery) {
    prepareModuleControls(key);
    const request = ++moduleDataRequest;
    const queryInput = byId("module-research-query");
    const query = typeof requestedQuery === "string" ? requestedQuery : (key === "research" ? queryInput?.value.trim() || "" : "");
    const params = new URLSearchParams({ key });
    if (query) params.set("q", query);
    byId("module-live-status").textContent = "Loading live module data…";
    try {
      const data = await getJson(`/api/module-data?${params.toString()}`);
      if (request !== moduleDataRequest) return;
      renderModuleLiveData(data);
      byId("module-live-status").textContent = data.snapshot_sha ? `Source snapshot ${String(data.snapshot_sha).slice(0, 12)} · results are local to this checkout.` : "Live data read from ARCHON's local runtime stores.";
    } catch (error) {
      if (request !== moduleDataRequest) return;
      byId("module-live-summary").textContent = "This module's live data endpoint is unavailable.";
      byId("module-live-metrics").replaceChildren();
      byId("module-live-sections").replaceChildren();
      byId("module-live-status").textContent = String(error.message || "module_data_unavailable");
    }
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
    else if (moduleKey) renderModuleDashboard(moduleKey);
    else document.title = "ARCHON — Mission Control";
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
