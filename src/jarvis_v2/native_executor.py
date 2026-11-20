"""Fail-closed native control-plane task execution.

Only deterministic, read-only operations are built in. Domain handlers that
can affect files, services, providers, devices, finance, or communications
must be supplied through a separately reviewed executor.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any

from .automation.queue_api import QueueEnvelope
from .backend.backup import BackupError, BackupManager
from .backend.module_manifest import (
    ACTIVE_MODULE_KEYS,
    EXPECTED_DEPENDENCIES,
    ALLOWED_PERMISSION_SCOPES,
    MODULE_IDS,
    ModuleManifest,
    validate_module_manifest,
)
from .health import HealthError, collect_health
from .sda.handoff import HandoffEvidence


SUPPORTED_OPERATIONS = (
    "native_capabilities",
    "module_health",
    "runtime_health",
    "inventory_digest",
    "queue_status",
    "database_inspect",
    "sda_handoff_status",
    "guardian_readiness",
)

REJECTED_OPERATION_REASONS = {
    "task_submission": "separate_authenticated queue admission required",
    "filesystem_write": "reviewed bounded handler and owner approval required",
    "service_control": "external trusted watchdog required",
    "network_request": "module-specific connector and authorization required",
    "provider_call": "configured provider gateway and authorization required",
    "finance_effect": "paper-only or owner-approved domain handler required",
    "communication_send": "explicit owner-approved connector required",
    "model_inference": "model gateway is not a native executor capability",
    "rollback_apply": "trusted watchdog and verified rollback gate required",
}

_DATABASES = {
    "atlas": "atlas.sqlite3",
    "runtime": "runtime.sqlite3",
    "code_index": "code_index.sqlite3",
}


class NativeExecutorError(RuntimeError):
    """Raised when a queued operation is not safe for the built-in executor."""


def _operation(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 64
        or any(not (char.isalnum() or char in "_.:-") for char in value)
    ):
        raise NativeExecutorError("invalid_native_operation")
    return value


def _module_manifest(module: str) -> ModuleManifest:
    if module not in ACTIVE_MODULE_KEYS:
        raise NativeExecutorError("unknown_native_module")
    return validate_module_manifest(
        ModuleManifest(
            module_id=next(
                module_id for module_id, key in MODULE_IDS.items()
                if key == module
            ),
            key=module,
            dependencies=EXPECTED_DEPENDENCIES[module],
            health_endpoint_label=module,
            permission_scopes=ALLOWED_PERMISSION_SCOPES[module],
        )
    )


class NativeControlPlaneExecutor:
    """Execute only bounded local observations from the native queue.

    This class deliberately does not import model clients, subprocess
    launchers, external connectors, or legacy Astra modules.
    """

    def __init__(self, *, repository: str | Path, state_dir: str | Path) -> None:
        self.repository = Path(repository).expanduser().resolve(strict=True)
        self.state_dir = Path(state_dir).expanduser().resolve(strict=True)
        if self.state_dir.is_symlink() or not self.state_dir.is_dir():
            raise NativeExecutorError("native_state_directory_unavailable")
        if self.state_dir.stat().st_mode & 0o077:
            raise NativeExecutorError("native_state_directory_permissions")

    @staticmethod
    def capabilities() -> tuple[str, ...]:
        """Return the operations safe for the built-in service executor."""
        return SUPPORTED_OPERATIONS

    @staticmethod
    def rejected_capabilities() -> Mapping[str, str]:
        """Return side-effect classes deliberately unavailable to this executor."""
        return dict(REJECTED_OPERATION_REASONS)

    def __call__(self, item: QueueEnvelope) -> Mapping[str, Any]:
        if not isinstance(item, QueueEnvelope):
            raise NativeExecutorError("queue_envelope_required")
        operation = _operation(item.payload.get("operation"))
        if operation == "native_capabilities":
            return self._native_capabilities(item)
        if operation == "module_health":
            return self._module_health(item)
        if operation == "runtime_health":
            return self._runtime_health(item)
        if operation == "inventory_digest":
            return self._inventory_digest(item)
        if operation == "queue_status":
            return self._queue_status(item)
        if operation == "database_inspect":
            return self._database_inspect(item)
        if operation == "sda_handoff_status":
            return self._sda_handoff_status(item)
        if operation == "guardian_readiness":
            return self._guardian_readiness(item)
        raise NativeExecutorError("unsupported_native_operation")

    def _native_capabilities(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "core":
            raise NativeExecutorError("native_capabilities_requires_core")
        return {
            "operation": "native_capabilities",
            "status": "ready",
            "read_only_operations": list(SUPPORTED_OPERATIONS),
            "rejected_operations": dict(REJECTED_OPERATION_REASONS),
            "domain_effect_handlers": "not_configured",
            "owner_approval_transport": "not_configured",
            "trusted_watchdog": "not_configured",
        }

    def _module_health(self, item: QueueEnvelope) -> dict[str, Any]:
        target = item.payload.get("module", item.module)
        if target != item.module or not isinstance(target, str):
            raise NativeExecutorError("module_target_mismatch")
        manifest = _module_manifest(target)
        return {
            "operation": "module_health",
            "status": "ready",
            "module": manifest.key,
            "module_id": manifest.module_id,
            "dependencies": list(manifest.dependencies),
            "permission_scopes": sorted(manifest.permission_scopes),
        }

    def _runtime_health(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "core":
            raise NativeExecutorError("runtime_health_requires_core")
        try:
            health = collect_health(state_dir=self.state_dir, repository=self.repository)
        except HealthError as exc:
            raise NativeExecutorError("native_health_unavailable") from exc
        return {
            "operation": "runtime_health",
            "status": health["status"],
            "mode": health.get("mode", "legacy"),
            "git": health.get("git", {}).get("checkout_sha", ""),
            "queue_total": health.get("queue", {}).get("total", 0),
        }

    def _inventory_digest(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "backend":
            raise NativeExecutorError("inventory_digest_requires_backend")
        path = self.state_dir / "host_inventory.json"
        if path.is_symlink() or not path.is_file():
            raise NativeExecutorError("host_inventory_unavailable")
        try:
            raw = path.read_bytes()
            inventory = json.loads(raw)
        except (OSError, UnicodeError, ValueError) as exc:
            raise NativeExecutorError("host_inventory_unreadable") from exc
        if not isinstance(inventory, Mapping):
            raise NativeExecutorError("host_inventory_invalid")
        filesystem = inventory.get("filesystem")
        if not isinstance(filesystem, Mapping):
            raise NativeExecutorError("host_inventory_invalid")
        coverage = filesystem.get("coverage", {})
        if not isinstance(coverage, Mapping):
            coverage = {}
        return {
            "operation": "inventory_digest",
            "status": "ready",
            "inventory_sha256": sha256(raw).hexdigest(),
            "scanned_entries": coverage.get("scanned_entries", 0),
            "truncated": bool(coverage.get("truncated", False)),
        }

    def _queue_status(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "core":
            raise NativeExecutorError("queue_status_requires_core")
        path = self.state_dir / "atlas.sqlite3"
        if path.is_symlink() or not path.is_file():
            raise NativeExecutorError("native_queue_unavailable")
        try:
            with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
                db.execute("PRAGMA query_only=ON")
                integrity = str(db.execute("PRAGMA integrity_check").fetchone()[0])
                if integrity != "ok":
                    raise NativeExecutorError("native_queue_integrity_failed")
                if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                    raise NativeExecutorError("native_queue_foreign_key_failed")
                counts = {
                    state: count
                    for state, count in db.execute(
                        "select state,count(*) from tasks group by state order by state"
                    )
                }
                control = db.execute(
                    "select state,reason,updated_at from core_controls where control_id=1"
                ).fetchone()
        except (OSError, sqlite3.Error) as exc:
            raise NativeExecutorError("native_queue_unreadable") from exc
        if control is None:
            raise NativeExecutorError("native_queue_control_missing")
        return {
            "operation": "queue_status",
            "status": "ready",
            "integrity": integrity,
            "task_counts": counts,
            "control": {
                "state": control[0],
                "reason": control[1],
                "updated_at": control[2],
            },
        }

    def _database_inspect(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "backend":
            raise NativeExecutorError("database_inspect_requires_backend")
        name = item.payload.get("database", "runtime")
        if not isinstance(name, str) or name not in _DATABASES:
            raise NativeExecutorError("database_name_not_allowed")
        path = self.state_dir / _DATABASES[name]
        if path.is_symlink():
            raise NativeExecutorError("database_symlink_disallowed")
        try:
            state = BackupManager().inspect(path)
        except (BackupError, OSError) as exc:
            raise NativeExecutorError("database_inspection_failed") from exc
        return {
            "operation": "database_inspect",
            "status": "ready",
            "database": name,
            "integrity": state["integrity"],
            "schema_version": state["schema_version"],
            "journal_mode": state["journal_mode"],
            "size_bytes": state["size_bytes"],
            "sha256": state["sha256"],
            "state_sha256": state["state_sha256"],
        }

    def _sda_handoff_status(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "sda":
            raise NativeExecutorError("sda_handoff_status_requires_sda")
        report = HandoffEvidence().report()
        return {
            "operation": "sda_handoff_status",
            "status": "blocked" if report["missing"] else "shadow",
            "missing": list(report["missing"]),
            "owner_approval_required": report["owner_approval_required"],
            "shadow_mode": report["shadow_mode"],
            "claims_live_task_ownership": report["claims_live_task_ownership"],
            "actual_cutover_performed": report["actual_cutover_performed"],
        }

    def _guardian_readiness(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "guardian":
            raise NativeExecutorError("guardian_readiness_requires_guardian")
        controls = tuple(
            marker for marker in ("STOP", "PAUSE", "PAUSED_QUOTA")
            if (self.state_dir / "controls" / marker).exists()
        )
        service_candidate = self.repository / "infra/systemd/archon.service"
        return {
            "operation": "guardian_readiness",
            "status": "blocked",
            "reason": "external_watchdog_identity_not_configured",
            "control_markers": list(controls),
            "native_service_candidate": service_candidate.is_file(),
            "trusted_watchdog": False,
            "route_switched": False,
            "owner_approval_required": True,
        }


__all__ = ["NativeControlPlaneExecutor", "NativeExecutorError", "SUPPORTED_OPERATIONS"]
