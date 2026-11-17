"""Permission- and modality-gated optional media analysis evidence."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .youtube import MAX_DURATION_MS


MAX_FINDING_BYTES = 4096
_MEDIA_ID = re.compile(r"^[A-Za-z0-9_.:-]{3,128}$")


class MediaAnalysisError(ValueError):
    """Raised when an analysis request or evidence record is malformed."""


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise MediaAnalysisError(f"invalid {label}")
    return value


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise MediaAnalysisError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class MediaAnalysisEvidence:
    evidence_id: str
    media_id: str
    media_kind: str
    start_ms: int
    end_ms: int
    modality: str
    permission_granted: bool
    observed_at: str
    status: str
    finding: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if not _MEDIA_ID.fullmatch(self.evidence_id) or not _MEDIA_ID.fullmatch(self.media_id):
            raise MediaAnalysisError("invalid media evidence identity")
        if self.media_kind not in {"youtube", "instagram"}:
            raise MediaAnalysisError("invalid media kind")
        if type(self.start_ms) is not int or type(self.end_ms) is not int or not 0 <= self.start_ms < self.end_ms <= MAX_DURATION_MS:
            raise MediaAnalysisError("invalid media offsets")
        if self.modality not in {"audio", "video", "audio_visual"}:
            raise MediaAnalysisError("invalid media modality")
        if type(self.permission_granted) is not bool:
            raise MediaAnalysisError("permission must be explicit")
        _text(self.observed_at, "observation timestamp", 64)
        if self.status not in {"ok", "blocked", "failed", "empty"}:
            raise MediaAnalysisError("invalid analysis status")
        if self.finding is not None:
            _text(self.finding, "finding", MAX_FINDING_BYTES)
        if self.failure_reason is not None:
            _text(self.failure_reason, "failure reason", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "media_id": self.media_id,
            "media_kind": self.media_kind,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "modality": self.modality,
            "permission_granted": self.permission_granted,
            "observed_at": self.observed_at,
            "status": self.status,
            "finding": self.finding,
            "failure_reason": self.failure_reason,
        }


@dataclass(frozen=True)
class MediaAnalysisResult:
    status: str
    evidence: MediaAnalysisEvidence

    def __post_init__(self) -> None:
        if self.status != self.evidence.status:
            raise MediaAnalysisError("result and evidence status differ")

    def as_dict(self) -> dict[str, object]:
        return self.evidence.as_dict()


class MediaAnalysisStore:
    """Append-only bounded evidence store for optional analysis observations."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self.db: sqlite3.Connection
        if isinstance(database, sqlite3.Connection):
            self._owns_connection = False
            self.db = database
        else:
            self._owns_connection = True
            self.db = sqlite3.connect(str(database))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS research_media_analysis (
                evidence_id TEXT PRIMARY KEY,
                media_id TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                failure_reason TEXT,
                evidence_json TEXT NOT NULL
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "MediaAnalysisStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save(self, evidence: MediaAnalysisEvidence) -> None:
        payload = json.dumps(evidence.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        try:
            with self.db:
                self.db.execute(
                    """INSERT OR IGNORE INTO research_media_analysis
                       (evidence_id, media_id, observed_at, status, failure_reason, evidence_json)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (evidence.evidence_id, evidence.media_id, evidence.observed_at,
                     evidence.status, evidence.failure_reason, payload),
                )
        except sqlite3.Error as exc:
            raise MediaAnalysisError("analysis evidence persistence failed") from exc

    def latest(self, media_id: str) -> MediaAnalysisEvidence | None:
        if not _MEDIA_ID.fullmatch(media_id):
            raise MediaAnalysisError("invalid media id")
        row = self.db.execute(
            "SELECT evidence_json FROM research_media_analysis WHERE media_id=? ORDER BY observed_at DESC LIMIT 1",
            (media_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            value = json.loads(row["evidence_json"])
            if not isinstance(value, Mapping):
                raise ValueError
            return self._evidence(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise MediaAnalysisError("stored analysis evidence is invalid") from exc

    @staticmethod
    def _evidence(data: Mapping[str, object]) -> MediaAnalysisEvidence:
        strings = {}
        for key, limit in (("evidence_id", 128), ("media_id", 128), ("media_kind", 32), ("modality", 32), ("observed_at", 64), ("status", 32)):
            strings[key] = _text(data.get(key), key, limit)
        start_ms = data.get("start_ms"); end_ms = data.get("end_ms")
        permission = data.get("permission_granted")
        if type(start_ms) is not int or type(end_ms) is not int or type(permission) is not bool:
            raise MediaAnalysisError("stored analysis fields are invalid")
        finding = data.get("finding"); failure = data.get("failure_reason")
        if finding is not None: finding = _text(finding, "finding", MAX_FINDING_BYTES)
        if failure is not None: failure = _text(failure, "failure reason", 128)
        return MediaAnalysisEvidence(
            strings["evidence_id"], strings["media_id"], strings["media_kind"],
            start_ms, end_ms, strings["modality"], permission, strings["observed_at"],
            strings["status"], finding, failure,
        )

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


Analyzer = Callable[[str, str, int, int], Mapping[str, object]]


class MediaAnalysisService:
    """Gate optional analysis before invoking an injected analyzer."""

    def __init__(self, store: MediaAnalysisStore, *, analyzer: Analyzer | None = None, clock: Callable[[], datetime] | None = None):
        if not isinstance(store, MediaAnalysisStore):
            raise MediaAnalysisError("analysis store is required")
        self.store = store
        self.analyzer = analyzer
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def analyze(self, media_id: str, media_kind: str, start_ms: int, end_ms: int, *, modality: str, permission_granted: bool) -> MediaAnalysisResult:
        if not _MEDIA_ID.fullmatch(media_id):
            raise MediaAnalysisError("invalid media id")
        if media_kind not in {"youtube", "instagram"}:
            raise MediaAnalysisError("invalid media kind")
        if type(start_ms) is not int or type(end_ms) is not int or not 0 <= start_ms < end_ms <= MAX_DURATION_MS:
            raise MediaAnalysisError("invalid media offsets")
        if modality not in {"audio", "video", "audio_visual"}:
            raise MediaAnalysisError("invalid media modality")
        observed_at = _timestamp(self.clock)
        if type(permission_granted) is not bool or not permission_granted:
            return self._save(media_id, media_kind, start_ms, end_ms, modality, False, observed_at, "blocked", None, "permission_required")
        if self.analyzer is None:
            return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "failed", None, "analyzer_unavailable")
        try:
            payload = self.analyzer(media_id, media_kind, start_ms, end_ms)
            if not isinstance(payload, Mapping):
                raise MediaAnalysisError("analyzer response is invalid")
            finding = payload.get("finding", payload.get("summary"))
            if not isinstance(finding, str) or not finding.strip():
                return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "empty", None, "analyzer_empty")
            _text(finding, "finding", MAX_FINDING_BYTES)
            return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "ok", finding, None)
        except TimeoutError:
            return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "failed", None, "provider_timeout")
        except (ConnectionError, OSError):
            return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "failed", None, "provider_unavailable")
        except (TypeError, ValueError, MediaAnalysisError):
            return self._save(media_id, media_kind, start_ms, end_ms, modality, True, observed_at, "failed", None, "provider_invalid")

    def _save(self, media_id: str, media_kind: str, start_ms: int, end_ms: int, modality: str,
              permission: bool, observed_at: str, status: str, finding: str | None,
              failure: str | None) -> MediaAnalysisResult:
        evidence_id = "analysis-" + hashlib.sha256(
            f"{media_id}|{media_kind}|{start_ms}|{end_ms}|{modality}|{observed_at}".encode("utf-8")
        ).hexdigest()[:32]
        evidence = MediaAnalysisEvidence(
            evidence_id, media_id, media_kind, start_ms, end_ms, modality,
            permission, observed_at, status, finding, failure,
        )
        self.store.save(evidence)
        return MediaAnalysisResult(status, evidence)


MediaAnalyzer = MediaAnalysisService


__all__ = [
    "MAX_FINDING_BYTES",
    "MediaAnalysisError",
    "MediaAnalysisEvidence",
    "MediaAnalysisResult",
    "MediaAnalysisStore",
    "MediaAnalysisService",
    "MediaAnalyzer",
]
