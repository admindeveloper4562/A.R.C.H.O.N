import { test } from "node:test";
import assert from "node:assert/strict";
import { allowRequest } from "../infra/cloudflare/rate_limit.js";

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.params = []; }
  bind(...params) { this.params = params; return this; }
  async run() {
    const [keyHash, windowStart, windowSeconds, now, nextWindow, resetWindow, resetNow, cap] = this.params;
    const row = this.db.rows.get(keyHash);
    if (!row) this.db.rows.set(keyHash, { window_start: windowStart, count: 1 });
    else if (row.window_start + windowSeconds <= now) Object.assign(row, { window_start: nextWindow, count: 1 });
    else row.count = Math.min(row.count + 1, cap);
    return {};
  }
  async first() { return this.db.rows.get(this.params[0]) || null; }
}
class MockDB {
  constructor() { this.rows = new Map(); }
  prepare(sql) { return new Statement(this, sql); }
}

const db = new MockDB();
const clock = [100];
const env = { DB: db, RATE_LIMIT_MAX_REQUESTS: "2", RATE_LIMIT_WINDOW_SECONDS: "10", __now: () => clock[0] };
const request = (ip) => new Request("https://worker.test/api", { headers: { "CF-Connecting-IP": ip } });

test("rate limit denies the third request in a bounded window", async () => {
  assert.equal(await allowRequest(request("192.0.2.1"), env, "api"), true);
  assert.equal(await allowRequest(request("192.0.2.1"), env, "api"), true);
  assert.equal(await allowRequest(request("192.0.2.1"), env, "api"), false);
});

test("new window resets and a separate client has independent capacity", async () => {
  clock[0] = 111;
  assert.equal(await allowRequest(request("192.0.2.1"), env, "api"), true);
  assert.equal(await allowRequest(request("192.0.2.2"), env, "api"), true);
  assert.equal(db.rows.size, 2);
});

test("stored bucket keys do not contain the raw client identifier", () => {
  for (const key of db.rows.keys()) assert.equal(key.includes("192.0.2."), false);
});
