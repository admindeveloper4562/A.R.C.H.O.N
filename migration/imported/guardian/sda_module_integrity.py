#!/usr/bin/env python3
"""JARVIS modular integrity triage: read-only fault isolation and SDA repair plans.

Consumes explicit health evidence, never probes production services or performs
stop/start, failover, deployment, queue writes, or privileged actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys

IDENT = re.compile(r"^[a-z][a-z0-9_-]{1,48}$")
CHECK = re.compile(r"^[a-z][a-z0-9_-]{1,64}$")
SCHEMA = 1
CRITICAL = "critical"
OK = "ok"
MAX_COMPONENTS = 100
MAX_INPUT = 65536


class IntegrityError(ValueError):
    pass


def _id(value: object, field: str) -> str:
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise IntegrityError("invalid " + field)
    return value


def _bool(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise IntegrityError(field + " must be boolean")
    return value


def plan(state: dict) -> dict:
    """Return a bounded, deterministic, non-executable recovery assessment."""
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        raise IntegrityError("unsupported input schema")
    if set(state) != {"schema", "components", "checks", "guardian"}:
        raise IntegrityError("unexpected input fields")

    components = state["components"]
    checks = state["checks"]
    guardian = state["guardian"]
    if not isinstance(components, list) or not 1 <= len(components) <= MAX_COMPONENTS:
        raise IntegrityError("components must have 1..100 entries")
    if not isinstance(checks, list) or len(checks) > 400:
        raise IntegrityError("at most 400 health checks are supported")
    if not isinstance(guardian, dict) or set(guardian) != {
            "known_good_release_verified", "checkpoint_compatible", "owner_stop_present"}:
        raise IntegrityError("guardian evidence incomplete")

    for key in guardian:
        _bool(guardian[key], "guardian." + key)

    registry = {}
    for c in components:
        if not isinstance(c, dict) or set(c) != {
                "id", "parent", "criticality", "version",
                "standby_ready", "standby_state_synced",
                "standby_fenced", "standby_contract_compatible"}:
            raise IntegrityError("invalid component manifest")
        name = _id(c["id"], "component id")
        parent = _id(c["parent"], "parent module")
        if name in registry:
            raise IntegrityError("duplicate component")
        if c["criticality"] not in ("normal", CRITICAL):
            raise IntegrityError("invalid criticality")
        version = c["version"]
        if not isinstance(version, str) or not re.fullmatch(
                r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
            raise IntegrityError("invalid unpadded component version")
        for field in ("standby_ready", "standby_state_synced",
                      "standby_fenced", "standby_contract_compatible"):
            _bool(c[field], field)
        registry[name] = {**c, "parent": parent}

    unique = {}
    for check in checks:
        if not isinstance(check, dict) or set(check) != {
                "component_id", "name", "status", "evidence_ref"}:
            raise IntegrityError("invalid integrity check")
        name = _id(check["component_id"], "check component")
        if name not in registry:
            raise IntegrityError("check references unknown component")
        category = check["name"]
        if not isinstance(category, str) or not CHECK.fullmatch(category):
            raise IntegrityError("invalid check identifier")
        if check["status"] not in (OK, "failed", "unknown"):
            raise IntegrityError("invalid check status")
        ref = check["evidence_ref"]
        # Evidence is an opaque, pointer-like identifier, not raw log content.
        if not isinstance(ref, str) or not re.fullmatch(r"[a-zA-Z0-9_:/.-]{1,180}", ref):
            raise IntegrityError("evidence must be a safe opaque reference")
        key = (name, category)
        if key in unique:
            raise IntegrityError("duplicate check identifier")
        unique[key] = check

    findings = []
    repair_tasks = []
    for (name, category), check in sorted(unique.items()):
        if check["status"] == OK:
            continue
        component = registry[name]
        critical = component["criticality"] == CRITICAL
        verified_standby = all(component[field] for field in (
            "standby_ready", "standby_state_synced",
            "standby_fenced", "standby_contract_compatible"))
        if check["status"] == "unknown":
            action = "observe_and_recheck"
        elif critical and verified_standby:
            action = "stage_verified_mirror_failover"
        elif critical:
            action = "degrade_and_request_owner_review"
        else:
            action = "isolate_micro_module_then_repair"

        fingerprint = hashlib.sha256((
            name + "/" + category + "/" + component["version"]
        ).encode()).hexdigest()[:16]
        finding = {
            "finding_id": "integrity-" + fingerprint,
            "module": component["parent"],
            "component": name,
            "observed_status": check["status"],
            "check": category,
            "evidence_ref": check["evidence_ref"],
            "criticality": component["criticality"],
            "response": action,
            "verified_standby_available": verified_standby,
            "auto_execute": False,
            "owner_review_required": critical,
        }
        findings.append(finding)
        if check["status"] == "failed":
            repair_tasks.append({
                "idempotency_key": finding["finding_id"],
                "target": component["parent"] + "/" + name,
                "task_kind": "sda_recovery_development",
                "source_version": component["version"],
                "source_evidence": [check["evidence_ref"]],
                "acceptance": [
                    "Reproduce and diagnose the integrity fault in an isolated test environment",
                    "Verify repair with targeted tests and full independent QC",
                    "Stage candidate canary and demonstrate a failing-health rollback",
                    "Preserve STOP/PAUSE/quota/owner approval and durable task state",
                ],
                "auto_enqueue_to_live_master": False,
                "eligible_for_review_queue": True,
                "requires_owner_review": critical,
            })

    guardian_allowed = (
        not guardian["owner_stop_present"] and
        guardian["known_good_release_verified"] and
        guardian["checkpoint_compatible"]
    )
    return {
        "schema": SCHEMA,
        "mode": "read_only",
        "monitored_components": len(registry),
        "failed_or_unknown_checks": len(findings),
        "findings": findings,
        "repair_task_proposals": repair_tasks,
        "live_queue_mutated": False,
        "services_restarted": False,
        "critical_traffic_migrated": False,
        "guardian_bootstrap_eligible_on_total_recovery_failure": guardian_allowed,
        "guardian_note": "Eligibility is not permission. External trusted guardian must independently verify owner controls, leases and state before any start.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS read-only module integrity and recovery planner")
    parser.add_argument("--input", default="-", help="JSON manifest/check snapshot file, or - for stdin")
    args = parser.parse_args()
    if args.input == "-":
        raw = sys.stdin.read(MAX_INPUT + 1)
    else:
        from pathlib import Path
        path = Path(args.input)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_INPUT:
            parser.error("input must be an ordinary bounded file")
        raw = path.read_text(encoding="utf-8")
    if len(raw.encode("utf-8")) > MAX_INPUT:
        parser.error("integrity snapshot exceeds 64 KiB")
    try:
        report = plan(json.loads(raw))
    except (IntegrityError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["failed_or_unknown_checks"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
