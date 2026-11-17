"""Deterministic source comparison with explicit uncertainty for conflicts."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import hashlib
import re


MAX_CLAIMS = 128
MAX_TEXT_BYTES = 4096
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class ComparisonError(ValueError):
    """Raised when a source claim is malformed or outside the bounded scope."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ComparisonError(f"invalid {label}")
    return value


def _text(value: object, label: str, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > MAX_TEXT_BYTES
        or any(ord(char) < 32 for char in value)
    ):
        raise ComparisonError(f"invalid {label}")
    return value


def _confidence(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ComparisonError("confidence is outside the bounded range")
    return float(value)


@dataclass(frozen=True)
class SourceClaim:
    """One source-backed assertion; it contains no permission decision."""

    subject: str
    assertion: str
    source_id: str
    citation: str
    observed_at: str
    source_date: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        _text(self.subject, "subject")
        _text(self.assertion, "assertion")
        _identifier(self.source_id, "source id")
        _text(self.citation, "citation")
        _text(self.observed_at, "observed timestamp")
        if self.source_date is not None:
            _text(self.source_date, "source date")
        object.__setattr__(self, "confidence", _confidence(self.confidence))

    def evidence_ref(self) -> str:
        return f"{self.source_id}:{self.citation}"


@dataclass(frozen=True)
class ResearchFinding:
    """Comparison output with provenance and an honest confidence value."""

    finding_id: str
    subject: str
    assertion: str | None
    claim_kind: str
    confidence: float | None
    source_ids: tuple[str, ...]
    citations: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    contradictory_assertions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _identifier(self.finding_id, "finding id")
        _text(self.subject, "subject")
        if self.assertion is not None:
            _text(self.assertion, "assertion")
        if self.claim_kind not in {"fact", "inference", "uncertain"}:
            raise ComparisonError("invalid claim kind")
        confidence = _confidence(self.confidence)
        if self.claim_kind == "uncertain" and confidence is not None:
            raise ComparisonError("uncertain findings cannot claim confidence")
        if not self.source_ids or len(self.source_ids) != len(self.citations):
            raise ComparisonError("finding provenance is incomplete")
        for value in self.source_ids:
            _identifier(value, "source id")
        for value in self.citations:
            _text(value, "citation")
        if len(self.evidence_refs) != len(self.source_ids):
            raise ComparisonError("finding evidence is incomplete")
        for value in self.evidence_refs:
            _text(value, "evidence reference")
        for value in self.contradictory_assertions:
            _text(value, "contradictory assertion")
        object.__setattr__(self, "confidence", confidence)

    def as_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "subject": self.subject,
            "assertion": self.assertion,
            "claim_kind": self.claim_kind,
            "confidence": self.confidence,
            "source_ids": list(self.source_ids),
            "citations": list(self.citations),
            "evidence_refs": list(self.evidence_refs),
            "contradictory_assertions": list(self.contradictory_assertions),
        }


@dataclass(frozen=True)
class SourceComparisonResult:
    status: str
    findings: tuple[ResearchFinding, ...]

    def __post_init__(self) -> None:
        if self.status not in {"empty", "consistent", "contradictory"}:
            raise ComparisonError("invalid comparison status")
        if any(not isinstance(item, ResearchFinding) for item in self.findings):
            raise ComparisonError("invalid comparison finding")

    def as_dict(self) -> dict[str, object]:
        return {"status": self.status, "findings": [item.as_dict() for item in self.findings]}


class SourceComparator:
    """Compare exact source assertions without inventing resolution."""

    def compare(self, claims: Iterable[SourceClaim]) -> SourceComparisonResult:
        if isinstance(claims, (str, bytes)):
            raise ComparisonError("claims must be a collection")
        try:
            values = tuple(claims)
        except TypeError as exc:
            raise ComparisonError("claims must be a collection") from exc
        if len(values) > MAX_CLAIMS or any(not isinstance(item, SourceClaim) for item in values):
            raise ComparisonError("claims are outside the bounded range")
        if not values:
            return SourceComparisonResult("empty", ())

        grouped: dict[str, list[SourceClaim]] = {}
        for claim in values:
            grouped.setdefault(claim.subject.casefold().strip(), []).append(claim)
        findings: list[ResearchFinding] = []
        for group in grouped.values():
            assertions: dict[str, str] = {}
            for claim in group:
                assertions.setdefault(" ".join(claim.assertion.casefold().split()), claim.assertion)
            contradictory = len(assertions) > 1
            source_ids = tuple(item.source_id for item in group)
            citations = tuple(item.citation for item in group)
            evidence_refs = tuple(item.evidence_ref() for item in group)
            confidence = None if contradictory or any(item.confidence is None for item in group) else min(
                item.confidence for item in group if item.confidence is not None
            )
            assertion = None if contradictory else next(iter(assertions.values()))
            digest_input = "|".join((group[0].subject, *evidence_refs))
            finding_id = "finding-" + hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:32]
            findings.append(ResearchFinding(
                finding_id,
                group[0].subject,
                assertion,
                "uncertain" if contradictory else "fact",
                confidence,
                source_ids,
                citations,
                evidence_refs,
                tuple(assertions.values()) if contradictory else (),
            ))
        status = "contradictory" if any(item.claim_kind == "uncertain" for item in findings) else "consistent"
        return SourceComparisonResult(status, tuple(findings))


ResearchSourceComparator = SourceComparator


__all__ = [
    "ComparisonError",
    "MAX_CLAIMS",
    "ResearchFinding",
    "ResearchSourceComparator",
    "SourceClaim",
    "SourceComparator",
    "SourceComparisonResult",
]
