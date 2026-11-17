import { test } from "node:test";
import assert from "node:assert/strict";
import worker from "../infra/cloudflare/dashboard_worker.js";

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.params = []; }
  bind(...params) { this.params = params; return this; }
  async all() {
    if (this.sql.includes("GROUP BY r.stage")) return { results: this.db.summary };
    if (this.sql.includes("FROM astra_runs") && this.sql.includes("LIMIT 100")) return { results: this.db.runs };
    if (this.sql.includes("FROM astra_events")) return { results: this.db.events.filter((row) => row.task_id === this.params[0]) };
    throw new Error(`unexpected SQL: ${this.sql}`);
  }
  async first() {
    if (this.sql.includes("FROM astra_runs") && this.sql.includes("WHERE task_id=?")) return this.db.runs.find((row) => row.task_id === this.params[0]) || null;
    throw new Error(`unexpected SQL: ${this.sql}`);
  }
}
class MockDB {
  constructor() {
    this.summary = [{ stage: "completed", count: 1 }, { stage: "failed", count: 1 }];
    this.runs = [{ run_id: "run-1", task_id: "AUTO-008", stage: "failed", step: "qc_rejected", branch: "feature/astra-auto-008", base_sha: "a".repeat(40), tool_count: 3, seq: 2, result: "test_failure", elapsed_s: 4, attempt: 2, last_seen_at: "2026-11-17T00:00:00Z" }];
    this.events = [
      { task_id: "AUTO-008", seq: 1, time: "2026-11-17T00:00:00Z", stage: "verifying", step: "deterministic_qc", tool_count: 2, result: "", elapsed_s: 2, attempt: 2 },
      { task_id: "AUTO-008", seq: 2, time: "2026-11-17T00:00:01Z", stage: "failed", step: "qc_rejected", tool_count: 3, result: "test_failure", elapsed_s: 4, attempt: 2 },
    ];
  }
  prepare(sql) { return new Statement(this, sql); }
}
const env = { DB: new MockDB(), DASHBOARD_VIEW_TOKEN: "view", __rateLimit: async () => true };

async function call(path, token = "") {
  const request = new Request(`https://dashboard.test${path}`, { headers: token ? { authorization: `Bearer ${token}` } : {} });
  const response = await worker.fetch(request, env);
  return { status: response.status, body: await response.json().catch(() => response.text()) };
}

test("public dashboard exposes only aggregate recorded counts", async () => {
  const page = await worker.fetch(new Request("https://dashboard.test/"), env);
  assert.equal(page.status, 200);
  assert.match(await page.text(), /ARCHON SDA dashboard/);
  const summary = await call("/api/public/summary");
  assert.deepEqual(summary.body.counts, { total: 2, completed: 1, failed: 1 });
});

test("private run and task APIs require the view token", async () => {
  assert.equal((await call("/api/private/runs")).status, 401);
  const runs = await call("/api/private/runs", "view");
  assert.equal(runs.body.runs[0].task_id, "AUTO-008");
  const detail = await call("/api/private/tasks/AUTO-008", "view");
  assert.equal(detail.body.phase, "failed");
  assert.equal(detail.body.worker.branch, "feature/astra-auto-008");
  assert.equal(detail.body.worker.identity, null);
  assert.equal(detail.body.qc[0].step, "deterministic_qc");
  assert.equal(detail.body.failures[0].result, "test_failure");
});

test("invalid task routes and unknown mutation routes fail closed", async () => {
  assert.equal((await call("/api/private/tasks/not-valid", "view")).status, 404);
  assert.equal((await call("/api/private/tasks/AUTO-008/execute", "view")).status, 404);
});
