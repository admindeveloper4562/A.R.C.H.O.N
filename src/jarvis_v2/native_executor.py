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
from typing import Any

from .automation.queue_api import QueueEnvelope
from .backend.module_manifest import (
    ACTIVE_MODULE_KEYS,
    EXPECTED_DEPENDENCIES,
    ALLOWED_PERMISSION_SCOPES,
    MODULE_IDS,
    ModuleManifest,
    validate_module_manifest,
)
from .health import HealthError, collect_health


SUPPORTED_OPERATIONS = (
    "module_health",
    "runtime_health",
    "inventory_digest",
)


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

    @staticmethod
    def capabilities() -> tuple[str, ...]:
        """Return the operations safe for the built-in service executor."""
        return SUPPORTED_OPERATIONS

    def __call__(self, item: QueueEnvelope) -> Mapping[str, Any]:
        if not isinstance(item, QueueEnvelope):
            raise NativeExecutorError("queue_envelope_required")
        operation = _operation(item.payload.get("operation"))
        if operation == "module_health":
            return self._module_health(item)
        if operation == "runtime_health":
            return self._runtime_health(item)
        if operation == "inventory_digest":
            return self._inventory_digest(item)
        raise NativeExecutorError("unsupported_native_operation")

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
        coverage = inventory.get("filesystem", {}).get("coverage", {})
        if not isinstance(coverage, Mapping):
            coverage = {}
        return {
            "operation": "inventory_digest",
            "status": "ready",
            "inventory_sha256": sha256(raw).hexdigest(),
            "scanned_entries": coverage.get("scanned_entries", 0),
            "truncated": bool(coverage.get("truncated", False)),
        }


__all__ = ["NativeControlPlaneExecutor", "NativeExecutorError", "SUPPORTED_OPERATIONS"]
