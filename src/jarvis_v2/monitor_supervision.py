"""Read-only supervisor, failure and batch telemetry for the ATLAS terminal monitor.

Only observes optional SQLite tables.  Never mutates the SDA database, invokes
workers, probes network services, or treats recorded rows as process liveness.
The existing five-worker Astra schema remains fully supported.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

PROJECT = "ARCHON-JARVIS-V2"
QUEUE_TABLES = ("project_queue", "pending_queue", "rebuild_queue", "review_queue", "merge_queue")
SUPERVISOR_LANES = ("repair_1", "repair_2", "upgrade_auditor")
_SAFE_VALUE = re.compile(r"[^A-Za-z0-9_./:-]")


def _safe(value: Any, size: int = 64) -> str:
    """Identifiers/statuses only; do not display prompts, logs or raw findings."""
    return _SAFE_VALUE.sub("_", str(value or ""))[:size]


def _cols(db: sqlite3.Connection, name: str) -> set[str]:
    if name not in set(QUEUE_TABLES) | {
        "tasks", "subtasks", "runs", "supervisor_cases",
        "supervisor_lanes", "upgrade_batches"
    }:
        return set()
    exists = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    if not exists:
        return set()
    return {str(row["name"]) for row in db.execute(f"PRAGMA table_info({name})")}


def _group(db: sqlite3.Connection, table: str, column: str, where: str = "",
           params: tuple = ()) -> dict[str, int]:
    rows = db.execute(
        f"SELECT {column} AS group_key, COUNT(*) AS count FROM {table} "
        f"{where} GROUP BY {column}", params
    )
    return {_safe(row["group_key"], 48): int(row["count"]) for row in rows}


def _sha(value: Any) -> str:
    s = str(value or "")
    return s[:12] if re.fullmatch(r"[a-f0-9]{40}", s) else ""


def collect(db: sqlite3.Connection, limit: int = 10) -> dict:
    """Collect telemetry inside the caller's single read-only SQLite transaction."""
    data: dict[str, Any] = {
        "project": None,
        "queues": {},
        "supervisor_cases": None,
        "supervisor_lanes": None,
        "upgrade_batch": None,
        "failure_codes": [],
        "telemetry_version": 1,
    }
    task_cols = _cols(db, "tasks")
    if "project_id" in task_cols and "status" in task_cols:
        project_counts = _group(
            db, "tasks", "status", "WHERE project_id=?", (PROJECT,)
        )
        project: dict[str, Any] = {
            "id": PROJECT,
            "parents_recorded": sum(project_counts.values()),
            "parent_statuses": project_counts,
            "subtasks_recorded": None,
            "subtask_statuses": {},
            "completion_evidence": "status_only_not_independently_verified",
        }
        sub_cols = _cols(db, "subtasks")
        if "status" in sub_cols:
            filter_sql = "WHERE project_id=?" if "project_id" in sub_cols else ""
            filters = (PROJECT,) if filter_sql else ()
            sub_counts = _group(db, "subtasks", "status", filter_sql, filters)
            project["subtasks_recorded"] = sum(sub_counts.values())
            project["subtask_statuses"] = sub_counts
        data["project"] = project

    for table in QUEUE_TABLES:
        if _cols(db, table):
            data["queues"][table] = int(
                db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            )
        else:
            data["queues"][table] = None

    run_cols = _cols(db, "runs")
    if {"error_code", "status"} <= run_cols:
        data["run_totals"] = _group(db, "runs", "status")
        rows = db.execute(
            "SELECT error_code, COUNT(*) AS n FROM runs "
            "WHERE error_code IS NOT NULL AND error_code <> '' "
            "GROUP BY error_code ORDER BY n DESC,error_code LIMIT 8"
        ).fetchall()
        data["failure_codes"] = [
            {"code": _safe(str(row["error_code"]).split(":", 1)[0].split("=", 1)[0]), "count": int(row["n"])}
            for row in rows
        ]
    else:
        data["run_totals"] = {}

    case_cols = _cols(db, "supervisor_cases")
    if {"case_id", "parent_id", "state", "category", "updated_at"} <= case_cols:
        data["supervisor_cases"] = {
            "states": _group(db, "supervisor_cases", "state"),
            "categories": _group(db, "supervisor_cases", "category"),
            "recent": [
                {
                    "case_id": _safe(row["case_id"]),
                    "parent_id": _safe(row["parent_id"]),
                    "state": _safe(row["state"]),
                    "category": _safe(row["category"]),
                    "updated_at": _safe(row["updated_at"], 40),
                }
                for row in db.execute(
                    "SELECT case_id,parent_id,state,category,updated_at "
                    "FROM supervisor_cases ORDER BY updated_at DESC,case_id LIMIT ?",
                    (min(limit, 20),),
                )
            ],
        }

    lane_cols = _cols(db, "supervisor_lanes")
    if {"lane_id", "role", "task_id", "state", "updated_at"} <= lane_cols:
        rows = db.execute(
            "SELECT lane_id,role,task_id,state,updated_at "
            "FROM supervisor_lanes WHERE lane_id IN (?,?,?) "
            "ORDER BY lane_id", SUPERVISOR_LANES
        ).fetchall()
        data["supervisor_lanes"] = [
            {
                "lane_id": _safe(row["lane_id"]),
                "role": _safe(row["role"]),
                "task_id": _safe(row["task_id"]),
                "state": _safe(row["state"]),
                "updated_at": _safe(row["updated_at"], 40),
            }
            for row in rows
        ]

    upgrade_cols = _cols(db, "upgrade_batches")
    if {"batch_id", "state", "candidate_sha", "rollback_sha", "updated_at"} <= upgrade_cols:
        row = db.execute(
            "SELECT batch_id,state,candidate_sha,rollback_sha,updated_at "
            "FROM upgrade_batches ORDER BY updated_at DESC,batch_id DESC LIMIT 1"
        ).fetchone()
        data["upgrade_batch"] = {
            "batch_id": _safe(row["batch_id"]),
            "state": _safe(row["state"]),
            "candidate_sha": _sha(row["candidate_sha"]),
            "rollback_sha": _sha(row["rollback_sha"]),
            "updated_at": _safe(row["updated_at"], 40),
        } if row else {}

    return data


def render_lines(data: dict) -> list[str]:
    """Produce informative terminal lines without fabricating agents or uptime."""
    if not data:
        return []
    lines = ["", "ARCHON FULL-BUILD / SUPERVISOR RECOVERY (recorded SQLite state)"]
    project = data.get("project")
    if project:
        parents = project.get("parents_recorded", 0)
        children = project.get("subtasks_recorded")
        lines.append(f"  Project {project.get('id', '')}  parents {parents}  children {children if children is not None else 'not recorded'}")
        lines.append("  Parent states: " + ", ".join(
            f"{k}={v}" for k, v in sorted(project.get("parent_statuses", {}).items())
        ))
        lines.append("  Child status is bookkeeping, not proof of independent acceptance.")
    else:
        lines.append("  Project child-level telemetry not available on this schema.")

    queues = data.get("queues", {})
    lines.extend(["", "DURABLE QUEUES (missing table = not instrumented)"])
    for name in QUEUE_TABLES:
        count = queues.get(name)
        lines.append(f"  {name:<16} {count if count is not None else 'not recorded'}")

    lines.extend(["", "SUPERVISOR REPAIR LANES / UPGRADE AUDITOR"])
    lane_data = data.get("supervisor_lanes")
    if lane_data is None:
        lines.append("  No supervisor lane telemetry schema yet; no active/idle inference.")
    else:
        mapping = {row["lane_id"]: row for row in lane_data}
        for lane in SUPERVISOR_LANES:
            r = mapping.get(lane)
            lines.append(
                f"  {lane:<16} {r['state']:<18} {r['task_id'] or 'no task recorded'}"
                if r else f"  {lane:<16} no recorded slot"
            )

    cases = data.get("supervisor_cases")
    lines.extend(["", "BLOCKED-TASK RECOVERY"])
    if cases is None:
        lines.append("  Recovery-case telemetry not yet instrumented.")
    else:
        states = cases.get("states", {})
        lines.append("  Cases: " + (", ".join(f"{k}={v}" for k, v in sorted(states.items())) or "none"))
        for r in cases.get("recent", [])[:5]:
            lines.append(f"  {r['case_id']}  {r['parent_id']}  {r['state']}  {r['category']}")

    batch = data.get("upgrade_batch")
    lines.extend(["", "SELF-UPGRADE BATCH"])
    if batch is None:
        lines.append("  Upgrade batch telemetry not yet instrumented.")
    elif not batch:
        lines.append("  No upgrade batches recorded.")
    else:
        lines.append(f"  {batch['batch_id']}  {batch['state']}  candidate {batch['candidate_sha'] or '—'}  rollback {batch['rollback_sha'] or '—'}")

    lines.extend(["", "RUN HISTORY / FAILURE HOTSPOTS"])
    totals = data.get("run_totals", {})
    lines.append("  Recorded runs: " + str(sum(totals.values())))
    codes = data.get("failure_codes", [])
    for item in codes[:5]:
        lines.append(f"  {item['code']:<52} x{item['count']}")
    if not codes:
        lines.append("  No categorized failures recorded.")
    return lines
