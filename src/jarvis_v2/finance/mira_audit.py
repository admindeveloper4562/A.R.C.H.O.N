"""Evidence-bound review contract for the external Mira finance service.

This module records metadata discovered during a read-only review.  It does
not connect to Mira, read financial rows, or expose Worker secret values.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Mapping, Sequence
from uuid import UUID


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SECRET_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
_REQUIRED_TABLES = frozenset({
    "couple_accounts",
    "couple_account_entries",
    "couple_account_links",
    "couple_budgets",
    "couple_categories",
    "couple_login_attempts",
    "couple_sessions",
    "couple_settings",
    "couple_transactions",
})


def schema_sha256(schema: Mapping[str, str]) -> str:
    """Hash ordered table definitions without retaining any table data."""
    if not schema or any(not isinstance(name, str) or not name for name in schema):
        raise ValueError("schema definitions are required")
    if any(not isinstance(sql, str) or not sql for sql in schema.values()):
        raise ValueError("schema SQL definitions are required")
    canonical = "\n".join(
        f"{name}\n{schema[name]}" for name in sorted(schema)
    ) + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MiraAuditSnapshot:
    """Sanitized, source-SHA-bound metadata from one external review."""

    worker_name: str
    worker_version_id: str
    worker_source_sha256: str
    d1_name: str
    d1_uuid: str
    d1_schema_sha256: str
    d1_tables: tuple[str, ...]
    db_binding_name: str
    db_binding_uuid: str
    secret_binding_names: tuple[str, ...]
    session_cookie_name: str
    session_ttl_seconds: int
    same_origin_enforced: bool
    partner_scope_enforced: bool
    read_route_count: int
    write_route_count: int
    archon_read_only_policy: bool = True

    def validate(self) -> None:
        """Reject incomplete or unsafe evidence before it enters a task receipt."""
        if self.worker_name != "personal-management":
            raise ValueError("unexpected Mira Worker identity")
        for label, value in (
            ("Worker source", self.worker_source_sha256),
            ("D1 schema", self.d1_schema_sha256),
        ):
            if not _SHA256.fullmatch(value):
                raise ValueError(f"{label} digest is invalid")
        try:
            UUID(self.d1_uuid)
            UUID(self.worker_version_id)
        except (ValueError, AttributeError, TypeError) as exc:
            raise ValueError("Mira identifiers are invalid") from exc
        if self.d1_name != "mira-finance":
            raise ValueError("unexpected Mira D1 identity")
        if self.db_binding_name != "DB" or self.db_binding_uuid != self.d1_uuid:
            raise ValueError("Mira Worker/D1 binding mismatch")
        if not _REQUIRED_TABLES.issubset(self.d1_tables):
            raise ValueError("Mira schema is missing required finance tables")
        if not self.secret_binding_names or any(
            not _SECRET_NAME.fullmatch(name) for name in self.secret_binding_names
        ):
            raise ValueError("secret bindings must contain names only")
        if not self.session_cookie_name.startswith("__Host-"):
            raise ValueError("Mira session cookie is not host-scoped")
        if self.session_ttl_seconds <= 0:
            raise ValueError("Mira session lifetime must be positive")
        if not self.same_origin_enforced or not self.partner_scope_enforced:
            raise ValueError("Mira authorization boundaries are incomplete")
        if self.read_route_count < 1 or self.write_route_count < 1:
            raise ValueError("Mira route inventory is incomplete")
        if not self.archon_read_only_policy:
            raise ValueError("ARCHON Mira policy must be read-only")

    def evidence(self) -> dict[str, object]:
        """Return bounded metadata suitable for an acceptance receipt."""
        self.validate()
        return {
            "worker": {
                "name": self.worker_name,
                "version_id": self.worker_version_id,
                "source_sha256": self.worker_source_sha256,
                "d1_binding": self.db_binding_name,
            },
            "d1": {
                "name": self.d1_name,
                "uuid": self.d1_uuid,
                "schema_sha256": self.d1_schema_sha256,
                "table_count": len(self.d1_tables),
                "required_tables": sorted(_REQUIRED_TABLES),
            },
            "authorization": {
                "secret_binding_names": sorted(self.secret_binding_names),
                "session_cookie": self.session_cookie_name,
                "session_ttl_seconds": self.session_ttl_seconds,
                "same_origin_enforced": self.same_origin_enforced,
                "partner_scope_enforced": self.partner_scope_enforced,
                "archon_read_only_policy": self.archon_read_only_policy,
                "read_routes": self.read_route_count,
                "write_routes_detected": self.write_route_count,
            },
            "data_access": "metadata_only; no financial rows read",
        }


def authorize_mira_method(method: str) -> bool:
    """Return whether ARCHON may use a method under its read-only contract."""
    return isinstance(method, str) and method.upper() == "GET"


__all__ = ["MiraAuditSnapshot", "authorize_mira_method", "schema_sha256"]
