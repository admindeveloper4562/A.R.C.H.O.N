from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_VERSION = 8


def prepare_path(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not path.is_file():
        raise sqlite3.OperationalError("JARVIS database path is not a regular file")
    if path.exists():
        path.chmod(0o600)


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    prepare_path(path)
    db = sqlite3.connect(path, timeout=5.0)
    # SQLite creates a new file after prepare_path; enforce the private mode
    # again so the first connection cannot leave the database world-readable.
    path.chmod(0o600)
    try:
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        yield db
        db.commit()
    except sqlite3.Error:
        db.rollback()
        raise
    finally:
        db.close()


def ensure_schema(path: Path) -> None:
    with connect(path) as db:
        current = int(db.execute("PRAGMA user_version").fetchone()[0])
        if current > SCHEMA_VERSION:
            raise sqlite3.DatabaseError(
                f"database schema {current} is newer than supported {SCHEMA_VERSION}"
            )
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY, event TEXT NOT NULL,
                detail TEXT NOT NULL, created REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS owner_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                bootstrapped INTEGER NOT NULL DEFAULT 0
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS file_index USING fts5(
                path, kind, size UNINDEXED, mtime UNINDEXED, mount UNINDEXED
            );
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
                kind TEXT NOT NULL, payload TEXT NOT NULL,
                state TEXT NOT NULL CHECK (state IN ('queued','running','waiting','blocked','done','failed','cancelled')),
                result TEXT, error TEXT, created REAL NOT NULL, updated REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS tasks_state_updated ON tasks(state, updated);
            CREATE TABLE IF NOT EXISTS task_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                state TEXT NOT NULL,
                detail TEXT NOT NULL,
                created REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS task_events_created ON task_events(event_id);
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                model TEXT,
                created REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS chat_messages_created ON chat_messages(created, id);
            CREATE TABLE IF NOT EXISTS scan_roots (
                path TEXT PRIMARY KEY,
                created REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS inventory_scans (
                path TEXT PRIMARY KEY,
                last_seen REAL NOT NULL,
                record_count INTEGER NOT NULL,
                complete INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS calendar_proposals (
                proposal_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                operation TEXT NOT NULL CHECK (operation IN ('create','update','cancel')),
                payload TEXT NOT NULL,
                state TEXT NOT NULL CHECK (state IN ('pending','approved','denied')),
                created REAL NOT NULL,
                decided REAL
            );
            CREATE TABLE IF NOT EXISTS email_drafts (
                draft_id TEXT PRIMARY KEY,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                created REAL NOT NULL
            );
            PRAGMA user_version=8;
            """
        )
        db.execute(
            """CREATE TABLE IF NOT EXISTS trash_manifests (
                request_id TEXT PRIMARY KEY, trash_path TEXT NOT NULL,
                original_path TEXT NOT NULL, checksum TEXT NOT NULL,
                device INTEGER NOT NULL, inode INTEGER NOT NULL, size INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL, created REAL NOT NULL, restored REAL,
                FOREIGN KEY(request_id) REFERENCES approval_requests(request_id)
            )"""
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS permission_audit "
            "(id INTEGER PRIMARY KEY, request_id TEXT NOT NULL, actor TEXT NOT NULL, "
            "capability TEXT NOT NULL, target_digest TEXT NOT NULL, decision TEXT NOT NULL, "
            "result TEXT NOT NULL, created REAL NOT NULL)"
        )
        db.execute("CREATE INDEX IF NOT EXISTS permission_audit_created ON permission_audit(created)")
        db.execute(
            """CREATE TABLE IF NOT EXISTS approval_requests (
                request_id TEXT PRIMARY KEY, action TEXT NOT NULL, reason TEXT NOT NULL,
                path TEXT NOT NULL, device INTEGER NOT NULL, inode INTEGER NOT NULL,
                size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL, expires_at REAL NOT NULL,
                state TEXT NOT NULL CHECK (state IN ('pending', 'approved', 'denied', 'consumed'))
            )"""
        )
        columns = {row[1] for row in db.execute("PRAGMA table_info(approval_requests)")}
        if "restore_target" not in columns:
            db.execute("ALTER TABLE approval_requests ADD COLUMN restore_target TEXT")
