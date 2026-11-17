-- Hashed request buckets only; raw client identifiers are never persisted.
CREATE TABLE IF NOT EXISTS rate_limit_buckets (
  key_hash TEXT PRIMARY KEY,
  window_start INTEGER NOT NULL,
  count INTEGER NOT NULL CHECK (count >= 0)
);
