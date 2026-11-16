"""Fail-closed launcher for an immutable, externally managed controller."""
from __future__ import annotations

from collections.abc import Callable, Sequence
import argparse
from hashlib import sha256
from pathlib import Path
import re
import stat
import subprocess
from typing import Any


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CONTROL_MARKERS = ("STOP", "PAUSE", "PAUSED_QUOTA")
_SAFE_ENV = {"PATH": "/usr/bin:/bin"}


class GuardianControllerError(ValueError):
    """Raised when a trusted controller cannot be verified or started."""


Runner = Callable[[tuple[str, ...], Path], int]


class TrustedControllerManager:
    """Verify and launch one pinned controller without changing control state.

    The manager never stops an existing process or changes a service pointer.
    The external service manager is responsible for fencing the old instance;
    this class only permits a fresh launch after the immutable artifact and
    STOP/PAUSE controls have been checked.
    """

    def __init__(
        self,
        executable: str | Path,
        expected_sha256: str,
        *,
        trusted_root: str | Path,
        control_dir: str | Path | None = None,
        command: Sequence[str] | None = None,
        runner: Runner | None = None,
    ) -> None:
        self.executable = Path(executable)
        self.trusted_root = Path(trusted_root)
        if not self.executable.is_absolute() or not self.trusted_root.is_absolute():
            raise GuardianControllerError("controller paths must be absolute")
        if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
            raise GuardianControllerError("invalid controller digest")
        self.expected_sha256 = expected_sha256
        self._trusted_root = self.trusted_root.resolve(strict=False)
        self.control_dir = (
            None if control_dir is None else Path(control_dir).resolve(strict=False)
        )
        values = (str(self.executable),) if command is None else tuple(command)
        self.command = self._validate_command(values)
        self._runner = runner or self._spawn

    def verify(self) -> dict[str, Any]:
        """Return bounded verification metadata without starting anything."""
        result: dict[str, Any] = {
            "trusted": False,
            "reason": "unverified",
            "artifact_sha256": "",
            "expected_sha256": self.expected_sha256,
        }
        active_controls = self._active_markers()
        if active_controls:
            result["reason"] = "control_marker_active"
            result["active_controls"] = active_controls
            return result
        try:
            if self.executable.is_symlink():
                result["reason"] = "controller_symlink"
                return result
            resolved = self.executable.resolve(strict=True)
            if not resolved.is_relative_to(self._trusted_root):
                result["reason"] = "controller_outside_trusted_root"
                return result
            info = resolved.stat()
            if not stat.S_ISREG(info.st_mode):
                result["reason"] = "controller_not_regular_file"
                return result
            if not info.st_mode & 0o111:
                result["reason"] = "controller_not_executable"
                return result
            if info.st_mode & 0o022:
                result["reason"] = "controller_writable_by_other_identity"
                return result
            digest = _sha256(resolved)
        except (OSError, RuntimeError):
            result["reason"] = "controller_unavailable"
            return result
        result["artifact_sha256"] = digest
        if digest != self.expected_sha256:
            result["reason"] = "controller_digest_mismatch"
            return result
        result["trusted"] = True
        result["reason"] = "trusted_immutable_controller"
        return result

    def restart(self) -> dict[str, Any]:
        """Launch the verified controller; never bypass an active control."""
        verification = self.verify()
        if not verification["trusted"]:
            raise GuardianControllerError(str(verification["reason"]))
        try:
            pid = self._runner(self.command, self._trusted_root)
        except (OSError, subprocess.SubprocessError) as exc:
            raise GuardianControllerError("trusted controller launch failed") from exc
        return {
            "status": "started",
            "pid": pid if type(pid) is int and pid > 0 else None,
            "artifact_sha256": verification["artifact_sha256"],
            "reason": verification["reason"],
        }

    def _active_markers(self) -> tuple[str, ...]:
        if self.control_dir is None:
            return ()
        return tuple(
            marker
            for marker in _CONTROL_MARKERS
            if (self.control_dir / marker).exists()
        )

    def _validate_command(self, command: tuple[str, ...]) -> tuple[str, ...]:
        if not command or command[0] != str(self.executable) or len(command) > 32:
            raise GuardianControllerError("command must start with the pinned controller")
        for argument in command:
            if not isinstance(argument, str) or not argument or len(argument) > 512:
                raise GuardianControllerError("invalid controller command")
            if any(ord(char) < 32 for char in argument):
                raise GuardianControllerError("invalid controller command")
        return command

    @staticmethod
    def _spawn(command: tuple[str, ...], cwd: Path) -> int:
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            env=dict(_SAFE_ENV),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
            shell=False,
        )
        return process.pid


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    """Run one fail-closed launch attempt for the reviewed service unit."""
    parser = argparse.ArgumentParser(prog="archon-guardian-manager")
    parser.add_argument("--trusted-root", required=True, type=Path)
    parser.add_argument("--controller", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--control-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        TrustedControllerManager(
            args.controller,
            args.sha256,
            trusted_root=args.trusted_root,
            control_dir=args.control_dir,
        ).restart()
    except GuardianControllerError:
        return 1
    return 0


__all__ = ["GuardianControllerError", "TrustedControllerManager", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
