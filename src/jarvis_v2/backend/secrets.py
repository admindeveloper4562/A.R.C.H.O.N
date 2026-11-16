"""Allowlisted secret retrieval with redacted metadata boundaries."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
import hashlib
import os
import re
from types import MappingProxyType


MAX_SECRET_VALUE_BYTES = 64 * 1024
_NAME = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class SecretBoundaryError(ValueError):
    """Raised when a secret crosses an unsafe boundary or is unavailable."""


class SecretUnavailable(SecretBoundaryError):
    """Raised when an explicitly allowlisted value is not available."""


def _name(value: str) -> str:
    if not isinstance(value, str) or not _NAME.fullmatch(value):
        raise SecretBoundaryError("invalid secret name")
    return value


def _names(values: Iterable[str]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise SecretBoundaryError("secret allowlist must be a collection")
    result = frozenset(_name(value) for value in values)
    if not result:
        raise SecretBoundaryError("secret allowlist must not be empty")
    return result


@dataclass(frozen=True, repr=False)
class SecretValue:
    """A value that stays redacted unless a consumer explicitly reveals it."""

    name: str
    _value: str = field(repr=False, compare=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self._value.encode("utf-8")).hexdigest()

    @property
    def length(self) -> int:
        return len(self._value.encode("utf-8"))

    def reveal(self) -> str:
        """Return the raw value only at the explicitly authorized use site."""
        return self._value

    def __str__(self) -> str:
        return "<redacted>"

    def __repr__(self) -> str:
        return f"SecretValue(name={self.name!r}, value=<redacted>)"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


class SecretStore:
    """Read only explicitly allowlisted values from an injected provider."""

    def __init__(self, values: Mapping[str, str], *, allowlist: Iterable[str]) -> None:
        if not isinstance(values, Mapping):
            raise SecretBoundaryError("secret provider must be a mapping")
        allowed = _names(allowlist)
        stored: dict[str, str] = {}
        for name in allowed:
            if name not in values:
                continue
            value = values[name]
            if not isinstance(value, str) or not value:
                raise SecretBoundaryError("secret values must be non-empty strings")
            if len(value.encode("utf-8")) > MAX_SECRET_VALUE_BYTES:
                raise SecretBoundaryError("secret value exceeds bounded size")
            stored[name] = value
        self._allowlist = allowed
        self._values = MappingProxyType(stored)

    @classmethod
    def from_environment(
        cls,
        allowlist: Iterable[str],
        *,
        environment: Mapping[str, str] | None = None,
    ) -> "SecretStore":
        return cls(os.environ if environment is None else environment, allowlist=allowlist)

    def get(self, name: str) -> SecretValue:
        name = _name(name)
        if name not in self._allowlist:
            raise SecretUnavailable("secret is not allowlisted")
        try:
            return SecretValue(name, self._values[name])
        except KeyError as exc:
            raise SecretUnavailable("allowlisted secret is unavailable") from exc

    def redact(self, text: str) -> str:
        if not isinstance(text, str):
            raise SecretBoundaryError("redaction input must be text")
        redacted = text
        for value in self._values.values():
            redacted = redacted.replace(value, "<redacted>")
        return redacted

    def public_metadata(self, name: str) -> dict[str, str | int]:
        value = self.get(name)
        return {"name": value.name, "sha256": value.digest, "length": value.length}


__all__ = [
    "MAX_SECRET_VALUE_BYTES",
    "SecretBoundaryError",
    "SecretStore",
    "SecretUnavailable",
    "SecretValue",
]
