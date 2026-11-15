-- Astra One metadata-only progress. No prompts, code, credentials or terminal logs.
CREATE TABLE IF NOT EXISTS astra_runs (
 run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, stage TEXT NOT NULL,
 step TEXT NOT NULL, branch TEXT NOT NULL, base_sha TEXT NOT NULL,
 seq INTEGER NOT NULL, tool_count INTEGER NOT NULL DEFAULT 0,
 result TEXT NOT NULL DEFAULT '', elapsed_s INTEGER NOT NULL DEFAULT 0,
 attempt INTEGER NOT NULL DEFAULT 1,
 first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS astra_runs_updated ON astra_runs(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS astra_runs_tasks ON astra_runs(task_id,last_seen_at);
CREATE TABLE IF NOT EXISTS astra_events (
 event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, task_id TEXT NOT NULL,
 seq INTEGER NOT NULL, time TEXT NOT NULL, stage TEXT NOT NULL,
 step TEXT NOT NULL, tool_count INTEGER NOT NULL, result TEXT NOT NULL DEFAULT '',
 elapsed_s INTEGER NOT NULL DEFAULT 0, attempt INTEGER NOT NULL DEFAULT 1,
 UNIQUE(run_id,seq)
);
CREATE INDEX IF NOT EXISTS astra_events_run ON astra_events(run_id,seq DESC);
