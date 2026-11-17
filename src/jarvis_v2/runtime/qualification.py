"""Bounded host-acceptance records for Runtime qualification."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import re


ACCEPTANCE_GATES = tuple(f"AC-{index:02d}" for index in range(1, 13))
QUALIFICATION_STATUSES = frozenset({
    "passed", "failed", "blocked", "unavailable", "not_run",
})
_GATE = re.compile(r"^AC-(?:0[1-9]|1[0-2])$")
_SHA = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
_MAX_COMMAND = 256
_MAX_REFERENCE = 256
_MAX_NOTE = 512


class HostQualificationError(ValueError):
    """Raised when host-acceptance evidence is malformed or incomplete."""


def _text(value: str, label: str, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise HostQualificationError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class HostAcceptanceRecord:
    """One source-bound acceptance observation without raw command output."""

    gate_id: str
    status: str
    evidence_ref: str
    commands: tuple[str, ...] = ()
    note: str = ""
    exit_code: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.gate_id, str) or not _GATE.fullmatch(self.gate_id):
            raise HostQualificationError("invalid acceptance gate")
        if self.status not in QUALIFICATION_STATUSES:
            raise HostQualificationError("invalid qualification status")
        if isinstance(self.commands, (str, bytes)):
            raise HostQualificationError("commands must be a collection")
        try:
            commands = tuple(self.commands)
        except TypeError as exc:
            raise HostQualificationError("commands must be a collection") from exc
        if len(commands) > 16:
            raise HostQualificationError("too many qualification commands")
        normalized = tuple(_text(command, "command", _MAX_COMMAND) for command in commands)
        if len(set(normalized)) != len(normalized):
            raise HostQualificationError("duplicate qualification command")
        _text(self.evidence_ref, "evidence reference", _MAX_REFERENCE)
        if self.note:
            _text(self.note, "qualification note", _MAX_NOTE)
        if self.exit_code is not None and (
            type(self.exit_code) is not int or not 0 <= self.exit_code <= 255
        ):
            raise HostQualificationError("invalid command exit code")
        if self.status == "passed" and self.exit_code not in (None, 0):
            raise HostQualificationError("passed evidence has a failing exit code")
        object.__setattr__(self, "commands", normalized)

    def as_dict(self) -> dict[str, object]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "evidence_ref": self.evidence_ref,
            "commands": list(self.commands),
            "note": self.note,
            "exit_code": self.exit_code,
        }


@dataclass(frozen=True)
class HostQualificationReport:
    """Complete AC-01..AC-12 report; missing gates are never implicit passes."""

    host: str
    platform: str
    source_sha: str
    captured_at: datetime
    checks: tuple[HostAcceptanceRecord, ...]

    def __post_init__(self) -> None:
        _text(self.host, "host", 128)
        _text(self.platform, "platform", 128)
        if not isinstance(self.source_sha, str) or not _SHA.fullmatch(self.source_sha):
            raise HostQualificationError("source SHA must be a full Git SHA")
        if not isinstance(self.captured_at, datetime) or self.captured_at.tzinfo is None:
            raise HostQualificationError("captured_at must be timezone-aware")
        if isinstance(self.checks, (str, bytes)):
            raise HostQualificationError("checks must be a collection")
        try:
            checks = tuple(self.checks)
        except TypeError as exc:
            raise HostQualificationError("checks must be a collection") from exc
        if len(checks) != len(ACCEPTANCE_GATES) or any(
            not isinstance(check, HostAcceptanceRecord) for check in checks
        ):
            raise HostQualificationError("exactly twelve acceptance records are required")
        gate_ids = tuple(check.gate_id for check in checks)
        if set(gate_ids) != set(ACCEPTANCE_GATES):
            raise HostQualificationError("acceptance records must cover AC-01..AC-12 exactly once")
        if len(gate_ids) != len(set(gate_ids)):
            raise HostQualificationError("duplicate acceptance gate")
        object.__setattr__(self, "captured_at", self.captured_at.astimezone(timezone.utc))
        object.__setattr__(self, "checks", tuple(sorted(checks, key=lambda check: check.gate_id)))

    @property
    def all_passed(self) -> bool:
        return all(check.status == "passed" for check in self.checks)

    @property
    def unresolved_gates(self) -> tuple[str, ...]:
        return tuple(check.gate_id for check in self.checks if check.status != "passed")

    def as_dict(self) -> dict[str, object]:
        return {
            "host": self.host,
            "platform": self.platform,
            "source_sha": self.source_sha,
            "captured_at": self.captured_at.isoformat().replace("+00:00", "Z"),
            "all_passed": self.all_passed,
            "unresolved_gates": list(self.unresolved_gates),
            "checks": [check.as_dict() for check in self.checks],
        }


def build_host_qualification_report(
    host: str,
    platform: str,
    source_sha: str,
    checks: Iterable[HostAcceptanceRecord],
    *,
    captured_at: datetime | None = None,
) -> HostQualificationReport:
    """Build a complete report from explicit observations supplied by a probe."""

    return HostQualificationReport(
        host=host,
        platform=platform,
        source_sha=source_sha,
        captured_at=captured_at or datetime.now(timezone.utc),
        checks=tuple(checks),
    )


__all__ = [
    "ACCEPTANCE_GATES",
    "QUALIFICATION_STATUSES",
    "HostAcceptanceRecord",
    "HostQualificationError",
    "HostQualificationReport",
    "build_host_qualification_report",
]
