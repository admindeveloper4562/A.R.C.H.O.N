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
    "/settings": ["Settings", "Settings changes require an authenticated owner session."]
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
})();
