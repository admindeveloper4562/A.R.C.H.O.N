const TASK_ID = /^[A-Z][A-Z0-9-]{2,48}$/;
const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
};
const HTML_HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "content-security-policy": "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'",
};
const DASHBOARD = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ARCHON SDA</title></head>
<body><h1>ARCHON SDA dashboard</h1><p>Public aggregate status only. Authenticated task evidence is available through the private API.</p>
<pre id="summary">Loading…</pre><script src="/dashboard.js" defer></script></body></html>`;
const DASHBOARD_JS = `fetch('/api/public/summary').then(r=>r.json()).then(v=>document.getElementById('summary').textContent=JSON.stringify(v,null,2)).catch(()=>document.getElementById('summary').textContent='unavailable');`;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });
}

function equal(a, b) {
  const left = new TextEncoder().encode(a);
  const right = new TextEncoder().encode(b);
  let difference = left.length ^ right.length;
  for (let index = 0; index < Math.max(left.length, right.length); index += 1) {
    difference |= (left[index] || 0) ^ (right[index] || 0);
  }
  return difference === 0 && left.length > 0;
}

function authorized(request, token) {
  return Boolean(token && equal(request.headers.get("authorization") || "", `Bearer ${token}`));
}

function taskId(path) {
  const parts = path.split("/");
  return parts.length === 5 && parts[1] === "api" && parts[2] === "private" && parts[3] === "tasks" && TASK_ID.test(parts[4])
    ? parts[4] : null;
}

function publicSummary(rows) {
  const counts = { total: 0 };
  for (const row of rows.results || []) {
    const count = Number(row.count);
    if (!Number.isSafeInteger(count) || count < 0) continue;
    counts[row.stage] = count;
    counts.total += count;
  }
  return { counts };
}

function taskEvidence(run, events) {
  const evidence = (events || []).map((event) => ({
    seq: event.seq, time: event.time, stage: event.stage, step: event.step,
    result: event.result, tool_count: event.tool_count, elapsed_s: event.elapsed_s, attempt: event.attempt,
  }));
  return {
    task_id: run?.task_id || null,
    phase: run?.stage || null,
    worker: run ? { identity: null, branch: run.branch, run_id: run.run_id, attempt: run.attempt } : null,
    qc: evidence.filter((event) => ["verifying", "awaiting_review", "approved"].includes(event.stage)),
    merge: evidence.filter((event) => event.stage === "completed" || event.step.includes("merge")),
    failures: evidence.filter((event) => ["failed", "interrupted", "stopped"].includes(event.stage)),
    events: evidence,
  };
}

async function privateRuns(env) {
  const rows = await env.DB.prepare(`SELECT run_id, task_id, stage, step, branch, base_sha,
    tool_count, seq, result, elapsed_s, attempt, last_seen_at FROM astra_runs
    ORDER BY last_seen_at DESC LIMIT 100`).all();
  return json({ runs: rows.results || [] });
}

async function privateTask(env, id) {
  const run = await env.DB.prepare(`SELECT run_id, task_id, stage, step, branch, base_sha,
    tool_count, seq, result, elapsed_s, attempt, last_seen_at FROM astra_runs
    WHERE task_id=? ORDER BY last_seen_at DESC LIMIT 1`).bind(id).first();
  const events = await env.DB.prepare(`SELECT seq, time, stage, step, tool_count, result, elapsed_s, attempt
    FROM astra_events WHERE task_id=? ORDER BY seq DESC LIMIT 100`).bind(id).all();
  return json(taskEvidence(run, (events.results || []).reverse()));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return new Response(DASHBOARD, { headers: HTML_HEADERS });
    if (request.method === "GET" && url.pathname === "/dashboard.js") return new Response(DASHBOARD_JS, { headers: { ...HTML_HEADERS, "content-type": "text/javascript; charset=utf-8" } });
    if (!env.DB || !env.DASHBOARD_VIEW_TOKEN) return json({ error: "not_configured" }, 503);
    if (request.method === "GET" && url.pathname === "/api/public/summary") {
      try {
        const rows = await env.DB.prepare(`SELECT r.stage, COUNT(*) AS count FROM astra_runs r
          WHERE r.run_id=(SELECT s.run_id FROM astra_runs s WHERE s.task_id=r.task_id
          ORDER BY s.last_seen_at DESC, s.run_id DESC LIMIT 1) GROUP BY r.stage`).all();
        return json(publicSummary(rows));
      } catch { return json({ error: "database_error" }, 500); }
    }
    if (!authorized(request, env.DASHBOARD_VIEW_TOKEN)) return json({ error: "unauthorized" }, 401);
    try {
      if (request.method === "GET" && url.pathname === "/api/private/runs") return await privateRuns(env);
      if (request.method === "GET" && taskId(url.pathname)) return await privateTask(env, taskId(url.pathname));
    } catch { return json({ error: "database_error" }, 500); }
    return json({ error: "not_found" }, 404);
  },
};

export { publicSummary, taskEvidence };
