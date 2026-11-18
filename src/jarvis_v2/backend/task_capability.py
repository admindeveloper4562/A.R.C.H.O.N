"""Linux task capability manifests and path-bound request validation."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import re

from .windows_agent import LOCAL_OPERATIONS


_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_ALLOWED_PATHS = 32


class TaskCapabilityError(ValueError):
    """Raised when a local task exceeds its capability manifest."""


def _paths(values: Iterable[str | Path]) -> tuple[Path, ...]:
    if isinstance(values, (str, bytes)):
        raise TaskCapabilityError("allowed paths must be a collection")
    try:
        items = tuple(values)
    except TypeError as exc:
        raise TaskCapabilityError("allowed paths must be a collection") from exc
    if not items or len(items) > MAX_ALLOWED_PATHS:
        raise TaskCapabilityError("allowed paths are outside the bounded policy")
    result: list[Path] = []
    for item in items:
        if not isinstance(item, (str, Path)):
            raise TaskCapabilityError("allowed path is invalid")
        path = Path(item)
        if not path.is_absolute():
            raise TaskCapabilityError("allowed path must be absolute")
        try:
            resolved = path.resolve(strict=False)
        except OSError as exc:
            raise TaskCapabilityError("allowed path cannot be resolved") from exc
        if resolved not in result:
            result.append(resolved)
    return tuple(result)


@dataclass(frozen=True)
class TaskCapabilityManifest:
    """Immutable Linux allowlist for one local task execution boundary."""

    operations: frozenset[str]
    allowed_paths: tuple[Path, ...]
    platform: str = "linux"

    def __post_init__(self) -> None:
        if self.platform != "linux":
            raise TaskCapabilityError("task capability manifest is Linux-only")
        if not isinstance(self.operations, frozenset) or not self.operations:
            raise TaskCapabilityError("operations must be a non-empty frozenset")
        if not self.operations <= LOCAL_OPERATIONS:
            raise TaskCapabilityError("operation is not allowlisted")
        object.__setattr__(self, "allowed_paths", _paths(self.allowed_paths))

    @classmethod
    def create(cls, operations: Iterable[str], allowed_paths: Iterable[str | Path]) -> "TaskCapabilityManifest":
        if isinstance(operations, (str, bytes)):
            raise TaskCapabilityError("operations must be a collection")
        try:
            normalized = frozenset(operations)
        except TypeError as exc:
            raise TaskCapabilityError("operations must be a collection") from exc
        return cls(normalized, _paths(allowed_paths))

    def as_dict(self) -> dict[str, object]:
        return {
            "platform": self.platform,
            "operations": sorted(self.operations),
            "allowed_paths": [str(path) for path in self.allowed_paths],
        }

    def validate_path(self, path: str | Path) -> Path:
        if not isinstance(path, (str, Path)):
            raise TaskCapabilityError("task path is invalid")
        candidate = Path(path)
        if not candidate.is_absolute():
            raise TaskCapabilityError("task path must be absolute")
        try:
            resolved = candidate.resolve(strict=False)
        except OSError as exc:
            raise TaskCapabilityError("task path cannot be resolved") from exc
        if not any(resolved == root or root in resolved.parents for root in self.allowed_paths):
            raise TaskCapabilityError("task path is outside the capability sandbox")
        return resolved

    def validate_operation(self, operation: str) -> str:
        if not isinstance(operation, str) or operation not in self.operations:
            raise TaskCapabilityError("task operation is not granted")
        return operation


@dataclass(frozen=True)
class ValidatedTaskRequest:
    """Digest-only request after manifest and input validation."""

    operation: str
    input_sha256: str
    path: Path | None


def validate_task_request(
    manifest: TaskCapabilityManifest,
    operation: str,
    input_sha256: str,
    *,
    path: str | Path | None = None,
) -> ValidatedTaskRequest:
    if not isinstance(manifest, TaskCapabilityManifest):
        raise TaskCapabilityError("task capability manifest is required")
    if not isinstance(input_sha256, str) or not _SHA256.fullmatch(input_sha256):
        raise TaskCapabilityError("input digest is invalid")
    checked_path = manifest.validate_path(path) if path is not None else None
    return ValidatedTaskRequest(manifest.validate_operation(operation), input_sha256.lower(), checked_path)


__all__ = [
    "MAX_ALLOWED_PATHS",
    "TaskCapabilityError",
    "TaskCapabilityManifest",
    "ValidatedTaskRequest",
    "validate_task_request",
]
