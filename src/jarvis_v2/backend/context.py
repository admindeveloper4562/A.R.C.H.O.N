"""Bounded context packing with non-compressible requirements and policy."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
import re
from typing import Any


MAX_CONTEXT_BYTES = 256 * 1024
MAX_CONTEXT_TOKENS = 65_536
DEFAULT_CONTEXT_TOKENS = 8_192
CHARS_PER_TOKEN = 4
_SENSITIVE_KEY = re.compile(r"(?i)(?:raw[_. -]?(?:prompt|log|model[_. -]?output)|private[_. -]?key|password|secret[_. -]?value)")


class ContextPackError(ValueError):
    """Raised when a bounded context packet cannot preserve protected data."""


def estimate_tokens(value: str) -> int:
    """Return a conservative, deterministic token estimate for UTF-8 text."""
    if not isinstance(value, str):
        raise ContextPackError("serialized context must be text")
    size = len(value.encode("utf-8"))
    return max(1, (size + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)


def _json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ContextPackError(f"{label} must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_CONTEXT_BYTES:
        raise ContextPackError(f"{label} exceeds bounded size")
    _reject_sensitive_keys(value, label)
    return encoded


def _reject_sensitive_keys(value: object, label: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str) or _SENSITIVE_KEY.search(key):
                raise ContextPackError(f"{label} contains a restricted field")
            _reject_sensitive_keys(child, label)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_sensitive_keys(child, label)


def _sequence(value: Sequence[Any] | None, label: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        raise ContextPackError(f"{label} must be a sequence")
    result = list(value)
    _json(result, label)
    return result


class ContextPacker:
    """Build a restartable context packet without dropping protected facts."""

    def __init__(self, *, default_max_tokens: int = DEFAULT_CONTEXT_TOKENS) -> None:
        self._validate_budget(default_max_tokens)
        self.default_max_tokens = default_max_tokens

    def pack(
        self,
        requirements: object,
        policy: object,
        recent_receipts: Sequence[Any] | None = None,
        history: Sequence[Any] | None = None,
        *,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Return a bounded packet while preserving all protected sections.

        ``history`` is optional context and may be shortened from oldest to
        newest. Requirements, policy and every supplied receipt are protected;
        if those sections alone exceed the budget, packing fails rather than
        silently weakening the task contract.
        """
        budget = self.default_max_tokens if max_tokens is None else max_tokens
        self._validate_budget(budget)
        requirements_json = _json(requirements, "requirements")
        policy_json = _json(policy, "policy")
        receipts = _sequence(recent_receipts, "recent_receipts")
        history_items = _sequence(history, "history")
        protected = {
            "requirements": json.loads(requirements_json),
            "policy": json.loads(policy_json),
            "recent_receipts": receipts,
        }
        protected_json = _json(protected, "protected context")
        if estimate_tokens(protected_json) > budget:
            raise ContextPackError("protected context exceeds token budget")

        included: list[Any] = []
        for item in reversed(history_items):
            candidate = list(reversed([*included, item]))
            packet = self._packet(protected, candidate, dropped=len(history_items) - len(candidate))
            if estimate_tokens(_json(packet, "context packet")) > budget:
                break
            included.append(item)
        included.reverse()
        protected_sha = hashlib.sha256(protected_json.encode("utf-8")).hexdigest()
        while True:
            dropped = len(history_items) - len(included)
            packet = self._packet(protected, included, dropped=dropped)
            serialized = _json(packet, "context packet")
            packet["metadata"] = {
                "estimated_tokens": 0,
                "history_items": len(included),
                "history_items_dropped": dropped,
                "protected_sha256": protected_sha,
            }
            final_serialized = _json(packet, "context packet")
            packet["metadata"]["estimated_tokens"] = estimate_tokens(final_serialized)
            final_serialized = _json(packet, "context packet")
            if estimate_tokens(final_serialized) <= budget:
                return packet
            if not included:
                raise ContextPackError("context metadata exceeds token budget")
            included.pop(0)

    @staticmethod
    def _packet(protected: Mapping[str, Any], history: list[Any], *, dropped: int) -> dict[str, Any]:
        return {
            "requirements": protected["requirements"],
            "policy": protected["policy"],
            "recent_receipts": protected["recent_receipts"],
            "history": history,
            "history_items_dropped": dropped,
        }

    @staticmethod
    def _validate_budget(value: int) -> None:
        if type(value) is not int or not 1 <= value <= MAX_CONTEXT_TOKENS:
            raise ContextPackError("token budget is outside the bounded range")


def pack_context(
    requirements: object,
    policy: object,
    recent_receipts: Sequence[Any] | None = None,
    history: Sequence[Any] | None = None,
    *,
    max_tokens: int = DEFAULT_CONTEXT_TOKENS,
) -> dict[str, Any]:
    """Functional convenience wrapper for one bounded context packet."""
    return ContextPacker(default_max_tokens=max_tokens).pack(
        requirements, policy, recent_receipts, history, max_tokens=max_tokens
    )


__all__ = [
    "CHARS_PER_TOKEN",
    "ContextPackError",
    "ContextPacker",
    "DEFAULT_CONTEXT_TOKENS",
    "MAX_CONTEXT_BYTES",
    "MAX_CONTEXT_TOKENS",
    "estimate_tokens",
    "pack_context",
]
