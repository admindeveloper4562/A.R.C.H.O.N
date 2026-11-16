"""Bounded identity and least-privilege capability authorization."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import hashlib
import json
import re
import time
from types import MappingProxyType
from uuid import uuid4

from jarvis_v2.core.registry import ModuleRegistry


MAX_GRANT_TTL_SECONDS = 3_600
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_IDENTITY_KINDS = frozenset({"service", "operator", "watchdog"})


class AuthorizationError(ValueError):
    """Raised when a capability or approval cannot be admitted."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise AuthorizationError(f"invalid {label}")
    return value


def _scope_set(target_module: str, scopes: Iterable[str], allowed: frozenset[str]) -> frozenset[str]:
    if isinstance(scopes, (str, bytes)):
        raise AuthorizationError("scopes must be a collection")
    values = tuple(scopes)
    if not values or len(values) != len(set(values)):
        raise AuthorizationError("scopes must be non-empty and unique")
    if any(not isinstance(scope, str) or not scope for scope in values):
        raise AuthorizationError("scopes must contain non-empty strings")
    expected_prefix = f"{target_module}:"
    if any(not scope.startswith(expected_prefix) or scope not in allowed for scope in values):
        raise AuthorizationError("scope exceeds the target module contract")
    return frozenset(values)


def _request_digest(identity_id: str, target_module: str, scopes: frozenset[str]) -> str:
    payload = {
        "identity_id": identity_id,
        "target_module": target_module,
        "scopes": sorted(scopes),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class AuthIdentity:
    """A stable control-plane identity bound to one ARCHON module."""

    identity_id: str
    module: str
    kind: str


@dataclass(frozen=True)
class OwnerApproval:
    """An exact, digest-bound approval for a scoped grant."""

    approval_id: str
    identity_id: str
    target_module: str
    scopes: frozenset[str]
    request_sha: str
    decision: str = "APPROVE"

    @classmethod
    def for_grant(
        cls,
        approval_id: str,
        identity_id: str,
        target_module: str,
        scopes: Iterable[str],
    ) -> "OwnerApproval":
        identity_id = _identifier(identity_id, "identity_id")
        approval_id = _identifier(approval_id, "approval_id")
        target_module = _identifier(target_module, "target_module")
        normalized = frozenset(scopes)
        if not normalized or any(not isinstance(scope, str) for scope in normalized):
            raise AuthorizationError("approval scopes are invalid")
        return cls(
            approval_id=approval_id,
            identity_id=identity_id,
            target_module=target_module,
            scopes=normalized,
            request_sha=_request_digest(identity_id, target_module, normalized),
        )


@dataclass(frozen=True)
class CapabilityGrant:
    """A short-lived, immutable grant for one identity and target module."""

    grant_id: str
    identity_id: str
    target_module: str
    scopes: frozenset[str]
    expires_at: float
    approval_id: str | None


class AuthorizationServer:
    """Enforce identity, module-local scopes and exact approval bindings."""

    def __init__(self, registry: ModuleRegistry) -> None:
        self.registry = registry
        self._identities: dict[str, AuthIdentity] = {}
        self._grants: dict[str, CapabilityGrant] = {}
        self._revoked: set[str] = set()

    def register_identity(self, identity_id: str, module: int | str, *, kind: str = "service") -> AuthIdentity:
        identity_id = _identifier(identity_id, "identity_id")
        resolved = self.registry.resolve(module)
        if kind not in _IDENTITY_KINDS:
            raise AuthorizationError("invalid identity kind")
        identity = AuthIdentity(identity_id, resolved.key, kind)
        existing = self._identities.get(identity_id)
        if existing is not None and existing != identity:
            raise AuthorizationError("identity registration conflict")
        self._identities[identity_id] = identity
        return identity

    def grant(
        self,
        identity_id: str,
        target_module: int | str,
        scopes: Iterable[str],
        *,
        approval: OwnerApproval | None = None,
        grant_id: str | None = None,
        ttl_seconds: int = 300,
    ) -> CapabilityGrant:
        identity = self._identity(identity_id)
        target = self.registry.resolve(target_module)
        normalized = _scope_set(target.key, scopes, target.permission_scopes)
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_GRANT_TTL_SECONDS:
            raise AuthorizationError("grant TTL is outside the bounded policy")
        if identity.module != target.key or approval is not None:
            self._check_approval(identity, target.key, normalized, approval)
        grant_id = _identifier(grant_id or uuid4().hex, "grant_id")
        existing = self._grants.get(grant_id)
        if existing is not None:
            if existing.identity_id != identity.identity_id or existing.target_module != target.key or existing.scopes != normalized:
                raise AuthorizationError("grant registration conflict")
            return existing
        grant = CapabilityGrant(
            grant_id=grant_id,
            identity_id=identity.identity_id,
            target_module=target.key,
            scopes=normalized,
            expires_at=time.time() + ttl_seconds,
            approval_id=approval.approval_id if approval is not None else None,
        )
        self._grants[grant_id] = grant
        return grant

    def authorize(self, identity_id: str, target_module: int | str, scope: str, *, grant_id: str | None = None) -> bool:
        identity = self._identities.get(identity_id)
        if identity is None:
            return False
        try:
            target = self.registry.resolve(target_module)
            if not isinstance(scope, str) or scope not in target.permission_scopes:
                return False
            if not scope.startswith(f"{target.key}:"):
                return False
        except (AuthorizationError, ValueError):
            return False
        grants = self._grants.values() if grant_id is None else (self._grants.get(grant_id),)
        return any(
            grant is not None
            and grant.grant_id not in self._revoked
            and grant.identity_id == identity.identity_id
            and grant.target_module == target.key
            and scope in grant.scopes
            and grant.expires_at > time.time()
            for grant in grants
        )

    def require(self, identity_id: str, target_module: int | str, scope: str, *, grant_id: str | None = None) -> CapabilityGrant:
        if not self.authorize(identity_id, target_module, scope, grant_id=grant_id):
            raise AuthorizationError("capability denied")
        if grant_id is not None:
            return self._grants[grant_id]
        return next(
            grant for grant in self._grants.values()
            if grant.identity_id == identity_id and grant.target_module == self.registry.resolve(target_module).key
            and scope in grant.scopes and grant.grant_id not in self._revoked and grant.expires_at > time.time()
        )

    def revoke(self, grant_id: str) -> None:
        grant_id = _identifier(grant_id, "grant_id")
        if grant_id not in self._grants:
            raise AuthorizationError("unknown grant")
        self._revoked.add(grant_id)

    def identities(self) -> MappingProxyType:
        return MappingProxyType(self._identities)

    def _identity(self, identity_id: str) -> AuthIdentity:
        identity_id = _identifier(identity_id, "identity_id")
        try:
            return self._identities[identity_id]
        except KeyError as exc:
            raise AuthorizationError("unknown identity") from exc

    @staticmethod
    def _check_approval(
        identity: AuthIdentity,
        target_module: str,
        scopes: frozenset[str],
        approval: OwnerApproval | None,
    ) -> None:
        if approval is None or approval.decision != "APPROVE":
            raise AuthorizationError("exact owner approval is required")
        if (
            approval.identity_id != identity.identity_id
            or approval.target_module != target_module
            or approval.scopes != scopes
            or approval.request_sha != _request_digest(identity.identity_id, target_module, scopes)
        ):
            raise AuthorizationError("owner approval is not bound to this grant")


__all__ = [
    "AuthIdentity",
    "AuthorizationError",
    "AuthorizationServer",
    "CapabilityGrant",
    "MAX_GRANT_TTL_SECONDS",
    "OwnerApproval",
]
