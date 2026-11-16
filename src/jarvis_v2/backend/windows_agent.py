"""Bounded Windows local-agent protocol and capability lease registry."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
import re
import time
from uuid import uuid4


MAX_HEARTBEAT_AGE_SECONDS = 120
MAX_JOB_TTL_SECONDS = 3_600
MAX_CONCURRENCY = 8
LOCAL_OPERATIONS = frozenset({"summarize", "extract", "index", "classify", "code_check"})
DATA_SCOPES = frozenset({"public_metadata", "internal_metadata", "scoped_private"})
NODE_STATUSES = frozenset({"online", "draining", "offline"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class WindowsAgentError(ValueError):
    """Raised when a local-agent identity, job or lease is invalid."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise WindowsAgentError(f"invalid {label}")
    return value


def _model(value: str) -> str:
    if not isinstance(value, str) or not _MODEL.fullmatch(value):
        raise WindowsAgentError("invalid model")
    return value


def _digest(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise WindowsAgentError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class NodeManifest:
    """Identity and capabilities advertised by one separate Windows agent."""

    node_id: str
    agent_version: str
    model: str
    capabilities: frozenset[str]
    data_scopes: frozenset[str]
    max_concurrency: int = 1
    platform: str = "windows"

    def __post_init__(self) -> None:
        _identifier(self.node_id, "node id")
        _model(self.agent_version)
        _model(self.model)
        if not isinstance(self.capabilities, frozenset) or not self.capabilities <= LOCAL_OPERATIONS:
            raise WindowsAgentError("node capabilities are invalid")
        if not self.capabilities:
            raise WindowsAgentError("node capabilities must not be empty")
        if not isinstance(self.data_scopes, frozenset) or not self.data_scopes <= DATA_SCOPES:
            raise WindowsAgentError("node data scopes are invalid")
        if not self.data_scopes:
            raise WindowsAgentError("node data scopes must not be empty")
        if type(self.max_concurrency) is not int or not 1 <= self.max_concurrency <= MAX_CONCURRENCY:
            raise WindowsAgentError("node concurrency is outside the bounded policy")
        if self.platform != "windows":
            raise WindowsAgentError("local-agent platform must be windows")


@dataclass(frozen=True)
class Heartbeat:
    node_id: str
    observed_at: float
    status: str
    cpu_percent: float | None = None
    memory_bytes: int | None = None
    free_vram_bytes: int | None = None

    def __post_init__(self) -> None:
        _identifier(self.node_id, "node id")
        if type(self.observed_at) not in (int, float) or self.observed_at < 0:
            raise WindowsAgentError("heartbeat time is invalid")
        if self.status not in NODE_STATUSES:
            raise WindowsAgentError("heartbeat status is invalid")
        if self.cpu_percent is not None and (
            type(self.cpu_percent) not in (int, float) or not 0 <= self.cpu_percent <= 100
        ):
            raise WindowsAgentError("CPU sample is invalid")
        for value, label in ((self.memory_bytes, "memory sample"), (self.free_vram_bytes, "VRAM sample")):
            if value is not None and (type(value) is not int or value < 0):
                raise WindowsAgentError(f"{label} is invalid")


@dataclass(frozen=True)
class LocalAgentJob:
    """Digest-only bounded work description; raw input never enters the ledger."""

    job_id: str
    idempotency_key: str
    operation: str
    input_sha256: str
    required_scope: str
    deadline_at: float
    task_id: str = ""
    requested_model: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.job_id, "job id")
        _identifier(self.idempotency_key, "idempotency key")
        if self.operation not in LOCAL_OPERATIONS:
            raise WindowsAgentError("job operation is not allowlisted")
        _digest(self.input_sha256, "input digest")
        if self.required_scope not in DATA_SCOPES:
            raise WindowsAgentError("job data scope is invalid")
        if type(self.deadline_at) not in (int, float) or self.deadline_at <= 0:
            raise WindowsAgentError("job deadline is invalid")
        if self.task_id:
            _identifier(self.task_id, "task id")
        if self.requested_model is not None:
            _model(self.requested_model)


@dataclass(frozen=True)
class NodeRoute:
    status: str
    node_id: str | None
    model: str | None
    reason: str


@dataclass(frozen=True)
class CapabilityLease:
    lease_id: str
    job_id: str
    node_id: str
    expires_at: float


class WindowsAgentRegistry:
    """Register nodes, route bounded jobs and fence one active lease per job."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] | None = None,
        heartbeat_age_seconds: int = MAX_HEARTBEAT_AGE_SECONDS,
    ) -> None:
        if type(heartbeat_age_seconds) is not int or heartbeat_age_seconds < 1:
            raise WindowsAgentError("heartbeat age must be positive")
        self._clock = clock or time.time
        self.heartbeat_age_seconds = heartbeat_age_seconds
        self._nodes: dict[str, tuple[NodeManifest, Heartbeat]] = {}
        self._jobs: dict[str, tuple[LocalAgentJob, str]] = {}
        self._jobs_by_key: dict[str, str] = {}
        self._leases: dict[str, CapabilityLease] = {}
        self._results: dict[str, dict[str, object]] = {}

    def register_node(self, manifest: NodeManifest) -> NodeManifest:
        if not isinstance(manifest, NodeManifest):
            raise WindowsAgentError("node manifest is required")
        current = self._nodes.get(manifest.node_id)
        if current is not None and current[0] != manifest:
            raise WindowsAgentError("node identity conflict")
        if current is None:
            self._nodes[manifest.node_id] = (manifest, Heartbeat(manifest.node_id, 0, "offline"))
        return manifest

    def heartbeat(
        self,
        node_id: str,
        *,
        status: str = "online",
        observed_at: float | None = None,
        cpu_percent: float | None = None,
        memory_bytes: int | None = None,
        free_vram_bytes: int | None = None,
    ) -> Heartbeat:
        node_id = _identifier(node_id, "node id")
        if node_id not in self._nodes:
            raise WindowsAgentError("node is not registered")
        observed_at = self._clock() if observed_at is None else observed_at
        beat = Heartbeat(node_id, observed_at, status, cpu_percent, memory_bytes, free_vram_bytes)
        if beat.observed_at > self._clock() + 1:
            raise WindowsAgentError("heartbeat is from the future")
        manifest, _ = self._nodes[node_id]
        self._nodes[node_id] = (manifest, beat)
        return beat

    def route(
        self,
        operation: str,
        required_scope: str,
        *,
        node_id: str | None = None,
        requested_model: str | None = None,
    ) -> NodeRoute:
        if operation not in LOCAL_OPERATIONS:
            raise WindowsAgentError("job operation is not allowlisted")
        if required_scope not in DATA_SCOPES:
            raise WindowsAgentError("job data scope is invalid")
        if requested_model is not None:
            _model(requested_model)
        self.reconcile()
        candidates = sorted(self._nodes.values(), key=lambda item: item[0].node_id)
        if node_id is not None:
            node_id = _identifier(node_id, "node id")
            candidates = [item for item in candidates if item[0].node_id == node_id]
        for manifest, beat in candidates:
            if beat.status != "online" or self._clock() - beat.observed_at > self.heartbeat_age_seconds:
                continue
            if requested_model is not None and manifest.model != requested_model:
                continue
            if operation not in manifest.capabilities or required_scope not in manifest.data_scopes:
                continue
            if self._active_leases(manifest.node_id) >= manifest.max_concurrency:
                continue
            return NodeRoute("routed", manifest.node_id, manifest.model, "capabilities_satisfied")
        reason = "requested_node_unavailable" if node_id is not None else "no_compatible_node"
        return NodeRoute("blocked", None, None, reason)

    def submit(self, job: LocalAgentJob) -> LocalAgentJob:
        if not isinstance(job, LocalAgentJob):
            raise WindowsAgentError("local-agent job is required")
        existing_id = self._jobs_by_key.get(job.idempotency_key)
        if existing_id is not None:
            existing = self._jobs[existing_id][0]
            if existing != job:
                raise WindowsAgentError("idempotency key conflict")
            return existing
        if job.job_id in self._jobs:
            raise WindowsAgentError("job id conflict")
        self._jobs[job.job_id] = (job, "queued")
        self._jobs_by_key[job.idempotency_key] = job.job_id
        return job

    def lease(self, job_id: str, node_id: str, *, ttl_seconds: int = 60) -> CapabilityLease:
        job_id = _identifier(job_id, "job id")
        node_id = _identifier(node_id, "node id")
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_JOB_TTL_SECONDS:
            raise WindowsAgentError("lease TTL is outside the bounded policy")
        self.reconcile()
        try:
            job, status = self._jobs[job_id]
        except KeyError as exc:
            raise WindowsAgentError("job is not registered") from exc
        if status != "queued":
            raise WindowsAgentError("job is not queued")
        if job.deadline_at <= self._clock():
            self._jobs[job_id] = (job, "expired")
            raise WindowsAgentError("job deadline has passed")
        route = self.route(job.operation, job.required_scope, node_id=node_id, requested_model=job.requested_model)
        if route.status != "routed" or route.node_id is None:
            raise WindowsAgentError("node route is unavailable")
        lease = CapabilityLease(uuid4().hex, job_id, node_id, min(self._clock() + ttl_seconds, job.deadline_at))
        self._leases[job_id] = lease
        self._jobs[job_id] = (job, "leased")
        return lease

    def complete(
        self,
        job_id: str,
        node_id: str,
        lease_id: str,
        *,
        result_sha256: str,
        error_code: str = "",
    ) -> dict[str, object]:
        job_id = _identifier(job_id, "job id")
        node_id = _identifier(node_id, "node id")
        lease_id = _identifier(lease_id, "lease id")
        _digest(result_sha256, "result digest")
        if not isinstance(error_code, str) or len(error_code) > 128 or any(ord(char) < 32 for char in error_code):
            raise WindowsAgentError("error code is invalid")
        try:
            job, status = self._jobs[job_id]
        except KeyError as exc:
            raise WindowsAgentError("job is not registered") from exc
        if status in {"completed", "failed"}:
            try:
                result = self._results[job_id]
            except KeyError as exc:
                raise WindowsAgentError("completed job result is missing") from exc
            if result["node_id"] != node_id or result["lease_id"] != lease_id:
                raise WindowsAgentError("stale or foreign completed job lease")
            return dict(result)
        try:
            lease = self._leases[job_id]
        except KeyError as exc:
            raise WindowsAgentError("active job lease is missing") from exc
        if status != "leased" or lease.lease_id != lease_id or lease.node_id != node_id:
            raise WindowsAgentError("stale or foreign job lease")
        if lease.expires_at <= self._clock():
            self._leases.pop(job_id, None)
            self._jobs[job_id] = (job, "queued")
            raise WindowsAgentError("job lease has expired")
        final_status = "failed" if error_code else "completed"
        self._leases.pop(job_id, None)
        self._jobs[job_id] = (job, final_status)
        result = {
            "job_id": job_id,
            "task_id": job.task_id,
            "status": final_status,
            "node_id": node_id,
            "lease_id": lease_id,
            "model": self._nodes[node_id][0].model,
            "result_sha256": result_sha256,
            "error_code": error_code,
            "completed_at": self._clock(),
        }
        self._results[job_id] = result
        return dict(result)

    def reconcile(self) -> int:
        """Requeue expired leases and leases whose node is no longer online."""
        changed = 0
        now = self._clock()
        for job_id, lease in tuple(self._leases.items()):
            _, beat = self._nodes[lease.node_id]
            if lease.expires_at > now and beat.status == "online" and now - beat.observed_at <= self.heartbeat_age_seconds:
                continue
            job, _ = self._jobs[job_id]
            self._leases.pop(job_id, None)
            self._jobs[job_id] = (job, "queued")
            changed += 1
        return changed

    def node_snapshot(self, node_id: str) -> dict[str, object]:
        node_id = _identifier(node_id, "node id")
        try:
            manifest, beat = self._nodes[node_id]
        except KeyError as exc:
            raise WindowsAgentError("node is not registered") from exc
        manifest_data = asdict(manifest)
        manifest_data["capabilities"] = sorted(manifest.capabilities)
        manifest_data["data_scopes"] = sorted(manifest.data_scopes)
        return {
            "manifest": manifest_data,
            "heartbeat": asdict(beat),
            "heartbeat_age_seconds": max(0.0, self._clock() - beat.observed_at) if beat.observed_at else None,
            "active_leases": self._active_leases(node_id),
        }

    def job_snapshot(self, job_id: str) -> dict[str, object]:
        job_id = _identifier(job_id, "job id")
        try:
            job, status = self._jobs[job_id]
        except KeyError as exc:
            raise WindowsAgentError("job is not registered") from exc
        return {
            "job": asdict(job),
            "status": status,
            "leased": job_id in self._leases,
            "result": dict(self._results[job_id]) if job_id in self._results else None,
        }

    def _active_leases(self, node_id: str) -> int:
        return sum(lease.node_id == node_id and lease.expires_at > self._clock() for lease in self._leases.values())


WindowsAgent = WindowsAgentRegistry
LocalAgentRegistry = WindowsAgentRegistry
WindowsNode = NodeManifest
WindowsJob = LocalAgentJob
JobLease = CapabilityLease


__all__ = [
    "CapabilityLease",
    "DATA_SCOPES",
    "Heartbeat",
    "JobLease",
    "LOCAL_OPERATIONS",
    "LocalAgentJob",
    "LocalAgentRegistry",
    "MAX_HEARTBEAT_AGE_SECONDS",
    "MAX_JOB_TTL_SECONDS",
    "NodeManifest",
    "NodeRoute",
    "WindowsAgent",
    "WindowsAgentError",
    "WindowsAgentRegistry",
    "WindowsJob",
    "WindowsNode",
]
