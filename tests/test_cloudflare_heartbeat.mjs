import { test } from "node:test";
import assert from "node:assert/strict";
import worker from "../infra/cloudflare/heartbeat_worker.js";

class MockStatement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.params = []; }
  bind(...params) { this.params = params; return this; }
  async run() {
    if (this.sql.includes("INSERT INTO device_heartbeats")) {
      const [deviceId, observedAt, receivedAt] = this.params;
      this.db.rows.set(deviceId, { device_id: deviceId, status: "online", observed_at: observedAt, received_at: receivedAt });
      return {};
    }
    if (this.sql.includes("UPDATE device_heartbeats")) {
      const [deviceId, staleBefore] = this.params;
      const row = this.db.rows.get(deviceId);
      if (row && row.status === "online" && row.received_at <= staleBefore) row.status = "offline";
      return {};
    }
    throw new Error(`unexpected SQL: ${this.sql}`);
  }
  async first() {
    if (!this.sql.includes("SELECT device_id")) throw new Error(`unexpected SQL: ${this.sql}`);
    return this.db.rows.get(this.params[0]) || null;
  }
}

class MockDB {
  constructor() { this.rows = new Map(); }
  prepare(sql) { return new MockStatement(this, sql); }
}

const env = { DB: new MockDB(), HEARTBEAT_INGEST_TOKEN: "ingest", HEARTBEAT_VIEW_TOKEN: "view",
  HEARTBEAT_TIMEOUT_SECONDS: "30", __now: () => 100, __rateLimit: async () => true };

async function call(path, method = "GET", body, token = "") {
  const headers = token ? { authorization: `Bearer ${token}` } : {};
  if (body !== undefined) headers["content-type"] = "application/json";
  const request = new Request(`https://worker.test${path}`, { method, headers,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
  const response = await worker.fetch(request, env);
  return { status: response.status, body: await response.json() };
}

test("heartbeat is authenticated and reports metadata without execution", async () => {
  assert.equal((await call("/v1/devices/windows-1/heartbeat", "POST", {}, "view")).status, 401);
  const result = await call("/v1/devices/windows-1/heartbeat", "POST", { observed_at: 99 }, "ingest");
  assert.equal(result.status, 201);
  assert.deepEqual(result.body, { device_id: "windows-1", status: "online", last_heartbeat_at: 100,
    observed_at: 99, execution_status: "not_executed" });
});

test("missing heartbeat marks a known device offline", async () => {
  const result = await call("/v1/devices/windows-2/status", "GET", undefined, "view");
  assert.equal(result.status, 200);
  assert.equal(result.body.status, "offline");
  assert.equal(result.body.stale, true);
  assert.equal(result.body.execution_status, "not_executed");
});

test("stale heartbeat is persisted offline and cannot be presented as execution", async () => {
  env.__now = () => 200;
  const result = await call("/v1/devices/windows-1/status", "GET", undefined, "view");
  assert.equal(result.body.status, "offline");
  assert.equal(env.DB.rows.get("windows-1").status, "offline");
  assert.equal(result.body.execution_status, "not_executed");
});

test("invalid heartbeat and unauthenticated status fail closed", async () => {
  env.__now = () => 100;
  assert.equal((await call("/v1/devices/windows-1/heartbeat", "POST", { status: "online" }, "ingest")).status, 400);
  assert.equal((await call("/v1/devices/windows-1/status")).status, 401);
  assert.equal((await call("/v1/devices/windows-1/execute", "POST", {}, "ingest")).status, 405);
});
