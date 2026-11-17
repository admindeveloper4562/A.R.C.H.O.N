const DEFAULT_MAX_REQUESTS = 60;
const DEFAULT_WINDOW_SECONDS = 60;

function setting(value, fallback, maximum) {
  const result = Number(value ?? fallback);
  return Number.isSafeInteger(result) && result >= 1 && result <= maximum ? result : null;
}

async function digest(value) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function allowRequest(request, env, scope) {
  if (typeof env.__rateLimit === "function") return env.__rateLimit(request, scope);
  const maxRequests = setting(env.RATE_LIMIT_MAX_REQUESTS, DEFAULT_MAX_REQUESTS, 10000);
  const windowSeconds = setting(env.RATE_LIMIT_WINDOW_SECONDS, DEFAULT_WINDOW_SECONDS, 86400);
  if (!env.DB || !maxRequests || !windowSeconds) throw new Error("rate_limit_not_configured");
  const now = typeof env.__now === "function" ? env.__now() : Math.floor(Date.now() / 1000);
  if (!Number.isSafeInteger(now) || now < 0) throw new Error("rate_limit_clock_unavailable");
  const identity = request.headers.get("CF-Connecting-IP") || "anonymous";
  const keyHash = await digest(`archon-rate-v1:${scope}:${identity}`);
  const windowStart = Math.floor(now / windowSeconds) * windowSeconds;
  await env.DB.prepare(`INSERT INTO rate_limit_buckets (key_hash, window_start, count)
    VALUES (?, ?, 1) ON CONFLICT(key_hash) DO UPDATE SET
    window_start=CASE WHEN window_start + ? <= ? THEN ? ELSE window_start END,
    count=CASE WHEN window_start + ? <= ? THEN 1 ELSE MIN(count + 1, ?) END`)
    .bind(keyHash, windowStart, windowSeconds, now, windowStart, windowSeconds, now, maxRequests + 1).run();
  const row = await env.DB.prepare("SELECT window_start, count FROM rate_limit_buckets WHERE key_hash=?").bind(keyHash).first();
  return Boolean(row && row.window_start === windowStart && row.count <= maxRequests);
}

export { DEFAULT_MAX_REQUESTS, DEFAULT_WINDOW_SECONDS, allowRequest };
