"""Validated Linux Ollama inference profiles and digest-free probe evidence."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
import re
from typing import Any


_MODEL = re.compile(r"^qwen3:[A-Za-z0-9._-]{1,32}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
KV_CACHE_TYPES = frozenset({"f16", "q4_0", "q8_0"})
ACCELERATOR_STATES = frozenset({"cpu", "cuda", "metal", "rocm", "unknown", "unavailable"})
ERROR_CATEGORIES = frozenset({"configuration", "input", "provider", "resource", "transport", "unknown"})
_RESOURCE_LIMIT_KEYS = frozenset({"max_gpu_layers", "num_ctx", "num_thread", "num_gpu"})


class OllamaProfileError(ValueError):
    """Raised when a local Ollama profile or probe is not trustworthy."""


def _non_negative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise OllamaProfileError(f"{label} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class OllamaInferenceProfile:
    """Bounded Linux-local Ollama settings for one model request."""

    model: str = "qwen3:8b"
    num_ctx: int = 16_384
    num_predict: int = 128
    kv_cache_type: str = "q8_0"
    flash_attn: bool = True
    platform: str = "linux"

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not _MODEL.fullmatch(self.model):
            raise OllamaProfileError("model must be a Qwen3 Ollama model")
        if type(self.num_ctx) is not int or not 1_024 <= self.num_ctx <= 131_072:
            raise OllamaProfileError("num_ctx is outside the bounded range")
        if type(self.num_predict) is not int or not 1 <= self.num_predict <= 4_096:
            raise OllamaProfileError("num_predict is outside the bounded range")
        if self.kv_cache_type not in KV_CACHE_TYPES:
            raise OllamaProfileError("kv_cache_type is not supported")
        if type(self.flash_attn) is not bool:
            raise OllamaProfileError("flash_attn must be boolean")
        if self.platform != "linux":
            raise OllamaProfileError("this profile is Linux-only")

    def options(self) -> dict[str, object]:
        """Return the exact bounded Ollama options without response data."""
        return {
            "num_ctx": self.num_ctx,
            "num_predict": self.num_predict,
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


@dataclass(frozen=True)
class OllamaErrorEvidence:
    """Redacted error attribution without retaining provider error text."""

    category: str
    retryable: bool

    def __post_init__(self) -> None:
        if self.category not in ERROR_CATEGORIES:
            raise OllamaProfileError("error category is not supported")
        if type(self.retryable) is not bool:
            raise OllamaProfileError("retryable must be boolean")

    def as_dict(self) -> dict[str, object]:
        return {"category": self.category, "retryable": self.retryable}


@dataclass(frozen=True)
class OllamaTelemetry:
    """Measured Linux telemetry with explicit unavailable capability states."""

    profile: OllamaInferenceProfile
    context_tokens: int
    prompt_tokens: int
    generated_tokens: int
    prompt_tokens_per_second: float | None
    generated_tokens_per_second: float | None
    accelerator: str
    resource_limits: tuple[tuple[str, int], ...]
    total_duration_ns: int
    error: OllamaErrorEvidence | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile, OllamaInferenceProfile):
            raise OllamaProfileError("profile is required")
        for value, label in (
            (self.context_tokens, "context_tokens"),
            (self.prompt_tokens, "prompt_tokens"),
            (self.generated_tokens, "generated_tokens"),
            (self.total_duration_ns, "total_duration_ns"),
        ):
            _non_negative_int(value, label)
        if self.total_duration_ns == 0:
            raise OllamaProfileError("telemetry duration is missing")
        if self.accelerator not in ACCELERATOR_STATES:
            raise OllamaProfileError("accelerator state is not supported")
        for key, value in self.resource_limits:
            if key not in _RESOURCE_LIMIT_KEYS or type(value) is not int or value < 0:
                raise OllamaProfileError("resource limit is invalid")
        for value, label in (
            (self.prompt_tokens_per_second, "prompt token rate"),
            (self.generated_tokens_per_second, "generated token rate"),
        ):
            if value is not None and (not math.isfinite(value) or value < 0):
                raise OllamaProfileError(f"{label} is invalid")

    def as_dict(self) -> dict[str, object]:
        return {
            "profile": self.profile.as_dict(),
            "context_tokens": self.context_tokens,
            "prompt_tokens": self.prompt_tokens,
            "generated_tokens": self.generated_tokens,
            "prompt_tokens_per_second": self.prompt_tokens_per_second,
            "generated_tokens_per_second": self.generated_tokens_per_second,
            "accelerator": self.accelerator,
            "resource_limits": dict(self.resource_limits),
            "total_duration_ns": self.total_duration_ns,
            "error": self.error.as_dict() if self.error else None,
        }


def _duration(payload: Mapping[str, object], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    return _non_negative_int(value, key)


def _rate(count: int, duration_ns: int | None) -> float | None:
    if duration_ns in (None, 0):
        return None
    return count / (duration_ns / 1_000_000_000)


def classify_ollama_error(payload: Mapping[str, object]) -> OllamaErrorEvidence:
    """Require an explicit category while keeping provider text out of evidence."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("error"), str) or not payload["error"]:
        raise OllamaProfileError("error payload is missing")
    category = payload.get("error_category")
    retryable = payload.get("retryable", False)
    if not isinstance(category, str) or category not in ERROR_CATEGORIES:
        raise OllamaProfileError("error category is missing or invalid")
    return OllamaErrorEvidence(category, retryable)


def parse_ollama_telemetry(
    payload: Mapping[str, object],
    profile: OllamaInferenceProfile,
) -> OllamaTelemetry:
    """Parse bounded response counters; raw context and error text are discarded."""
    if not isinstance(payload, Mapping) or not isinstance(profile, OllamaInferenceProfile):
        raise OllamaProfileError("telemetry payload and profile are required")
    if payload.get("error") is not None:
        raise OllamaProfileError("successful telemetry cannot contain an error")
    if payload.get("model") != profile.model or payload.get("done") is not True:
        raise OllamaProfileError("telemetry identity or completion marker is invalid")
    context = payload.get("context", [])
    if not isinstance(context, list) or any(type(item) is not int or item < 0 for item in context):
        raise OllamaProfileError("context telemetry is invalid")
    prompt_tokens = _non_negative_int(payload.get("prompt_eval_count"), "prompt_eval_count")
    generated_tokens = _non_negative_int(payload.get("eval_count"), "eval_count")
    total_duration_ns = _non_negative_int(payload.get("total_duration"), "total_duration")
    if total_duration_ns == 0:
        raise OllamaProfileError("telemetry duration is missing")
    limits: dict[str, int] = {"num_ctx": profile.num_ctx}
    supplied_limits = payload.get("resource_limits", {})
    if not isinstance(supplied_limits, Mapping):
        raise OllamaProfileError("resource limits are invalid")
    for key, value in supplied_limits.items():
        if key not in _RESOURCE_LIMIT_KEYS or type(value) is not int or value < 0:
            raise OllamaProfileError("resource limit is invalid")
        limits[key] = value
    accelerator = payload.get("accelerator", "unavailable")
    if not isinstance(accelerator, str) or accelerator.casefold() not in ACCELERATOR_STATES:
        raise OllamaProfileError("accelerator state is invalid")
    return OllamaTelemetry(
        profile=profile,
        context_tokens=len(context),
        prompt_tokens=prompt_tokens,
        generated_tokens=generated_tokens,
        prompt_tokens_per_second=_rate(prompt_tokens, _duration(payload, "prompt_eval_duration")),
        generated_tokens_per_second=_rate(generated_tokens, _duration(payload, "eval_duration")),
        accelerator=accelerator.casefold(),
        resource_limits=tuple(sorted(limits.items())),
        total_duration_ns=total_duration_ns,
    )


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
    "ACCELERATOR_STATES",
    "ERROR_CATEGORIES",
    "OllamaErrorEvidence",
    "OllamaInferenceProfile",
    "OllamaProbeEvidence",
    "OllamaProfileError",
    "OllamaTelemetry",
    "classify_ollama_error",
    "parse_ollama_probe",
    "parse_ollama_telemetry",
]
