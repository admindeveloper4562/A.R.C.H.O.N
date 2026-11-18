"""SHA-bound cache for reproducible deterministic test evidence.

Only successful deterministic test results are reusable.  Independent QC and
release checks must still execute their own required validation.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


CACHE_VERSION = 1
_VOLATILE_CONTEXT = {"run_id", "attempt", "candidate_sha"}
_SKIP_DIRS = {".git", ".serena", "__pycache__", ".pytest_cache", ".mypy_cache",
              ".ruff_cache", "build", "dist", "node_modules", "ci-artifacts"}
_LOCK_NAMES = {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "poetry.lock",
               "uv.lock", "Pipfile.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
_ENV_NAMES = ("CI", "LANG", "LC_ALL", "NODE_ENV", "OMP_NUM_THREADS", "PYTHONHASHSEED", "TZ")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head(worktree: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=10, check=False,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and len(value) == 40 else None


def _tree_sha(worktree: Path) -> str | None:
    """Hash every regular candidate file, including untracked files."""
    digest = hashlib.sha256()
    try:
        for root, directories, files in os.walk(worktree, followlinks=False):
            directories[:] = sorted(name for name in directories if name not in _SKIP_DIRS)
            for name in sorted(files):
                path = Path(root) / name
                if path.is_symlink() or not path.is_file():
                    return None
                relative = path.relative_to(worktree).as_posix().encode()
                digest.update(relative + b"\0")
                digest.update(_sha256_file(path).encode())
    except (OSError, ValueError):
        return None
    return digest.hexdigest()


def _dependency_lock_sha(worktree: Path) -> str:
    digest = hashlib.sha256()
    found = False
    for root, directories, files in os.walk(worktree, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in _SKIP_DIRS)
        for name in sorted(files):
            if name not in _LOCK_NAMES:
                continue
            path = Path(root) / name
            if path.is_symlink() or not path.is_file():
                continue
            found = True
            digest.update(path.relative_to(worktree).as_posix().encode() + b"\0")
            digest.update(_sha256_file(path).encode())
    return digest.hexdigest() if found else "none"


def _security_policy_sha(worktree: Path) -> str:
    path = worktree / "SECURITY.md"
    return _sha256_file(path) if path.is_file() and not path.is_symlink() else "missing"


def _runner_version(command: list[str], context: dict[str, Any]) -> str | None:
    supplied = context.get("runner_version")
    if isinstance(supplied, str) and supplied:
        return supplied[:200]
    if command and Path(command[0]).name.startswith("python"):
        return f"{platform.python_implementation()}-{platform.python_version()}"
    if command and Path(command[0]).name == "node":
        result = subprocess.run([command[0], "--version"], capture_output=True, text=True,
                                timeout=5, check=False)
        value = result.stdout.strip()
        return value[:200] if result.returncode == 0 and value else None
    return None


def build_cache_material(worktree: Path, image_digest: str, command: list[str],
                         context: dict[str, Any] | None = None) -> dict[str, Any] | None:
    context = context or {}
    source_commit_sha = _git_head(worktree)
    tree_sha = _tree_sha(worktree)
    runner_version = _runner_version(command, context)
    if not source_commit_sha or not tree_sha or not image_digest or not runner_version:
        return None
    stable_context = {key: context[key] for key in sorted(context)
                      if key not in _VOLATILE_CONTEXT and key not in {"secret", "token", "password"}}
    material = {
        "version": CACHE_VERSION,
        "source_commit_sha": source_commit_sha,
        "source_tree_sha": tree_sha,
        "dependency_lock_sha": _dependency_lock_sha(worktree),
        "python_environment": sys.executable,
        "docker_image_digest": image_digest,
        "command": list(command),
        "test_config": stable_context,
        "environment": {name: os.environ.get(name, "") for name in _ENV_NAMES},
        "security_policy_sha": _security_policy_sha(worktree),
        "external_capability": context.get("external_capability", "none"),
        "toolchain_identity": context.get("toolchain_identity", image_digest),
        "fixture_sha": context.get("fixture_sha", "none"),
        "platform": {"system": platform.system(), "release": platform.release(),
                     "machine": platform.machine()},
        "runner_version": runner_version,
    }
    return material


def cache_key(material: dict[str, Any]) -> str:
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return _sha256_bytes(encoded)


class EvidenceCache:
    def __init__(self, directory: Path):
        self.directory = directory

    def load(self, key: str) -> dict[str, Any] | None:
        path = self.directory / f"{key}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if data.get("version") != CACHE_VERSION or data.get("key") != key:
            return None
        receipt = data.get("receipt")
        if not isinstance(receipt, dict) or receipt.get("passed") is not True:
            return None
        allowed = {"passed", "exit_code", "sandbox", "tests_detected"}
        if not set(receipt) <= allowed or not isinstance(receipt.get("exit_code"), int):
            return None
        return dict(receipt)

    def store(self, key: str, receipt: dict[str, Any]) -> None:
        if receipt.get("passed") is not True:
            return
        payload = {"version": CACHE_VERSION, "key": key,
                   "receipt": {name: receipt[name] for name in
                               ("passed", "exit_code", "sandbox", "tests_detected") if name in receipt}}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        path = self.directory / f"{key}.json"
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        temporary.write_text(raw + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(path)


__all__ = ["EvidenceCache", "build_cache_material", "cache_key"]
