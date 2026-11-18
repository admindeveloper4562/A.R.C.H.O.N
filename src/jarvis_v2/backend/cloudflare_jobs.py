"""Outbound-only client for the durable REL-005 Cloudflare job queue."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .windows_agent import LocalAgentJob


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_STATES = frozenset({"pending", "leased", "completed", "failed"})
_MAX_BODY_BYTES = 2_048
TokenProvider = Callable[[], str]
Transport = Callable[[Request], tuple[int, bytes]]


class CloudflareJobAdapterError(ValueError):
    """Raised when the outbound job boundary cannot validate or complete a call."""


def _identifier(value: object, label: str, limit: int = 128) -> str:
    if not isinstance(value, str) or len(value) > limit or not _IDENTIFIER.fullmatch(value):
        raise CloudflareJobAdapterError(f"invalid {label}")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise CloudflareJobAdapterError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class CloudflareJobRecord:
    """Redacted durable job state returned by the REL-005 service."""

    job_id: str
    idempotency_key: str
    operation: str
    input_sha256: str
    required_scope: str
    deadline_at: int
    state: str
    device_id: str
    lease_id: str
    lease_expires_at: int
    result_sha256: str
    ok: bool | None

    @classmethod
    def from_payload(cls, value: object) -> "CloudflareJobRecord":
        if not isinstance(value, Mapping):
            raise CloudflareJobAdapterError("job response is not an object")
        required = (
            "job_id", "idempotency_key", "operation", "input_sha256", "required_scope",
            "deadline_at", "state", "device_id", "lease_id", "lease_expires_at",
            "result_sha256", "ok",
        )
        if any(key not in value for key in required):
            raise CloudflareJobAdapterError("job response is incomplete")
        deadline = value["deadline_at"]
        lease_expires = value["lease_expires_at"]
        if type(deadline) is not int or type(lease_expires) is not int:
            raise CloudflareJobAdapterError("job timestamps are invalid")
        ok = value["ok"]
        if ok is not None and type(ok) is not bool:
            raise CloudflareJobAdapterError("job completion marker is invalid")
        state = value["state"]
        if not isinstance(state, str) or state not in _STATES:
            raise CloudflareJobAdapterError("job state is invalid")
        return cls(
            job_id=_identifier(value["job_id"], "job id"),
            idempotency_key=_identifier(value["idempotency_key"], "idempotency key"),
            operation=_identifier(value["operation"], "operation"),
            input_sha256=_digest(value["input_sha256"], "input digest"),
            required_scope=_identifier(value["required_scope"], "required scope"),
            deadline_at=deadline,
            state=state,
            device_id=_identifier(value["device_id"], "device id") if value["device_id"] else "",
            lease_id=_identifier(value["lease_id"], "lease id") if value["lease_id"] else "",
            lease_expires_at=lease_expires,
            result_sha256=_digest(value["result_sha256"], "result digest") if value["result_sha256"] else "",
            ok=ok,
        )


class CloudflareJobAdapter:
    """Use the configured Cloudflare monitor without opening a local listener.

    The bearer token is obtained per request and is never placed in a job
    payload, record, exception, or log.  D1 remains the durable queue store.
    """

    def __init__(
        self,
        base_url: str,
        token_provider: TokenProvider,
        *,
        transport: Transport | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise CloudflareJobAdapterError("base URL must be an HTTPS origin without credentials")
        if not callable(token_provider):
            raise CloudflareJobAdapterError("token provider is required")
        if type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= 60:
            raise CloudflareJobAdapterError("timeout is outside the bounded range")
        self._base_url = base_url.rstrip("/")
        self._token_provider = token_provider
        self._transport = transport
        self._timeout_seconds = timeout_seconds

    @staticmethod
    def _urlopen(request: Request, timeout: float) -> tuple[int, bytes]:
        with urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read(_MAX_BODY_BYTES + 1)

    def create(self, job: LocalAgentJob) -> CloudflareJobRecord:
        if not isinstance(job, LocalAgentJob):
            raise CloudflareJobAdapterError("local-agent job is required")
        return self._call(
            "/api/jobs",
            {
                "job_id": job.job_id,
                "idempotency_key": job.idempotency_key,
                "operation": job.operation,
                "input_sha256": job.input_sha256,
                "required_scope": job.required_scope,
                "deadline_at": int(job.deadline_at),
            },
        )

    submit = create

    def claim(self, job_id: str, device_id: str, lease_id: str, *, lease_seconds: int = 60) -> CloudflareJobRecord:
        _identifier(job_id, "job id")
        _identifier(device_id, "device id")
        _identifier(lease_id, "lease id")
        if type(lease_seconds) is not int or not 30 <= lease_seconds <= 900:
            raise CloudflareJobAdapterError("lease duration is outside the bounded range")
        return self._call(f"/api/jobs/{job_id}/claim", {
            "device_id": device_id,
            "lease_id": lease_id,
            "lease_seconds": lease_seconds,
        })

    def complete(self, job_id: str, lease_id: str, *, ok: bool, result_sha256: str) -> CloudflareJobRecord:
        _identifier(job_id, "job id")
        _identifier(lease_id, "lease id")
        if type(ok) is not bool:
            raise CloudflareJobAdapterError("completion marker must be boolean")
        _digest(result_sha256, "result digest")
        return self._call(f"/api/jobs/{job_id}/complete", {
            "lease_id": lease_id,
            "ok": ok,
            "result_sha256": result_sha256,
        })

    def _call(self, path: str, payload: Mapping[str, object]) -> CloudflareJobRecord:
        token = self._token_provider()
        if not isinstance(token, str) or not token or len(token) > 512 or any(ord(char) < 32 for char in token):
            raise CloudflareJobAdapterError("job token is invalid")
        body = json.dumps(dict(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(body) > _MAX_BODY_BYTES:
            raise CloudflareJobAdapterError("job payload is too large")
        request = Request(
            f"{self._base_url}{path}",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            if self._transport is None:
                status, raw = self._urlopen(request, self._timeout_seconds)
            else:
                status, raw = self._transport(request)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise CloudflareJobAdapterError("Cloudflare job request failed") from exc
        if not isinstance(status, int) or not isinstance(raw, bytes) or len(raw) > _MAX_BODY_BYTES:
            raise CloudflareJobAdapterError("invalid Cloudflare job response")
        if status < 200 or status >= 300:
            raise CloudflareJobAdapterError(f"Cloudflare job request returned HTTP {status}")
        try:
            response = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise CloudflareJobAdapterError("Cloudflare job response is not JSON") from exc
        if not isinstance(response, Mapping) or not isinstance(response.get("job"), Mapping):
            raise CloudflareJobAdapterError("Cloudflare job response is incomplete")
        return CloudflareJobRecord.from_payload(response["job"])


__all__ = ["CloudflareJobAdapter", "CloudflareJobAdapterError", "CloudflareJobRecord"]
