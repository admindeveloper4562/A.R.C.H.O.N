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
    value = {
        "task_id": task_id, "generation": generation, "category": category,
        "code": code[:160], "base_sha": base_sha[:40], "candidate_sha": candidate_sha[:40],
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
        with self.state.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT attempt,base_sha,candidate_sha,project_id FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if not row:
                db.execute("ROLLBACK")
                raise ValueError("unknown recovery task")
            generation = int(row["attempt"] if generation is None else generation)
            base_sha = base_sha or row["base_sha"] or ""
            candidate_sha = candidate_sha or row["candidate_sha"] or ""
            fingerprint = failure_fingerprint(task_id, generation, category, failure_code, base_sha, candidate_sha)
            state = "triaged" if category in ACTIONABLE_CATEGORIES else "external_blocker"
            case_id = f"{task_id}-g{generation}-{fingerprint[:12]}"
            timestamp = now()
            db.execute(
                "INSERT INTO supervisor_cases(case_id,parent_id,generation,state,category,failure_fingerprint,"
                "failure_code,base_sha,candidate_sha,updated_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(parent_id,generation,failure_fingerprint) DO UPDATE SET state=excluded.state,"
                "category=excluded.category,failure_code=excluded.failure_code,base_sha=excluded.base_sha,"
                "candidate_sha=excluded.candidate_sha,updated_at=excluded.updated_at",
                (case_id, task_id, generation, state, category, fingerprint, failure_code[:160],
                 base_sha, candidate_sha, timestamp, timestamp),
            )
            db.execute("COMMIT")
        return {"case_id": case_id, "task_id": task_id, "generation": generation,
                "category": category, "state": state, "fingerprint": fingerprint}

    def claim_recovery(self, case_id: str, lane_id: str) -> dict:
        if lane_id not in RECOVERY_LANES or not _SAFE_CODE.fullmatch(case_id):
            raise ValueError("invalid recovery lane or case")
        with self.state.master_lock():
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
        with self.state.master_lock():
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
        with self.state.master_lock():
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
                    "SELECT status,last_run,attempt,candidate_sha,integrated_sha FROM tasks WHERE id=?", (lane["task_id"],)
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
                    if ancestry.returncode:
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
                    "completed_count": counts.get("completed", 0), "task_status": counts}

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
                existing = {r[0] for r in db.execute("SELECT parent_id FROM batch_members WHERE batch_id=?", (batch_id,))}
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
                    if len(existing) + len(selected) >= target:
                        break
                timestamp = now()
                start = len(existing) + 1
                db.executemany(
                    "INSERT INTO batch_members(batch_id,parent_id,ordinal,state,admitted_at,updated_at) VALUES(?,?,?,?,?,?)",
                    ((batch_id, task_id, start + n, "admitted", timestamp, timestamp) for n, task_id in enumerate(selected)),
                )
                db.execute("UPDATE batch_epochs SET admitted_count=?,target_count=MAX(target_count,?),updated_at=? WHERE batch_id=?",
                           (len(existing) + len(selected), target, timestamp, batch_id))
                db.execute("COMMIT")
        return {"batch_id": batch_id, "added": selected, "admitted_count": len(existing) + len(selected)}

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
            return {"available": True, "cases": cases, "lanes": lanes, "upgrades": upgrades}

    def tick(self, limit: int = 50) -> dict:
        """Open cases for failed tasks; no retry, approval, merge or model call."""
        if not 1 <= limit <= 500:
            raise ValueError("invalid supervisor scan limit")
        opened = []
        with self.state.master_lock():
            with self.state.db() as db:
                failures = db.execute(
                    "SELECT id,last_error,attempt,base_sha,candidate_sha FROM tasks "
                    "WHERE status IN ('failed','conflict','interrupted','stopped') "
                    "ORDER BY updated_at,id LIMIT ?", (limit,)
                ).fetchall()
                db.execute("BEGIN IMMEDIATE")
                expired = self._reconcile_recovery_leases_locked(db)
                db.execute("COMMIT")
            for row in failures:
                if row["last_error"]:
                    opened.append(self.triage_failure(row["id"], row["last_error"], base_sha=row["base_sha"],
                                                      candidate_sha=row["candidate_sha"], generation=row["attempt"]))
        return {"scanned": len(failures), "opened": opened, "expired_leases": expired,
                "status": self.status()}
