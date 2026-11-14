"""Write a bounded CI receipt containing only fixed, non-sensitive metadata."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Mapping


PYTHON_CHECK_ORDER = (
    "unit_tests",
    "policy",
    "foundation",
    "bootstrap",
    "dependency_scan",
    "secret_scan",
    "security_scan",
)
IOS_CHECK_ORDER = ("ios_tests",)
PROFILES = {"python": PYTHON_CHECK_ORDER, "ios": IOS_CHECK_ORDER}
ALLOWED_UNAVAILABLE = {"python": frozenset({"policy"}), "ios": frozenset()}
REMEDIATIONS = {
    "unit_tests": "inspect_unit_test_failure",
    "policy": "review_branch_commit_policy",
    "foundation": "inspect_foundation_metadata",
    "bootstrap": "inspect_astra_bootstrap_checks",
    "dependency_scan": "inspect_project_dependency_metadata",
    "secret_scan": "remove_secret_and_rotate_if_exposed",
    "security_scan": "review_workflow_security_policy",
    "ios_tests": "inspect_ios_scaffold_tests",
}
CHECK_ORDER = PYTHON_CHECK_ORDER
CHECKS = frozenset(PYTHON_CHECK_ORDER)
STATUSES = frozenset({"passed", "failed", "unavailable", "cancelled"})
REMOTE_STATUSES = frozenset({"DEFERRED_QUOTA", "EXECUTED_HOSTED"})
PROVENANCE_KEYS = frozenset({"repository", "workflow", "job", "matrix", "artifact"})
SAFE_TOKEN = re.compile(r"[A-Za-z0-9_.-]{1,128}")
SAFE_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}")
MAX_REPORT_BYTES = 16 * 1024
ZERO_SHA = "0" * 40
DEFAULT_PROVENANCE = {
    "repository": "local/unknown",
    "workflow": "unknown",
    "job": "unknown",
    "matrix": "unknown",
    "artifact": "unknown",
}


def normalize_report(
    checks: list[Mapping[str, object]], *, profile: str = "python", commit: str = ZERO_SHA, run_id: str = "0",
    remote_status: str = "DEFERRED_QUOTA", provenance: Mapping[str, str] | None = None,
) -> dict[str, object]:
    expected = PROFILES.get(profile)
    if expected is None or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("invalid report provenance")
    if not isinstance(run_id, str) or not run_id.isdigit() or len(run_id) > 32:
        raise ValueError("invalid report run ID")
    if remote_status not in REMOTE_STATUSES:
        raise ValueError("invalid remote status")
    provenance_values = dict(DEFAULT_PROVENANCE if provenance is None else provenance)
    if set(provenance_values) != PROVENANCE_KEYS:
        raise ValueError("invalid report provenance fields")
    if (
        not isinstance(provenance_values["repository"], str)
        or not SAFE_REPOSITORY.fullmatch(provenance_values["repository"])
        or any(
            not isinstance(provenance_values[key], str) or not SAFE_TOKEN.fullmatch(provenance_values[key])
            for key in PROVENANCE_KEYS - {"repository"}
        )
    ):
        raise ValueError("invalid report provenance fields")
    if not isinstance(checks, list) or len(checks) != len(expected):
        raise ValueError("invalid report checks")
    normalized = []
    seen = set()
    for check in checks:
        if not isinstance(check, Mapping) or set(check) != {"name", "status", "exit_code"}:
            raise ValueError("invalid check schema")
        name, status, exit_code = check["name"], check["status"], check["exit_code"]
        if not isinstance(name, str) or name not in expected or name in seen:
            raise ValueError("invalid check name")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError("invalid check status")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int) or not 0 <= exit_code <= 255:
            raise ValueError("invalid check exit code")
        if (
            (status == "passed" and exit_code != 0)
            or (status == "failed" and exit_code == 0)
            or (status == "unavailable" and (exit_code != 0 or name not in ALLOWED_UNAVAILABLE[profile]))
            or (status == "cancelled" and exit_code != 0)
        ):
            raise ValueError("status and exit code disagree")
        seen.add(name)
        normalized.append({"name": name, "status": status, "exit_code": exit_code})
    if seen != set(expected):
        raise ValueError("incomplete report checks")
    return {
        "schema_version": 1,
        "profile": profile,
        "commit": commit.lower(),
        "run_id": run_id,
        "remote_ci": remote_status,
        "provenance": provenance_values,
        "checks": normalized,
        "remediation": {name: REMEDIATIONS[name] for name in expected},
    }


def _safe_target(path: Path, root: Path) -> Path:
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("report root must be an absolute non-symlink directory")
    root_resolved = root.resolve()
    if path.is_absolute():
        candidate = path
    else:
        if any(part in ("", ".", "..") for part in path.parts):
            raise ValueError("report path must be relative without traversal")
        candidate = root / path
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError("report path contains a symlink")
    resolved = candidate.resolve(strict=False)
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError("report path escapes report root")
    if candidate.exists() or candidate.is_symlink():
        raise ValueError("report already exists")
    return candidate


def _open_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise ValueError("report parent must be an existing directory")
    fd = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            if part in ("", ".", ".."):
                raise ValueError("invalid report parent")
            child = os.open(part, flags | nofollow, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except Exception:
        os.close(fd)
        raise


def _write_report(
    path: Path,
    checks: list[Mapping[str, object]],
    root: Path,
    *,
    profile: str = "python",
    commit: str = ZERO_SHA,
    run_id: str = "0",
    remote_status: str = "DEFERRED_QUOTA",
    provenance: Mapping[str, str] | None = None,
) -> Path:
    normalized = normalize_report(
        checks, profile=profile, commit=commit, run_id=run_id,
        remote_status=remote_status, provenance=provenance,
    )
    target = _safe_target(Path(path), Path(root))
    encoded = (json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_REPORT_BYTES:
        raise ValueError("report exceeds size limit")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    parent_fd = _open_directory(target.parent)
    try:
        fd = os.open(target.name, flags, 0o600, dir_fd=parent_fd)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded)
        except OSError as exc:
            raise ValueError("report write failed") from exc
    except OSError as exc:
        raise ValueError("report path unavailable") from exc
    finally:
        os.close(parent_fd)
    return target


def write_report(
    path: Path,
    checks: list[Mapping[str, object]],
    *,
    root: Path,
    profile: str = "python",
    commit: str = ZERO_SHA,
    run_id: str = "0",
    remote_status: str = "DEFERRED_QUOTA",
    provenance: Mapping[str, str] | None = None,
) -> Path:
    """Write only beneath the explicitly selected artifact directory."""
    return _write_report(
        Path(path), checks, Path(root), profile=profile, commit=commit, run_id=run_id,
        remote_status=remote_status, provenance=provenance,
    )


def main(argv: list[str] | None = None) -> int:
    values = list(argv if argv is not None else sys.argv[1:])
    flags = ("--profile", "--root", "--output", "--commit", "--run-id", "--remote-status", "--repository", "--workflow", "--job", "--matrix", "--artifact")
    if len(values) < 23 or any(values.count(flag) != 1 for flag in flags):
        return 2
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--profile", choices=tuple(PROFILES))
    parser.add_argument("--root")
    parser.add_argument("--output")
    parser.add_argument("--commit")
    parser.add_argument("--run-id")
    parser.add_argument("--remote-status", choices=tuple(REMOTE_STATUSES))
    parser.add_argument("--repository")
    parser.add_argument("--workflow")
    parser.add_argument("--job")
    parser.add_argument("--matrix")
    parser.add_argument("--artifact")
    parser.add_argument("checks", nargs="+")
    try:
        parsed = parser.parse_args(values)
        profile, root, output = parsed.profile, Path(parsed.root), Path(parsed.output)
        commit, run_id = parsed.commit, parsed.run_id
        provenance = {
            "repository": parsed.repository,
            "workflow": parsed.workflow,
            "job": parsed.job,
            "matrix": parsed.matrix,
            "artifact": parsed.artifact,
        }
        checks = []
        for item in parsed.checks:
            if item.count("=") != 1:
                raise ValueError("invalid check argument")
            name, code = item.split("=", 1)
            if code == "SKIPPED":
                checks.append({"name": name, "status": "unavailable", "exit_code": 0})
                continue
            if code == "CANCELLED":
                checks.append({"name": name, "status": "cancelled", "exit_code": 0})
                continue
            exit_code = int(code)
            if not 0 <= exit_code <= 255:
                raise ValueError("invalid exit code")
            checks.append({"name": name, "status": "passed" if exit_code == 0 else "failed", "exit_code": exit_code})
        normalize_report(
            checks, profile=profile, commit=commit, run_id=run_id,
            remote_status=parsed.remote_status, provenance=provenance,
        )
        write_report(
            output, checks, root=root, profile=profile, commit=commit, run_id=run_id,
            remote_status=parsed.remote_status, provenance=provenance,
        )
    except (ValueError, OSError, argparse.ArgumentError, SystemExit):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
