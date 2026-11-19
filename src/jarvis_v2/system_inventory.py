"""Read-only, bounded Linux host and filesystem metadata inventory."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from typing import Any


class InventoryError(RuntimeError):
    """Raised when a host inventory cannot be collected safely."""


_VIRTUAL_ROOTS = frozenset({"proc", "sys", "dev", "run"})
_TOOLS = (
    "python3",
    "git",
    "node",
    "npm",
    "rustc",
    "cargo",
    "docker",
    "podman",
    "ollama",
    "blender",
    "ffmpeg",
    "lspci",
    "findmnt",
    "lsblk",
)
CommandRunner = Callable[[list[str]], tuple[int, str, str]]


def _command(args: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout[:16_384], result.stderr[:2_048]


def _command_summary(args: list[str], runner: CommandRunner) -> dict[str, Any]:
    code, stdout, stderr = runner(args)
    return {
        "command": args,
        "exit_code": code,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
    }


def _optional_command_summary(args: list[str], runner: CommandRunner) -> dict[str, Any]:
    executable = shutil.which(args[0])
    if executable is None:
        return {"available": False, "command": args}
    result = _command_summary(args, runner)
    result["available"] = True
    result["path"] = executable
    return result


def _metadata(path: Path, info: os.stat_result, kind: str) -> dict[str, Any]:
    return {
        "path": str(path),
        "type": kind,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "uid": info.st_uid,
        "gid": info.st_gid,
        "mode": stat.S_IMODE(info.st_mode),
        "filesystem_id": info.st_dev,
    }


def scan_filesystem(root: Path = Path("/"), *, max_entries: int = 10_000) -> dict[str, Any]:
    """Collect metadata without reading file contents or crossing mounts."""
    if type(max_entries) is not int or not 1 <= max_entries <= 100_000:
        raise InventoryError("filesystem entry bound is outside the supported range")
    root = root.expanduser().resolve()
    try:
        root_info = root.stat()
    except OSError as exc:
        raise InventoryError(f"inventory root is unavailable: {root}") from exc
    root_device = root_info.st_dev
    pending = [root]
    entries: list[dict[str, Any]] = [_metadata(root, root_info, "directory")]
    denied: list[str] = []
    skipped_mounts: list[str] = []
    skipped_virtual: list[str] = []
    truncated = False

    while pending and len(entries) < max_entries:
        current = pending.pop(0)
        try:
            children = sorted(os.scandir(current), key=lambda item: item.name)
        except PermissionError:
            denied.append(str(current))
            continue
        except OSError:
            denied.append(str(current))
            continue
        for child in children:
            if len(entries) >= max_entries:
                truncated = True
                break
            path = Path(child.path)
            try:
                info = child.stat(follow_symlinks=False)
            except PermissionError:
                denied.append(str(path))
                continue
            except OSError:
                denied.append(str(path))
                continue
            if child.is_symlink():
                kind = "symlink"
            elif stat.S_ISDIR(info.st_mode):
                kind = "directory"
            elif stat.S_ISREG(info.st_mode):
                kind = "file"
            else:
                kind = "other"
            entries.append(_metadata(path, info, kind))
            if kind != "directory":
                continue
            if current == root and child.name in _VIRTUAL_ROOTS:
                skipped_virtual.append(str(path))
                continue
            if info.st_dev != root_device:
                skipped_mounts.append(str(path))
                continue
            pending.append(path)
    if pending:
        truncated = True
    return {
        "root": str(root),
        "entries": entries,
        "coverage": {
            "scanned_entries": len(entries),
            "max_entries": max_entries,
            "truncated": truncated,
            "permission_denied": sorted(set(denied)),
            "skipped_mounts": sorted(set(skipped_mounts)),
            "skipped_virtual_filesystems": sorted(set(skipped_virtual)),
            "symlink_recursion": False,
        },
    }


def _hardware(runner: CommandRunner) -> dict[str, Any]:
    return {
        "uname": _command_summary(["uname", "-srvm"], runner),
        "cpu": _command_summary(["lscpu", "-J"], runner),
        "memory": _command_summary(["free", "-b"], runner),
        "storage": _command_summary(["lsblk", "-J", "-o", "NAME,FSTYPE,SIZE,FSAVAIL,FSUSE%,MOUNTPOINTS"], runner),
        "mounts": _command_summary(["findmnt", "-J"], runner),
        "gpu": _command_summary(["lspci"], runner),
    }


def _software(runner: CommandRunner) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for tool in _TOOLS:
        path = shutil.which(tool)
        if not path:
            continue
        result[tool] = {
            "path": path,
            "version": _command_summary([tool, "--version"], runner),
        }
    return result


def _runtime_capabilities(runner: CommandRunner) -> dict[str, Any]:
    return {
        "model_runtimes": {
            "ollama_models": _optional_command_summary(["ollama", "list"], runner),
        },
        "acceleration": {
            "nvidia_smi": _optional_command_summary(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader",
                ],
                runner,
            ),
            "vainfo": _optional_command_summary(["vainfo"], runner),
            "rocminfo": _optional_command_summary(["rocminfo"], runner),
            "clinfo": _optional_command_summary(["clinfo"], runner),
        },
    }


def collect_inventory(
    *,
    root: Path = Path("/"),
    max_entries: int = 10_000,
    runner: CommandRunner = _command,
) -> dict[str, Any]:
    """Collect safe host facts and bounded filesystem metadata."""
    filesystem = scan_filesystem(root, max_entries=max_entries)
    try:
        usage = shutil.disk_usage(root)
        filesystem["capacity"] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
        }
    except OSError as exc:
        filesystem["capacity_error"] = str(exc)
    payload = {
        "schema_version": 1,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "hardware": _hardware(runner),
        "software": _software(runner),
        "runtime_capabilities": _runtime_capabilities(runner),
        "filesystem": filesystem,
        "environment": {
            "user": os.getuid(),
            "groups": sorted(os.getgroups()),
            "path_entries": len(os.environ.get("PATH", "").split(os.pathsep)),
        },
    }
    payload["inventory_sha256"] = inventory_digest(payload)
    return payload


def inventory_digest(inventory: Mapping[str, Any]) -> str:
    """Hash stable inventory content while ignoring collection time and digest."""
    stable = json.loads(json.dumps(inventory, sort_keys=True))
    stable.pop("collected_at", None)
    stable.pop("inventory_sha256", None)
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compare_inventories(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    """Return bounded metadata changes between two inventories."""
    old = {
        item["path"]: item
        for item in previous.get("filesystem", {}).get("entries", [])
        if isinstance(item, Mapping) and "path" in item
    }
    new = {
        item["path"]: item
        for item in current.get("filesystem", {}).get("entries", [])
        if isinstance(item, Mapping) and "path" in item
    }
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(path for path in set(old) & set(new) if old[path] != new[path])
    return {
        "added": added[:200],
        "removed": removed[:200],
        "changed": changed[:200],
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
    }


def write_inventory(path: Path, inventory: Mapping[str, Any]) -> None:
    """Persist private inventory metadata with restrictive directory/file modes."""
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


__all__ = [
    "InventoryError",
    "collect_inventory",
    "compare_inventories",
    "inventory_digest",
    "scan_filesystem",
    "write_inventory",
]
