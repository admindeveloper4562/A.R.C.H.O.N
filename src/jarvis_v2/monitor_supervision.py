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
_SAFE_FAILURE_CODES = frozenset({
    "ok", "local_only", "qc_pass", "qc_passed_candidate_ready", "safe_auto_approval",
    "static_diff_review", "docker_no_network_tests", "independent_qc_start",
    "worker_failed", "worker_timeout", "worker_io_error", "worker_result_invalid",
    "worker_output_invalid", "worker_runtime_error", "codex_nonzero", "codex_nonzero_exit",
    "codex_file_change_failed", "model_error", "timeout", "quota_or_rate_limit",
    "quota_paused", "owner_stop", "owner_stop_requested", "sandbox_unavailable",
    "no_file_changes", "changed_file_limit_exceeded", "changed_size_limit_exceeded",
    "unsafe_changed_path", "protected_file_modified", "invalid_changed_file",
    "git_status_invalid", "git_diff_check_failed", "isolated_tests_failed",
    "docker_unavailable", "docker_access_denied", "docker_image_missing",
    "docker_test_config_invalid", "docker_context_invalid", "qc_agent_failed",
    "qc_invalid_verdict", "qc_invalid_findings", "qc_invalid_child_evidence",
    "qc_rejected", "merger_agent_failed", "merger_invalid_verdict", "merger_invalid_findings",
    "merger_runtime_error", "merger_rejected", "integration_patch_conflict",
    "integration_apply_failed", "integration_forbidden_change", "subtask_evidence_incomplete",
    "state_database_error", "state_database_locked", "worker_input_invalid",
    "progress_event_invalid", "worker_state_update_failed", "runtime_limit",
    "preflight_or_runner_error", "deterministic_qc_start", "qc_passed_owner_review_required",
    "task_type_invalid", "design_documentation_only", "audit_model_error", "audit_output_invalid",
    "audit_checks_failed", "audit_failed",
})
_SAFE_FAILURE_PATTERNS = (
    re.compile(r"^(?:worker|repairer)_[1-5]_(?:leased|codex_start)$"),
)


def _safe(value: Any, size: int = 64) -> str:
    """Identifiers/statuses only; do not display prompts, logs or raw findings."""
    return _SAFE_VALUE.sub("_", str(value or ""))[:size]


def _cols(db: sqlite3.Connection, name: str) -> set[str]:
    if name not in set(QUEUE_TABLES) | {
        "tasks", "subtasks", "runs", "subtask_receipts", "supervisor_cases",
        "supervisor_lanes", "upgrade_batches", "upgrade_audits", "batch_epochs", "batch_members"
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


def safe_failure_code(value: Any, size: int = 64) -> str:
    """Expose only an allow-listed category prefix, never arbitrary telemetry text."""
    first = str(value or "").split(":", 1)[0].split("=", 1)[0]
    if first not in _SAFE_FAILURE_CODES and not any(pattern.fullmatch(first) for pattern in _SAFE_FAILURE_PATTERNS):
        return "redacted"
    return _safe(first, size)


def _sha(value: Any) -> str:
    s = str(value or "")
    return s[:12] if re.fullmatch(r"[a-f0-9]{40}", s) else ""


def _digest(value: Any) -> str:
    s = str(value or "")
    return s[:12] if re.fullmatch(r"[a-f0-9]{64}", s) else _sha(s)


def collect(db: sqlite3.Connection, limit: int = 10) -> dict:
    """Collect telemetry inside the caller's single read-only SQLite transaction."""
    data: dict[str, Any] = {
        "project": None,
        "queues": {},
        "supervisor_cases": None,
        "supervisor_lanes": None,
        "upgrade_batch": None,
        "upgrade_audits": None,
        "batch": None,
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
            "verified_subtask_receipts": None,
        }
        sub_cols = _cols(db, "subtasks")
        if "status" in sub_cols:
            filter_sql = "WHERE project_id=?" if "project_id" in sub_cols else ""
            filters = (PROJECT,) if filter_sql else ()
            sub_counts = _group(db, "subtasks", "status", filter_sql, filters)
            project["subtasks_recorded"] = sum(sub_counts.values())
            project["subtask_statuses"] = sub_counts
        receipt_cols = _cols(db, "subtask_receipts")
        if {"parent_id", "candidate_sha", "verifier"} <= receipt_cols:
            project["verified_subtask_receipts"] = int(db.execute(
                "SELECT COUNT(*) FROM subtask_receipts r JOIN tasks t ON t.id=r.parent_id "
                "WHERE t.project_id=? AND r.verifier='independent_qc'", (PROJECT,)
            ).fetchone()[0])
            project["completion_evidence"] = "receipt_backed_for_recorded_children"
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
            {"code": safe_failure_code(row["error_code"]), "count": int(row["n"])}
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

    audit_cols = _cols(db, "upgrade_audits")
    if {"audit_id", "task_id", "status", "model", "updated_at"} <= audit_cols:
        data["upgrade_audits"] = [
            {
                "audit_id": _safe(row["audit_id"]),
                "task_id": _safe(row["task_id"]),
                "status": _safe(row["status"]),
                "model": _safe(row["model"], 40),
                "report_sha": _digest(row["report_sha"]) if "report_sha" in audit_cols else "",
                "evidence_sha": _digest(row["evidence_sha"]) if "evidence_sha" in audit_cols else "",
                "updated_at": _safe(row["updated_at"], 40),
            }
            for row in db.execute(
                "SELECT audit_id,task_id,status,model,report_sha,evidence_sha,updated_at "
                "FROM upgrade_audits ORDER BY updated_at DESC,audit_id DESC LIMIT ?",
                (min(limit, 10),),
            )
        ]

    epoch_cols = _cols(db, "batch_epochs")
    if {"batch_id", "state", "admitted_count", "completed_count", "updated_at"} <= epoch_cols:
        target_expr = "target_count" if "target_count" in epoch_cols else "admitted_count"
        row = db.execute(
            f"SELECT batch_id,state,admitted_count,completed_count,{target_expr} AS target_count,updated_at "
            "FROM batch_epochs ORDER BY updated_at DESC,batch_id DESC LIMIT 1"
        ).fetchone()
        data["batch"] = {
            "batch_id": _safe(row["batch_id"]),
            "state": _safe(row["state"]),
            "admitted": int(row["admitted_count"]),
            "completed": int(row["completed_count"]),
            "target": int(row["target_count"]),
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
        receipts = project.get("verified_subtask_receipts")
        lines.append(
            "  Child evidence: " +
            (f"{receipts} receipt-backed records" if receipts is not None else "not independently verified")
        )
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
    audits = data.get("upgrade_audits")
    if audits:
        latest = audits[0]
        lines.append(
            f"  U1 latest          {latest['task_id']} {latest['status']} "
            f"{latest['model']} report {latest['report_sha'] or '—'}"
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

    cohort = data.get("batch")
    lines.extend(["", "CURRENT BATCH COHORT"])
    if cohort is None:
        lines.append("  Batch epoch telemetry not recorded.")
    elif not cohort:
        lines.append("  No batch cohort recorded.")
    else:
        lines.append(f"  {cohort['batch_id']}  {cohort['state']}  completed {cohort['completed']}/{cohort['target']} "
                     f"(recorded members {cohort['admitted']})")

    lines.extend(["", "RUN HISTORY / FAILURE HOTSPOTS"])
    totals = data.get("run_totals", {})
    lines.append("  Recorded runs: " + str(sum(totals.values())))
    codes = data.get("failure_codes", [])
    for item in codes[:5]:
        lines.append(f"  {item['code']:<52} x{item['count']}")
    if not codes:
        lines.append("  No categorized failures recorded.")
    return lines
