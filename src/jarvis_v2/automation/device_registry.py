"""Authenticated device boundary for the local Windows-agent protocol."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import re

from jarvis_v2.backend.windows_agent import (
    CapabilityLease,
    Heartbeat,
    LocalAgentJob,
    NodeManifest,
    WindowsAgentError,
    WindowsAgentRegistry,
)


MIN_KEY_BYTES = 32
MAX_KEY_BYTES = 128
MAX_PROOF_BYTES = 4_096
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class DeviceAuthError(ValueError):
    """Raised when device identity or authentication cannot be verified."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise DeviceAuthError(f"invalid {label}")
    return value


def _key(value: bytes | bytearray, label: str = "key") -> bytes:
    if isinstance(value, bytearray):
        value = bytes(value)
    if not isinstance(value, bytes) or not MIN_KEY_BYTES <= len(value) <= MAX_KEY_BYTES:
        raise DeviceAuthError(f"{label} must be a bounded byte key")
    return value


def _proof(value: bytes | str) -> bytes:
    if isinstance(value, str):
        try:
            value = bytes.fromhex(value)
        except ValueError as exc:
            raise DeviceAuthError("proof is not hexadecimal") from exc
    if not isinstance(value, bytes) or len(value) != hashlib.sha256().digest_size:
        raise DeviceAuthError("proof is invalid")
    return value


def _message(value: str | bytes) -> bytes:
    if isinstance(value, str):
        value = value.encode("utf-8")
    if not isinstance(value, bytes) or not value or len(value) > MAX_PROOF_BYTES:
        raise DeviceAuthError("authentication message is invalid")
    return value


@dataclass(frozen=True)
class DeviceRecord:
    device_id: str
    key_id: str
    key_sha256: str
    generation: int = 1
    status: str = "active"

    def __post_init__(self) -> None:
        _identifier(self.device_id, "device id")
        _identifier(self.key_id, "key id")
        if not re.fullmatch(r"[0-9a-f]{64}", self.key_sha256):
            raise DeviceAuthError("key digest is invalid")
        if type(self.generation) is not int or self.generation < 1:
            raise DeviceAuthError("key generation is invalid")
        if self.status not in {"active", "revoked"}:
            raise DeviceAuthError("device status is invalid")


class AuthenticatedDeviceRegistry:
    """Authenticate device operations before delegating to the job registry."""

    def __init__(self, agents: WindowsAgentRegistry | None = None) -> None:
        self.agents = agents or WindowsAgentRegistry()
        self._devices: dict[str, DeviceRecord] = {}
        self._keys: dict[str, bytes] = {}

    @staticmethod
    def claim_message(job_id: str) -> str:
        return f"claim:{_identifier(job_id, 'job id')}"

    @staticmethod
    def complete_message(job_id: str, lease_id: str, result_sha256: str) -> str:
        return f"complete:{_identifier(job_id, 'job id')}:{_identifier(lease_id, 'lease id')}:{result_sha256}"

    @staticmethod
    def rotation_message(device_id: str, current_key_id: str, next_key_id: str, next_key_sha256: str) -> str:
        _identifier(device_id, "device id")
        _identifier(current_key_id, "key id")
        _identifier(next_key_id, "key id")
        if not re.fullmatch(r"[0-9a-f]{64}", next_key_sha256):
            raise DeviceAuthError("next key digest is invalid")
        return f"rotate:{device_id}:{current_key_id}:{next_key_id}:{next_key_sha256}"

    @staticmethod
    def make_proof(key_material: bytes | bytearray, message: str | bytes) -> str:
        return hmac.new(_key(key_material), _message(message), hashlib.sha256).hexdigest()

    def register(self, manifest: NodeManifest, key_material: bytes | bytearray, *, key_id: str = "key-1") -> DeviceRecord:
        if not isinstance(manifest, NodeManifest):
            raise DeviceAuthError("node manifest is required")
        key_id = _identifier(key_id, "key id")
        material = _key(key_material)
        digest = hashlib.sha256(material).hexdigest()
        current = self._devices.get(manifest.node_id)
        if current is not None:
            if current.status == "active" and current.key_id == key_id and current.key_sha256 == digest:
                return current
            raise DeviceAuthError("device registration conflict")
        try:
            self.agents.register_node(manifest)
        except WindowsAgentError as exc:
            raise DeviceAuthError("device registration rejected") from exc
        record = DeviceRecord(manifest.node_id, key_id, digest)
        self._devices[manifest.node_id] = record
        self._keys[manifest.node_id] = material
        return record

    register_device = register

    def authenticate(self, device_id: str, key_id: str, message: str | bytes, proof: bytes | str) -> DeviceRecord:
        device_id = _identifier(device_id, "device id")
        key_id = _identifier(key_id, "key id")
        record = self._devices.get(device_id)
        if record is None or record.status != "active" or record.key_id != key_id:
            raise DeviceAuthError("device credential is not active")
        expected = hmac.new(self._keys[device_id], _message(message), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _proof(proof)):
            raise DeviceAuthError("device proof is invalid")
        return record

    def rotate_key(
        self,
        device_id: str,
        current_key_id: str,
        next_key_id: str,
        next_key_material: bytes | bytearray,
        proof: bytes | str,
    ) -> DeviceRecord:
        device_id = _identifier(device_id, "device id")
        current = self._devices.get(device_id)
        if current is None or current.key_id != current_key_id or current.status != "active":
            raise DeviceAuthError("current device credential is not active")
        next_key_id = _identifier(next_key_id, "key id")
        if next_key_id == current_key_id:
            raise DeviceAuthError("next key must be different")
        material = _key(next_key_material, "next key")
        digest = hashlib.sha256(material).hexdigest()
        message = self.rotation_message(device_id, current_key_id, next_key_id, digest)
        self.authenticate(device_id, current_key_id, message, proof)
        record = DeviceRecord(device_id, next_key_id, digest, current.generation + 1)
        self._keys[device_id] = material
        self._devices[device_id] = record
        return record

    rotate = rotate_key

    def revoke(self, device_id: str) -> DeviceRecord:
        device_id = _identifier(device_id, "device id")
        current = self._devices.get(device_id)
        if current is None:
            raise DeviceAuthError("device is not registered")
        record = DeviceRecord(device_id, current.key_id, current.key_sha256, current.generation, "revoked")
        self._devices[device_id] = record
        self._keys.pop(device_id, None)
        return record

    def submit(self, job: LocalAgentJob) -> LocalAgentJob:
        return self.agents.submit(job)

    def heartbeat(
        self,
        device_id: str,
        key_id: str,
        proof: bytes | str,
        *,
        status: str = "online",
        observed_at: float | None = None,
        cpu_percent: float | None = None,
        memory_bytes: int | None = None,
        free_vram_bytes: int | None = None,
    ) -> Heartbeat:
        message = f"heartbeat:{device_id}:{status}:{observed_at}" if observed_at is not None else f"heartbeat:{device_id}:{status}"
        self.authenticate(device_id, key_id, message, proof)
        try:
            return self.agents.heartbeat(
                device_id,
                status=status,
                observed_at=observed_at,
                cpu_percent=cpu_percent,
                memory_bytes=memory_bytes,
                free_vram_bytes=free_vram_bytes,
            )
        except WindowsAgentError as exc:
            raise DeviceAuthError("device heartbeat rejected") from exc

    def claim(self, job_id: str, device_id: str, key_id: str, proof: bytes | str, *, ttl_seconds: int = 60) -> CapabilityLease:
        self.authenticate(device_id, key_id, self.claim_message(job_id), proof)
        try:
            return self.agents.lease(job_id, device_id, ttl_seconds=ttl_seconds)
        except WindowsAgentError as exc:
            raise DeviceAuthError("device cannot claim job") from exc

    def complete(self, job_id: str, device_id: str, key_id: str, proof: bytes | str, lease_id: str, *, result_sha256: str, error_code: str = "") -> dict[str, object]:
        self.authenticate(device_id, key_id, self.complete_message(job_id, lease_id, result_sha256), proof)
        try:
            return self.agents.complete(job_id, device_id, lease_id, result_sha256=result_sha256, error_code=error_code)
        except WindowsAgentError as exc:
            raise DeviceAuthError("device completion rejected") from exc

    def snapshot(self, device_id: str) -> dict[str, object]:
        device_id = _identifier(device_id, "device id")
        try:
            record = self._devices[device_id]
        except KeyError as exc:
            raise DeviceAuthError("device is not registered") from exc
        return {"device": asdict(record), "node": self.agents.node_snapshot(device_id)}


DeviceRegistry = AuthenticatedDeviceRegistry

__all__ = ["AuthenticatedDeviceRegistry", "DeviceAuthError", "DeviceRecord", "DeviceRegistry"]
