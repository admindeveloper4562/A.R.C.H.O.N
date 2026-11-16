"""Optional local reranking with bounded resource use and safe fallback."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import math
import queue
import re
import threading
import time
from typing import Any


class RerankingError(ValueError):
    """Raised when a reranking configuration is invalid."""


@dataclass(frozen=True)
class HardwareBudget:
    """Hard input and execution limits for an optional local reranker."""

    max_candidates: int = 32
    max_text_bytes: int = 128 * 1024
    max_memory_bytes: int = 512 * 1024
    max_time_ms: int = 100
    dimensions: int = 32

    def __post_init__(self) -> None:
        for name in (
            "max_candidates",
            "max_text_bytes",
            "max_memory_bytes",
            "max_time_ms",
            "dimensions",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise RerankingError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class RerankResult(Sequence[Mapping[str, Any]]):
    """Ordered candidates plus auditable fallback information."""

    items: tuple[Mapping[str, Any], ...]
    used_embeddings: bool
    fallback_reason: str | None
    elapsed_ms: float

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int | slice) -> Mapping[str, Any] | tuple[Mapping[str, Any], ...]:
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    @property
    def mode(self) -> str:
        return "embedding" if self.used_embeddings else "keyword"


_WORDS = re.compile(r"[\w]+", re.UNICODE)


def _keywords(value: str) -> list[str]:
    return _WORDS.findall(value.casefold())


def _keyword_order(query: str, candidates: tuple[Mapping[str, Any], ...], text_key: str) -> tuple[Mapping[str, Any], ...]:
    query_terms = set(_keywords(query))
    if not query_terms:
        return candidates
    scored: list[tuple[int, int, Mapping[str, Any]]] = []
    for index, candidate in enumerate(candidates):
        text = candidate.get(text_key, "")
        text = text if isinstance(text, str) else ""
        score = sum(1 for word in _keywords(text) if word in query_terms)
        scored.append((-score, index, candidate))
    scored.sort(key=lambda item: (item[0], item[1]))
    return tuple(item[2] for item in scored)


def _hashed_embedding(text: str, dimensions: int) -> tuple[float, ...]:
    """Create a deterministic local vector without downloading a model."""
    vector = [0.0] * dimensions
    for word in _keywords(text):
        digest = hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest()
        position = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[position] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return tuple(value / norm for value in vector) if norm else tuple(vector)


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


class LocalEmbeddingReranker:
    """Rerank bounded candidates with a local vectorizer or injected model.

    The optional model is never called when the input or hardware budget is
    exceeded. A failed or timed-out model call returns deterministic keyword
    ordering instead of silently selecting another provider.
    """

    def __init__(
        self,
        *,
        budget: HardwareBudget | None = None,
        embedder: Callable[[str], Sequence[float]] | None = None,
        enabled: bool = True,
        text_key: str = "snippet",
    ) -> None:
        self.budget = budget or HardwareBudget()
        if not callable(embedder) and embedder is not None:
            raise RerankingError("embedder must be callable")
        if type(enabled) is not bool:
            raise RerankingError("enabled must be boolean")
        if not isinstance(text_key, str) or not text_key or len(text_key) > 64:
            raise RerankingError("text key is invalid")
        self.embedder = embedder
        self.enabled = enabled
        self.text_key = text_key

    def rerank(
        self,
        query: str,
        candidates: Iterable[Mapping[str, Any]],
    ) -> RerankResult:
        started = time.monotonic()
        if not isinstance(query, str):
            raise RerankingError("query must be text")
        values = tuple(candidates)
        if any(not isinstance(candidate, Mapping) for candidate in values):
            raise RerankingError("candidates must be mappings")
        values = tuple(values)
        if not values:
            return self._result(values, False, None, started)
        if not self.enabled:
            return self._result(values, False, "disabled", started)
        if len(values) > self.budget.max_candidates:
            return self._fallback(query, values, "candidate_limit", started)

        texts: list[str] = []
        total_bytes = len(query.encode("utf-8"))
        for candidate in values:
            text = candidate.get(self.text_key, "")
            if not isinstance(text, str):
                return self._fallback(query, values, "invalid_text", started)
            texts.append(text)
            total_bytes += len(text.encode("utf-8"))
        vector_bytes = (len(values) + 1) * self.budget.dimensions * 8
        if total_bytes > self.budget.max_text_bytes or total_bytes + vector_bytes > self.budget.max_memory_bytes:
            return self._fallback(query, values, "memory_budget", started)

        embedder = self.embedder or (lambda value: _hashed_embedding(value, self.budget.dimensions))
        deadline = started + self.budget.max_time_ms / 1000
        vectors: list[tuple[float, ...]] = []
        for text in (query, *texts):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return self._fallback(query, values, "time_budget", started)
            vector, reason = self._bounded_embed(embedder, text, remaining)
            if vector is None:
                return self._fallback(query, values, reason or "embedding_error", started)
            vectors.append(vector)
        if len({len(vector) for vector in vectors}) != 1:
            return self._fallback(query, values, "embedding_error", started)
        vector_bytes = sum(len(vector) * 8 for vector in vectors)
        if total_bytes + vector_bytes > self.budget.max_memory_bytes:
            return self._fallback(query, values, "memory_budget", started)
        query_vector = vectors[0]
        ranked = sorted(
            enumerate(values),
            key=lambda item: (-_cosine(query_vector, vectors[item[0] + 1]), item[0]),
        )
        return self._result(tuple(item[1] for item in ranked), True, None, started)

    rank = rerank

    def _fallback(
        self,
        query: str,
        candidates: tuple[Mapping[str, Any], ...],
        reason: str,
        started: float,
    ) -> RerankResult:
        return self._result(_keyword_order(query, candidates, self.text_key), False, reason, started)

    @staticmethod
    def _bounded_embed(
        embedder: Callable[[str], Sequence[float]],
        text: str,
        timeout: float,
    ) -> tuple[tuple[float, ...] | None, str | None]:
        result: queue.Queue[tuple[str, object]] = queue.Queue(maxsize=1)

        def invoke() -> None:
            try:
                result.put(("ok", embedder(text)))
            except Exception as exc:  # model adapters must not escape into the caller
                result.put(("error", exc))

        thread = threading.Thread(target=invoke, daemon=True)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            return None, "time_budget"
        try:
            status, value = result.get_nowait()
        except queue.Empty:
            return None, "embedding_error"
        if status != "ok" or not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            return None, "embedding_error"
        vector = tuple(value)
        if not vector or len(vector) > 4096 or any(
            type(component) not in (int, float) or not math.isfinite(component)
            for component in vector
        ):
            return None, "embedding_error"
        return vector, None

    def _result(
        self,
        items: tuple[Mapping[str, Any], ...],
        used_embeddings: bool,
        fallback_reason: str | None,
        started: float,
    ) -> RerankResult:
        return RerankResult(
            items=items,
            used_embeddings=used_embeddings,
            fallback_reason=fallback_reason,
            elapsed_ms=(time.monotonic() - started) * 1000,
        )


EmbeddingReranker = LocalEmbeddingReranker
RerankerBudget = HardwareBudget


__all__ = [
    "EmbeddingReranker",
    "HardwareBudget",
    "LocalEmbeddingReranker",
    "RerankResult",
    "RerankerBudget",
    "RerankingError",
]
