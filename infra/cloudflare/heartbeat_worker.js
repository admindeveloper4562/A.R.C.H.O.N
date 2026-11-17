const DEFAULT_TIMEOUT_SECONDS = 120;
const MAX_BODY_BYTES = 512;
const DEVICE_ID = /^[A-Za-z0-9_.:-]{1,128}$/;
const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
};

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

function clock(env) {
  return typeof env.__now === "function" ? env.__now() : Math.floor(Date.now() / 1000);
}

function timeout(env) {
  const value = env.HEARTBEAT_TIMEOUT_SECONDS ?? DEFAULT_TIMEOUT_SECONDS;
  const seconds = Number(value);
  return Number.isSafeInteger(seconds) && seconds >= 1 && seconds <= 86400 ? seconds : null;
}

function devicePath(url) {
  const parts = url.pathname.split("/");
  if (parts.length !== 5 || parts[1] !== "v1" || parts[2] !== "devices" || !DEVICE_ID.test(parts[3])) {
    return null;
  }
  return { deviceId: parts[3], action: parts[4] };
}

async function heartbeat(request, env, deviceId, receivedAt) {
  const length = request.headers.get("content-length");
  if (length && Number(length) > MAX_BODY_BYTES) return json({ error: "payload_too_large" }, 413);
  const text = await request.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) return json({ error: "payload_too_large" }, 413);

  let body = {};
  if (text.trim()) {
    try { body = JSON.parse(text); } catch { return json({ error: "invalid_json" }, 400); }
  }
  if (!body || typeof body !== "object" || Array.isArray(body) ||
      Object.keys(body).some((key) => key !== "observed_at")) {
    return json({ error: "invalid_heartbeat" }, 400);
  }
  const observedAt = body.observed_at ?? receivedAt;
  if (!Number.isSafeInteger(observedAt) || observedAt < 0 || observedAt > receivedAt + 1) {
    return json({ error: "invalid_heartbeat" }, 400);
  }
  await env.DB.prepare(`INSERT INTO device_heartbeats
    (device_id, status, observed_at, received_at) VALUES (?, 'online', ?, ?)
    ON CONFLICT(device_id) DO UPDATE SET status='online', observed_at=excluded.observed_at,
    received_at=excluded.received_at`).bind(deviceId, observedAt, receivedAt).run();
  return json({ device_id: deviceId, status: "online", last_heartbeat_at: receivedAt,
    observed_at: observedAt, execution_status: "not_executed" }, 201);
}

async function status(env, deviceId, now, timeoutSeconds) {
  const staleBefore = now - timeoutSeconds;
  await env.DB.prepare(`UPDATE device_heartbeats SET status='offline'
    WHERE device_id=? AND status='online' AND received_at <= ?`).bind(deviceId, staleBefore).run();
  const row = await env.DB.prepare(`SELECT device_id, status, observed_at, received_at
    FROM device_heartbeats WHERE device_id=?`).bind(deviceId).first();
  if (!row) {
    return json({ device_id: deviceId, status: "offline", known: false,
      stale: true, execution_status: "not_executed" });
  }
  const online = row.status === "online" && row.received_at > staleBefore;
  return json({ device_id: deviceId, status: online ? "online" : "offline", known: true,
    stale: !online, last_heartbeat_at: row.received_at, observed_at: row.observed_at,
    execution_status: "not_executed" });
}

export default {
  async fetch(request, env) {
    const route = devicePath(new URL(request.url));
    if (!route) return json({ error: "not_found" }, 404);
    const timeoutSeconds = timeout(env);
    if (!env.DB || !env.HEARTBEAT_INGEST_TOKEN || !env.HEARTBEAT_VIEW_TOKEN || timeoutSeconds === null) {
      return json({ error: "not_configured" }, 503);
    }
    const now = clock(env);
    if (!Number.isSafeInteger(now) || now < 0) return json({ error: "clock_unavailable" }, 503);
    if (route.action === "heartbeat" && request.method === "POST") {
      if (!authorized(request, env.HEARTBEAT_INGEST_TOKEN)) return json({ error: "unauthorized" }, 401);
      try { return await heartbeat(request, env, route.deviceId, now); }
      catch { return json({ error: "database_error" }, 500); }
    }
    if (route.action === "status" && request.method === "GET") {
      if (!authorized(request, env.HEARTBEAT_VIEW_TOKEN)) return json({ error: "unauthorized" }, 401);
      try { return await status(env, route.deviceId, now, timeoutSeconds); }
      catch { return json({ error: "database_error" }, 500); }
    }
    return json({ error: "method_not_allowed" }, 405);
  },
};

export { DEFAULT_TIMEOUT_SECONDS };
