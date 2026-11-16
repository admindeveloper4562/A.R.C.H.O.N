"""Permission-scoped, independently revocable connector access."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from types import MappingProxyType
import re
import time
from uuid import uuid4


MAX_CONNECTOR_GRANT_TTL_SECONDS = 3_600
CONNECTORS = frozenset({"google", "github", "mira", "cloudflare"})
CONNECTOR_SCOPES = MappingProxyType(
    {connector: frozenset({f"{connector}:read"}) for connector in CONNECTORS}
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class ConnectorAuthorizationError(ValueError):
    """Raised when connector access cannot be admitted or used."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ConnectorAuthorizationError(f"invalid {label}")
    return value


def _connector(value: str) -> str:
    if not isinstance(value, str) or value not in CONNECTORS:
        raise ConnectorAuthorizationError("unknown connector")
    return value


def _scopes(connector: str, values: Iterable[str]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise ConnectorAuthorizationError("connector scopes must be a collection")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise ConnectorAuthorizationError("connector scopes must be a collection") from exc
    if not normalized or len(normalized) != len(set(normalized)):
        raise ConnectorAuthorizationError("connector scopes must be non-empty and unique")
    if any(scope not in CONNECTOR_SCOPES[connector] for scope in normalized):
        raise ConnectorAuthorizationError("connector scope is not allowlisted")
    return frozenset(normalized)


@dataclass(frozen=True)
class ConnectorGrant:
    """A short-lived grant containing names and scopes, never credential data."""

    grant_id: str
    identity_id: str
    connector: str
    scopes: frozenset[str]
    expires_at: float
    credential_ref: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class ConnectorBroker:
    """Issue and revoke connector grants without performing connector I/O.

    The caller must authenticate ``identity_id`` through the existing
    authorization boundary before calling this broker.  The broker then
    narrows access to one connector and its explicit read-only scope.
    """

    def __init__(self) -> None:
        self._grants: dict[str, ConnectorGrant] = {}
        self._revoked: set[str] = set()

    def grant(
        self,
        identity_id: str,
        connector: str,
        scopes: Iterable[str],
        *,
        credential_ref: str | None = None,
        grant_id: str | None = None,
        ttl_seconds: int = 300,
    ) -> ConnectorGrant:
        identity_id = _identifier(identity_id, "identity id")
        connector = _connector(connector)
        normalized = _scopes(connector, scopes)
        if credential_ref is not None:
            credential_ref = _identifier(credential_ref, "credential reference")
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_CONNECTOR_GRANT_TTL_SECONDS:
            raise ConnectorAuthorizationError("grant TTL is outside the bounded policy")
        grant_id = _identifier(grant_id or uuid4().hex, "grant id")
        existing = self._grants.get(grant_id)
        if existing is not None:
            if (
                existing.identity_id != identity_id
                or existing.connector != connector
                or existing.scopes != normalized
                or existing.credential_ref != credential_ref
            ):
                raise ConnectorAuthorizationError("grant registration conflict")
            return existing
        grant = ConnectorGrant(
            grant_id=grant_id,
            identity_id=identity_id,
            connector=connector,
            scopes=normalized,
            expires_at=time.time() + ttl_seconds,
            credential_ref=credential_ref,
        )
        self._grants[grant_id] = grant
        return grant

    def authorize(
        self,
        identity_id: str,
        connector: str,
        scope: str,
        *,
        grant_id: str | None = None,
    ) -> bool:
        try:
            identity_id = _identifier(identity_id, "identity id")
            connector = _connector(connector)
        except ConnectorAuthorizationError:
            return False
        grants = (self._grants.get(grant_id),) if grant_id is not None else self._grants.values()
        return any(
            grant is not None
            and grant.grant_id not in self._revoked
            and grant.identity_id == identity_id
            and grant.connector == connector
            and grant.scopes.__contains__(scope)
            and grant.expires_at > time.time()
            for grant in grants
        )

    def require(
        self,
        identity_id: str,
        connector: str,
        scope: str,
        *,
        grant_id: str | None = None,
    ) -> ConnectorGrant:
        if not self.authorize(identity_id, connector, scope, grant_id=grant_id):
            raise ConnectorAuthorizationError("connector capability denied")
        grants = (self._grants[grant_id],) if grant_id is not None else self._grants.values()
        return next(
            grant
            for grant in grants
            if grant is not None
            and grant.grant_id not in self._revoked
            and grant.identity_id == identity_id
            and grant.connector == connector
            and scope in grant.scopes
            and grant.expires_at > time.time()
        )

    def revoke(self, grant_id: str) -> None:
        grant_id = _identifier(grant_id, "grant id")
        if grant_id not in self._grants:
            raise ConnectorAuthorizationError("unknown grant")
        self._revoked.add(grant_id)

    def revoke_connector(self, identity_id: str, connector: str) -> int:
        """Revoke one identity's connector grants without affecting others."""
        identity_id = _identifier(identity_id, "identity id")
        connector = _connector(connector)
        grant_ids = [
            grant.grant_id
            for grant in self._grants.values()
            if grant.identity_id == identity_id and grant.connector == connector
        ]
        self._revoked.update(grant_ids)
        return len(grant_ids)

    def grants(self) -> tuple[dict[str, object], ...]:
        """Return redacted grant metadata for audit; no credential values."""
        return tuple(
            grant.as_dict()
            | {"revoked": grant.grant_id in self._revoked, "active": self._active(grant)}
            for grant in self._grants.values()
        )

    def _active(self, grant: ConnectorGrant) -> bool:
        return grant.grant_id not in self._revoked and grant.expires_at > time.time()


ConnectorAccessBroker = ConnectorBroker
RevocableConnectorBroker = ConnectorBroker


__all__ = [
    "CONNECTORS",
    "CONNECTOR_SCOPES",
    "ConnectorAccessBroker",
    "ConnectorAuthorizationError",
    "ConnectorBroker",
    "ConnectorGrant",
    "MAX_CONNECTOR_GRANT_TTL_SECONDS",
    "RevocableConnectorBroker",
]
