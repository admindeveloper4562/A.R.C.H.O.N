"""Deterministic model-alias admission for Core routing decisions."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
import re


_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class ModelPolicyError(ValueError):
    """Raised when a model alias is not a valid bounded policy value."""


@dataclass(frozen=True)
class ModelResolution:
    """The bounded result of one model-routing decision."""

    requested: str
    selected: str | None
    status: str
    reason: str

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


class ModelPolicy:
    """Allow requested models only from an explicit availability set.

    Fallback is never inferred from the availability set: callers must name a
    fallback and opt in for that particular resolution.
    """

    def __init__(self, available_models: Iterable[str]) -> None:
        if isinstance(available_models, str):
            raise ModelPolicyError("available models must be an iterable")
        try:
            models = frozenset(self._alias(model) for model in available_models)
        except TypeError as exc:
            raise ModelPolicyError("available models must be an iterable") from exc
        self._available = models

    @property
    def available_models(self) -> frozenset[str]:
        return self._available

    def resolve(
        self,
        requested: str,
        *,
        fallback: str | None = None,
        allow_fallback: bool = False,
    ) -> ModelResolution:
        requested = self._alias(requested)
        if requested in self._available:
            return ModelResolution(requested, requested, "available", "requested_model")

        if not allow_fallback:
            return ModelResolution(requested, None, "blocked", "unsupported_model_alias")
        if fallback is None:
            return ModelResolution(requested, None, "blocked", "fallback_not_configured")
        fallback = self._alias(fallback)
        if fallback not in self._available:
            return ModelResolution(requested, None, "blocked", "fallback_unavailable")
        return ModelResolution(requested, fallback, "fallback", "explicit_fallback_policy")

    @staticmethod
    def _alias(value: str) -> str:
        if not isinstance(value, str) or not _MODEL.fullmatch(value):
            raise ModelPolicyError("invalid model alias")
        return value


__all__ = ["ModelPolicy", "ModelPolicyError", "ModelResolution"]
