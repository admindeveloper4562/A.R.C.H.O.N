"""Mira-owned, short-lived read-only connector capability."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeVar

from jarvis_v2.backend.connectors import ConnectorAuthorizationError, ConnectorBroker


MIRA_READ_SCOPE = "mira:read"
_Result = TypeVar("_Result")
_AUDIT_FIELDS = MappingProxyType(
    {
        "grant_id": "grant_id",
        "identity_id": "identity_id",
        "connector": "connector",
        "scopes": "scopes",
        "expires_at": "expires_at",
        "revoked": "revoked",
        "active": "active",
    }
)


@dataclass(frozen=True)
class MiraExportToken:
    """Redacted capability metadata; no credential material is stored here."""

    token_id: str
    identity_id: str
    expires_at: float
    scope: str = MIRA_READ_SCOPE


class MiraConnectorTokenBroker:
    """Issue only the scoped Mira read capability through the existing broker."""

    def __init__(self) -> None:
        self._broker = ConnectorBroker()

    def issue(
        self,
        identity_id: str,
        *,
        token_id: str | None = None,
        ttl_seconds: int = 300,
    ) -> MiraExportToken:
        grant = self._broker.grant(
            identity_id,
            "mira",
            [MIRA_READ_SCOPE],
            credential_ref="mira-read-only",
            grant_id=token_id,
            ttl_seconds=ttl_seconds,
        )
        return MiraExportToken(grant.grant_id, grant.identity_id, grant.expires_at)

    def authorize(self, identity_id: str, token_id: str, scope: str = MIRA_READ_SCOPE) -> bool:
        return scope == MIRA_READ_SCOPE and self._broker.authorize(
            identity_id, "mira", MIRA_READ_SCOPE, grant_id=token_id
        )

    def revoke(self, token_id: str) -> None:
        self._broker.revoke(token_id)

    def run_read_sync(
        self,
        identity_id: str,
        token_id: str,
        operation: Callable[[], _Result],
    ) -> _Result:
        """Run one read-only sync only while the scoped grant is active."""
        if not self.authorize(identity_id, token_id):
            raise ConnectorAuthorizationError("Mira sync capability denied")
        return operation()

    def audit(self) -> tuple[dict[str, object], ...]:
        """Return capability metadata without credential references or values."""
        result = []
        for item in self._broker.grants():
            result.append({key: item[source] for key, source in _AUDIT_FIELDS.items()})
        return tuple(result)


__all__ = ["MIRA_READ_SCOPE", "MiraConnectorTokenBroker", "MiraExportToken"]
