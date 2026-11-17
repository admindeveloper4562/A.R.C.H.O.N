"""Bounded YouTube metadata/transcript ingestion with durable provenance."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import parse_qs, urlsplit


MAX_SEGMENTS = 1000
MAX_TEXT_BYTES = 4096
MAX_RECORD_BYTES = 512 * 1024
MAX_DURATION_MS = 24 * 60 * 60 * 1000
_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{6,32}$")


class YouTubeResearchError(ValueError):
    """Raised when media metadata or persistence is malformed."""


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise YouTubeResearchError(f"invalid {label}")
    return value


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise YouTubeResearchError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def video_id_from_url(value: str) -> str:
    """Return an ID only for bounded HTTPS YouTube URL forms."""
    if not isinstance(value, str) or len(value.encode("utf-8")) > 2048:
        raise YouTubeResearchError("invalid video URL")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise YouTubeResearchError("invalid video URL") from exc
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.hostname not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
    ):
        raise YouTubeResearchError("video URL is not allowlisted")
    if parsed.hostname == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.path == "/watch":
        candidate = parse_qs(parsed.query, keep_blank_values=True).get("v", [""])[0]
    elif parsed.path.startswith(("/shorts/", "/embed/")):
        candidate = parsed.path.split("/", 2)[2]
    else:
        candidate = ""
    if not _VIDEO_ID.fullmatch(candidate):
        raise YouTubeResearchError("invalid video ID")
    return candidate


@dataclass(frozen=True)
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str
    source_link: str

    def __post_init__(self) -> None:
        if (
            type(self.start_ms) is not int
            or type(self.end_ms) is not int
            or not 0 <= self.start_ms < self.end_ms <= MAX_DURATION_MS
        ):
            raise YouTubeResearchError("invalid transcript offsets")
        _text(self.text, "transcript text", MAX_TEXT_BYTES)
        _text(self.source_link, "source link", 2048)

    def as_dict(self) -> dict[str, object]:
        return {"start_ms": self.start_ms, "end_ms": self.end_ms, "text": self.text, "source_link": self.source_link}


@dataclass(frozen=True)
class VideoRecord:
    video_id: str
    source_url: str
    title: str
    published_at: str | None
    observed_at: str
    status: str
    transcript: tuple[TranscriptSegment, ...] = ()
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if not _VIDEO_ID.fullmatch(self.video_id):
            raise YouTubeResearchError("invalid video ID")
        _text(self.source_url, "source URL", 2048)
        _text(self.title, "title", 512, empty=True)
        if self.published_at is not None:
            _text(self.published_at, "publication timestamp", 64)
        _text(self.observed_at, "observation timestamp", 64)
        if self.status not in {"ok", "partial", "failed", "empty", "blocked"}:
            raise YouTubeResearchError("invalid video status")
        if len(self.transcript) > MAX_SEGMENTS or any(
            not isinstance(item, TranscriptSegment) for item in self.transcript
        ):
            raise YouTubeResearchError("transcript is outside the bounded range")
        if self.failure_reason is not None:
            _text(self.failure_reason, "failure reason", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "video_id": self.video_id,
            "source_url": self.source_url,
            "title": self.title,
            "published_at": self.published_at,
            "observed_at": self.observed_at,
            "status": self.status,
            "transcript": [item.as_dict() for item in self.transcript],
            "failure_reason": self.failure_reason,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "VideoRecord":
        raw = data.get("transcript", ())
        if isinstance(raw, (str, bytes, Mapping)):
            raise YouTubeResearchError("stored transcript is invalid")
        if not isinstance(raw, (list, tuple)):
            raise YouTubeResearchError("stored transcript is invalid")
        segments_list: list[TranscriptSegment] = []
        for item in raw:
            if not isinstance(item, Mapping):
                raise YouTubeResearchError("stored transcript is invalid")
            start_ms = item.get("start_ms")
            end_ms = item.get("end_ms")
            text = item.get("text")
            source_link = item.get("source_link")
            if (
                type(start_ms) is not int
                or type(end_ms) is not int
                or not isinstance(text, str)
                or not isinstance(source_link, str)
            ):
                raise YouTubeResearchError("stored transcript is invalid")
            segments_list.append(TranscriptSegment(start_ms, end_ms, text, source_link))
        segments = tuple(segments_list)
        video_id = _text(data.get("video_id"), "video ID", 32)
        source_url = _text(data.get("source_url"), "source URL", 2048)
        title = _text(data.get("title", ""), "title", 512, empty=True)
        published_at = data.get("published_at")
        observed_at = _text(data.get("observed_at"), "observation timestamp", 64)
        status = _text(data.get("status"), "status", 32)
        failure_reason = data.get("failure_reason")
        if published_at is not None:
            published_at = _text(published_at, "publication timestamp", 64)
        if failure_reason is not None:
            failure_reason = _text(failure_reason, "failure reason", 128)
        return cls(
            video_id, source_url, title, published_at, observed_at, status,
            segments, failure_reason,
        )


@dataclass(frozen=True)
class VideoResult:
    status: str
    record: VideoRecord | None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "partial", "failed", "empty", "blocked"}:
            raise YouTubeResearchError("invalid video result status")
        if self.record is not None and not isinstance(self.record, VideoRecord):
            raise YouTubeResearchError("invalid video record")
        if self.failure_reason is not None:
            _text(self.failure_reason, "failure reason", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "record": None if self.record is None else self.record.as_dict(),
            "failure_reason": self.failure_reason,
        }


class VideoResearchStore:
    """Persist immutable observations without replacing earlier attempts."""

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
            """CREATE TABLE IF NOT EXISTS research_video_records (
                video_id TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                source_url TEXT NOT NULL,
                status TEXT NOT NULL,
                failure_reason TEXT,
                record_json TEXT NOT NULL,
                PRIMARY KEY (video_id, observed_at)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "VideoResearchStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save(self, record: VideoRecord) -> None:
        payload = json.dumps(record.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise YouTubeResearchError("video record exceeds the bounded size")
        try:
            with self.db:
                self.db.execute(
                    """INSERT OR IGNORE INTO research_video_records
                       (video_id, observed_at, source_url, status, failure_reason, record_json)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (record.video_id, record.observed_at, record.source_url,
                     record.status, record.failure_reason, payload),
                )
        except sqlite3.Error as exc:
            raise YouTubeResearchError("video record persistence failed") from exc

    def latest(self, video_id: str) -> VideoRecord | None:
        if not _VIDEO_ID.fullmatch(video_id):
            raise YouTubeResearchError("invalid video ID")
        row = self.db.execute(
            "SELECT record_json FROM research_video_records WHERE video_id=? ORDER BY observed_at DESC LIMIT 1",
            (video_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            value = json.loads(row["record_json"])
            if not isinstance(value, Mapping):
                raise ValueError
            return VideoRecord.from_dict(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise YouTubeResearchError("stored video record is invalid") from exc

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


MetadataTransport = Callable[[str, str], Mapping[str, object]]
TranscriptTransport = Callable[[str, str], Iterable[Mapping[str, object]]]


class YouTubeResearchService:
    """Use injected provider results and persist every valid video observation."""

    def __init__(
        self,
        store: VideoResearchStore,
        *,
        metadata_transport: MetadataTransport | None = None,
        transcript_transport: TranscriptTransport | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(store, VideoResearchStore):
            raise YouTubeResearchError("video store is required")
        self.store = store
        self.metadata_transport = metadata_transport
        self.transcript_transport = transcript_transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def fetch(self, source_url: str) -> VideoResult:
        observed_at = _timestamp(self.clock)
        try:
            video_id = video_id_from_url(source_url)
        except YouTubeResearchError:
            return VideoResult("blocked", None, "invalid_video_url")
        if self.metadata_transport is None:
            return self._save(video_id, source_url, observed_at, "failed", "metadata_unavailable")
        try:
            metadata = self.metadata_transport(video_id, source_url)
            if not isinstance(metadata, Mapping):
                raise YouTubeResearchError("metadata response is invalid")
            title = metadata.get("title", "")
            published_at = metadata.get("published_at")
            if not isinstance(title, str) or (published_at is not None and not isinstance(published_at, str)):
                raise YouTubeResearchError("metadata fields are invalid")
            _text(title, "title", 512, empty=True)
            if published_at is not None:
                _text(published_at, "publication timestamp", 64)
        except TimeoutError:
            return self._save(video_id, source_url, observed_at, "failed", "provider_timeout")
        except (ConnectionError, OSError):
            return self._save(video_id, source_url, observed_at, "failed", "provider_unavailable")
        except (TypeError, ValueError, YouTubeResearchError):
            return self._save(video_id, source_url, observed_at, "failed", "provider_invalid")

        if self.transcript_transport is None:
            return self._save(video_id, source_url, observed_at, "partial", "transcript_unavailable", title, published_at)
        try:
            values = self.transcript_transport(video_id, source_url)
            if isinstance(values, (str, bytes, Mapping)):
                raise YouTubeResearchError("transcript response is invalid")
            segments = self._segments(values, source_url)
            if not segments:
                return self._save(video_id, source_url, observed_at, "partial", "transcript_empty", title, published_at)
        except TimeoutError:
            return self._save(video_id, source_url, observed_at, "partial", "provider_timeout", title, published_at)
        except (ConnectionError, OSError):
            return self._save(video_id, source_url, observed_at, "partial", "provider_unavailable", title, published_at)
        except (TypeError, ValueError, YouTubeResearchError):
            return self._save(video_id, source_url, observed_at, "failed", "provider_invalid", title, published_at)
        return self._save(video_id, source_url, observed_at, "ok", None, title, published_at, segments)

    def _save(self, video_id: str, source_url: str, observed_at: str, status: str,
              failure: str | None, title: str = "", published_at: str | None = None,
              transcript: tuple[TranscriptSegment, ...] = ()) -> VideoResult:
        record = VideoRecord(video_id, source_url, title, published_at, observed_at, status, transcript, failure)
        self.store.save(record)
        return VideoResult(status, record, failure)

    @staticmethod
    def _segments(values: Iterable[Mapping[str, object]], source_url: str) -> tuple[TranscriptSegment, ...]:
        segments: list[TranscriptSegment] = []
        for item in values:
            if not isinstance(item, Mapping):
                raise YouTubeResearchError("transcript segment is invalid")
            start_ms = item.get("start_ms")
            end_ms = item.get("end_ms")
            text = item.get("text")
            if type(start_ms) is not int or type(end_ms) is not int or not isinstance(text, str):
                raise YouTubeResearchError("transcript segment fields are invalid")
            link = f"{source_url}#t={start_ms / 1000:g}s"
            segments.append(TranscriptSegment(start_ms, end_ms, text, link))
            if len(segments) > MAX_SEGMENTS:
                raise YouTubeResearchError("transcript is too large")
        if any(left.start_ms >= right.start_ms for left, right in zip(segments, segments[1:])):
            raise YouTubeResearchError("transcript offsets are not ordered")
        return tuple(segments)


YouTubeAdapter = YouTubeResearchService
YouTubeStore = VideoResearchStore


__all__ = [
    "MAX_DURATION_MS",
    "MAX_SEGMENTS",
    "TranscriptSegment",
    "VideoRecord",
    "VideoResearchStore",
    "VideoResult",
    "YouTubeAdapter",
    "YouTubeResearchError",
    "YouTubeResearchService",
    "YouTubeStore",
    "video_id_from_url",
]
