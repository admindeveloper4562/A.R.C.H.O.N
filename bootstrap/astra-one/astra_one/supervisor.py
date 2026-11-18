"""Durable Astra One v3 Supervisor state transitions.

This module is deliberately deterministic.  It records bounded recovery cases,
lane leases, batch cohorts and upgrade checkpoints; it never approves code,
invokes Codex, or changes the integration branch.  Model work remains behind
the existing worker/QC/Merger contracts.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any

from .linux_sda import PROJECT_ID, SHA, State, now

LANES = ("repair_1", "repair_2", "upgrade_auditor")
RECOVERY_LANES = ("repair_1", "repair_2")
RECOVERY_LEASE_TTL_SECONDS = 3600
ACTIONABLE_CATEGORIES = frozenset({
    "code_defect", "qc_rejection", "semantic_incompatibility", "suspected_engine_bug",
})
EXTERNAL_CATEGORIES = frozenset({
    "dependency_wait", "approval_required", "credential_required", "device_unavailable",
    "privilege_required", "provider_quota", "infrastructure", "resource_pressure", "sandbox",
})
_SAFE_CODE = re.compile(r"^[A-Za-z0-9_.:,-]{1,160}$")


def classify_failure(code: str) -> str:
    """Classify a stable task error without inspecting model prose."""
    prefix = str(code or "").split(":", 1)[0].split("=", 1)[0]
    if prefix in {"dependency_wait", "approval_required"}:
        return prefix
    if prefix in {"quota_or_rate_limit", "quota_paused"}:
        return "provider_quota"
    if prefix in {"sandbox_unavailable", "sandbox"}:
        return "sandbox"
    if prefix in {"docker_unavailable", "docker_access_denied", "docker_image_missing",
                  "docker_test_config_invalid", "state_database_locked", "state_database_error",
                  "worker_io_error", "worker_timeout", "timeout"}:
        return "infrastructure"
    if prefix in {"privilege_required", "credential_required", "device_unavailable"}:
        return prefix
    if prefix.startswith("merger_rejected") or prefix.startswith("qc_rejected"):
        return "qc_rejection"
    if prefix.startswith("integration_") or prefix in {"conflict", "integration_patch_conflict"}:
        return "semantic_incompatibility"
    if prefix in {"no_file_changes", "changed_file_limit_exceeded", "changed_size_limit_exceeded",
                  "unsafe_changed_path", "protected_file_modified", "git_status_invalid",
                  "invalid_changed_file", "codex_file_change_failed", "codex_nonzero",
                  "model_error", "isolated_tests_failed", "worker_result_invalid",
                  "worker_output_invalid", "worker_runtime_error"}:
        return "code_defect"
    return "code_defect"


def failure_fingerprint(task_id: str, generation: int, category: str, code: str,
                        base_sha: str = "", candidate_sha: str = "") -> str:
    """Return a stable fault identity; generation and SHAs remain evidence, not identity."""
    value = {
        "task_id": task_id, "category": category, "code": code[:160],
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class SupervisorController:
    """Single-writer coordinator for recovery, upgrade and batch metadata."""

    def __init__(self, state: State):
        self.state = state

    def ensure_schema(self) -> dict:
        return self.state.ensure_full_plan_schema()

    @staticmethod
    def _lease_expired(updated_at: str, max_age_seconds: int) -> bool:
        try:
            updated = datetime.fromisoformat(updated_at).timestamp()
        except (TypeError, ValueError, OverflowError):
            return True
        return datetime.now(timezone.utc).timestamp() - updated > max_age_seconds

    def _reconcile_recovery_leases_locked(self, db: sqlite3.Connection,
                                          max_age_seconds: int = RECOVERY_LEASE_TTL_SECONDS) -> list[dict]:
        """Fence leases left behind by a crashed recovery process."""
        if not 60 <= max_age_seconds <= 86_400:
            raise ValueError("invalid recovery lease TTL")
        expired = []
        lanes = db.execute(
            "SELECT lane_id,task_id,case_id,run_id,generation,updated_at FROM supervisor_lanes "
            "WHERE state='leased' AND lane_id IN ('repair_1','repair_2')"
        ).fetchall()
        for lane in lanes:
            if not self._lease_expired(lane["updated_at"], max_age_seconds):
                continue
            timestamp = now()
            task = db.execute(
                "SELECT status,last_run,integrated_sha FROM tasks WHERE id=?", (lane["task_id"],)
            ).fetchone()
            if lane["run_id"] and task and task["last_run"] == lane["run_id"]:
                if task["status"] != "completed":
                    db.execute(
                        "UPDATE tasks SET status='interrupted',last_run='',last_error='recovery_lease_expired',"
                        "updated_at=? WHERE id=? AND last_run=?",
                        (timestamp, lane["task_id"], lane["run_id"]),
                    )
                db.execute(
                    "UPDATE runs SET status='interrupted',error_code='recovery_lease_expired',finished_at=? "
                    "WHERE id=? AND status NOT IN ('completed','failed','interrupted','stopped')",
                    (timestamp, lane["run_id"]),
                )
            case_state = "blocked" if task and task["status"] == "completed" else "triaged"
            db.execute(
                "UPDATE supervisor_cases SET state=?,failure_code='recovery_lease_expired',updated_at=? "
                "WHERE case_id=? AND state='recovery_assigned'",
                (case_state, timestamp, lane["case_id"]),
            )
            db.execute(
                "UPDATE supervisor_lanes SET task_id='',case_id='',state='idle',lease_token='',generation=0,"
                "run_id='',candidate_sha='',updated_at=? WHERE lane_id=?",
                (timestamp, lane["lane_id"]),
            )
            expired.append({"lane_id": lane["lane_id"], "case_id": lane["case_id"],
                            "task_id": lane["task_id"], "state": case_state})
        return expired

    @staticmethod
    def _reconcile_completed_cases_locked(db: sqlite3.Connection) -> list[dict]:
        """Close historical failure cases only after the task has durable completion."""
        rows = db.execute(
            "SELECT c.case_id,c.parent_id,c.generation,t.candidate_sha,t.integrated_sha "
            "FROM supervisor_cases c JOIN tasks t ON t.id=c.parent_id "
            "WHERE t.status='completed' AND c.state<>'resolved' "
            "ORDER BY c.updated_at,c.case_id"
        ).fetchall()
        resolved = []
        timestamp = now()
        for row in rows:
            db.execute(
                "UPDATE supervisor_cases SET state='resolved',candidate_sha=COALESCE(NULLIF(?,''),candidate_sha),"
                "updated_at=? WHERE case_id=? AND state<>'resolved'",
                (row["candidate_sha"] or "", timestamp, row["case_id"]),
            )
            # A recovery process can finish the candidate and Merger commit
            # before its final ledger callback.  Reconcile the lane as part of
            # the same transaction so a completed task cannot strand a slot.
            db.execute(
                "UPDATE supervisor_lanes SET task_id='',case_id='',state='idle',lease_token='',"
                "generation=0,run_id='',candidate_sha='',updated_at=? "
                "WHERE case_id=? AND state='leased'",
                (timestamp, row["case_id"]),
            )
            resolved.append({
                "case_id": row["case_id"], "parent_id": row["parent_id"],
                "generation": row["generation"], "candidate_sha": row["candidate_sha"],
                "integrated_sha": row["integrated_sha"],
            })
        return resolved

    def _candidate_patch_is_integrated(self, worktree: str, base_sha: str,
                                       candidate_sha: str, integration: Path) -> bool:
        """Prove a patch-applied candidate is present without trusting ancestry.

        The serialized Merger applies the reviewed candidate diff and creates a
        new local integration commit.  That commit intentionally does not have
        the worker's candidate commit as an ancestor.  Reverse-applying the
        exact bounded candidate patch in check-only mode proves the integrated
        tree contains the candidate change without storing model output.
        """
        candidate = Path(worktree).expanduser()
        worktree_root = (self.state.home / "worktrees").resolve()
        try:
            candidate = candidate.resolve(strict=True)
            candidate.relative_to(worktree_root)
        except (OSError, ValueError):
            return False
        if candidate.is_symlink() or not candidate.is_dir():
            return False
        try:
            head = subprocess.check_output(
                ["git", "-C", str(candidate), "rev-parse", "HEAD"],
                text=True, stderr=subprocess.DEVNULL, timeout=30,
            ).strip()
            if head != candidate_sha:
                return False
            patch = subprocess.run(
                ["git", "-C", str(candidate), "diff", "--binary", base_sha, candidate_sha],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=30, check=False,
            )
            if patch.returncode or not patch.stdout or len(patch.stdout) > 6_000_000:
                return False
            reverse = subprocess.run(
                ["git", "-C", str(integration), "apply", "--reverse", "--check", "--index", "-"],
                input=patch.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=30, check=False,
            )
            return reverse.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def reconcile_recovery_leases(self, max_age_seconds: int = RECOVERY_LEASE_TTL_SECONDS) -> dict:
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                expired = self._reconcile_recovery_leases_locked(db, max_age_seconds)
                db.execute("COMMIT")
        return {"expired": expired, "count": len(expired)}

    def triage_failure(self, task_id: str, failure_code: str, *, base_sha: str = "",
                       candidate_sha: str = "", generation: int | None = None) -> dict:
        if not _SAFE_CODE.fullmatch(str(failure_code or "")):
            raise ValueError("failure code must be a bounded category")
        if base_sha and not SHA.fullmatch(base_sha):
            raise ValueError("invalid recovery base SHA")
        if candidate_sha and not SHA.fullmatch(candidate_sha):
            raise ValueError("invalid recovery candidate SHA")
        category = classify_failure(failure_code)
        with self.state.master_lock(blocking=True):
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT attempt,base_sha,candidate_sha,project_id,spec FROM tasks WHERE id=?", (task_id,)
                ).fetchone()
                if not row:
                    db.execute("ROLLBACK")
                    raise ValueError("unknown recovery task")
                generation = max(1, int(row["attempt"] if generation is None else generation))
                base_sha = base_sha or row["base_sha"] or ""
                candidate_sha = candidate_sha or row["candidate_sha"] or ""
                fingerprint = failure_fingerprint(task_id, generation, category, failure_code, base_sha, candidate_sha)
                state = "triaged" if category in ACTIONABLE_CATEGORIES else "external_blocker"
                timestamp = now()
                existing = db.execute(
                    "SELECT case_id,generation,state,category,base_sha,candidate_sha FROM supervisor_cases "
                    "WHERE parent_id=? AND failure_fingerprint=? AND state IN "
                    "('triaged','recovery_assigned','qc_rejected','merge_rejected','blocked','external_blocker','reopened') "
                    "ORDER BY updated_at DESC,case_id LIMIT 1",
                    (task_id, fingerprint),
                ).fetchone()
                deduplicated = existing is not None
                if existing:
                    case_id = existing["case_id"]
                    state = state if existing["state"] == "reopened" else existing["state"]
                    generation = existing["generation"]
                    db.execute(
                        "UPDATE supervisor_cases SET state=?,category=?,failure_code=?,"
                        "base_sha=COALESCE(NULLIF(?,''),base_sha),"
                        "candidate_sha=COALESCE(NULLIF(?,''),candidate_sha),updated_at=? WHERE case_id=?",
                        (state, category, failure_code[:160], base_sha, candidate_sha, timestamp, case_id),
                    )
                else:
                    case_id = f"{task_id}-g{generation}-{fingerprint[:12]}"
                    db.execute(
                        "INSERT INTO supervisor_cases(case_id,parent_id,generation,state,category,failure_fingerprint,"
                        "failure_code,base_sha,candidate_sha,updated_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (case_id, task_id, generation, state, category, fingerprint, failure_code[:160],
                         base_sha, candidate_sha, timestamp, timestamp),
                    )
                db.execute("COMMIT")
        try:
            spec = json.loads(row["spec"])
        except (TypeError, UnicodeError, json.JSONDecodeError):
            spec = {}
        roots = spec.get("suggested_scope_roots", []) if isinstance(spec, dict) else []
        if not isinstance(roots, list):
            roots = []
        execution_mode = spec.get("execution_mode", "implementation") if isinstance(spec, dict) else "implementation"
        if not isinstance(execution_mode, str) or not _SAFE_CODE.fullmatch(execution_mode):
            execution_mode = "unknown"
        scope_roots = [root[:200] for root in roots[:16]
                       if isinstance(root, str) and 0 < len(root) <= 200 and ".." not in root
                       and not root.startswith("/")]
        return {"case_id": case_id, "task_id": task_id, "generation": generation,
                "category": category, "state": state, "fingerprint": fingerprint,
                "deduplicated": deduplicated, "execution_mode": execution_mode,
                "scope_roots": scope_roots}

    def self_doctor(self, limit: int = 50) -> dict:
        """Create bounded, deduplicated proposals from recorded task failures."""
        if not 1 <= limit <= 500:
            raise ValueError("invalid self-doctor scan limit")
        with self.state.master_lock(blocking=True):
            with self.state.db() as db:
                failures = db.execute(
                    "SELECT id,last_error,attempt,base_sha,candidate_sha FROM tasks "
                    "WHERE status IN ('failed','conflict','interrupted','stopped') AND last_error<>'' "
                    "ORDER BY updated_at,id LIMIT ?", (limit,)
                ).fetchall()
        proposals = []
        external = []
        skipped = []
        for row in failures:
            try:
                proposal = self.triage_failure(
                    row["id"], row["last_error"], base_sha=row["base_sha"],
                    candidate_sha=row["candidate_sha"], generation=row["attempt"],
                )
            except ValueError:
                skipped.append({"task_id": row["id"], "reason": "triage_rejected"})
                continue
            (proposals if proposal["category"] in ACTIONABLE_CATEGORIES else external).append(proposal)
        return {
            "scanned": len(failures), "proposals": proposals, "external": external,
            "skipped": skipped, "deduplicated": sum(item["deduplicated"] for item in proposals + external),
        }

    def mark_external_blocker(self, case_id: str, category: str, failure_code: str = "") -> dict:
        """Fence a non-coding blocker without consuming another worker generation."""
        if category not in EXTERNAL_CATEGORIES:
            raise ValueError("invalid external blocker category")
        failure_code = failure_code or category
        if not _SAFE_CODE.fullmatch(failure_code):
            raise ValueError("failure code must be a bounded category")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT c.parent_id,c.state,t.status,t.last_run FROM supervisor_cases c "
                    "JOIN tasks t ON t.id=c.parent_id WHERE c.case_id=?",
                    (case_id,),
                ).fetchone()
                if not row or row["state"] not in {"triaged", "qc_rejected", "merge_rejected", "external_blocker"}:
                    db.execute("ROLLBACK")
                    raise ValueError("case is not externally classifiable")
                if row["status"] not in {"failed", "conflict", "interrupted", "stopped", "blocked", "pending"}:
                    db.execute("ROLLBACK")
                    raise ValueError("task is not blocked or failed")
                timestamp = now()
                db.execute(
                    "UPDATE tasks SET status='blocked',last_error=?,updated_at=? WHERE id=?",
                    (failure_code[:160], timestamp, row["parent_id"]),
                )
                if row["last_run"]:
                    db.execute(
                        "UPDATE runs SET status='blocked',error_code=?,finished_at=COALESCE(finished_at,?) "
                        "WHERE id=? AND status NOT IN ('completed','failed','interrupted','blocked')",
                        (failure_code[:160], timestamp, row["last_run"]),
                    )
                for queue in ("pending_queue", "rebuild_queue", "review_queue", "merge_queue"):
                    db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (row["parent_id"],))
                db.execute(
                    "UPDATE subtasks SET status='waiting',updated_at=? "
                    "WHERE parent_id=? AND status IN ('running','pending')",
                    (timestamp, row["parent_id"]),
                )
                db.execute(
                    "UPDATE supervisor_cases SET state='external_blocker',category=?,failure_code=?,updated_at=? "
                    "WHERE case_id=?",
                    (category, failure_code[:160], timestamp, case_id),
                )
                db.execute("COMMIT")
        return {"case_id": case_id, "task_id": row["parent_id"],
                "state": "external_blocker", "category": category,
                "failure_code": failure_code[:160]}

    def resolve_external(self, task_id: str, evidence_path: Path) -> dict:
        """Re-admit one external blocker only after task-specific evidence passes."""
        if not _SAFE_CODE.fullmatch(task_id):
            raise ValueError("invalid task ID")
        self.state.ensure_full_plan_schema()
        path = evidence_path.expanduser().resolve()
        try:
            path.relative_to((self.state.home / "private").resolve())
        except ValueError as exc:
            raise ValueError("external evidence must be below private state") from exc
        if path.is_symlink() or not path.is_file() or (path.stat().st_mode & 0o777) != 0o600:
            raise ValueError("external evidence must be a regular owner-private mode 0600 file")
        raw = path.read_bytes()
        if len(raw) > 32_000:
            raise ValueError("external evidence exceeds the size limit")
        try:
            evidence = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("external evidence is not valid JSON") from exc
        if not isinstance(evidence, dict) or evidence.get("task_id") != task_id:
            raise ValueError("external evidence task mismatch")
        if any(
            str(key).lower() != "no_secrets_or_payloads"
            and any(word in str(key).lower() for word in ("secret", "password", "private_key", "raw_token"))
            for key in evidence
        ):
            raise ValueError("external evidence contains a sensitive field")
        expected_kinds = {
            "BASE-013": "cloudflare_readonly_inventory",
            "FIN-001": "mira_readonly_inventory",
            "MIG-002": "github_policy_and_ci",
            "RES-015": "research_live_source_benchmark",
            "AUTO-013": "cloudflare_worker_deployment",
            "REL-005": "cloudflare_pending_jobs",
            "TWS-011": "tws_blender_asset",
        }
        if task_id == "WIN-002":
            raise ValueError("WIN-002 requires real Windows device evidence")
        if evidence.get("kind") != expected_kinds.get(task_id):
            raise ValueError("unsupported or mismatched external evidence kind")
        if evidence.get("archon_read_only_policy") is not True:
            raise ValueError("external evidence must preserve the ARCHON read-only policy")
        if task_id == "RES-015":
            self._validate_research_benchmark_evidence(evidence)
        if task_id == "AUTO-013":
            self._validate_cloudflare_deployment_evidence(evidence)
        if task_id == "REL-005":
            self._validate_pending_jobs_evidence(evidence)
        if task_id == "MIG-002":
            self._validate_github_free_evidence(evidence)
        if task_id == "TWS-011":
            self._validate_tws_blender_evidence(evidence)
        evidence_sha = hashlib.sha256(raw).hexdigest()
        with self.state.master_lock():
            stamp = re.sub(r"[^0-9A-Za-z_-]", "", now())[:32]
            directory = self.state.home / "backups" / f"pre-external-resolution-{task_id}-{stamp}"
            directory.mkdir(mode=0o700, parents=True, exist_ok=False)
            backup_path = directory / "sda.sqlite3"
            with sqlite3.connect(self.state.database) as source, sqlite3.connect(backup_path) as target:
                source.backup(target)
                integrity = target.execute("PRAGMA integrity_check").fetchone()[0]
                schema = target.execute("PRAGMA user_version").fetchone()[0]
            if integrity != "ok":
                raise ValueError("external-resolution backup integrity failed")
            backup_sha = hashlib.sha256(backup_path.read_bytes()).hexdigest()
            manifest = directory / "DB_BACKUP_MANIFEST.json"
            fd = os.open(manifest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"purpose": "pre-external-blocker-resolution", "task_id": task_id,
                           "backup_path": str(backup_path), "backup_sha256": backup_sha,
                           "schema_version": schema, "integrity_check": integrity,
                           "created_at_utc": now()}, handle, sort_keys=True, indent=2)
                handle.write("\n")
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT t.*,c.case_id,c.state AS case_state,c.category AS case_category "
                    "FROM tasks t JOIN supervisor_cases c ON c.parent_id=t.id "
                    "WHERE t.id=? AND c.case_id=? LIMIT 1",
                    (task_id, evidence.get("case_id", "")),
                ).fetchone()
                if not row or row["case_state"] != "external_blocker" or row["status"] != "blocked":
                    db.execute("ROLLBACK")
                    raise ValueError("task has no matching external blocker case")
                settings = {item[0]: item[1] for item in db.execute(
                    "SELECT key,value FROM settings WHERE key IN ('source_sha','integration_sha')"
                )}
                if evidence.get("source_sha") != settings.get("source_sha") or evidence.get("integration_sha") != settings.get("integration_sha"):
                    db.execute("ROLLBACK")
                    raise ValueError("external evidence checkpoint mismatch")
                spec = json.loads(row["spec"])
                dependencies = [db.execute("SELECT status FROM tasks WHERE id=?", (dep,)).fetchone()
                                for dep in spec.get("depends_on", [])]
                if any(item is None or item[0] != "completed" for item in dependencies):
                    db.execute("ROLLBACK")
                    raise ValueError("external evidence dependencies are incomplete")
                if task_id == "FIN-001":
                    if any(evidence.get(key) != value for key, value in {
                        "worker_name": "personal-management",
                        "d1_name": "mira-finance",
                        "archon_read_only_policy": True,
                        "no_financial_rows_read": True,
                    }.items()):
                        db.execute("ROLLBACK")
                        raise ValueError("FIN-001 Mira evidence is incomplete")
                    if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("worker_source_sha256", ""))) or not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("d1_schema_sha256", ""))):
                        db.execute("ROLLBACK")
                        raise ValueError("FIN-001 source evidence digest is invalid")
                    owner = db.execute(
                        "SELECT receipt_sha256 FROM owner_approval_receipts "
                        "WHERE task_id=? AND decision='APPROVE' ORDER BY created_at DESC LIMIT 1",
                        (task_id,),
                    ).fetchone()
                    if not owner or evidence.get("owner_receipt_sha256") != owner[0]:
                        db.execute("ROLLBACK")
                        raise ValueError("FIN-001 owner receipt binding is missing")
                if db.execute(
                    "SELECT 1 FROM external_resolution_receipts WHERE case_id=? AND evidence_sha256=?",
                    (row["case_id"], evidence_sha),
                ).fetchone():
                    db.execute("ROLLBACK")
                    return {"task_id": task_id, "state": "pending", "idempotent": True,
                            "evidence_sha256": evidence_sha}
                timestamp = now()
                db.execute(
                    "INSERT INTO external_resolution_receipts(receipt_id,case_id,task_id,category,evidence_path,evidence_sha256,"
                    "backup_path,backup_sha256,source_sha,integration_sha,verifier,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(uuid.uuid4()), row["case_id"], task_id, row["case_category"], str(path), evidence_sha,
                     str(backup_path), backup_sha, settings["source_sha"], settings["integration_sha"],
                     "deterministic_master", timestamp),
                )
                db.execute("UPDATE supervisor_cases SET state='resolved_external',updated_at=? WHERE case_id=?",
                           (timestamp, row["case_id"]))
                db.execute("UPDATE tasks SET status='pending',available_at=0,last_run='',last_error='',updated_at=? WHERE id=?",
                           (timestamp, task_id))
                for queue in ("pending_queue", "rebuild_queue", "review_queue", "merge_queue"):
                    db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (task_id,))
                db.execute(
                    "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) VALUES(?,?,?,?,?)",
                    (task_id, row["project_id"], row["enqueue_seq"], 0, timestamp),
                )
                db.execute("UPDATE subtasks SET status='waiting',evidence='',updated_at=? WHERE parent_id=? AND status NOT IN ('completed','archived')",
                           (timestamp, task_id))
                first = db.execute(
                    "SELECT id,spec FROM subtasks WHERE parent_id=? AND status='waiting' ORDER BY sequence LIMIT 1",
                    (task_id,),
                ).fetchone()
                if first and all(db.execute("SELECT status FROM subtasks WHERE id=?", (dep,)).fetchone()[0] == "completed"
                                 for dep in json.loads(first["spec"]).get("depends_on", [])):
                    db.execute("UPDATE subtasks SET status='pending',updated_at=? WHERE id=?", (timestamp, first["id"]))
                db.execute("UPDATE batch_members SET state='admitted',updated_at=? WHERE parent_id=? AND state='external_blocker'",
                           (timestamp, task_id))
                db.execute("COMMIT")
        return {"task_id": task_id, "state": "pending", "idempotent": False,
                "evidence_sha256": evidence_sha, "backup_sha256": backup_sha}

    def _validate_github_free_evidence(self, evidence: dict) -> None:
        """Bind MIG-002 to the recorded Free-plan amendment, never to a fake pass."""
        for key in ("original_plan_sha256", "amended_plan_sha256", "amendment_artifact_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get(key, ""))):
                raise ValueError("MIG-002 plan amendment digest is invalid")
        if evidence.get("github_private") is not True or evidence.get("remote_protection_status") != 403:
            raise ValueError("MIG-002 GitHub Free limitation evidence is incomplete")
        if evidence.get("hosted_ci_status") != "deferred_plan":
            raise ValueError("MIG-002 hosted CI status must remain explicitly deferred")
        if evidence.get("local_policy_status") != "verified":
            raise ValueError("MIG-002 local policy evidence is incomplete")
        if evidence.get("no_secrets_or_payloads") is not True:
            raise ValueError("MIG-002 evidence must exclude secrets and payloads")
        with self.state.db() as db:
            row = db.execute(
                "SELECT original_plan_sha256,amended_plan_sha256,artifact_sha256,status "
                "FROM task_plan_amendments WHERE amendment_id=? AND parent_id='MIG-002'",
                (evidence.get("amendment_id", ""),),
            ).fetchone()
        if (not row or row["status"] != "active" or
                (row["original_plan_sha256"], row["amended_plan_sha256"], row["artifact_sha256"]) != (
                    evidence["original_plan_sha256"], evidence["amended_plan_sha256"],
                    evidence["amendment_artifact_sha256"])):
            raise ValueError("MIG-002 evidence is not bound to an active plan amendment")

    def _validate_tws_blender_evidence(self, evidence: dict) -> None:
        """Validate real Linux Blender artifacts while keeping device gates open."""
        if (evidence.get("native_validation_scope") != "blender-linux" or
                evidence.get("follow_on_device_validation") != "not_claimed"):
            raise ValueError("TWS-011 evidence scope is invalid")
        if evidence.get("no_secrets_or_payloads") is not True:
            raise ValueError("TWS-011 evidence must exclude secrets and payloads")
        if evidence.get("blender_version") != "5.3.0":
            raise ValueError("TWS-011 Blender version is not pinned")
        if (evidence.get("blend_reopen_passed") is not True or
                evidence.get("usd_export_passed") is not True or
                evidence.get("mesh_count") != 8 or evidence.get("armature_count") != 1 or
                evidence.get("armature_modifier_count") != 8):
            raise ValueError("TWS-011 Blender validation evidence is incomplete")
        for key in ("source_sha256", "blender_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get(key, ""))):
                raise ValueError("TWS-011 provenance digest is invalid")
        for key, suffix in (("blend_path", ".blend"), ("usdz_path", ".usdz")):
            value = evidence.get(key)
            if not isinstance(value, str) or not value.endswith(suffix):
                raise ValueError("TWS-011 artifact path is invalid")
            path = Path(value).expanduser().resolve()
            try:
                path.relative_to(self.state.home.resolve())
            except ValueError as exc:
                raise ValueError("TWS-011 artifacts must remain in Astra state") from exc
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
                raise ValueError("TWS-011 artifact is unavailable or too large")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != evidence[f"{key[:-5]}_sha256"]:
                raise ValueError("TWS-011 artifact digest mismatch")

    def _validate_cloudflare_deployment_evidence(self, evidence: dict) -> None:
        """Require bounded, non-secret proof of the owner-operated monitor deployment."""
        if evidence.get("worker_name") != "astra-one-monitor":
            raise ValueError("Cloudflare worker name is incorrect")
        worker_url = evidence.get("worker_url")
        if not isinstance(worker_url, str) or not re.fullmatch(
                r"https://[A-Za-z0-9][A-Za-z0-9.-]*\.workers\.dev", worker_url):
            raise ValueError("Cloudflare worker URL is invalid")
        if evidence.get("health_status") != 200 or evidence.get("health_service") != "astra-one-monitor":
            raise ValueError("Cloudflare health evidence is incomplete")
        if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                            str(evidence.get("deployment_version_id", ""))):
            raise ValueError("Cloudflare deployment version is invalid")
        if evidence.get("d1_name") != "astra-one-monitor" or not re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                str(evidence.get("d1_id", ""))):
            raise ValueError("Cloudflare D1 evidence is incomplete")
        tables = evidence.get("d1_tables")
        if (not isinstance(tables, list) or len(tables) > 16
                or any(not isinstance(item, str) or len(item) > 80 for item in tables)
                or not {"astra_events", "astra_runs"}.issubset(tables)):
            raise ValueError("Cloudflare D1 schema evidence is incomplete")
        if evidence.get("d1_rows_written") != 0:
            raise ValueError("Cloudflare evidence must be read-only")
        if evidence.get("owner_deployment_confirmed") is not True:
            raise ValueError("owner deployment confirmation is required")
        if (not isinstance(evidence.get("release_approval_reference"), str)
                or not 1 <= len(evidence["release_approval_reference"]) <= 200):
            raise ValueError("release approval reference is required")

    def _validate_pending_jobs_evidence(self, evidence: dict) -> None:
        """Require deployed, metadata-only reconnect evidence for REL-005."""
        if evidence.get("worker_name") != "astra-one-monitor":
            raise ValueError("Cloudflare pending-job worker name is incorrect")
        worker_url = evidence.get("worker_url")
        if not isinstance(worker_url, str) or not re.fullmatch(
                r"https://[A-Za-z0-9][A-Za-z0-9.-]*\.workers\.dev", worker_url):
            raise ValueError("Cloudflare pending-job worker URL is invalid")
        if evidence.get("health_status") != 200 or evidence.get("health_service") != "astra-one-monitor":
            raise ValueError("Cloudflare pending-job health evidence is incomplete")
        if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                            str(evidence.get("deployment_version_id", ""))):
            raise ValueError("Cloudflare pending-job deployment version is invalid")
        if evidence.get("d1_name") != "astra-one-monitor" or not re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                str(evidence.get("d1_id", ""))):
            raise ValueError("Cloudflare pending-job D1 evidence is incomplete")
        tables = evidence.get("d1_tables")
        if (not isinstance(tables, list) or len(tables) > 16
                or any(not isinstance(item, str) or len(item) > 80 for item in tables)
                or not {"astra_events", "astra_runs", "astra_jobs"}.issubset(tables)):
            raise ValueError("Cloudflare pending-job schema evidence is incomplete")
        if (type(evidence.get("d1_job_rows")) is not int or evidence["d1_job_rows"] < 0
                or evidence.get("metadata_only") is not True):
            raise ValueError("pending-job evidence must be empty and metadata-only")
        if evidence.get("no_secrets_or_payloads") is not True:
            raise ValueError("pending-job evidence must exclude secrets and payloads")
        if evidence.get("local_typecheck_passed") is not True or evidence.get("wrangler_dry_run_passed") is not True:
            raise ValueError("pending-job deterministic checks are incomplete")
        if type(evidence.get("local_test_count")) is not int or evidence["local_test_count"] < 7:
            raise ValueError("pending-job test evidence is incomplete")
        if evidence.get("live_job_smoke_passed") is not True or evidence.get("live_job_final_state") != "completed":
            raise ValueError("live pending-job smoke evidence is incomplete")
        if (not isinstance(evidence.get("live_job_id"), str)
                or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", evidence["live_job_id"])):
            raise ValueError("live pending-job smoke identity is invalid")
        if evidence.get("schema_migration_applied") is not True:
            raise ValueError("pending-job schema migration evidence is incomplete")
        if evidence.get("owner_deployment_confirmed") is not True:
            raise ValueError("owner deployment confirmation is required")
        if (not isinstance(evidence.get("release_approval_reference"), str)
                or not 1 <= len(evidence["release_approval_reference"]) <= 200):
            raise ValueError("release approval reference is required")

    def _validate_research_benchmark_evidence(self, evidence: dict) -> None:
        """Require a bounded source report before re-admitting RES-015."""
        if evidence.get("benchmark_status") != "ready_for_qc":
            raise ValueError("research benchmark is not ready for independent QC")
        if evidence.get("no_credentials_used") is not True:
            raise ValueError("research evidence must confirm no credentials were used")
        for key in ("live_source_count", "timestamped_source_count"):
            if type(evidence.get(key)) is not int or evidence[key] < 2:
                raise ValueError("research evidence has too few live timestamped sources")
        source_ids = evidence.get("source_ids")
        if (
            not isinstance(source_ids, list)
            or any(not isinstance(item, str) for item in source_ids)
            or not {"python_docs", "youtube"}.issubset(source_ids)
        ):
            raise ValueError("research evidence source identities are incomplete")
        limitations = evidence.get("known_limitations")
        if not isinstance(limitations, list) or not limitations or any(
            not isinstance(item, str) or not item.strip() for item in limitations
        ):
            raise ValueError("research evidence must record known limitations")
        report_value = evidence.get("report_path")
        report_sha = evidence.get("report_sha256")
        if not isinstance(report_value, str) or not re.fullmatch(r"[0-9a-f]{64}", str(report_sha)):
            raise ValueError("research evidence report binding is invalid")
        report_path = Path(report_value).expanduser().resolve()
        try:
            report_path.relative_to((self.state.home / "worktrees").resolve())
        except ValueError as exc:
            raise ValueError("research evidence report must be in an Astra worktree") from exc
        if report_path.is_symlink() or not report_path.is_file():
            raise ValueError("research evidence report is unavailable")
        if hashlib.sha256(report_path.read_bytes()).hexdigest() != report_sha:
            raise ValueError("research evidence report digest mismatch")

    def claim_recovery(self, case_id: str, lane_id: str) -> dict:
        if lane_id not in RECOVERY_LANES or not _SAFE_CODE.fullmatch(case_id):
            raise ValueError("invalid recovery lane or case")
        with self.state.master_lock(blocking=True):
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                self._reconcile_recovery_leases_locked(db)
                lane = db.execute("SELECT * FROM supervisor_lanes WHERE lane_id=?", (lane_id,)).fetchone()
                case = db.execute("SELECT * FROM supervisor_cases WHERE case_id=?", (case_id,)).fetchone()
                if not lane or lane["state"] != "idle":
                    db.execute("ROLLBACK")
                    raise ValueError("recovery lane is not idle")
                if not case or case["state"] not in {"triaged", "qc_rejected", "merge_rejected"}:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery case is not actionable")
                task = db.execute("SELECT status FROM tasks WHERE id=?", (case["parent_id"],)).fetchone()
                if not task or task["status"] not in {"failed", "conflict", "interrupted", "stopped"}:
                    db.execute("ROLLBACK")
                    raise ValueError("task is still owned by the normal pipeline")
                if db.execute(
                    "SELECT 1 FROM supervisor_lanes WHERE task_id=? AND state<>'idle'", (case["parent_id"],)
                ).fetchone():
                    db.execute("ROLLBACK")
                    raise ValueError("task already has an active recovery lease")
                token = hashlib.sha256(f"{case_id}:{now()}".encode()).hexdigest()[:24]
                timestamp = now()
                db.execute(
                    "UPDATE supervisor_lanes SET task_id=?,case_id=?,state='leased',lease_token=?,updated_at=? WHERE lane_id=?",
                    (case["parent_id"], case_id, token, timestamp, lane_id),
                )
                db.execute("UPDATE supervisor_cases SET state='recovery_assigned',updated_at=? WHERE case_id=?",
                           (timestamp, case_id))
                db.execute("COMMIT")
                return {"lane_id": lane_id, "case_id": case_id, "task_id": case["parent_id"], "lease_token": token}

    def bind_recovery_candidate(self, lane_id: str, case_id: str, *, lease_token: str,
                                run_id: str, generation: int, candidate_sha: str) -> dict:
        """Bind the recovery lease to the exact QC-approved candidate before merge."""
        if lane_id not in RECOVERY_LANES or not re.fullmatch(r"[a-f0-9]{24}", lease_token):
            raise ValueError("invalid recovery lease token")
        if not re.fullmatch(r"[0-9a-f-]{20,80}", run_id) or generation < 1 or not SHA.fullmatch(candidate_sha):
            raise ValueError("invalid recovery candidate binding")
        with self.state.master_lock(blocking=True):
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                lane = db.execute(
                    "SELECT task_id,case_id,state,lease_token,generation,run_id FROM supervisor_lanes WHERE lane_id=?",
                    (lane_id,),
                ).fetchone()
                task = db.execute(
                    "SELECT status,last_run,attempt,candidate_sha FROM tasks WHERE id=?",
                    (lane["task_id"],) if lane else ("",),
                ).fetchone()
                if (not lane or lane["case_id"] != case_id or lane["state"] != "leased"
                        or lane["lease_token"] != lease_token or lane["generation"] != generation
                        or lane["run_id"] != run_id or not task
                        or task["last_run"] != run_id or task["attempt"] != generation
                        or task["candidate_sha"] != candidate_sha
                        or task["status"] not in {"awaiting_review", "approved"}):
                    db.execute("ROLLBACK")
                    raise ValueError("recovery candidate binding mismatch")
                db.execute(
                    "UPDATE supervisor_lanes SET candidate_sha=?,updated_at=? WHERE lane_id=?",
                    (candidate_sha, now(), lane_id),
                )
                db.execute("COMMIT")
        return {"lane_id": lane_id, "case_id": case_id, "candidate_sha": candidate_sha}

    def finish_recovery(self, lane_id: str, case_id: str, *, lease_token: str,
                        run_id: str, generation: int, candidate_sha: str = "", state: str) -> dict:
        if lane_id not in RECOVERY_LANES or state not in {"qc_pending", "resolved", "blocked"}:
            raise ValueError("invalid recovery completion")
        if not re.fullmatch(r"[a-f0-9]{24}", lease_token):
            raise ValueError("invalid recovery lease token")
        if not re.fullmatch(r"[0-9a-f-]{20,80}", run_id) or generation < 1:
            raise ValueError("invalid recovery run generation")
        if candidate_sha and not SHA.fullmatch(candidate_sha):
            raise ValueError("invalid recovery candidate SHA")
        with self.state.master_lock(blocking=True):
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                lane = db.execute(
                    "SELECT task_id,case_id,state,lease_token,generation,run_id,candidate_sha "
                    "FROM supervisor_lanes WHERE lane_id=?", (lane_id,)
                ).fetchone()
                if (not lane or lane["case_id"] != case_id or lane["state"] != "leased"
                        or lane["lease_token"] != lease_token or lane["run_id"] != run_id
                        or lane["generation"] != generation):
                    db.execute("ROLLBACK")
                    raise ValueError("recovery lease mismatch")
                task = db.execute(
                    "SELECT status,last_run,attempt,candidate_sha,integrated_sha,base_sha,worktree "
                    "FROM tasks WHERE id=?", (lane["task_id"],)
                ).fetchone()
                if not task or task["last_run"] != run_id or task["attempt"] != generation:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery task generation mismatch")
                if candidate_sha and task["candidate_sha"] != candidate_sha:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery candidate mismatch")
                expected_states = {
                    "resolved": {"completed"},
                    "qc_pending": {"awaiting_review", "approved"},
                    "blocked": {"failed", "conflict", "interrupted", "stopped"},
                }
                if task["status"] not in expected_states[state]:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery outcome does not match task state")
                if state == "resolved":
                    if not SHA.fullmatch(candidate_sha) or lane["candidate_sha"] != candidate_sha:
                        db.execute("ROLLBACK")
                        raise ValueError("resolved recovery requires bound candidate")
                    integrated_sha = task["integrated_sha"]
                    if not SHA.fullmatch(integrated_sha) or integrated_sha != self.state.get("integration_sha"):
                        db.execute("ROLLBACK")
                        raise ValueError("resolved recovery lacks integrated checkpoint")
                    repository = self._integration_repository()
                    self._verify_commit(repository, candidate_sha)
                    self._verify_commit(repository, integrated_sha)
                    ancestry = subprocess.run(
                        ["git", "-C", str(repository), "merge-base", "--is-ancestor", candidate_sha, integrated_sha],
                        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    if ancestry.returncode and not self._candidate_patch_is_integrated(
                        task["worktree"], task["base_sha"], candidate_sha, repository,
                    ):
                        db.execute("ROLLBACK")
                        raise ValueError("integrated checkpoint does not contain recovery candidate")
                timestamp = now()
                db.execute("UPDATE supervisor_cases SET state=?,candidate_sha=COALESCE(NULLIF(?,''),candidate_sha),updated_at=? WHERE case_id=?",
                           (state, candidate_sha, timestamp, case_id))
                db.execute("UPDATE supervisor_lanes SET task_id='',case_id='',state='idle',lease_token='',generation=0,run_id='',candidate_sha='',updated_at=? WHERE lane_id=?",
                           (timestamp, lane_id))
                db.execute("COMMIT")
        return {"lane_id": lane_id, "case_id": case_id, "state": state}

    def release_unstarted_recovery(self, lane_id: str, case_id: str, *, lease_token: str) -> dict:
        """Return a lease when transfer failed before a recovery run existed."""
        if lane_id not in RECOVERY_LANES or not re.fullmatch(r"[a-f0-9]{24}", lease_token):
            raise ValueError("invalid recovery lease token")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                lane = db.execute(
                    "SELECT case_id,state,lease_token,generation,run_id FROM supervisor_lanes WHERE lane_id=?",
                    (lane_id,),
                ).fetchone()
                if (not lane or lane["case_id"] != case_id or lane["state"] != "leased"
                        or lane["lease_token"] != lease_token or lane["generation"] != 0
                        or lane["run_id"]):
                    db.execute("ROLLBACK")
                    raise ValueError("recovery lease is already running")
                timestamp = now()
                db.execute("UPDATE supervisor_cases SET state='blocked',updated_at=? WHERE case_id=?",
                           (timestamp, case_id))
                db.execute(
                    "UPDATE supervisor_lanes SET task_id='',case_id='',state='idle',lease_token='',"
                    "generation=0,run_id='',candidate_sha='',updated_at=? WHERE lane_id=?",
                    (timestamp, lane_id),
                )
                db.execute("COMMIT")
        return {"lane_id": lane_id, "case_id": case_id, "state": "blocked"}

    def claim_upgrade_audit(self, task_id: str, *, model: str) -> dict:
        """Lease the single read-only U1 auditor without touching task state."""
        if not _SAFE_CODE.fullmatch(task_id) or not 1 <= len(model) <= 80:
            raise ValueError("invalid upgrade audit request")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                lane = db.execute(
                    "SELECT state FROM supervisor_lanes WHERE lane_id='upgrade_auditor'"
                ).fetchone()
                task = db.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone()
                if not lane or lane["state"] != "idle":
                    db.execute("ROLLBACK")
                    raise ValueError("upgrade auditor is not idle")
                if not task:
                    db.execute("ROLLBACK")
                    raise ValueError("unknown upgrade audit task")
                audit_id = f"U1-{task_id}-{uuid.uuid4().hex[:12]}"
                run_id = str(uuid.uuid4())
                timestamp = now()
                db.execute(
                    "INSERT INTO upgrade_audits(audit_id,task_id,lane_id,run_id,model,status,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (audit_id, task_id, "upgrade_auditor", run_id, model, "running", timestamp, timestamp),
                )
                db.execute(
                    "UPDATE supervisor_lanes SET task_id=?,case_id=?,state='leased',run_id=?,updated_at=? "
                    "WHERE lane_id='upgrade_auditor'",
                    (task_id, audit_id, run_id, timestamp),
                )
                db.execute("COMMIT")
                return {"audit_id": audit_id, "task_id": task_id, "lane_id": "upgrade_auditor",
                        "run_id": run_id, "model": model}

    def finish_upgrade_audit(self, audit_id: str, *, run_id: str, status: str,
                             report_path: str = "", report_sha: str = "",
                             evidence_sha: str = "", failure_code: str = "") -> dict:
        """Record only bounded U1 metadata, then release the auditor lane."""
        if status not in {"completed", "failed"} or not _SAFE_CODE.fullmatch(audit_id):
            raise ValueError("invalid upgrade audit completion")
        if not re.fullmatch(r"[0-9a-f-]{20,80}", run_id):
            raise ValueError("invalid upgrade audit run")
        for value, size in ((report_sha, 64), (evidence_sha, 64)):
            if value and (len(value) != size or not re.fullmatch(r"[0-9a-f]+", value)):
                raise ValueError("invalid upgrade audit hash")
        if report_path:
            path = Path(report_path).expanduser()
            root = (self.state.home / "private" / "upgrade-audits").resolve()
            try:
                resolved = path.resolve(strict=True)
                resolved.relative_to(root)
            except (OSError, ValueError):
                raise ValueError("upgrade audit report outside private state")
        if failure_code and not _SAFE_CODE.fullmatch(failure_code):
            raise ValueError("invalid upgrade audit failure code")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                audit = db.execute(
                    "SELECT lane_id,status FROM upgrade_audits WHERE audit_id=? AND run_id=?",
                    (audit_id, run_id),
                ).fetchone()
                if not audit or audit["status"] != "running":
                    db.execute("ROLLBACK")
                    raise ValueError("upgrade audit lease mismatch")
                timestamp = now()
                db.execute(
                    "UPDATE upgrade_audits SET status=?,report_path=?,report_sha=?,evidence_sha=?,"
                    "failure_code=?,updated_at=? WHERE audit_id=? AND run_id=?",
                    (status, report_path[:300], report_sha, evidence_sha, failure_code[:160], timestamp,
                     audit_id, run_id),
                )
                db.execute(
                    "UPDATE supervisor_lanes SET task_id='',case_id='',state='idle',lease_token='',"
                    "generation=0,run_id='',candidate_sha='',updated_at=? "
                    "WHERE lane_id='upgrade_auditor' AND case_id=? AND run_id=?",
                    (timestamp, audit_id, run_id),
                )
                db.execute("COMMIT")
        return {"audit_id": audit_id, "status": status, "report_sha": report_sha,
                "evidence_sha": evidence_sha}

    def start_batch(self, batch_id: str, limit: int = 20) -> dict:
        if not re.fullmatch(r"[A-Z0-9_.-]{3,80}", batch_id) or not 1 <= limit <= 20:
            raise ValueError("invalid batch")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                if db.execute("SELECT 1 FROM batch_epochs WHERE batch_id=?", (batch_id,)).fetchone():
                    db.execute("ROLLBACK")
                    raise ValueError("batch already exists")
                rows = db.execute(
                    "SELECT id,spec FROM tasks WHERE project_id=? AND status IN ('pending','queued') "
                    "AND owner_gate=0 AND NOT EXISTS (SELECT 1 FROM batch_members active_members "
                    "JOIN batch_epochs active_epochs ON active_epochs.batch_id=active_members.batch_id "
                    "WHERE active_members.parent_id=tasks.id AND active_epochs.state IN ('running','draining')) "
                    "ORDER BY CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 "
                    "WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 WHEN 'P4' THEN 4 ELSE 5 END,enqueue_seq,created_at,id",
                    (PROJECT_ID,),
                ).fetchall()
                eligible = []
                for row in rows:
                    spec = json.loads(row["spec"])
                    deps = spec.get("depends_on", [])
                    if all(db.execute("SELECT status FROM tasks WHERE id=?", (dep,)).fetchone()[0] == "completed" for dep in deps):
                        eligible.append(row["id"])
                    if len(eligible) == limit:
                        break
                timestamp = now()
                db.execute("INSERT INTO batch_epochs(batch_id,state,admitted_count,completed_count,target_count,updated_at,created_at) VALUES(?,?,?,?,?,?,?)",
                           (batch_id, "running", len(eligible), 0, limit, timestamp, timestamp))
                db.executemany(
                    "INSERT INTO batch_members(batch_id,parent_id,ordinal,state,admitted_at,updated_at) VALUES(?,?,?,?,?,?)",
                    ((batch_id, task_id, n, "admitted", timestamp, timestamp) for n, task_id in enumerate(eligible, 1)),
                )
                db.execute("COMMIT")
        return {"batch_id": batch_id, "admitted": eligible, "count": len(eligible), "state": "running"}

    def batch_status(self, batch_id: str) -> dict:
        with self.state.db() as db:
            row = db.execute("SELECT * FROM batch_epochs WHERE batch_id=?", (batch_id,)).fetchone()
            if not row:
                raise ValueError("unknown batch")
            counts = {r[0]: r[1] for r in db.execute(
                "SELECT t.status,count(*) FROM batch_members b JOIN tasks t ON t.id=b.parent_id "
                "WHERE b.batch_id=? GROUP BY t.status", (batch_id,)
            )}
            return {"batch_id": batch_id, "state": row["state"], "admitted_count": row["admitted_count"],
                    "target_count": row["target_count"], "completed_count": counts.get("completed", 0),
                    "task_status": counts}

    def replenish_batch(self, batch_id: str, target: int = 20) -> dict:
        """Admit newly eligible parents without replacing existing cohort members."""
        if not re.fullmatch(r"[A-Z0-9_.-]{3,80}", batch_id) or not 1 <= target <= 20:
            raise ValueError("invalid batch target")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                batch = db.execute("SELECT admitted_count,state,target_count FROM batch_epochs WHERE batch_id=?", (batch_id,)).fetchone()
                if not batch or batch["state"] not in {"running", "draining"}:
                    db.execute("ROLLBACK")
                    raise ValueError("batch is not replenishable")
                # External blockers remain recorded in the cohort history but
                # must not consume one of the trial's verified-completion
                # slots.  Mark them and replenish against the eligible count.
                timestamp = now()
                db.execute(
                    "UPDATE batch_members SET state='external_blocker',updated_at=? "
                    "WHERE batch_id=? AND parent_id IN ("
                    "SELECT c.parent_id FROM supervisor_cases c WHERE c.state='external_blocker')",
                    (timestamp, batch_id),
                )
                existing_rows = db.execute(
                    "SELECT parent_id,state FROM batch_members WHERE batch_id=?", (batch_id,)
                ).fetchall()
                existing = {r[0] for r in existing_rows}
                eligible_existing = sum(r[1] != "external_blocker" for r in existing_rows)
                rows = db.execute(
                    "SELECT id,spec FROM tasks WHERE project_id=? AND status IN ('pending','queued') "
                    "AND owner_gate=0 AND NOT EXISTS (SELECT 1 FROM batch_members active_members "
                    "JOIN batch_epochs active_epochs ON active_epochs.batch_id=active_members.batch_id "
                    "WHERE active_members.parent_id=tasks.id AND active_epochs.state IN ('running','draining')) "
                    "ORDER BY CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 "
                    "WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 WHEN 'P4' THEN 4 ELSE 5 END,enqueue_seq,created_at,id",
                    (PROJECT_ID,),
                ).fetchall()
                selected = []
                for row in rows:
                    if row["id"] in existing:
                        continue
                    spec = json.loads(row["spec"])
                    if all(db.execute("SELECT status FROM tasks WHERE id=?", (dep,)).fetchone()[0] == "completed" for dep in spec.get("depends_on", [])):
                        selected.append(row["id"])
                    if eligible_existing + len(selected) >= target:
                        break
                start = len(existing) + 1
                db.executemany(
                    "INSERT INTO batch_members(batch_id,parent_id,ordinal,state,admitted_at,updated_at) VALUES(?,?,?,?,?,?)",
                    ((batch_id, task_id, start + n, "admitted", timestamp, timestamp) for n, task_id in enumerate(selected)),
                )
                db.execute("UPDATE batch_epochs SET admitted_count=?,target_count=MAX(target_count,?),updated_at=? WHERE batch_id=?",
                           (len(existing) + len(selected), target, timestamp, batch_id))
                db.execute("COMMIT")
        return {"batch_id": batch_id, "added": selected, "admitted_count": len(existing) + len(selected),
                "eligible_count": eligible_existing + len(selected), "target_count": target}

    def create_upgrade(self, batch_id: str, candidate_sha: str, rollback_sha: str) -> dict:
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,80}", batch_id) or not SHA.fullmatch(candidate_sha) or not SHA.fullmatch(rollback_sha):
            raise ValueError("invalid upgrade checkpoint")
        if rollback_sha != self.state.get("integration_sha"):
            raise ValueError("rollback checkpoint must equal current integration SHA")
        integration = self._integration_repository()
        self._verify_commit(integration, candidate_sha)
        self._verify_commit(integration, rollback_sha)
        ancestry = subprocess.run(
            ["git", "-C", str(integration), "merge-base", "--is-ancestor",
             self.state.get("integration_sha"), candidate_sha], check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if ancestry.returncode:
            raise ValueError("upgrade candidate is not derived from canonical integration SHA")
        with self.state.master_lock():
            with self.state.db() as db:
                timestamp = now()
                db.execute("BEGIN IMMEDIATE")
                db.execute("INSERT INTO upgrade_batches(batch_id,state,candidate_sha,rollback_sha,updated_at,created_at) VALUES(?,?,?,?,?,?)",
                           (batch_id, "PROPOSED", candidate_sha, rollback_sha, timestamp, timestamp))
                db.execute("UPDATE supervisor_lanes SET state='idle',updated_at=? WHERE lane_id='upgrade_auditor'", (timestamp,))
                db.execute("COMMIT")
        return {"batch_id": batch_id, "state": "PROPOSED", "candidate_sha": candidate_sha, "rollback_sha": rollback_sha}

    def _integration_repository(self) -> Path:
        raw = Path(self.state.get("integration_path")).expanduser()
        if raw.is_symlink() or not raw.is_dir():
            raise ValueError("integration checkpoint path is unavailable")
        repository = raw.resolve(strict=True)
        head = subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if head != self.state.get("integration_sha"):
            raise ValueError("integration checkpoint SHA does not match Git HEAD")
        return repository

    @staticmethod
    def _verify_commit(repository: Path, sha: str) -> None:
        subprocess.run(
            ["git", "-C", str(repository), "cat-file", "-e", f"{sha}^{{commit}}"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    def _candidate_checkout(self, repository: Path, candidate_sha: str) -> tempfile.TemporaryDirectory:
        """Materialize a bounded, read-only test checkout from a verified commit."""
        archive = subprocess.run(
            ["git", "-C", str(repository), "archive", "--format=tar", candidate_sha],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, timeout=90,
        )
        if archive.returncode or not archive.stdout or len(archive.stdout) > 50_000_000:
            raise ValueError("upgrade candidate archive unavailable")
        checkout = tempfile.TemporaryDirectory(prefix="astra-upgrade-canary-")
        try:
            with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:
                root = Path(checkout.name).resolve()
                for member in tar.getmembers():
                    if member.issym() or member.islnk() or member.isdev():
                        raise ValueError("upgrade candidate archive contains a link or device")
                    target = (root / member.name).resolve()
                    target.relative_to(root)
                tar.extractall(checkout.name)
        except Exception:
            checkout.cleanup()
            raise
        return checkout

    def _run_candidate_tests(self, repository: Path, candidate_sha: str, *, canary: bool = False) -> str:
        checkout = self._candidate_checkout(repository, candidate_sha)
        try:
            root = Path(checkout.name)
            env = os.environ.copy()
            if canary:
                commands = [
                    ([sys.executable, "-m", "astra_one.linux_cli", "--help"], root, ""),
                    ([sys.executable, "-m", "unittest", "discover", "-s",
                      "bootstrap/astra-one/tests", "-p", "test_supervisor_v3.py", "-q"], root, "astra_canary"),
                    ([sys.executable, "-m", "unittest", "discover", "-s",
                      "tests", "-p", "test_monitor_supervision.py", "-q"], root, "root_canary"),
                ]
            else:
                if not (root / "tests").is_dir() or not (root / "bootstrap" / "astra-one" / "tests").is_dir():
                    raise ValueError("upgrade test suite unavailable")
                commands = [
                    ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"],
                     root, "root"),
                    ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"],
                     root / "bootstrap" / "astra-one", "astra"),
                ]
            proofs = []
            for command, cwd, suite in commands:
                command_env = dict(env)
                if suite == "root":
                    command_env["PYTHONPATH"] = ":".join(
                        str(path) for path in (root / "src", root / "bootstrap" / "astra-one") if path.is_dir()
                    )
                elif suite == "astra":
                    command_env["PYTHONPATH"] = str(root / "bootstrap" / "astra-one")
                elif suite == "astra_canary":
                    command_env["PYTHONPATH"] = ":".join(
                        str(path) for path in (root / "src", root / "bootstrap" / "astra-one") if path.is_dir()
                    )
                elif suite == "root_canary":
                    command_env["PYTHONPATH"] = ":".join(
                        str(path) for path in (root / "src", root / "bootstrap" / "astra-one") if path.is_dir()
                    )
                else:
                    command_env["PYTHONPATH"] = ":".join(
                        str(path) for path in (root / "src", root / "bootstrap" / "astra-one") if path.is_dir()
                    )
                result = subprocess.run(command, cwd=cwd, env=command_env, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, check=False, timeout=600)
                if result.returncode:
                    raise ValueError("upgrade candidate tests failed")
                if "unittest" in command and not command[-1] == "--help":
                    if not re.search(r"Ran\s+([1-9][0-9]*)\s+tests?", result.stdout):
                        raise ValueError("upgrade candidate tests produced no test evidence")
                proofs.append(result.stdout[-20_000:])
            return hashlib.sha256("\n---\n".join(proofs).encode()).hexdigest()
        finally:
            checkout.cleanup()

    def _verify_database_backup(self, batch_id: str) -> str:
        backup_dir = self.state.home / "backups" / "upgrade-checks"
        backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        path = backup_dir / f"{batch_id}-backup-{hashlib.sha256(now().encode()).hexdigest()[:12]}.sqlite3"
        with sqlite3.connect(self.state.database) as source, sqlite3.connect(path) as target:
            source.backup(target)
            if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("upgrade backup integrity check failed")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return digest

    def run_upgrade_check(self, batch_id: str, stage: str, artifact_sha: str) -> dict:
        """Perform a check while holding the single upgrade/claim fence."""
        with self.state.master_lock():
            return self._run_upgrade_check_locked(batch_id, stage, artifact_sha)

    def _run_upgrade_check_locked(self, batch_id: str, stage: str, artifact_sha: str) -> dict:
        """Perform and record a real bounded check; callers cannot self-report PASS."""
        if stage not in {"TESTED", "BACKUP", "CANARY", "HEALTH"} or not SHA.fullmatch(artifact_sha):
            raise ValueError("invalid upgrade check")
        integration = self._integration_repository()
        with self.state.db() as db:
            row = db.execute(
                "SELECT state,candidate_sha,rollback_sha FROM upgrade_batches WHERE batch_id=?", (batch_id,)
            ).fetchone()
        if not row or row["state"] in {"ROLLBACK_PENDING", "ROLLED_BACK", "COMMITTED"}:
            raise ValueError("upgrade is not checkable")
        self._verify_commit(integration, artifact_sha)
        if stage in {"TESTED", "CANARY"} and artifact_sha != row["candidate_sha"]:
            raise ValueError("candidate check must bind the candidate SHA")
        if stage == "BACKUP" and artifact_sha != row["rollback_sha"]:
            raise ValueError("backup check must bind the rollback checkpoint")
        if stage == "TESTED":
            proof = self._run_candidate_tests(integration, artifact_sha)
        elif stage == "CANARY":
            proof = self._run_candidate_tests(integration, artifact_sha, canary=True)
        elif stage == "BACKUP":
            proof = self._verify_database_backup(batch_id)
        else:
            with sqlite3.connect(self.state.database) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("health check database integrity failed")
            if subprocess.check_output(
                ["git", "-C", str(integration), "rev-parse", "HEAD"], text=True,
                stderr=subprocess.DEVNULL,
            ).strip() != self.state.get("integration_sha"):
                raise ValueError("health check integration checkpoint moved")
            proof = hashlib.sha256((artifact_sha + "|health|ok").encode()).hexdigest()
        timestamp = now()
        with self.state.db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO upgrade_checks(batch_id,stage,result,artifact_sha,evidence_sha,recorded_at,verifier) "
                "VALUES(?,?,?,?,?,?,?) ON CONFLICT(batch_id,stage) DO UPDATE SET result=excluded.result,"
                "artifact_sha=excluded.artifact_sha,evidence_sha=excluded.evidence_sha,"
                "recorded_at=excluded.recorded_at,verifier=excluded.verifier",
                (batch_id, stage, "PASS", artifact_sha, proof, timestamp, "deterministic_controller"),
            )
            db.execute("COMMIT")
        return {"batch_id": batch_id, "stage": stage, "result": "PASS",
                "artifact_sha": artifact_sha, "evidence_sha": proof}

    def transition_upgrade(self, batch_id: str, state: str) -> dict:
        # Public CLI transitions stop before external watchdog approval. There
        # is deliberately no generic command that can record a commit or
        # pointer switch as if the trusted watchdog had approved it.
        allowed = {"PROPOSED", "PATCH_IN_ISOLATION", "TESTED", "DRAIN_NEW_CLAIMS", "STAGED_CANARY",
                   "HEALTH_SOAK"}
        if state not in allowed:
            raise ValueError("invalid upgrade state")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT state FROM upgrade_batches WHERE batch_id=?", (batch_id,)).fetchone()
                if not row:
                    db.execute("ROLLBACK")
                    raise ValueError("unknown upgrade batch")
                current = row["state"]
                transitions = {
                    "PROPOSED": {"PATCH_IN_ISOLATION"},
                    "PATCH_IN_ISOLATION": {"TESTED"},
                    "TESTED": {"DRAIN_NEW_CLAIMS"},
                    "DRAIN_NEW_CLAIMS": {"STAGED_CANARY"},
                    "STAGED_CANARY": {"HEALTH_SOAK"},
                    "HEALTH_SOAK": set(),
                }
                if state not in transitions.get(current, set()):
                    db.execute("ROLLBACK")
                    raise ValueError("invalid upgrade transition")
                if state == "PATCH_IN_ISOLATION":
                    repository = self._integration_repository()
                    self._verify_commit(repository, db.execute(
                        "SELECT candidate_sha FROM upgrade_batches WHERE batch_id=?", (batch_id,)
                    ).fetchone()[0])
                    self._verify_commit(repository, db.execute(
                        "SELECT rollback_sha FROM upgrade_batches WHERE batch_id=?", (batch_id,)
                    ).fetchone()[0])
                required_check = {"TESTED": "TESTED", "DRAIN_NEW_CLAIMS": "BACKUP",
                                  "STAGED_CANARY": "CANARY", "HEALTH_SOAK": "HEALTH"}.get(state)
                if required_check and not db.execute(
                    "SELECT 1 FROM upgrade_checks WHERE batch_id=? AND stage=? AND result='PASS'",
                    (batch_id, required_check),
                ).fetchone():
                    db.execute("ROLLBACK")
                    raise ValueError(f"upgrade check required: {required_check}")
                db.execute("UPDATE upgrade_batches SET state=?,updated_at=? WHERE batch_id=?", (state, now(), batch_id))
                db.execute("COMMIT")
        return {"batch_id": batch_id, "state": state}

    def status(self) -> dict:
        with self.state.db() as db:
            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "supervisor_cases" not in tables:
                return {"available": False, "reason": "schema_v3_not_migrated"}
            cases = {r[0]: r[1] for r in db.execute("SELECT state,count(*) FROM supervisor_cases GROUP BY state")}
            lanes = [dict(r) for r in db.execute(
                "SELECT lane_id,role,task_id,case_id,state,updated_at FROM supervisor_lanes ORDER BY lane_id")]
            upgrades = [dict(r) for r in db.execute(
                "SELECT batch_id,state,candidate_sha,rollback_sha,updated_at FROM upgrade_batches ORDER BY updated_at DESC LIMIT 5")]
            audits = [dict(r) for r in db.execute(
                "SELECT audit_id,task_id,status,model,report_sha,evidence_sha,updated_at "
                "FROM upgrade_audits ORDER BY updated_at DESC LIMIT 10")]
            return {"available": True, "cases": cases, "lanes": lanes, "upgrades": upgrades,
                    "upgrade_audits": audits}

    def tick(self, limit: int = 50) -> dict:
        """Open cases for failed tasks; no retry, approval, merge or model call."""
        if not 1 <= limit <= 500:
            raise ValueError("invalid supervisor scan limit")
        with self.state.master_lock():
            with self.state.db() as db:
                db.execute("BEGIN IMMEDIATE")
                expired = self._reconcile_recovery_leases_locked(db)
                resolved = self._reconcile_completed_cases_locked(db)
                db.execute("COMMIT")
        doctor = self.self_doctor(limit)
        return {"scanned": doctor["scanned"], "opened": doctor["proposals"] + doctor["external"],
                "proposals": doctor["proposals"], "external": doctor["external"],
                "skipped": doctor["skipped"], "deduplicated": doctor["deduplicated"],
                "expired_leases": expired,
                "resolved_cases": resolved,
                "status": self.status()}
