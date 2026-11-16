"""Bounded last-known-good artifact selection and staging rollback."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from typing import Any

from .release import inspect_canary


MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_FAILED_CANARY = frozenset({"failed", "unhealthy"})


class RollbackError(ValueError):
    """Raised when a rollback cannot be proven safe."""


@dataclass(frozen=True)
class RollbackPlan:
    """A verified, bounded artifact restore plan."""

    root: Path
    candidate_artifact: str
    last_known_good_artifact: str
    rollback_target: str
    candidate_sha: str
    candidate_artifact_sha256: str
    last_known_good_artifact_sha256: str
    state_checkpoint: str | None = None
    state_checkpoint_sha256: str | None = None
    canary_status: str = ""

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["root"] = str(self.root)
        return result


def select_last_known_good(
    manifest_path: str | Path, *, canary_status: str
) -> RollbackPlan:
    """Verify a failed canary and return a read-only last-known-good plan."""
    status = _status(canary_status)
    if status not in _FAILED_CANARY:
        raise RollbackError("rollback requires a failed or unhealthy canary")

    manifest = _regular(Path(manifest_path), "release manifest")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RollbackError("release manifest is unreadable") from exc

    candidate_sha = data.get("candidate_sha")
    if not isinstance(candidate_sha, str) or not _GIT_SHA.fullmatch(candidate_sha):
        raise RollbackError("invalid candidate SHA")

    root = manifest.parent.resolve(strict=True)
    candidate_rel = _relative(data.get("artifact"), "candidate artifact")
    previous_rel = _relative(
        data.get("previous_healthy_artifact", data.get("last_known_good_artifact")),
        "last-known-good artifact",
    )
    target_rel = _relative(data.get("rollback_target"), "rollback target")
    candidate = _safe_file(root, candidate_rel, "candidate artifact")

    canary = inspect_canary(manifest)
    if not canary["eligible_for_canary"]:
        raise RollbackError("canary evidence is not eligible for rollback")

    previous = _safe_file(root, previous_rel, "last-known-good artifact")
    target = _safe_file(root, target_rel, "rollback target")
    if target == previous or target == candidate:
        raise RollbackError("rollback target must be separate from source artifacts")

    candidate_digest = _digest(candidate)
    declared_candidate = data.get("sha256")
    if candidate_digest != declared_candidate:
        raise RollbackError("candidate artifact checksum mismatch")
    previous_digest = data.get("previous_healthy_artifact_sha256")
    if not isinstance(previous_digest, str) or not _DIGEST.fullmatch(previous_digest):
        raise RollbackError("invalid last-known-good artifact digest")
    if _digest(previous) != previous_digest:
        raise RollbackError("last-known-good artifact checksum mismatch")
    if _digest(target) != candidate_digest:
        raise RollbackError("rollback target does not match the failed candidate")

    state_rel = data.get("state_checkpoint")
    state = None
    state_digest = None
    if state_rel is not None:
        state_rel = _relative(state_rel, "state checkpoint")
        state = _safe_file(root, state_rel, "state checkpoint")
        if state in {candidate, previous, target}:
            raise RollbackError("state checkpoint must be separate from artifacts")
        state_digest = _digest(state)

    return RollbackPlan(
        root=root,
        candidate_artifact=candidate_rel,
        last_known_good_artifact=previous_rel,
        rollback_target=target_rel,
        candidate_sha=candidate_sha,
        candidate_artifact_sha256=candidate_digest,
        last_known_good_artifact_sha256=previous_digest,
        state_checkpoint=state_rel,
        state_checkpoint_sha256=state_digest,
        canary_status=status,
    )


def restore_last_known_good(plan: RollbackPlan) -> dict[str, Any]:
    """Atomically restore a verified artifact without changing checkpoint state."""
    if not isinstance(plan, RollbackPlan):
        raise RollbackError("rollback plan is invalid")
    root = _root(plan.root)
    previous = _safe_file(root, plan.last_known_good_artifact, "last-known-good artifact")
    target = _safe_file(root, plan.rollback_target, "rollback target")
    if _digest(previous) != plan.last_known_good_artifact_sha256:
        raise RollbackError("last-known-good artifact changed after planning")
    if _digest(target) != plan.candidate_artifact_sha256:
        raise RollbackError("rollback target changed after planning")

    state_before = _checkpoint_digest(root, plan)
    mode = stat.S_IMODE(target.stat().st_mode)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{target.name}.rollback-", dir=target.parent, delete=False
        ) as temporary:
            temporary_name = Path(temporary.name)
            with previous.open("rb") as source:
                shutil.copyfileobj(source, temporary, length=1024 * 1024)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, target)
        _fsync_directory(target.parent)
    except (OSError, shutil.Error) as exc:
        raise RollbackError("last-known-good restore failed") from exc
    finally:
        if temporary_name is not None:
            try:
                temporary_name.unlink(missing_ok=True)
            except OSError:
                pass

    state_after = _checkpoint_digest(root, plan)
    if state_after != state_before:
        raise RollbackError("state checkpoint changed during rollback")
    return {
        "restored": True,
        "rollback_target": plan.rollback_target,
        "restored_sha256": _digest(target),
        "candidate_preserved": _digest(_safe_file(root, plan.candidate_artifact, "candidate artifact"))
        == plan.candidate_artifact_sha256,
        "state_preserved": True,
        "route_switched": False,
        "writes": [plan.rollback_target],
    }


def _status(value: str) -> str:
    if not isinstance(value, str) or value not in _FAILED_CANARY | {"healthy", "unknown"}:
        raise RollbackError("canary status is invalid")
    return value


def _relative(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise RollbackError(f"{label} path is missing")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or len(value) > 512:
        raise RollbackError(f"{label} path is unsafe")
    return path.as_posix()


def _safe_file(root: Path, relative: str, label: str) -> Path:
    raw = root / relative
    resolved = raw.resolve(strict=False)
    if not resolved.is_relative_to(root) or raw.is_symlink():
        raise RollbackError(f"{label} is outside the rollback root")
    try:
        info = resolved.stat()
    except OSError as exc:
        raise RollbackError(f"{label} is unavailable") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARTIFACT_BYTES:
        raise RollbackError(f"{label} is not a bounded regular file")
    return resolved


def _regular(path: Path, label: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise RollbackError(f"{label} is unavailable")
    return path


def _root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise RollbackError("rollback root is unavailable")
    return path.resolve(strict=True)


def _digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_digest(root: Path, plan: RollbackPlan) -> str | None:
    if plan.state_checkpoint is None:
        return None
    checkpoint = _safe_file(root, plan.state_checkpoint, "state checkpoint")
    return _digest(checkpoint)


def _fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


__all__ = ["RollbackError", "RollbackPlan", "select_last_known_good", "restore_last_known_good"]
