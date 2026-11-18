PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workers (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'offline'
    CHECK (status IN ('online', 'offline')),
  capabilities_json TEXT NOT NULL DEFAULT '{}',
  last_seen_at INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (length(kind) BETWEEN 1 AND 100),
  priority INTEGER NOT NULL DEFAULT 100 CHECK (priority BETWEEN 0 AND 1000000),
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued'
    CHECK (status IN ('queued', 'leased', 'completed', 'failed')),
  idempotency_key TEXT UNIQUE,
  worker_id TEXT REFERENCES workers(id) ON DELETE SET NULL,
  lease_token TEXT,
  leased_at INTEGER,
  lease_expires_at INTEGER,
  attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 20),
  available_at INTEGER NOT NULL,
  result_json TEXT,
  error TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  completed_at INTEGER
);

CREATE INDEX IF NOT EXISTS jobs_claim_idx
  ON jobs (status, available_at, priority, created_at);

CREATE INDEX IF NOT EXISTS jobs_lease_expiry_idx
  ON jobs (status, lease_expires_at);

CREATE INDEX IF NOT EXISTS jobs_worker_idx
  ON jobs (worker_id, status);

CREATE INDEX IF NOT EXISTS jobs_retention_idx
  ON jobs (status, updated_at);

CREATE INDEX IF NOT EXISTS workers_heartbeat_idx
  ON workers (last_seen_at);

