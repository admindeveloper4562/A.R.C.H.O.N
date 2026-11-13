"""Deterministic durable Core task queue: no AI model and no external effects."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

PRIORITIES = ("P0", "P1", "P2", "P3", "P4", "P5")
STATES = ("pending", "leased", "completed", "failed", "cancelled")

class TaskQueue:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, priority INTEGER NOT NULL, module TEXT NOT NULL,
                payload TEXT NOT NULL, state TEXT NOT NULL,
                created_id INTEGER NOT NULL UNIQUE,
                lease TEXT, receipt TEXT, title TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                kind TEXT NOT NULL, detail TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id));
        """)
        # The task ledger owns schema migrations; the separate monitor never writes.
        # A non-secret title lets the monitor describe work without reading payload.
        if 'title' not in {r['name'] for r in self.db.execute('PRAGMA table_info(tasks)')}:
            self.db.execute("ALTER TABLE tasks ADD COLUMN title TEXT NOT NULL DEFAULT ''")
        self.db.commit()

    def add(self, *, task_id: str, priority: str, module: str, payload: dict, title: str = '') -> None:
        if (priority not in PRIORITIES or not task_id or not module or not isinstance(payload, dict)
                or not isinstance(title, str) or len(title) > 180 or any(ord(c) < 32 for c in title)):
            raise ValueError("invalid task input")
        with self.db:
            seq = self.db.execute("SELECT COALESCE(MAX(created_id),0)+1 FROM tasks").fetchone()[0]
            self.db.execute("INSERT INTO tasks (id,priority,module,payload,state,created_id,lease,receipt,title) VALUES (?,?,?,?,?,?,?,?,?)", (task_id, PRIORITIES.index(priority), module, json.dumps(payload,sort_keys=True), "pending", seq, None, None, title))
            self.db.execute("INSERT INTO events(task_id,kind,detail) VALUES (?,?,?)", (task_id,"pending", "queued"))

    def lease_next(self, *, guardian_waiting: bool = False, allowed_modules: set[str] | None = None) -> dict | None:
        """Dispatch next eligible task. This seed has no multi-host lease-expiry/recovery yet."""
        where = "state='pending'"
        args: list[str] = []
        if guardian_waiting:
            where += " AND priority <= 1"
        if allowed_modules is not None:
            if not allowed_modules: return None
            where += " AND module IN (" + ",".join("?" for _ in allowed_modules) + ")"
            args.extend(sorted(allowed_modules))
        with self.db:
            row = self.db.execute(f"SELECT * FROM tasks WHERE {where} ORDER BY priority,created_id LIMIT 1", args).fetchone()
            if row is None:return None
            lease = uuid4().hex
            self.db.execute("UPDATE tasks SET state='leased',lease=? WHERE id=? AND state='pending'", (lease,row["id"]))
            self.db.execute("INSERT INTO events(task_id,kind,detail) VALUES (?,?,?)", (row["id"],"leased",lease))
            return {"id":row["id"],"priority":PRIORITIES[row["priority"]],"module":row["module"],"payload":json.loads(row["payload"]),"lease":lease}

    def finish(self, task_id: str, lease: str, *, ok: bool, receipt: str) -> None:
        if not isinstance(receipt,str) or not receipt or not isinstance(lease,str): raise ValueError("receipt and lease required")
        with self.db:
            res=self.db.execute("UPDATE tasks SET state=?,receipt=?,lease=NULL WHERE id=? AND state='leased' AND lease=?", ("completed" if ok else "failed", receipt, task_id,lease))
            if res.rowcount!=1: raise ValueError("unknown or stale lease")
            self.db.execute("INSERT INTO events(task_id,kind,detail) VALUES (?,?,?)", (task_id,"completed" if ok else "failed",receipt))

    def status(self) -> list[dict]:
        return [dict(row) for row in self.db.execute("SELECT id,priority,module,state,receipt FROM tasks ORDER BY created_id")]

    def close(self): self.db.close()
