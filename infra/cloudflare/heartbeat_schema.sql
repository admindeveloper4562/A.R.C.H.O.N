-- Device liveness metadata only. Jobs remain queued elsewhere while a device is offline.
CREATE TABLE IF NOT EXISTS device_heartbeats (
  device_id TEXT PRIMARY KEY,
  status TEXT NOT NULL CHECK (status IN ('online', 'offline')),
  observed_at INTEGER NOT NULL,
  received_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS device_heartbeats_status
  ON device_heartbeats(status, received_at);
