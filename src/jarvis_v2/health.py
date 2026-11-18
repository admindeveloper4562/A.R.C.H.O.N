"""Compact, read-only ARCHON control-plane health reporting."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sqlite3
import subprocess
from typing import Any


class HealthError(RuntimeError):
    """Raised when the canonical health state cannot be read safely."""


def _systemd_state(unit: str) -> str:
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", unit],
            capture_output=True, text=True, timeout=3, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    value = result.stdout.strip()
    return value if value else ("unknown" if result.returncode == 1 else "inactive")


def _git_head(repository: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=3, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise HealthError("Git checkout is unavailable") from exc
    if result.returncode or len(result.stdout.strip()) != 40:
        raise HealthError("Git checkout SHA is unavailable")
    return result.stdout.strip()


def _root_blockers(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    status = {row["id"]: row["status"] for row in rows}
    incomplete_children: Counter[str] = Counter()
    parsed: dict[str, list[str]] = {}
    for row in rows:
        try:
            spec = json.loads(row["spec"] or "{}")
        except (TypeError, ValueError):
            spec = {}
        deps = spec.get("depends_on", []) if isinstance(spec, dict) else []
        parsed[row["id"]] = deps if isinstance(deps, list) else []
    for task_id, deps in parsed.items():
        for other, other_deps in parsed.items():
            if task_id in other_deps and status.get(other) != "completed":
                incomplete_children[task_id] += 1
    result = []
    for row in rows:
        if row["status"] not in {"blocked", "approval_required", "waiting"}:
            continue
        deps = parsed[row["id"]]
        if any(status.get(dep) != "completed" for dep in deps):
            continue
        result.append({
            "task_id": row["id"],
            "status": row["status"],
            "error": row["last_error"] or "",
            "unlocks": incomplete_children[row["id"]],
        })
    return sorted(result, key=lambda item: (-item["unlocks"], item["task_id"]))


def collect_health(*, state_dir: Path, repository: Path) -> dict[str, Any]:
    """Read the canonical state without creating or mutating any file."""
    state_dir = state_dir.expanduser().resolve()
    raw_database = state_dir / "sda.sqlite3"
    if raw_database.is_symlink() or not raw_database.is_file():
        raise HealthError("canonical SDA database is unavailable")
    database = raw_database.resolve(strict=True)
    try:
        db = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True, timeout=3)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA busy_timeout=3000")
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise HealthError("canonical SDA integrity check failed")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required = {"settings", "projects", "tasks", "subtasks"}
        if not required <= tables:
            raise HealthError("canonical SDA schema is incomplete")
        settings = {row[0]: row[1] for row in db.execute("SELECT key,value FROM settings")}
        project = db.execute(
            "SELECT id,parent_task_count,subtask_count,payload_sha FROM projects "
            "WHERE id='ARCHON-JARVIS-V2'"
        ).fetchone()
        if project is None:
            raise HealthError("ARCHON project envelope is unavailable")
        tasks = db.execute(
            "SELECT id,status,last_error,spec,candidate_sha,integrated_sha,updated_at "
            "FROM tasks WHERE project_id='ARCHON-JARVIS-V2'"
        ).fetchall()
        parent_status = dict(Counter(row["status"] for row in tasks))
        queue_counts = {}
        for name in ("project_queue", "pending_queue", "rebuild_queue", "review_queue", "merge_queue"):
            queue_counts[name] = db.execute(
                f"SELECT count(*) FROM {name}" if name in tables else "SELECT 0"
            ).fetchone()[0]
        active_runs = db.execute(
            "SELECT count(*) FROM runs WHERE status IN "
            "('preflight','coding','verifying','awaiting_review','approved','running','leased','merging')"
        ).fetchone()[0] if "runs" in tables else 0
        active_lanes = db.execute(
            "SELECT count(*) FROM supervisor_lanes WHERE state <> 'idle'"
        ).fetchone()[0] if "supervisor_lanes" in tables else 0
        approval_wait = db.execute(
            "SELECT count(*) FROM tasks WHERE project_id='ARCHON-JARVIS-V2' AND status='approval_required'"
        ).fetchone()[0]
        last_qc = None
        if "candidate_submissions" in tables:
            row = db.execute(
                "SELECT task_id,candidate_sha,status,updated_at FROM candidate_submissions "
                "WHERE status IN ('passed','merged') ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
            if row:
                last_qc = dict(row)
        last_integrated = db.execute(
            "SELECT id,candidate_sha,integrated_sha,updated_at FROM tasks "
            "WHERE project_id='ARCHON-JARVIS-V2' AND status='completed' "
            "ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        result = {
            "status": "healthy",
            "git": {"checkout_sha": _git_head(repository.resolve())},
            "sqlite": {"path": str(database), "integrity": integrity,
                        "schema": int(settings.get("schema_version", "0"))},
            "integration_sha": settings.get("integration_sha", ""),
            "plan": {"parent_total": project["parent_task_count"],
                     "subtask_total": project["subtask_count"],
                     "payload_sha": project["payload_sha"]},
            "parents": parent_status,
            "root_blockers": _root_blockers(tasks),
            "queues": queue_counts,
            "active": {"runs": active_runs, "supervisor_lanes": active_lanes},
            "owner_approvals_waiting": approval_wait,
            "controls": {name: (state_dir / name).exists() for name in ("STOP", "PAUSE", "PAUSED_QUOTA")},
            "controller": {"service": _systemd_state("archon-astra.service"),
                           "timer": _systemd_state("archon-astra.timer")},
            "last_successful_qc": last_qc,
            "last_integrated_candidate": dict(last_integrated) if last_integrated else None,
        }
        db.close()
        return result
    except sqlite3.Error as exc:
        raise HealthError("canonical SDA read failed") from exc


__all__ = ["HealthError", "collect_health"]
