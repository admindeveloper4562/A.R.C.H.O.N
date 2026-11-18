interface Env {
  DB: D1Database;
  COORDINATOR_TOKEN: string;
  LEASE_SECONDS?: string;
  RETENTION_DAYS?: string;
}

type JobStatus = "queued" | "leased" | "completed" | "failed";
type JsonObject = Record<string, unknown>;

interface JobRow {
  id: string;
  kind: string;
  priority: number;
  payload_json: string;
  status: JobStatus;
  idempotency_key: string | null;
  worker_id: string | null;
  lease_token: string | null;
  leased_at: number | null;
  lease_expires_at: number | null;
  attempts: number;
  max_attempts: number;
  available_at: number;
  result_json: string | null;
  error: string | null;
  created_at: number;
  updated_at: number;
  completed_at: number | null;
}

interface WorkerRow {
  id: string;
  status: "online" | "offline";
  capabilities_json: string;
  last_seen_at: number;
  created_at: number;
  updated_at: number;
}

class HttpError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const MAX_BODY_BYTES = 256_000;
const MAX_RESULT_BYTES = 256_000;
const DEFAULT_LEASE_SECONDS = 120;
const MAX_LEASE_SECONDS = 900;
const DEFAULT_RETENTION_DAYS = 14;
const MAX_ERROR_LENGTH = 4_000;

function nowSeconds(): number {
  return Math.floor(Date.now() / 1000);
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function parseBoundedInteger(
  value: unknown,
  field: string,
  fallback: number,
  minimum: number,
  maximum: number,
): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isInteger(value)) {
    throw new HttpError(400, `${field} must be an integer`);
  }
  if (value < minimum || value > maximum) {
    throw new HttpError(400, `${field} must be between ${minimum} and ${maximum}`);
  }
  return value;
}

function requiredString(
  body: JsonObject,
  field: string,
  maximumLength: number,
): string {
  const value = body[field];
  if (typeof value !== "string" || value.length === 0 || value.length > maximumLength) {
    throw new HttpError(400, `${field} must be a non-empty string of at most ${maximumLength} characters`);
  }
  return value;
}

function optionalString(
  body: JsonObject,
  field: string,
  maximumLength: number,
): string | null {
  const value = body[field];
  if (value === undefined || value === null) return null;
  if (typeof value !== "string" || value.length > maximumLength) {
    throw new HttpError(400, `${field} must be a string of at most ${maximumLength} characters`);
  }
  return value;
}

function asObject(value: unknown, field = "body"): JsonObject {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new HttpError(400, `${field} must be a JSON object`);
  }
  return value as JsonObject;
}

function jsonText(value: unknown, field: string, maximumBytes: number): string {
  let encoded: string | undefined;
  try {
    encoded = JSON.stringify(value);
  } catch {
    throw new HttpError(400, `${field} must be JSON serializable`);
  }
  if (encoded === undefined) {
    throw new HttpError(400, `${field} must be JSON serializable`);
  }
  if (new TextEncoder().encode(encoded).byteLength > maximumBytes) {
    throw new HttpError(413, `${field} is too large`);
  }
  return encoded;
}

function parseStoredJson(value: string | null): unknown {
  if (value === null) return null;
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function publicJob(row: JobRow): Record<string, unknown> {
  return {
    id: row.id,
    kind: row.kind,
    priority: row.priority,
    payload: parseStoredJson(row.payload_json),
    status: row.status,
    idempotency_key: row.idempotency_key,
    worker_id: row.worker_id,
    attempts: row.attempts,
    max_attempts: row.max_attempts,
    available_at: row.available_at,
    leased_at: row.leased_at,
    lease_expires_at: row.lease_expires_at,
    lease_token: row.lease_token,
    result: parseStoredJson(row.result_json),
    error: row.error,
    created_at: row.created_at,
    updated_at: row.updated_at,
    completed_at: row.completed_at,
  };
}

function publicWorker(row: WorkerRow): Record<string, unknown> {
  return {
    id: row.id,
    status: row.status,
    capabilities: parseStoredJson(row.capabilities_json),
    last_seen_at: row.last_seen_at,
    created_at: row.created_at,
    updated_at: row.updated_at,
  };
}

async function readJson(request: Request): Promise<JsonObject> {
  const contentLength = request.headers.get("content-length");
  if (contentLength !== null && Number(contentLength) > MAX_BODY_BYTES) {
    throw new HttpError(413, "request body is too large");
  }
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_BODY_BYTES) {
    throw new HttpError(413, "request body is too large");
  }
  if (text.trim().length === 0) return {};
  try {
    return asObject(JSON.parse(text));
  } catch (error) {
    if (error instanceof HttpError) throw error;
    throw new HttpError(400, "request body must be valid JSON");
  }
}

function isAuthorized(request: Request, env: Env): boolean {
  const token = env.COORDINATOR_TOKEN;
  return typeof token === "string" && token.length > 0 && request.headers.get("authorization") === `Bearer ${token}`;
}

function configuredInteger(
  value: string | undefined,
  fallback: number,
  minimum: number,
  maximum: number,
): number {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < minimum || parsed > maximum) return fallback;
  return parsed;
}

async function requeueExpiredLeases(env: Env, now: number): Promise<void> {
  await env.DB.prepare(
    `UPDATE jobs
     SET status = CASE WHEN attempts < max_attempts THEN 'queued' ELSE 'failed' END,
         worker_id = NULL,
         lease_token = NULL,
         leased_at = NULL,
         lease_expires_at = NULL,
         error = CASE WHEN attempts < max_attempts THEN 'lease expired; requeued' ELSE 'lease expired after final attempt' END,
         completed_at = CASE WHEN attempts < max_attempts THEN NULL ELSE ? END,
         updated_at = ?
     WHERE status = 'leased' AND lease_expires_at IS NOT NULL AND lease_expires_at <= ?`,
  )
    .bind(now, now, now)
    .run();
}

async function registerWorker(request: Request, env: Env): Promise<Response> {
  const body = await readJson(request);
  const workerId = requiredString(body, "worker_id", 100);
  const capabilities = body.capabilities ?? {};
  const capabilitiesJson = jsonText(capabilities, "capabilities", 32_000);
  const now = nowSeconds();

  await env.DB.prepare(
    `INSERT INTO workers (id, status, capabilities_json, last_seen_at, created_at, updated_at)
     VALUES (?, 'online', ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       status = 'online',
       capabilities_json = excluded.capabilities_json,
       last_seen_at = excluded.last_seen_at,
       updated_at = excluded.updated_at`,
  )
    .bind(workerId, capabilitiesJson, now, now, now)
    .run();

  const row = await env.DB.prepare("SELECT * FROM workers WHERE id = ?")
    .bind(workerId)
    .first<WorkerRow>();
  if (!row) throw new HttpError(500, "worker registration was not persisted");
  return jsonResponse({ worker: publicWorker(row) }, 201);
}

async function heartbeatWorker(request: Request, env: Env): Promise<Response> {
  const body = await readJson(request);
  const workerId = requiredString(body, "worker_id", 100);
  const now = nowSeconds();
  const result = await env.DB.prepare(
    "UPDATE workers SET status = 'online', last_seen_at = ?, updated_at = ? WHERE id = ?",
  )
    .bind(now, now, workerId)
    .run();
  if (result.meta.changes !== 1) throw new HttpError(404, "worker is not registered");

  const row = await env.DB.prepare("SELECT * FROM workers WHERE id = ?")
    .bind(workerId)
    .first<WorkerRow>();
  if (!row) throw new HttpError(404, "worker is not registered");
  return jsonResponse({ worker: publicWorker(row) });
}

async function enqueueJob(request: Request, env: Env): Promise<Response> {
  const body = await readJson(request);
  const kind = requiredString(body, "kind", 100);
  const payload = body.payload;
  if (payload === undefined) throw new HttpError(400, "payload is required");
  const payloadJson = jsonText(payload, "payload", MAX_BODY_BYTES);
  const idempotencyKey = optionalString(body, "idempotency_key", 200);
  const priority = parseBoundedInteger(body.priority, "priority", 100, 0, 1_000_000);
  const maxAttempts = parseBoundedInteger(body.max_attempts, "max_attempts", 3, 1, 20);
  const availableAt = parseBoundedInteger(body.available_at, "available_at", nowSeconds(), 0, 4_102_444_800);

  if (idempotencyKey !== null) {
    const existing = await env.DB.prepare("SELECT * FROM jobs WHERE idempotency_key = ?")
      .bind(idempotencyKey)
      .first<JobRow>();
    if (existing) return jsonResponse({ job: publicJob(existing), duplicate: true });
  }

  const now = nowSeconds();
  const jobId = crypto.randomUUID();
  try {
    await env.DB.prepare(
      `INSERT INTO jobs (
         id, kind, priority, payload_json, status, idempotency_key,
         attempts, max_attempts, available_at, created_at, updated_at
       ) VALUES (?, ?, ?, ?, 'queued', ?, 0, ?, ?, ?, ?)`,
    )
      .bind(jobId, kind, priority, payloadJson, idempotencyKey, maxAttempts, availableAt, now, now)
      .run();
  } catch (error) {
    if (idempotencyKey !== null) {
      const existing = await env.DB.prepare("SELECT * FROM jobs WHERE idempotency_key = ?")
        .bind(idempotencyKey)
        .first<JobRow>();
      if (existing) return jsonResponse({ job: publicJob(existing), duplicate: true });
    }
    throw error;
  }

  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?")
    .bind(jobId)
    .first<JobRow>();
  if (!row) throw new HttpError(500, "job was not persisted");
  return jsonResponse({ job: publicJob(row), duplicate: false }, 201);
}

async function leaseJob(request: Request, env: Env): Promise<Response> {
  const body = await readJson(request);
  const workerId = requiredString(body, "worker_id", 100);
  const leaseSeconds = parseBoundedInteger(
    body.lease_seconds,
    "lease_seconds",
    configuredInteger(env.LEASE_SECONDS, DEFAULT_LEASE_SECONDS, 15, MAX_LEASE_SECONDS),
    15,
    MAX_LEASE_SECONDS,
  );
  const now = nowSeconds();
  await requeueExpiredLeases(env, now);

  const worker = await env.DB.prepare("SELECT id FROM workers WHERE id = ?")
    .bind(workerId)
    .first<{ id: string }>();
  if (!worker) throw new HttpError(404, "worker is not registered");

  const leaseToken = crypto.randomUUID();
  const claim = await env.DB.prepare(
    `UPDATE jobs
     SET status = 'leased', worker_id = ?, lease_token = ?, leased_at = ?,
         lease_expires_at = ?, attempts = attempts + 1, updated_at = ?
     WHERE id = (
       SELECT id FROM jobs
       WHERE status = 'queued'
         AND available_at <= ?
         AND attempts < max_attempts
         AND NOT EXISTS (
           SELECT 1 FROM jobs AS active
           WHERE active.worker_id = ? AND active.status = 'leased'
         )
       ORDER BY priority ASC, available_at ASC, created_at ASC
       LIMIT 1
     )`,
  )
    .bind(workerId, leaseToken, now, now + leaseSeconds, now, now, workerId)
    .run();

  if (claim.meta.changes !== 1) return jsonResponse({ job: null });
  const row = await env.DB.prepare("SELECT * FROM jobs WHERE lease_token = ?")
    .bind(leaseToken)
    .first<JobRow>();
  if (!row) throw new HttpError(500, "job lease was not persisted");
  return jsonResponse({ job: publicJob(row) });
}

async function heartbeatJob(request: Request, env: Env, pathJobId?: string): Promise<Response> {
  const body = await readJson(request);
  const jobId = pathJobId ?? requiredString(body, "job_id", 100);
  const workerId = requiredString(body, "worker_id", 100);
  const leaseToken = requiredString(body, "lease_token", 100);
  const leaseSeconds = parseBoundedInteger(
    body.lease_seconds,
    "lease_seconds",
    configuredInteger(env.LEASE_SECONDS, DEFAULT_LEASE_SECONDS, 15, MAX_LEASE_SECONDS),
    15,
    MAX_LEASE_SECONDS,
  );
  const now = nowSeconds();
  const result = await env.DB.prepare(
    `UPDATE jobs
     SET lease_expires_at = ?, updated_at = ?
     WHERE id = ? AND status = 'leased' AND worker_id = ? AND lease_token = ?`,
  )
    .bind(now + leaseSeconds, now, jobId, workerId, leaseToken)
    .run();
  if (result.meta.changes !== 1) throw new HttpError(409, "job lease is no longer valid");

  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?")
    .bind(jobId)
    .first<JobRow>();
  if (!row) throw new HttpError(404, "job not found");
  return jsonResponse({ job: publicJob(row) });
}

async function completeJob(request: Request, env: Env, pathJobId?: string): Promise<Response> {
  const body = await readJson(request);
  const jobId = pathJobId ?? requiredString(body, "job_id", 100);
  const workerId = requiredString(body, "worker_id", 100);
  const leaseToken = requiredString(body, "lease_token", 100);
  const resultJson = jsonText(body.result ?? null, "result", MAX_RESULT_BYTES);
  const now = nowSeconds();
  const result = await env.DB.prepare(
    `UPDATE jobs
     SET status = 'completed', worker_id = NULL, lease_token = NULL,
         leased_at = NULL, lease_expires_at = NULL, result_json = ?,
         error = NULL, completed_at = ?, updated_at = ?
     WHERE id = ? AND status = 'leased' AND worker_id = ? AND lease_token = ?`,
  )
    .bind(resultJson, now, now, jobId, workerId, leaseToken)
    .run();
  if (result.meta.changes !== 1) throw new HttpError(409, "job lease is no longer valid");

  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?")
    .bind(jobId)
    .first<JobRow>();
  if (!row) throw new HttpError(404, "job not found");
  return jsonResponse({ job: publicJob(row) });
}

async function failJob(request: Request, env: Env, pathJobId?: string): Promise<Response> {
  const body = await readJson(request);
  const jobId = pathJobId ?? requiredString(body, "job_id", 100);
  const workerId = requiredString(body, "worker_id", 100);
  const leaseToken = requiredString(body, "lease_token", 100);
  const suppliedError = optionalString(body, "error", MAX_ERROR_LENGTH) ?? "worker reported failure";
  const retry = body.retry !== false;
  const now = nowSeconds();
  const result = await env.DB.prepare(
    `UPDATE jobs
     SET status = CASE WHEN ? = 1 AND attempts < max_attempts THEN 'queued' ELSE 'failed' END,
         worker_id = NULL, lease_token = NULL, leased_at = NULL, lease_expires_at = NULL,
         available_at = CASE
           WHEN ? = 1 AND attempts < max_attempts
           THEN ? + MIN(300, 5 * (1 << MIN(attempts, 6)))
           ELSE available_at
         END,
         error = ?, completed_at = CASE WHEN ? = 1 AND attempts < max_attempts THEN NULL ELSE ? END,
         updated_at = ?
     WHERE id = ? AND status = 'leased' AND worker_id = ? AND lease_token = ?`,
  )
    .bind(retry ? 1 : 0, retry ? 1 : 0, now, suppliedError, retry ? 1 : 0, now, now, jobId, workerId, leaseToken)
    .run();
  if (result.meta.changes !== 1) throw new HttpError(409, "job lease is no longer valid");

  const row = await env.DB.prepare("SELECT * FROM jobs WHERE id = ?")
    .bind(jobId)
    .first<JobRow>();
  if (!row) throw new HttpError(404, "job not found");
  return jsonResponse({ job: publicJob(row) });
}

async function stats(env: Env): Promise<Response> {
  const rows = await env.DB.prepare("SELECT status, COUNT(*) AS count FROM jobs GROUP BY status")
    .all<{ status: JobStatus; count: number }>();
  const counts: Record<string, number> = {};
  for (const row of rows.results) counts[row.status] = row.count;
  return jsonResponse({ jobs: counts });
}

async function maintenance(env: Env): Promise<void> {
  const now = nowSeconds();
  await requeueExpiredLeases(env, now);
  const retentionDays = configuredInteger(
    env.RETENTION_DAYS,
    DEFAULT_RETENTION_DAYS,
    1,
    3650,
  );
  await env.DB.prepare(
    "DELETE FROM jobs WHERE status IN ('completed', 'failed') AND updated_at < ?",
  )
    .bind(now - retentionDays * 86_400)
    .run();
  await env.DB.prepare(
    "UPDATE workers SET status = 'offline', updated_at = ? WHERE status = 'online' AND last_seen_at < ?",
  )
    .bind(now, now - 300)
    .run();
}

async function handleRequest(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (request.method === "GET" && url.pathname === "/health") {
    return jsonResponse({ ok: true, service: "jarvis-coordinator" });
  }
  if (!url.pathname.startsWith("/v1/")) throw new HttpError(404, "not found");
  if (!isAuthorized(request, env)) throw new HttpError(401, "unauthorized");

  if (request.method === "POST" && url.pathname === "/v1/workers/register") {
    return registerWorker(request, env);
  }
  if (request.method === "POST" && url.pathname === "/v1/workers/heartbeat") {
    return heartbeatWorker(request, env);
  }
  if (request.method === "POST" && url.pathname === "/v1/jobs") {
    return enqueueJob(request, env);
  }
  if (request.method === "POST" && url.pathname === "/v1/jobs/lease") {
    return leaseJob(request, env);
  }
  const heartbeatMatch = url.pathname.match(/^\/v1\/jobs\/([^/]+)\/heartbeat$/);
  if (request.method === "POST" && url.pathname === "/v1/jobs/heartbeat") {
    return heartbeatJob(request, env);
  }
  if (request.method === "POST" && heartbeatMatch) {
    return heartbeatJob(request, env, heartbeatMatch[1]);
  }
  const completeMatch = url.pathname.match(/^\/v1\/jobs\/([^/]+)\/complete$/);
  if (request.method === "POST" && url.pathname === "/v1/jobs/complete") {
    return completeJob(request, env);
  }
  if (request.method === "POST" && completeMatch) {
    return completeJob(request, env, completeMatch[1]);
  }
  const failMatch = url.pathname.match(/^\/v1\/jobs\/([^/]+)\/fail$/);
  if (request.method === "POST" && url.pathname === "/v1/jobs/fail") {
    return failJob(request, env);
  }
  if (request.method === "POST" && failMatch) {
    return failJob(request, env, failMatch[1]);
  }
  if (request.method === "GET" && url.pathname === "/v1/jobs/stats") {
    return stats(env);
  }
  throw new HttpError(404, "not found");
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      if (error instanceof HttpError) return jsonResponse({ error: error.message }, error.status);
      console.error("coordinator request failed", error);
      return jsonResponse({ error: "internal server error" }, 500);
    }
  },

  async scheduled(_controller: ScheduledController, env: Env, context: ExecutionContext): Promise<void> {
    context.waitUntil(maintenance(env));
  },
} satisfies ExportedHandler<Env>;

