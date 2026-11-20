"""Fail-closed native control-plane task execution.

Only deterministic, read-only operations are built in. Domain handlers that
can affect files, services, providers, devices, finance, or communications
must be supplied through a separately reviewed executor.
"""
from __future__ import annotations

from base64 import b64decode
from collections.abc import Mapping
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile
import time
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .automation.queue_api import QueueEnvelope
from .backend.backup import BackupError, BackupManager
from .backend.effects import EffectJournal, EffectJournalError
from .backend.task_capability import TaskCapabilityError, TaskCapabilityManifest
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
    "task_submission": "signed local queue admission is separate from executor operations",
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
_WRITE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_KEY_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
_APPROVAL_FIELDS = frozenset({
    "schema", "approval_id", "key_id", "task_id", "operation", "target",
    "content_sha256", "expires_at", "decision",
})
_MAX_WRITE_BYTES = 64 * 1024
_MAX_KEY_STORE_BYTES = 16 * 1024
_MAX_APPROVAL_TTL_SECONDS = 24 * 60 * 60


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


def _load_owner_keys(path: str | Path | None) -> dict[str, bytes]:
    if path is None:
        return {}
    descriptor = -1
    try:
        descriptor = os.open(
            Path(path).expanduser(),
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
        )
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or stat.S_IMODE(details.st_mode) & 0o022:
            raise NativeExecutorError("owner_key_store_permissions")
        raw = bytearray()
        while len(raw) <= _MAX_KEY_STORE_BYTES:
            chunk = os.read(descriptor, min(4096, _MAX_KEY_STORE_BYTES + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        if not raw or len(raw) > _MAX_KEY_STORE_BYTES:
            raise NativeExecutorError("owner_key_store_invalid")
        document = json.loads(raw)
    except NativeExecutorError:
        raise
    except (OSError, UnicodeError, ValueError) as exc:
        raise NativeExecutorError("owner_key_store_invalid") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if (
        not isinstance(document, dict)
        or set(document) != {"schema", "keys"}
        or type(document["schema"]) is not int
        or document["schema"] != 1
        or not isinstance(document["keys"], dict)
        or not 1 <= len(document["keys"]) <= 32
    ):
        raise NativeExecutorError("owner_key_store_invalid")
    keys: dict[str, bytes] = {}
    for key_id, encoded in document["keys"].items():
        if not isinstance(key_id, str) or not _KEY_NAME.fullmatch(key_id) or not isinstance(encoded, str):
            raise NativeExecutorError("owner_key_store_invalid")
        try:
            public_key = b64decode(encoded, validate=True)
        except ValueError as exc:
            raise NativeExecutorError("owner_key_store_invalid") from exc
        if len(public_key) != 32:
            raise NativeExecutorError("owner_key_store_invalid")
        keys[key_id] = public_key
    return keys


def _verify_signed_approval(
    approval: Any,
    owner_keys: Mapping[str, bytes],
    *,
    task_id: str,
    target: str,
    content_sha256: str,
    operation: str = "workspace_write",
) -> str:
    if not isinstance(approval, Mapping) or set(approval) != _APPROVAL_FIELDS | {"signature"}:
        raise NativeExecutorError("owner_approval_invalid")
    now = int(time.time())
    if (
        type(approval["schema"]) is not int
        or approval["schema"] != 1
        or approval["decision"] != "APPROVE"
        or approval["operation"] != operation
        or approval["task_id"] != task_id
        or approval["target"] != target
        or approval["content_sha256"] != content_sha256
        or not isinstance(approval["approval_id"], str)
        or not _KEY_NAME.fullmatch(approval["approval_id"])
        or not isinstance(approval["key_id"], str)
        or not _KEY_NAME.fullmatch(approval["key_id"])
        or type(approval["expires_at"]) is not int
        or not now < approval["expires_at"] <= now + _MAX_APPROVAL_TTL_SECONDS
    ):
        raise NativeExecutorError("owner_approval_scope_invalid")
    public_key = owner_keys.get(approval["key_id"])
    signature_text = approval["signature"]
    if public_key is None or not isinstance(signature_text, str) or len(signature_text) > 128:
        raise NativeExecutorError("owner_approval_signature_invalid")
    try:
        signature = b64decode(signature_text, validate=True)
        claims = {name: approval[name] for name in sorted(_APPROVAL_FIELDS)}
        message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, message)
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise NativeExecutorError("owner_approval_signature_invalid") from exc
    return approval["approval_id"]


def _workspace_file_sha256(path: Path) -> str | None:
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
        )
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise NativeExecutorError("workspace_target_unavailable") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise NativeExecutorError("workspace_target_not_regular")
        digest = sha256()
        total = 0
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            while chunk := stream.read(8192):
                total += len(chunk)
                if total > _MAX_WRITE_BYTES:
                    raise NativeExecutorError("workspace_target_too_large")
                digest.update(chunk)
        return digest.hexdigest()
    except OSError as exc:
        raise NativeExecutorError("workspace_target_unreadable") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _write_new_workspace_file(root: Path, target: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=".archon-effect-", dir=root)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary_name, target, follow_symlinks=False)
        except FileExistsError:
            pass
        directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


class NativeControlPlaneExecutor:
    """Execute only bounded local observations from the native queue.

    This class deliberately does not import model clients, subprocess
    launchers, external connectors, or legacy Astra modules.
    """

    def __init__(
        self,
        *,
        repository: str | Path,
        state_dir: str | Path,
        workspace_root: str | Path | None = None,
        owner_keys: Mapping[str, bytes] | None = None,
    ) -> None:
        self.repository = Path(repository).expanduser().resolve(strict=True)
        state_path = Path(state_dir).expanduser()
        if state_path.is_symlink() or not state_path.is_dir():
            raise NativeExecutorError("native_state_directory_unavailable")
        state_details = state_path.stat()
        if state_details.st_uid != os.geteuid() or stat.S_IMODE(state_details.st_mode) & 0o077:
            raise NativeExecutorError("native_state_directory_permissions")
        self.state_dir = state_path.resolve(strict=True)
        self.workspace_root = None
        if workspace_root is not None:
            workspace = Path(workspace_root).expanduser()
            if workspace.is_symlink() or not workspace.is_dir():
                raise NativeExecutorError("workspace_unavailable")
            workspace_details = workspace.stat()
            if workspace_details.st_uid != os.geteuid() or stat.S_IMODE(workspace_details.st_mode) & 0o077:
                raise NativeExecutorError("workspace_permissions")
            self.workspace_root = workspace.resolve(strict=True)
        if owner_keys is None:
            owner_keys = {}
        if not isinstance(owner_keys, Mapping):
            raise NativeExecutorError("owner_key_store_invalid")
        self.owner_keys: dict[str, bytes] = {}
        for key_id, public_key in owner_keys.items():
            if (
                not isinstance(key_id, str)
                or not _KEY_NAME.fullmatch(key_id)
                or not isinstance(public_key, bytes)
                or len(public_key) != 32
            ):
                raise NativeExecutorError("owner_key_store_invalid")
            self.owner_keys[key_id] = public_key

    def capabilities(self) -> tuple[str, ...]:
        """Return operations enabled by the configured native executor."""
        if self.workspace_root is not None and self.owner_keys:
            return (*SUPPORTED_OPERATIONS, "workspace_write")
        return SUPPORTED_OPERATIONS

    def rejected_capabilities(self) -> Mapping[str, str]:
        """Return side-effect classes unavailable to this executor."""
        reasons = dict(REJECTED_OPERATION_REASONS)
        if self.workspace_root is not None and self.owner_keys:
            reasons["filesystem_write"] = "only exact signed workspace_write effects are enabled"
        else:
            reasons["filesystem_write"] = "workspace_write requires a private workspace and owner key store"
        return reasons

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
        if operation == "workspace_write":
            return self._workspace_write(item)
        raise NativeExecutorError("unsupported_native_operation")

    def _native_capabilities(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "core":
            raise NativeExecutorError("native_capabilities_requires_core")
        enabled_write = self.workspace_root is not None and bool(self.owner_keys)
        return {
            "operation": "native_capabilities",
            "status": "ready",
            "read_only_operations": list(SUPPORTED_OPERATIONS),
            "enabled_operations": list(self.capabilities()),
            "rejected_operations": dict(self.rejected_capabilities()),
            "domain_effect_handlers": "workspace_write" if enabled_write else "not_configured",
            "owner_approval_transport": "ed25519_key_store" if self.owner_keys else "not_configured",
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


    def _workspace_write(self, item: QueueEnvelope) -> dict[str, Any]:
        if item.module != "core":
            raise NativeExecutorError("workspace_write_requires_core")
        if self.workspace_root is None or not self.owner_keys:
            raise NativeExecutorError("workspace_write_not_configured")
        target_name = item.payload.get("target")
        text = item.payload.get("content")
        if not isinstance(target_name, str) or not _WRITE_NAME.fullmatch(target_name):
            raise NativeExecutorError("workspace_target_invalid")
        if not isinstance(text, str) or "\x00" in text:
            raise NativeExecutorError("workspace_content_invalid")
        content = text.encode("utf-8")
        if len(content) > _MAX_WRITE_BYTES:
            raise NativeExecutorError("workspace_content_too_large")
        target = self.workspace_root / target_name
        try:
            checked_target = TaskCapabilityManifest.create(
                ("workspace_write",), (self.workspace_root,)
            ).validate_path(target)
        except TaskCapabilityError as exc:
            raise NativeExecutorError("workspace_target_outside_capability") from exc
        if checked_target != target:
            raise NativeExecutorError("workspace_target_symlink_disallowed")
        content_digest = sha256(content).hexdigest()
        approval_id = _verify_signed_approval(
            item.payload.get("approval"),
            self.owner_keys,
            task_id=item.task_id,
            target=target_name,
            content_sha256=content_digest,
        )
        effect_path = self.state_dir / "effects.sqlite3"
        if effect_path.is_symlink() or (effect_path.exists() and not effect_path.is_file()):
            raise NativeExecutorError("effect_journal_unavailable")
        journal_exists = effect_path.exists()
        if journal_exists and stat.S_IMODE(effect_path.stat().st_mode) & 0o077:
            raise NativeExecutorError("effect_journal_permissions")
        effect_id = sha256(item.task_id.encode("utf-8")).hexdigest()
        request = {
            "approval_id": approval_id,
            "content_sha256": content_digest,
            "size_bytes": len(content),
        }
        result = {
            "operation": "workspace_write",
            "target": target_name,
            "sha256": content_digest,
            "bytes": len(content),
            "approval_id": approval_id,
        }
        try:
            with EffectJournal(effect_path) as journal:
                if not journal_exists:
                    os.chmod(effect_path, 0o600)
                prepared = journal.prepare(
                    effect_id,
                    item.task_id,
                    operation="workspace_write",
                    target=target_name,
                    request=request,
                )
                existing_digest = _workspace_file_sha256(target)
                if not prepared["execution_permitted"]:
                    status = prepared["status"]
                    if status == "completed":
                        if existing_digest != content_digest:
                            raise NativeExecutorError("workspace_effect_requires_reconciliation")
                        return journal.complete(effect_id, result)["result"]
                    if status != "needs_reconciliation":
                        raise NativeExecutorError("workspace_effect_requires_reconciliation")
                    if existing_digest is not None and existing_digest != content_digest:
                        raise NativeExecutorError("workspace_target_conflict")
                elif existing_digest is not None and existing_digest != content_digest:
                    raise NativeExecutorError("workspace_target_conflict")
                if existing_digest is None:
                    _write_new_workspace_file(self.workspace_root, target, content)
                    existing_digest = _workspace_file_sha256(target)
                if existing_digest != content_digest:
                    raise NativeExecutorError("workspace_effect_verification_failed")
                return journal.complete(effect_id, result)["result"]
        except NativeExecutorError:
            raise
        except (EffectJournalError, OSError, sqlite3.Error) as exc:
            raise NativeExecutorError("workspace_effect_failed") from exc


__all__ = ["NativeControlPlaneExecutor", "NativeExecutorError", "SUPPORTED_OPERATIONS"]
