"""Bounded, read-only integrity checks for Guardian observations."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
import re
from typing import Any


MAX_ITEMS = 64
MAX_QUEUE_DEPTH = 10_000_000
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class IntegrityScanError(ValueError):
    """Raised when a supplied integrity snapshot is malformed."""


@dataclass(frozen=True)
class IntegrityReport:
    """Bounded result from one integrity observation."""

    ok: bool
    status: str
    version: str
    schemas: tuple[tuple[str, str], ...]
    queues: tuple[tuple[str, int], ...]
    hashes: tuple[tuple[str, str], ...]
    findings: tuple[str, ...]
    read_only: bool = True

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["schemas"] = dict(self.schemas)
        result["queues"] = dict(self.queues)
        result["hashes"] = dict(self.hashes)
        result["findings"] = list(self.findings)
        return result


class IntegrityScanner:
    """Compare bounded runtime observations with immutable expectations.

    The caller supplies observations collected by a separate read-only probe;
    this class never opens, changes or deletes a database, queue or artifact.
    """

    def __init__(
        self,
        expected_version: str | int,
        *,
        expected_schemas: Mapping[str, str | int],
        required_queues: Iterable[str],
        expected_hashes: Mapping[str, str] | None = None,
    ) -> None:
        self._expected_version = _version(expected_version, "expected version")
        self._expected_schemas = _versions(expected_schemas, "expected schemas")
        self._required_queues = _identifiers(required_queues, "required queues")
        self._expected_hashes = _hashes(expected_hashes or {}, "expected hashes")

    def scan(
        self,
        *,
        version: str | int,
        schemas: Mapping[str, str | int],
        queues: Mapping[str, int],
        hashes: Mapping[str, str],
    ) -> IntegrityReport:
        """Return a bounded report without causing any external effect."""
        observed_version = _version(version, "version")
        observed_schemas = _versions(schemas, "schemas")
        observed_queues = _queues(queues)
        observed_hashes = _hashes(hashes, "hashes")
        findings: list[str] = []

        if observed_version != self._expected_version:
            findings.append("version_mismatch")
        findings.extend(_mapping_findings("schema", self._expected_schemas, observed_schemas))

        required = set(self._required_queues)
        observed = set(observed_queues)
        findings.extend(f"queue_missing:{name}" for name in sorted(required - observed))
        findings.extend(f"queue_unexpected:{name}" for name in sorted(observed - required))
        findings.extend(_hash_findings(self._expected_hashes, observed_hashes))

        result_findings = tuple(findings)
        return IntegrityReport(
            ok=not result_findings,
            status="healthy" if not result_findings else "failed",
            version=observed_version,
            schemas=tuple(sorted(observed_schemas.items())),
            queues=tuple(sorted(observed_queues.items())),
            hashes=tuple(sorted(observed_hashes.items())),
            findings=result_findings,
        )


def _version(value: str | int, label: str) -> str:
    if type(value) is int:
        if value < 0:
            raise IntegrityScanError(f"{label} is invalid")
        return str(value)
    if not isinstance(value, str) or not value or len(value) > 32 or any(ord(char) < 32 for char in value):
        raise IntegrityScanError(f"{label} is invalid")
    return value


def _identifiers(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise IntegrityScanError(f"{label} must be a collection")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise IntegrityScanError(f"{label} must be iterable") from exc
    if len(normalized) > MAX_ITEMS or len(normalized) != len(set(normalized)):
        raise IntegrityScanError(f"{label} are invalid")
    if any(not isinstance(value, str) or not _IDENTIFIER.fullmatch(value) for value in normalized):
        raise IntegrityScanError(f"{label} are invalid")
    return normalized


def _versions(values: Mapping[str, str | int], label: str) -> dict[str, str]:
    if not isinstance(values, Mapping) or len(values) > MAX_ITEMS:
        raise IntegrityScanError(f"{label} are invalid")
    result: dict[str, str] = {}
    for name, value in values.items():
        key = _identifiers((name,), label)[0]
        result[key] = _version(value, f"{label} version")
    return result


def _queues(values: Mapping[str, int]) -> dict[str, int]:
    if not isinstance(values, Mapping) or len(values) > MAX_ITEMS:
        raise IntegrityScanError("queues are invalid")
    result: dict[str, int] = {}
    for name, depth in values.items():
        key = _identifiers((name,), "queue names")[0]
        if type(depth) is not int or not 0 <= depth <= MAX_QUEUE_DEPTH:
            raise IntegrityScanError("queue depth is invalid")
        result[key] = depth
    return result


def _hashes(values: Mapping[str, str], label: str) -> dict[str, str]:
    if not isinstance(values, Mapping) or len(values) > MAX_ITEMS:
        raise IntegrityScanError(f"{label} are invalid")
    result: dict[str, str] = {}
    for name, digest in values.items():
        key = _identifiers((name,), label)[0]
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise IntegrityScanError(f"{label} contain an invalid SHA-256")
        result[key] = digest
    return result


def _mapping_findings(
    kind: str,
    expected: Mapping[str, str],
    observed: Mapping[str, str],
) -> list[str]:
    findings: list[str] = []
    for name in sorted(set(expected) - set(observed)):
        findings.append(f"{kind}_missing:{name}")
    for name in sorted(set(observed) - set(expected)):
        findings.append(f"{kind}_unexpected:{name}")
    for name in sorted(set(expected) & set(observed)):
        if expected[name] != observed[name]:
            findings.append(f"{kind}_mismatch:{name}")
    return findings


def _hash_findings(expected: Mapping[str, str], observed: Mapping[str, str]) -> list[str]:
    findings: list[str] = []
    for name in sorted(set(expected) - set(observed)):
        findings.append(f"hash_missing:{name}")
    for name in sorted(set(observed) - set(expected)):
        findings.append(f"hash_unexpected:{name}")
    for name in sorted(set(expected) & set(observed)):
        if expected[name] != observed[name]:
            findings.append(f"hash_mismatch:{name}")
    return findings


__all__ = ["IntegrityReport", "IntegrityScanError", "IntegrityScanner"]
