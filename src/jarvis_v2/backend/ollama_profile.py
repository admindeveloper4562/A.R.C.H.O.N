"""Validated Linux Ollama inference profiles and digest-free probe evidence."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any


_MODEL = re.compile(r"^qwen3:[A-Za-z0-9._-]{1,32}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
KV_CACHE_TYPES = frozenset({"f16", "q4_0", "q8_0"})


class OllamaProfileError(ValueError):
    """Raised when a local Ollama profile or probe is not trustworthy."""


def _non_negative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise OllamaProfileError(f"{label} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class OllamaInferenceProfile:
    """The bounded options used for one Linux-local Ollama probe."""

    model: str = "qwen3:8b"
    num_ctx: int = 16_384
    kv_cache_type: str = "q8_0"
    flash_attn: bool = True
    platform: str = "linux"

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not _MODEL.fullmatch(self.model):
            raise OllamaProfileError("model must be a Qwen3 Ollama model")
        if type(self.num_ctx) is not int or not 1_024 <= self.num_ctx <= 131_072:
            raise OllamaProfileError("num_ctx is outside the bounded range")
        if self.kv_cache_type not in KV_CACHE_TYPES:
            raise OllamaProfileError("kv_cache_type is not supported")
        if type(self.flash_attn) is not bool:
            raise OllamaProfileError("flash_attn must be boolean")
        if self.platform != "linux":
            raise OllamaProfileError("this profile is Linux-only")

    def options(self) -> dict[str, object]:
        """Return the exact Ollama options without provider response data."""
        return {
            "num_ctx": self.num_ctx,
            "kv_cache_type": self.kv_cache_type,
            "flash_attn": self.flash_attn,
        }

    def as_dict(self) -> dict[str, object]:
        return {"model": self.model, "platform": self.platform, **self.options()}


@dataclass(frozen=True)
class OllamaProbeEvidence:
    """Redacted, measured probe result suitable for an acceptance receipt."""

    profile: OllamaInferenceProfile
    marker: str
    total_duration_ns: int
    prompt_eval_count: int
    eval_count: int
    artifact_sha256: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile, OllamaInferenceProfile):
            raise OllamaProfileError("profile is required")
        if self.marker != "READY":
            raise OllamaProfileError("probe marker is not READY")
        for value, label in (
            (self.total_duration_ns, "total_duration_ns"),
            (self.prompt_eval_count, "prompt_eval_count"),
            (self.eval_count, "eval_count"),
        ):
            _non_negative_int(value, label)
        if self.total_duration_ns == 0:
            raise OllamaProfileError("probe duration is missing")
        if self.artifact_sha256 is not None and not _SHA256.fullmatch(self.artifact_sha256):
            raise OllamaProfileError("artifact_sha256 is invalid")

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "profile": self.profile.as_dict(),
            "marker": self.marker,
            "total_duration_ns": self.total_duration_ns,
            "prompt_eval_count": self.prompt_eval_count,
            "eval_count": self.eval_count,
        }
        if self.artifact_sha256 is not None:
            result["artifact_sha256"] = self.artifact_sha256
        return result


def parse_ollama_probe(
    payload: Mapping[str, object],
    profile: OllamaInferenceProfile,
    *,
    expected_marker: str = "READY",
    artifact_sha256: str | None = None,
) -> OllamaProbeEvidence:
    """Validate one final Ollama response without retaining its raw text."""
    if not isinstance(payload, Mapping) or not isinstance(profile, OllamaInferenceProfile):
        raise OllamaProfileError("probe payload and profile are required")
    if expected_marker != "READY":
        raise OllamaProfileError("only the READY probe marker is accepted")
    if payload.get("model") != profile.model or payload.get("done") is not True:
        raise OllamaProfileError("probe identity or completion marker is invalid")
    marker = payload.get("response")
    if not isinstance(marker, str):
        message = payload.get("message")
        marker = message.get("content") if isinstance(message, Mapping) else None
    if marker != expected_marker:
        raise OllamaProfileError("probe response marker is invalid")
    return OllamaProbeEvidence(
        profile=profile,
        marker=marker,
        total_duration_ns=_non_negative_int(payload.get("total_duration"), "total_duration"),
        prompt_eval_count=_non_negative_int(payload.get("prompt_eval_count"), "prompt_eval_count"),
        eval_count=_non_negative_int(payload.get("eval_count"), "eval_count"),
        artifact_sha256=artifact_sha256,
    )


__all__ = [
    "KV_CACHE_TYPES",
    "OllamaInferenceProfile",
    "OllamaProbeEvidence",
    "OllamaProfileError",
    "parse_ollama_probe",
]
