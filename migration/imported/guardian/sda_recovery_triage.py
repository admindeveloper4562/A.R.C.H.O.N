#!/usr/bin/env python3
"""Read-only SDA self-doctor triage and bounded post-restart task handoff.

Produces a suggested repair task and verified checkpoint summary. It never
restarts a process, edits Git, clears owner control markers, or executes code.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPAIR_GUIDANCE = {
    "TEST_FAILURE": ("reproduce_test_failure", "Create isolated worktree and focused regression test"),
    "MERGE_CONFLICT": ("review_serial_integration", "Use a disposable integration worktree and preserve both branches"),
    "STALE_INTEGRATION": ("refresh_integration_base", "Revalidate develop base and re-run all required CI"),
    "DEPENDENCY_MISSING": ("inspect_dependency", "Verify package manifest and local environment without installing automatically"),
    "PROCESS_INTERRUPTED": ("reconcile_checkpoint", "Verify process identity and resume only idempotent operations"),
    "INFRASTRUCTURE_FAILURE": ("inspect_environment", "Check transport and local resources with bounded retries"),
    "MODEL_UNAVAILABLE": ("select_verified_model", "Choose an owner-approved available free route"),
    "QUOTA_EXHAUSTED": ("wait_for_quota", "Never reset quota marker or invoke paid fallback"),
    "AUTH_REQUIRED": ("owner_authentication", "Ask owner to restore authorized credentials outside model context"),
    "OWNER_APPROVAL_REQUIRED": ("owner_review", "Request explicit owner authorization"),
    "WORKTREE_COLLISION": ("isolate_worktree", "Review existing worktrees; never delete or reset them automatically"),
    "UNKNOWN_FAILURE": ("manual_diagnosis", "Collect sanitized reproduction evidence and classify"),
}


def _load_script(filename: str):
    spec = importlib.util.spec_from_file_location("sda_plan_" + filename, HERE / filename)
    if spec is None or spec.loader is None:
        raise ValueError("SDA diagnostic dependency unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def plan(doctor: dict, checkpoint: dict | None = None, *, limit: int = 8) -> dict:
    if not isinstance(doctor, dict) or doctor.get("mode") != "read_only":
        raise ValueError("only sanitized SDA doctor snapshots are accepted")
    if not 1 <= limit <= 20:
        raise ValueError("task limit must be 1..20")

    markers = set(doctor.get("control_markers", []))
    failures = doctor.get("recent_tasks", [])
    if not isinstance(failures, list):
        raise ValueError("invalid recent task list")
    active = set(doctor.get("role_states", {}).values())
    diagnostics = set(doctor.get("diagnostic_codes", []))
    checkpoint_commit = None
    if checkpoint:
        packet = checkpoint.get("packet", {})
        commit = packet.get("source_git_commit", "") if isinstance(packet, dict) else ""
        if (checkpoint.get("status") == "restored_summary" and
                re.fullmatch(r"[0-9a-f]{40}", str(commit))):
            checkpoint_commit = commit

    blockers = []
    if markers & {"STOP", "PAUSE", "PAUSED_QUOTA"}:
        blockers.append("owner_control_marker")
    if doctor.get("queue_integrity") != "ok":
        blockers.append("queue_integrity_not_verified")
    if "queue_schema_missing_tables" in diagnostics or "queue_schema_missing_columns" in diagnostics:
        blockers.append("unknown_legacy_queue_schema")
    if "running" in active:
        blockers.append("live_role_requires_process_identity_review")

    concise = []
    for task in failures[:limit]:
        if not isinstance(task, dict):
            continue
        ident = task.get("task", "")
        if not re.fullmatch(r"JRV-\d{3}", str(ident)):
            continue
        category = str(task.get("failure_category", "none"))
        state = str(task.get("state", "unknown"))
        if category not in REPAIR_GUIDANCE:
            category = "UNKNOWN_FAILURE" if state == "blocked" else "none"
        action, explanation = REPAIR_GUIDANCE.get(
            category, ("revalidate_task", "Confirm acceptance tests and dependencies"))
        concise.append({
            "task": ident, "state": state if state in {
                "pending", "waiting", "running", "qc", "repairing",
                "merge", "merging", "rebuild", "done", "blocked"} else "unknown",
            "diagnosis": category,
            "proposed_action": action,
            "rationale": explanation,
            "saved_session_available": bool(task.get("has_saved_worker_session")),
            "repeat_count": min(999, max(0, int(task.get("repeated_failure_count", 0)))),
        })

    can_propose = not blockers
    return {
        "schema": 1, "operation": "self_doctor_triage",
        "mode": "read_only", "live_restarts_enabled": False,
        "autonomous_code_changes_enabled": False,
        "can_propose_isolated_repair": can_propose,
        "can_resume_live_master": False,
        "requires_owner_approval_for_release": True,
        "requires_independent_qc": True,
        "blockers": blockers,
        "checkpoint_commit": checkpoint_commit,
        "memory_reconstruction": "bounded verified checkpoint metadata; no model weight training",
        "task_packets": concise,
        "next_step": (
            "Stop: preserve operator markers, verify queue and process ownership."
            if blockers else
            "Propose isolated reproduction tasks; do not execute or merge until authorized."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SDA read-only failure triage")
    parser.add_argument("--root", type=Path, default=HERE.parent)
    parser.add_argument("--state", type=Path, default=Path.home() / ".local/state/jarvis/workhorse-v2")
    parser.add_argument("--checkpoint-dir", type=Path,
                        default=Path.home() / ".local/state/jarvis/sda-checkpoints")
    args = parser.parse_args()
    doctor = _load_script("sda_self_doctor.py").inspect(args.root, args.state)
    checkpoint = None
    try:
        checkpoint = _load_script("sda_checkpoint.py").restore(args.checkpoint_dir)
    except (ValueError, OSError):
        pass
    result = plan(doctor, checkpoint)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
