"""Bounded local AEGIS model selection and health probing."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import re
import subprocess


DEFAULT_MODEL = "qwen3:4b"
PROBE_TIMEOUT_SECONDS = 20
_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,79}$")


class GuardianModelError(ValueError):
    """Raised when a local Guardian model configuration is invalid."""


@dataclass(frozen=True)
class GuardianModelHealth:
    """Digest-free health metadata; model output is never retained."""

    provider: str
    model: str
    available: bool
    inference_verified: bool
    deterministic_stop_available: bool
    reason: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _model(value: str) -> str:
    if not isinstance(value, str) or not _MODEL.fullmatch(value):
        raise GuardianModelError("invalid local Guardian model")
    return value


class LocalGuardianModel:
    """Probe exactly one installed Ollama model without any provider fallback."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        runner: Callable[[list[str], int], int] | None = None,
        timeout_seconds: int = PROBE_TIMEOUT_SECONDS,
    ) -> None:
        self.model = _model(model)
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 120:
            raise GuardianModelError("probe timeout is outside the bounded range")
        self.timeout_seconds = timeout_seconds
        self._runner = runner or self._run

    def probe(self, *, verify_inference: bool = True) -> GuardianModelHealth:
        """Return bounded health metadata and discard all command output."""
        if self._runner(["ollama", "show", self.model], self.timeout_seconds) != 0:
            return self._health(False, False, "model_unavailable")
        if verify_inference and self._runner(
            ["ollama", "run", self.model, "Reply READY only"], self.timeout_seconds
        ) != 0:
            return self._health(False, False, "inference_unavailable")
        return self._health(True, verify_inference, "local_model_verified")

    def _health(self, available: bool, inference_verified: bool, reason: str) -> GuardianModelHealth:
        return GuardianModelHealth(
            provider="ollama",
            model=self.model,
            available=available,
            inference_verified=inference_verified,
            deterministic_stop_available=True,
            reason=reason,
        )

    def _run(self, command: list[str], timeout_seconds: int) -> int:
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return 1
        return result.returncode


__all__ = [
    "DEFAULT_MODEL",
    "GuardianModelError",
    "GuardianModelHealth",
    "LocalGuardianModel",
    "PROBE_TIMEOUT_SECONDS",
]
