"""Bounded Linux user-service profiles for safe local controller startup."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import re
import shlex


_UNIT = re.compile(r"^[a-z][a-z0-9@_.-]{0,62}\.service$")
_SHELLS = frozenset({"bash", "cmd", "fish", "powershell", "sh", "zsh"})


class LinuxServiceError(ValueError):
    """Raised when a Linux service profile or startup decision is unsafe."""


def _argument(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256 or any(ord(c) < 32 for c in value):
        raise LinuxServiceError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class LinuxServiceProfile:
    """A shell-free user service definition; installation remains external."""

    unit_name: str
    executable: str
    health_command: tuple[str, ...]
    restart_seconds: int = 5

    def __post_init__(self) -> None:
        if not isinstance(self.unit_name, str) or not _UNIT.fullmatch(self.unit_name):
            raise LinuxServiceError("invalid unit name")
        if not isinstance(self.executable, str) or not Path(self.executable).is_absolute():
            raise LinuxServiceError("service executable must be absolute")
        _argument(self.executable, "service executable")
        command = tuple(self.health_command)
        if not 1 <= len(command) <= 16 or any(not isinstance(item, str) for item in command):
            raise LinuxServiceError("health command is invalid")
        for item in command:
            _argument(item, "health command argument")
        if Path(command[0]).name in _SHELLS:
            raise LinuxServiceError("health command must not invoke a shell")
        if type(self.restart_seconds) is not int or not 1 <= self.restart_seconds <= 300:
            raise LinuxServiceError("restart interval is outside the bounded range")
        object.__setattr__(self, "health_command", command)

    def render(self) -> str:
        """Render a user-unit without shell evaluation or secret material."""
        return "\n".join((
            "[Unit]",
            f"Description=ARCHON {self.unit_name}",
            "After=default.target",
            "",
            "[Service]",
            f"ExecStart={shlex.join((self.executable,))}",
            f"ExecStartPost={shlex.join(self.health_command)}",
            "Restart=on-failure",
            f"RestartSec={self.restart_seconds}",
            "NoNewPrivileges=yes",
            "PrivateTmp=yes",
            "ProtectSystem=strict",
            "ProtectHome=read-only",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ))


def startup_decision(
    profile: LinuxServiceProfile,
    active_units: Mapping[str, object],
    health_ok: bool,
) -> str:
    """Return a deterministic action without starting or stopping a process."""
    if not isinstance(profile, LinuxServiceProfile) or not isinstance(active_units, Mapping):
        raise LinuxServiceError("service state is required")
    active = active_units.get(profile.unit_name, 0)
    if type(active) is not int or active < 0:
        raise LinuxServiceError("active unit count is invalid")
    if active > 1:
        raise LinuxServiceError("duplicate service instances detected")
    if active == 1:
        return "already_running" if health_ok is True else "health_failed"
    return "start" if health_ok is True else "health_failed"


__all__ = ["LinuxServiceError", "LinuxServiceProfile", "startup_decision"]
