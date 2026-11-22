(() => {
  "use strict";
  const pages = Object.freeze({
    "/": ["Home", "Local dashboard navigation is ready."],
    "/calendar": ["Calendar", "Calendar handoffs remain behind authenticated Runtime permissions."],
    "/email": ["Email", "Email views remain read-only until an approved connector is available."],
    "/actions": ["Actions", "Owner-approved actions are shown through the control plane."],
    "/files": ["Files", "File inventory is presented as bounded metadata."],
    "/system": ["System", "System health is read-only and evidence-backed."],
    "/projects": ["Projects", "Project state is supplied by the authenticated task boundary."],
    "/voice": ["Voice", "Voice capabilities remain disabled until a local adapter is configured."],
    "/activity": ["Activity", "Activity is rendered from durable, redacted event records."],
    "/settings": ["Settings", "Settings changes require an authenticated owner session."],
    "/world": ["World", "Source-backed world cards retain publication, fetch and event dates."],
    "/world/timeline": ["World timeline", "Chronological cards retain source attribution and corrections."]
  });
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  const page = pages[path] || pages["/"];
  const title = document.querySelector("[data-page-title]");
  const summary = document.querySelector("[data-page-summary]");
  if (title) title.textContent = page[0];
  if (summary) summary.textContent = page[1];
  document.title = `ARCHON — ${page[0]}`;
  document.querySelectorAll("[data-route]").forEach((link) => {
    if (link.getAttribute("data-route") === path) link.setAttribute("aria-current", "page");
  });

  const worldPanel = document.querySelector("[data-world-overview]");
  const empty = document.querySelector("[data-world-empty]");
  const timeline = document.querySelector("[data-world-timeline]");

  function renderWorldTimeline(cards) {
    if (!worldPanel || !empty || !timeline) return;
    const isWorldRoute = path === "/world" || path === "/world/timeline";
    worldPanel.hidden = !isWorldRoute;
    if (!isWorldRoute) return;
    const values = Array.isArray(cards) ? cards.slice(0, 32) : [];
    timeline.replaceChildren();
    empty.hidden = values.length > 0;
    timeline.hidden = values.length === 0;
    values.forEach((card) => {
      if (!card || typeof card !== "object" || typeof card.title !== "string") return;
      const item = document.createElement("li");
      item.className = "world-card";
      const heading = document.createElement("h3");
      heading.textContent = card.title;
      item.append(heading);
      const dates = document.createElement("dl");
      [["Source/published date", "published_at"], ["Fetched date", "fetched_at"],
        ["Event date", "event_at"], ["Status", "status"]].forEach(([label, key]) => {
        const term = document.createElement("dt");
        term.textContent = label;
        const value = document.createElement("dd");
        value.textContent = typeof card[key] === "string" ? card[key] : "Unknown";
        dates.append(term, value);
      });
      item.append(dates);
      if (Array.isArray(card.source_urls)) {
        const sources = document.createElement("p");
        sources.className = "world-card-sources";
        card.source_urls.slice(0, 32).forEach((source) => {
          if (typeof source !== "string" || !/^https:\/\//.test(source)) return;
          const link = document.createElement("a");
          link.href = source;
          link.textContent = "Source";
          link.rel = "noreferrer";
          sources.append(link);
        });
        if (sources.childElementCount) item.append(sources);
      }
      if (typeof card.correction === "string" && card.correction.trim()) {
        const correction = document.createElement("p");
        correction.className = "world-card-correction";
        correction.textContent = `Correction: ${card.correction}`;
        item.append(correction);
      }
      timeline.append(item);
    });
    if (timeline.childElementCount) {
      empty.hidden = true;
      timeline.hidden = false;
    }
  }

  renderWorldTimeline(window.ARCHON_WORLD_CARDS);

  const history = document.querySelector("#chat-history");
  const chatForm = document.querySelector("#chat-form");
  const chatStatus = document.querySelector("#chat-status");
  const conversationKey = "archon.local.conversation";
  let conversationId = sessionStorage.getItem(conversationKey);
  if (!conversationId) {
    conversationId = crypto.randomUUID();
    sessionStorage.setItem(conversationKey, conversationId);
  }

  function addTurn(turn) {
    const item = document.createElement("li");
    const role = document.createElement("strong");
    role.textContent = turn.role === "assistant" ? "ARCHON" : "You";
    const content = document.createElement("p");
    content.textContent = turn.content;
    item.append(role, content);
    history.append(item);
  }

  async function loadRuntime() {
    const status = document.querySelector("#runtime-status");
    const details = document.querySelector("#runtime-details");
    try {
      const [healthResponse, taskResponse, moduleResponse, modelResponse] = await Promise.all([
        fetch("/api/health"), fetch("/api/tasks"), fetch("/api/modules"), fetch("/api/models")
      ]);
      if (![healthResponse, taskResponse, moduleResponse, modelResponse].every((response) => response.ok)) throw new Error();
      const [health, tasks, modules, modelInfo] = await Promise.all([
        healthResponse.json(), taskResponse.json(), moduleResponse.json(), modelResponse.json()
      ]);
      status.textContent = `Runtime ${health.status}; queue control ${health.queue.control.state}; ${health.queue.total} queued tasks.`;
      const modelStatus = modelInfo.configured_available ? `${modelInfo.configured} ready` : `${modelInfo.configured} unavailable`;
      details.textContent = `${modules.modules.length} module definitions; ${tasks.tasks.length} persisted task records; local model ${modelStatus}; service unit ${health.controller.service}.`;
    } catch {
      status.textContent = "Runtime status is unavailable.";
    }
  }

  if (history && chatForm && chatStatus) {
    fetch(`/api/chat?conversation_id=${encodeURIComponent(conversationId)}`)
      .then((response) => response.ok ? response.json() : { turns: [] })
      .then((result) => (result.turns || []).forEach(addTurn))
      .catch(() => {});
    chatForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const message = document.querySelector("#chat-message");
      const button = document.querySelector("#chat-send");
      const text = message.value.trim();
      if (!text) return;
      button.disabled = true;
      chatStatus.textContent = "Asking the local model…";
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
        chatStatus.textContent = `Answered by ${result.model}; conversation saved locally.`;
      } catch {
        chatStatus.textContent = "Local chat failed; no response was saved.";
      } finally {
        button.disabled = false;
        message.focus();
      }
    });
  }
  loadRuntime();
})();
