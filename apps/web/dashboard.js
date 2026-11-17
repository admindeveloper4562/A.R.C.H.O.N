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
})();
