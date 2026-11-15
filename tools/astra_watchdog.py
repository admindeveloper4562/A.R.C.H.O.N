#!/usr/bin/env python3
"""Minimal out-of-process Astra upgrade watchdog.

This file intentionally has no import path into the Supervisor or worker
runtime. It is a separate, fail-closed control plane: it verifies the
canonical checkpoint and, for a pre-commit upgrade, records a rollback only
after independently checking the rollback commit and taking the Master lock.
It never starts workers, approves code, changes Git refs, switches a service
pointer, clears STOP/PAUSE/quota markers, or writes model output.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

SHA = re.compile(r"[0-9a-f]{40}")
UPGRADE_TABLE = "upgrade_batches"
ROLLBACK_ELIGIBLE = {
    "PROPOSED", "PATCH_IN_ISOLATION", "TESTED", "DRAIN_NEW_CLAIMS",
    "STAGED_CANARY", "HEALTH_SOAK",
}


def _regular(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink() or not raw.is_file():
        raise ValueError(f"{label} is not a regular file")
    return raw.resolve(strict=True)


def _read_settings(db: sqlite3.Connection) -> dict[str, str]:
    return {row[0]: row[1] for row in db.execute("SELECT key,value FROM settings")}


def _git_commit_exists(repository: Path, sha: str) -> None:
    if not SHA.fullmatch(sha):
        raise ValueError("rollback checkpoint is not a full commit SHA")
    subprocess.run(
        ["git", "-C", str(repository), "cat-file", "-e", f"{sha}^{{commit}}"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _open_readonly(db_path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True, timeout=2)
    db.execute("PRAGMA query_only=ON")
    db.execute("PRAGMA busy_timeout=2000")
    return db


def _verified_backup(state_dir: Path, db_path: Path, batch_id: str) -> tuple[Path, str]:
    backup_dir = state_dir / "backups" / "watchdog"
    backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    suffix = hashlib.sha256(datetime.now(timezone.utc).isoformat().encode()).hexdigest()[:12]
    backup_path = backup_dir / f"{batch_id}-{suffix}.sqlite3"
    with sqlite3.connect(db_path) as source, sqlite3.connect(backup_path) as target:
        source.backup(target)
        if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("watchdog database backup integrity check failed")
    return backup_path, hashlib.sha256(backup_path.read_bytes()).hexdigest()


def check(state_dir: Path) -> dict:
    raw_state = state_dir.expanduser()
    if raw_state.is_symlink() or not raw_state.is_dir():
        raise ValueError("canonical Astra state directory is unavailable")
    state_dir = raw_state.resolve(strict=True)
    db_path = _regular(state_dir / "sda.sqlite3", "canonical SDA database")
    with _open_readonly(db_path) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError("canonical SDA integrity check failed")
        settings = _read_settings(db)
        has_upgrade_table = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (UPGRADE_TABLE,)
        ).fetchone()
        upgrade = None
        if has_upgrade_table:
            row = db.execute(
                "SELECT batch_id,state,candidate_sha,rollback_sha FROM upgrade_batches "
                "ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
            if row:
                upgrade = dict(zip(("batch_id", "state", "candidate_sha", "rollback_sha"), row))
    integration_raw = Path(settings.get("integration_path", "")).expanduser()
    if integration_raw.is_symlink() or not integration_raw.is_dir():
        raise ValueError("integration checkpoint path is unavailable")
    integration = integration_raw.resolve(strict=True)
    head = subprocess.check_output(
        ["git", "-C", str(integration), "rev-parse", "HEAD"], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    if head != settings.get("integration_sha"):
        raise ValueError("integration checkpoint SHA does not match Git HEAD")
    return {
        "integrity": integrity,
        "schema_version": int(settings.get("schema_version", "0")),
        "integration_sha": head,
        "upgrade": upgrade,
        "controls": {name: (state_dir / name).exists() for name in ("STOP", "PAUSE", "PAUSED_QUOTA")},
        "pointer_switch": "not_configured",
    }


def rollback(state_dir: Path, batch_id: str) -> dict:
    """Record a verified rollback-pending checkpoint under the independent lock.

    Astra currently has no service-version pointer to switch. Therefore this
    operation deliberately refuses to claim that code was restored: it
    validates the last-known-good Git commit and current HEAD, atomically
    records ``ROLLBACK_PENDING``, and returns ``pointer_switch=not_configured``
    for the operator. A separate version-pointer implementation must complete
    the restore before any caller may mark the upgrade committed.
    """
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,80}", batch_id):
        raise ValueError("invalid upgrade batch id")
    raw_state = state_dir.expanduser()
    if raw_state.is_symlink() or not raw_state.is_dir():
        raise ValueError("canonical Astra state directory is unavailable")
    state_dir = raw_state.resolve(strict=True)
    db_path = _regular(state_dir / "sda.sqlite3", "canonical SDA database")
    lock_path = state_dir / "master.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another Astra Linux master is running") from exc
        with sqlite3.connect(db_path, timeout=2, isolation_level=None) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA busy_timeout=2000")
            db.execute("PRAGMA foreign_keys=ON")
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("canonical SDA integrity check failed")
            if not db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (UPGRADE_TABLE,)
            ).fetchone():
                raise ValueError("upgrade checkpoint table is unavailable")
            if not db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='upgrade_rollbacks'"
            ).fetchone():
                raise ValueError("rollback receipt table is unavailable")
            row = db.execute(
                "SELECT state,candidate_sha,rollback_sha FROM upgrade_batches WHERE batch_id=?",
                (batch_id,),
            ).fetchone()
            if not row:
                raise ValueError("unknown upgrade batch")
            if row["state"] not in ROLLBACK_ELIGIBLE:
                raise ValueError("upgrade is not rollback eligible")
            settings = _read_settings(db)
            if row["rollback_sha"] != settings.get("integration_sha"):
                raise ValueError("rollback checkpoint is no longer the canonical integration SHA")
            integration_raw = Path(settings.get("integration_path", "")).expanduser()
            if integration_raw.is_symlink() or not integration_raw.is_dir():
                raise ValueError("integration checkpoint path is unavailable")
            integration = integration_raw.resolve(strict=True)
            head = subprocess.check_output(
                ["git", "-C", str(integration), "rev-parse", "HEAD"], text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if head != settings.get("integration_sha"):
                raise ValueError("integration HEAD does not match canonical checkpoint")
            _git_commit_exists(integration, row["rollback_sha"])
            if row["rollback_sha"] != settings.get("integration_sha"):
                raise ValueError("rollback checkpoint is no longer the canonical integration SHA")
            backup_path, backup_sha = _verified_backup(state_dir, db_path, batch_id)
            db.execute("BEGIN IMMEDIATE")
            timestamp = datetime.now(timezone.utc).isoformat()
            rollback_id = f"{batch_id}-{backup_sha[:12]}"
            db.execute(
                "INSERT INTO upgrade_rollbacks(rollback_id,batch_id,state,rollback_sha,current_head,backup_path,backup_sha,created_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (rollback_id, batch_id, "ROLLBACK_PENDING", row["rollback_sha"], head,
                 str(backup_path), backup_sha, timestamp),
            )
            db.execute(
                "UPDATE upgrade_batches SET state='ROLLBACK_PENDING',updated_at=? WHERE batch_id=?",
                (timestamp, batch_id),
            )
            db.execute("COMMIT")
            return {
                "batch_id": batch_id,
                "state": "ROLLBACK_PENDING",
                "rollback_sha": row["rollback_sha"],
                "rollback_commit_verified": True,
                "integration_head_verified": True,
                "backup_path": str(backup_path),
                "backup_sha": backup_sha,
                "pointer_switch": "not_configured",
            }
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=Path.home() / ".local/state/archon-astra")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rollback")
    args = parser.parse_args()
    try:
        if args.check or not args.rollback:
            print(json.dumps(check(args.state), sort_keys=True))
        if args.rollback:
            print(json.dumps(rollback(args.state, args.rollback), sort_keys=True))
        return 0
    except (OSError, ValueError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"watchdog refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
