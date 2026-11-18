"""Validate the bounded legacy-to-v2 contract map without executing legacy code.

This module is a migration-time adapter.  It returns provenance and target
metadata only; staged files under ``migration/imported`` are never imported.
"""
from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any


_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_AREAS = ("core", "backend", "runtime")

SOURCE_TARGETS = {
    "core": (
        "migration/imported/core/tasks.py",
        "migration/imported/core/worker.py",
    ),
    "backend": (
        "migration/imported/backend/storage.py",
        "migration/imported/backend/permissions.py",
        "migration/imported/backend/router.py",
        "migration/imported/backend/colibri.py",
    ),
    "runtime": (
        "migration/imported/runtime/server.py",
        "migration/imported/runtime/voice.py",
        "migration/imported/runtime/inventory.py",
        "migration/imported/runtime/email.py",
        "migration/imported/runtime/calendar.py",
    ),
}

V2_TARGETS = {
    "core": (
        "src/jarvis_v2/core/queue.py",
        "src/jarvis_v2/core/dispatch.py",
        "src/jarvis_v2/core/dependency.py",
    ),
    "backend": (
        "src/jarvis_v2/backend/storage.py",
        "src/jarvis_v2/backend/authorization.py",
        "src/jarvis_v2/backend/routing.py",
    ),
    "runtime": (
        "src/jarvis_v2/runtime/service.py",
        "src/jarvis_v2/runtime/speech.py",
        "src/jarvis_v2/runtime/calendar.py",
        "src/jarvis_v2/runtime/email.py",
    ),
}


class MigrationCompatibilityError(ValueError):
    """Raised when a pinned migration contract cannot be verified."""


@dataclass(frozen=True)
class ContractRecord:
    """A metadata-only source/target contract record."""

    area: str
    source_target: str
    source_ref: str
    source_commit: str
    source_blob: str
    source_sha256: str
    size: int

    def as_dict(self) -> dict[str, object]:
        return {
            "area": self.area,
            "source_target": self.source_target,
            "source_ref": self.source_ref,
            "source_commit": self.source_commit,
            "source_blob": self.source_blob,
            "source_sha256": self.source_sha256,
            "size": self.size,
        }


def _within(root: Path, value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or "\\" in value or ".." in path.parts or not value:
        raise MigrationCompatibilityError(f"invalid {label}")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise MigrationCompatibilityError(f"{label} escapes repository") from exc
    return resolved


class LegacyContractAdapter:
    """Read and validate the Core/Backend/Runtime migration contract."""

    def __init__(self, repository: str | Path, import_log: str | Path | None = None) -> None:
        self.repository = Path(repository).resolve()
        if not self.repository.is_dir():
            raise MigrationCompatibilityError("repository is unavailable")
        self.import_log = (self.repository / "migration/provenance/import-log.json").resolve()
        if import_log is not None:
            self.import_log = _within(self.repository, str(import_log), "import log")
        if not self.import_log.is_file() or self.import_log.is_symlink():
            raise MigrationCompatibilityError("import log is unavailable")

    def _records(self) -> list[ContractRecord]:
        try:
            document = json.loads(self.import_log.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MigrationCompatibilityError("import log is unreadable") from exc
        entries = document.get("entries") if isinstance(document, dict) else None
        if document.get("schema") != "jarvis-v2.legacy-provenance/1" or not isinstance(entries, list):
            raise MigrationCompatibilityError("unsupported import log")
        expected = {path for paths in SOURCE_TARGETS.values() for path in paths}
        records: list[ContractRecord] = []
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise MigrationCompatibilityError("invalid provenance entry")
            target = entry.get("target")
            area = entry.get("area")
            if area not in _AREAS or target not in expected or target in seen:
                continue
            if target not in SOURCE_TARGETS[area]:
                raise MigrationCompatibilityError("provenance area does not match target")
            source_commit = entry.get("source_commit")
            source_blob = entry.get("source_blob")
            source_sha256 = entry.get("sha256")
            size = entry.get("size")
            if (not isinstance(source_commit, str) or not _SHA1.fullmatch(source_commit)
                    or not isinstance(source_blob, str) or not re.fullmatch(r"[0-9a-f]{40}", source_blob)
                    or not isinstance(source_sha256, str) or not _SHA256.fullmatch(source_sha256)
                    or type(size) is not int or size < 0):
                raise MigrationCompatibilityError("invalid provenance digest")
            records.append(ContractRecord(
                area=area,
                source_target=target,
                source_ref=str(entry.get("source_ref", "")),
                source_commit=source_commit,
                source_blob=source_blob,
                source_sha256=source_sha256,
                size=size,
            ))
            seen.add(target)
        if seen != expected:
            raise MigrationCompatibilityError("Core/Backend/Runtime provenance is incomplete")
        return records

    def snapshot(self) -> dict[str, Any]:
        """Return bounded metadata after verifying staged bytes and v2 targets."""
        records = self._records()
        for record in records:
            staged = _within(self.repository, record.source_target, "staged target")
            if staged.is_symlink() or not staged.is_file():
                raise MigrationCompatibilityError("staged target is not a regular file")
            content = staged.read_bytes()
            if len(content) != record.size or hashlib.sha256(content).hexdigest() != record.source_sha256:
                raise MigrationCompatibilityError("staged target digest mismatch")
            if staged.suffix == ".py":
                try:
                    ast.parse(content.decode("utf-8"), filename=str(staged))
                except (UnicodeDecodeError, SyntaxError) as exc:
                    raise MigrationCompatibilityError("staged Python syntax is invalid") from exc
        targets: dict[str, list[str]] = {}
        for area, paths in V2_TARGETS.items():
            targets[area] = []
            for path in paths:
                target = _within(self.repository, path, "v2 target")
                if target.is_symlink() or not target.is_file():
                    raise MigrationCompatibilityError("v2 target is unavailable")
                targets[area].append(path)
        by_area = {area: [record.as_dict() for record in records if record.area == area] for area in _AREAS}
        return {
            "schema": "archon.migration-compatibility/1",
            "source_log_sha256": hashlib.sha256(self.import_log.read_bytes()).hexdigest(),
            "contracts": by_area,
            "v2_targets": targets,
            "execution": "metadata_and_ast_only",
        }
