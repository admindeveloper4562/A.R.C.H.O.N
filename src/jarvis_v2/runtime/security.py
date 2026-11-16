"""Small, transport-neutral security boundary for the Runtime module."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re
import secrets
import time
from types import MappingProxyType
from urllib.parse import urlsplit


SESSION_TTL_SECONDS = 3_600
_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
_OPAQUE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")

SECURITY_HEADERS = MappingProxyType({
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'self'; connect-src 'self'; object-src 'none'; "
        "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    ),
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
})


class RuntimeSecurityError(ValueError):
    """Raised when a Runtime request fails its security contract."""

    def __init__(self, code: str, status: int) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


@dataclass(frozen=True)
class OwnerSession:
    """One short-lived owner session and its request-bound CSRF value."""

    session_id: str
    identity_id: str
    csrf_token: str
    expires_at: float

    def as_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "identity_id": self.identity_id,
            "csrf_token": self.csrf_token,
            "expires_at": self.expires_at,
        }


def _opaque(value: str, label: str) -> str:
    if not isinstance(value, str) or not _OPAQUE.fullmatch(value):
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    return value


def _authority(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 255:
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    if any(char.isspace() or ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    parsed = urlsplit(f"//{value}")
    if (not parsed.netloc or parsed.username is not None or parsed.password is not None
            or parsed.path or parsed.query or parsed.fragment):
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    try:
        parsed.port
    except ValueError as exc:
        raise RuntimeSecurityError(f"invalid_{label}", 400) from exc
    return parsed.netloc.lower()


def _origin(value: str, allowed: frozenset[str], label: str = "origin") -> str:
    if not isinstance(value, str) or len(value) > 255:
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    if any(char.isspace() or ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    parsed = urlsplit(value)
    if (parsed.scheme not in {"http", "https"} or not parsed.netloc
            or parsed.username is not None or parsed.password is not None
            or parsed.path or parsed.query or parsed.fragment):
        raise RuntimeSecurityError(f"invalid_{label}", 400)
    try:
        parsed.port
    except ValueError as exc:
        raise RuntimeSecurityError(f"invalid_{label}", 400) from exc
    normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
    if normalized not in allowed:
        raise RuntimeSecurityError("origin_denied", 403)
    return normalized


class RuntimeSecurity:
    """Bind browser-style requests to an identity, host and CSRF value.

    Sessions are intentionally process-local. The Runtime transport must not
    persist bearer credentials in task or event databases; callers can issue a
    new bounded session after a trusted process restart.
    """

    def __init__(
        self,
        *,
        expected_host: str = "127.0.0.1:8765",
        allowed_origins: Iterable[str] | None = None,
        ttl_seconds: int = SESSION_TTL_SECONDS,
        clock=time.time,
    ) -> None:
        self.expected_host = _authority(expected_host, "host")
        origins = allowed_origins
        if origins is None:
            origins = (f"http://{self.expected_host}",)
        normalized = []
        for value in origins:
            parsed = urlsplit(value)
            if (parsed.scheme not in {"http", "https"} or not parsed.netloc
                    or parsed.path or parsed.query or parsed.fragment):
                raise RuntimeSecurityError("invalid_origin", 400)
            normalized.append(_origin(value, frozenset({f"{parsed.scheme}://{parsed.netloc.lower()}"})))
        if not normalized:
            raise RuntimeSecurityError("origins_required", 400)
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= SESSION_TTL_SECONDS:
            raise RuntimeSecurityError("invalid_session_ttl", 400)
        self.allowed_origins = frozenset(normalized)
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._sessions: dict[str, OwnerSession] = {}

    @staticmethod
    def response_headers() -> dict[str, str]:
        """Return defensive browser headers for an adapter response."""
        return dict(SECURITY_HEADERS)

    def issue(self, identity_id: str, *, now: float | None = None) -> OwnerSession:
        identity_id = _opaque(identity_id, "identity_id")
        issued_at = self._now(now)
        session_id = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        session = OwnerSession(
            session_id=session_id,
            identity_id=identity_id,
            csrf_token=csrf_token,
            expires_at=issued_at + self.ttl_seconds,
        )
        self._sessions[session_id] = session
        return session

    def validate(
        self,
        *,
        session_id: str,
        identity_id: str,
        method: str,
        host: str,
        origin: str | None = None,
        csrf_token: str | None = None,
        now: float | None = None,
    ) -> OwnerSession:
        if not isinstance(method, str) or method.upper() not in _SAFE_METHODS | _MUTATING_METHODS:
            raise RuntimeSecurityError("invalid_method", 400)
        method = method.upper()
        if not isinstance(session_id, str) or not _TOKEN.fullmatch(session_id):
            raise RuntimeSecurityError("session_required", 401)
        identity_id = _opaque(identity_id, "identity_id")
        if _authority(host, "host") != self.expected_host:
            raise RuntimeSecurityError("host_denied", 403)
        session = self._sessions.get(session_id)
        if session is None or self._expired(session, now):
            self._sessions.pop(session_id, None)
            raise RuntimeSecurityError("session_expired", 401)
        if session.identity_id != identity_id:
            raise RuntimeSecurityError("session_identity_mismatch", 403)
        if origin is not None:
            normalized_origin = _origin(origin, self.allowed_origins)
            if urlsplit(normalized_origin).netloc != self.expected_host:
                raise RuntimeSecurityError("origin_host_mismatch", 403)
        if method in _MUTATING_METHODS:
            if origin is None:
                raise RuntimeSecurityError("origin_required", 403)
            if not isinstance(csrf_token, str) or not secrets.compare_digest(csrf_token, session.csrf_token):
                raise RuntimeSecurityError("csrf_denied", 403)
        elif csrf_token is not None and (
            not isinstance(csrf_token, str)
            or not secrets.compare_digest(csrf_token, session.csrf_token)
        ):
            raise RuntimeSecurityError("csrf_denied", 403)
        return session

    def rotate(
        self,
        *,
        session_id: str,
        identity_id: str,
        method: str,
        host: str,
        origin: str | None = None,
        csrf_token: str | None = None,
        now: float | None = None,
    ) -> OwnerSession:
        current = self.validate(
            session_id=session_id,
            identity_id=identity_id,
            method=method,
            host=host,
            origin=origin,
            csrf_token=csrf_token,
            now=now,
        )
        self._sessions.pop(current.session_id, None)
        return self.issue(current.identity_id, now=now)

    def revoke(self, session_id: str) -> None:
        if not isinstance(session_id, str) or not _TOKEN.fullmatch(session_id):
            raise RuntimeSecurityError("invalid_session", 400)
        self._sessions.pop(session_id, None)

    def _expired(self, session: OwnerSession, now: float | None) -> bool:
        return self._now(now) >= session.expires_at

    def _now(self, now: float | None) -> float:
        value = self._clock() if now is None else now
        if not isinstance(value, (int, float)):
            raise RuntimeSecurityError("invalid_clock", 400)
        return float(value)


__all__ = [
    "OwnerSession",
    "RuntimeSecurity",
    "RuntimeSecurityError",
    "SECURITY_HEADERS",
    "SESSION_TTL_SECONDS",
]
