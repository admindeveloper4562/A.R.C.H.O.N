#!/usr/bin/env python3
"""Minimal out-of-process Astra upgrade watchdog.

This file intentionally has no import path into the Supervisor or worker
runtime. It is a separate, fail-closed control plane: it verifies the
canonical checkpoint and activates only a fully tested fast-forward upgrade
after independently checking the candidate, backup, controls and Master lock.
It never starts workers, approves code, clears STOP/PAUSE/quota markers, or
writes model output.
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
ACTIVATION_CHECKS = ("TESTED", "BACKUP", "CANARY", "HEALTH")


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


def _git_head(repository: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def _git_clean(repository: Path) -> None:
    status = subprocess.check_output(
        ["git", "-C", str(repository), "status", "--porcelain=v1"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    if status:
        raise ValueError("integration worktree is dirty")


def _git_fast_forward(repository: Path, sha: str) -> None:
    subprocess.run(
        ["git", "-C", str(repository), "merge", "--ff-only", sha],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )


def _git_restore(repository: Path, sha: str) -> None:
    """Restore a clean fast-forward worktree without discarding local files."""
    _git_clean(repository)
    subprocess.run(
        ["git", "-C", str(repository), "reset", "--keep", sha],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )


def _activation_journal(state_dir: Path, batch_id: str) -> Path:
    directory = state_dir / "upgrade-activations"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory / f"{batch_id}.json"


def _write_journal(path: Path, payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(encoded + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _read_journal(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("activation journal is unavailable or invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("activation journal is invalid")
    required = {"batch_id", "previous_sha", "candidate_sha", "backup_path", "backup_sha"}
    if set(payload) - required - {"state", "created_at", "activated_at", "current_head"}:
        raise ValueError("activation journal contains unknown fields")
    if not required <= set(payload):
        raise ValueError("activation journal is incomplete")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,80}", str(payload["batch_id"])):
        raise ValueError("activation journal batch is invalid")
    for key in ("previous_sha", "candidate_sha"):
        if not SHA.fullmatch(str(payload[key])):
            raise ValueError("activation journal commit is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", str(payload["backup_sha"])):
        raise ValueError("activation journal backup digest is invalid")
    return payload


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
        "pointer_switch": "configured",
    }


def _activation_ready(db: sqlite3.Connection, batch_id: str) -> sqlite3.Row:
    row = db.execute(
        "SELECT state,candidate_sha,rollback_sha FROM upgrade_batches WHERE batch_id=?",
        (batch_id,),
    ).fetchone()
    if not row:
        raise ValueError("unknown upgrade batch")
    if row["state"] not in {"HEALTH_SOAK", "ACTIVATION_PENDING"}:
        raise ValueError("upgrade is not activation-ready")
    if not SHA.fullmatch(row["candidate_sha"]) or not SHA.fullmatch(row["rollback_sha"]):
        raise ValueError("upgrade checkpoint contains an invalid commit")
    checks = {
        item[0]: item[1]
        for item in db.execute(
            "SELECT stage,result FROM upgrade_checks WHERE batch_id=?", (batch_id,)
        )
    }
    if any(checks.get(stage) != "PASS" for stage in ACTIVATION_CHECKS):
        raise ValueError("all upgrade checks must pass before activation")
    if "tasks" in {item[0] for item in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
        active = db.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN "
            "('preflight','coding','verifying','awaiting_review','approved','running','leased')"
        ).fetchone()[0]
        if active:
            raise ValueError("active task work prevents activation")
    return row


def _require_no_controls(state_dir: Path) -> None:
    present = [name for name in ("STOP", "PAUSE", "PAUSED_QUOTA") if (state_dir / name).exists()]
    if present:
        raise ValueError("control marker blocks activation: " + ",".join(present))


def activate(state_dir: Path, batch_id: str) -> dict:
    """Atomically activate a tested controller candidate through the watchdog.

    The candidate must be a fast-forward of the last-known-good integration
    checkout. The short watchdog lock fences the Git pointer and SQLite
    checkpoint together; no model or worker process is started here.
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
    repository: Path | None = None
    previous_sha = ""
    candidate_sha = ""
    journal_path = _activation_journal(state_dir, batch_id)
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
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='upgrade_checks'"
            ).fetchone():
                raise ValueError("upgrade check table is unavailable")
            row = _activation_ready(db, batch_id)
            settings = _read_settings(db)
            candidate_sha = row["candidate_sha"]
            pending = row["state"] == "ACTIVATION_PENDING"
            if pending:
                journal = _read_journal(journal_path)
                if journal["batch_id"] != batch_id or journal["candidate_sha"] != candidate_sha:
                    raise ValueError("activation journal does not match upgrade batch")
                previous_sha = journal["previous_sha"]
                backup_path = _regular(Path(journal["backup_path"]), "activation backup")
                try:
                    backup_path.relative_to(state_dir)
                except ValueError as exc:
                    raise ValueError("activation backup is outside Astra state") from exc
                if hashlib.sha256(backup_path.read_bytes()).hexdigest() != journal["backup_sha"]:
                    raise ValueError("activation backup digest mismatch")
                with sqlite3.connect(backup_path) as backup:
                    if backup.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("activation backup integrity check failed")
            else:
                previous_sha = settings.get("integration_sha", "")
            if row["rollback_sha"] != previous_sha:
                raise ValueError("rollback checkpoint is no longer canonical")
            integration_raw = Path(settings.get("integration_path", "")).expanduser()
            if integration_raw.is_symlink() or not integration_raw.is_dir():
                raise ValueError("integration checkpoint path is unavailable")
            repository = integration_raw.resolve(strict=True)
            _git_clean(repository)
            current_head = _git_head(repository)
            head_matches = current_head in {previous_sha, candidate_sha} if pending else current_head == previous_sha
            if not head_matches:
                raise ValueError("integration HEAD does not match canonical checkpoint")
            _git_commit_exists(repository, previous_sha)
            _git_commit_exists(repository, candidate_sha)
            ancestry = subprocess.run(
                ["git", "-C", str(repository), "merge-base", "--is-ancestor",
                 previous_sha, candidate_sha], check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if ancestry.returncode:
                raise ValueError("activation candidate is not a fast-forward")
            _require_no_controls(state_dir)

            if not pending:
                journal = {
                    "batch_id": batch_id,
                    "state": "PENDING",
                    "previous_sha": previous_sha,
                    "candidate_sha": candidate_sha,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                backup_path, backup_sha = _verified_backup(state_dir, db_path, batch_id)
                journal.update({"backup_path": str(backup_path), "backup_sha": backup_sha})
                journal_sha = _write_journal(journal_path, journal)
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "UPDATE upgrade_batches SET state='ACTIVATION_PENDING',updated_at=? WHERE batch_id=?",
                    (datetime.now(timezone.utc).isoformat(), batch_id),
                )
                db.execute(
                    "INSERT INTO upgrade_checks(batch_id,stage,result,artifact_sha,evidence_sha,recorded_at,verifier) "
                    "VALUES(?,?,?,?,?,?,?) ON CONFLICT(batch_id,stage) DO UPDATE SET result=excluded.result,"
                    "artifact_sha=excluded.artifact_sha,evidence_sha=excluded.evidence_sha,"
                    "recorded_at=excluded.recorded_at,verifier=excluded.verifier",
                    (batch_id, "ACTIVATION", "PENDING", candidate_sha, journal_sha,
                     datetime.now(timezone.utc).isoformat(), "trusted_watchdog"),
                )
                db.execute("COMMIT")

            try:
                _require_no_controls(state_dir)
                if _git_head(repository) == previous_sha:
                    _git_fast_forward(repository, candidate_sha)
                if _git_head(repository) != candidate_sha:
                    raise ValueError("activation did not reach candidate checkpoint")
                _require_no_controls(state_dir)
            except Exception as exc:
                try:
                    if repository is not None and _git_head(repository) == candidate_sha:
                        _git_restore(repository, previous_sha)
                finally:
                    failed = dict(journal)
                    failed.update({"state": "FAILED", "failure": type(exc).__name__})
                    failed_sha = _write_journal(journal_path, failed)
                    db.execute("BEGIN IMMEDIATE")
                    db.execute(
                        "UPDATE upgrade_batches SET state='HEALTH_SOAK',updated_at=? WHERE batch_id=?",
                        (datetime.now(timezone.utc).isoformat(), batch_id),
                    )
                    db.execute(
                        "UPDATE upgrade_checks SET result='REJECTED',evidence_sha=?,recorded_at=?,verifier=? "
                        "WHERE batch_id=? AND stage='ACTIVATION'",
                        (failed_sha, datetime.now(timezone.utc).isoformat(), "trusted_watchdog", batch_id),
                    )
                    db.execute("COMMIT")
                raise

            final = dict(journal)
            final.update({"state": "COMMITTED", "activated_at": datetime.now(timezone.utc).isoformat(),
                          "current_head": candidate_sha})
            final_sha = _write_journal(journal_path, final)
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE settings SET value=? WHERE key='integration_sha'", (candidate_sha,))
            db.execute(
                "UPDATE upgrade_batches SET state='COMMITTED',updated_at=? WHERE batch_id=?",
                (datetime.now(timezone.utc).isoformat(), batch_id),
            )
            db.execute(
                "UPDATE upgrade_checks SET result='PASS',evidence_sha=?,recorded_at=?,verifier=? "
                "WHERE batch_id=? AND stage='ACTIVATION'",
                (final_sha, datetime.now(timezone.utc).isoformat(), "trusted_watchdog", batch_id),
            )
            db.execute("COMMIT")
            return {
                "batch_id": batch_id,
                "state": "COMMITTED",
                "previous_sha": previous_sha,
                "candidate_sha": candidate_sha,
                "integration_head_verified": True,
                "backup_path": journal["backup_path"],
                "backup_sha": journal["backup_sha"],
                "activation_receipt": str(journal_path),
                "activation_evidence_sha": final_sha,
            }
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def rollback(state_dir: Path, batch_id: str) -> dict:
    """Record a verified rollback-pending checkpoint under the independent lock.

    Rollback remains intentionally a checkpoint operation: it validates the
    last-known-good commit and records the verified backup, but does not switch
    the integration pointer automatically.
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
    parser.add_argument("--activate")
    args = parser.parse_args()
    try:
        if args.rollback and args.activate:
            parser.error("--rollback and --activate are mutually exclusive")
        if args.check or not args.rollback and not args.activate:
            print(json.dumps(check(args.state), sort_keys=True))
        if args.rollback:
            print(json.dumps(rollback(args.state, args.rollback), sort_keys=True))
        if args.activate:
            print(json.dumps(activate(args.state, args.activate), sort_keys=True))
        return 0
    except (OSError, ValueError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"watchdog refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
