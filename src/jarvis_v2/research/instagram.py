"""Bounded public Instagram Reel metadata/caption/audio access."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit

from .youtube import MAX_DURATION_MS, TranscriptSegment


MAX_RECORD_BYTES = 512 * 1024
MAX_SEGMENTS = 1000
_REEL_ID = re.compile(r"^[A-Za-z0-9_-]{3,64}$")


class InstagramResearchError(ValueError):
    """Raised when a Reel source or public-content record is malformed."""


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise InstagramResearchError(f"invalid {label}")
    return value


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InstagramResearchError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def instagram_reel_id_from_url(value: str) -> str:
    if not isinstance(value, str) or len(value.encode("utf-8")) > 2048:
        raise InstagramResearchError("invalid Reel URL")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise InstagramResearchError("invalid Reel URL") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"instagram.com", "www.instagram.com"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise InstagramResearchError("Reel URL is not allowlisted")
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 2 or parts[0] not in {"reel", "reels", "p"} or not _REEL_ID.fullmatch(parts[1]):
        raise InstagramResearchError("invalid Reel ID")
    return parts[1]


@dataclass(frozen=True)
class InstagramReelRecord:
    reel_id: str
    source_url: str
    title: str
    caption: str
    observed_at: str
    status: str
    audio_segments: tuple[TranscriptSegment, ...] = ()
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if not _REEL_ID.fullmatch(self.reel_id):
            raise InstagramResearchError("invalid Reel ID")
        _text(self.source_url, "source URL", 2048)
        _text(self.title, "title", 512, empty=True)
        _text(self.caption, "caption", 8192, empty=True)
        _text(self.observed_at, "observation timestamp", 64)
        if self.status not in {"ok", "partial", "failed", "blocked", "empty"}:
            raise InstagramResearchError("invalid Reel status")
        if len(self.audio_segments) > MAX_SEGMENTS or any(
            not isinstance(item, TranscriptSegment) for item in self.audio_segments
        ):
            raise InstagramResearchError("audio transcript is outside the bounded range")
        if self.failure_reason is not None:
            _text(self.failure_reason, "failure reason", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "reel_id": self.reel_id,
            "source_url": self.source_url,
            "title": self.title,
            "caption": self.caption,
            "observed_at": self.observed_at,
            "status": self.status,
            "audio_segments": [item.as_dict() for item in self.audio_segments],
            "failure_reason": self.failure_reason,
        }


@dataclass(frozen=True)
class InstagramResult:
    status: str
    record: InstagramReelRecord | None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "partial", "failed", "blocked", "empty"}:
            raise InstagramResearchError("invalid Reel result status")
        if self.record is not None and not isinstance(self.record, InstagramReelRecord):
            raise InstagramResearchError("invalid Reel record")
        if self.failure_reason is not None:
            _text(self.failure_reason, "failure reason", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "record": None if self.record is None else self.record.as_dict(),
            "failure_reason": self.failure_reason,
        }


class InstagramReelStore:
    """Persist public Reel observations without replacing earlier attempts."""

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
            """CREATE TABLE IF NOT EXISTS research_instagram_records (
                reel_id TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                source_url TEXT NOT NULL,
                status TEXT NOT NULL,
                failure_reason TEXT,
                record_json TEXT NOT NULL,
                PRIMARY KEY (reel_id, observed_at)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "InstagramReelStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save(self, record: InstagramReelRecord) -> None:
        payload = json.dumps(record.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise InstagramResearchError("Reel record exceeds the bounded size")
        try:
            with self.db:
                self.db.execute(
                    """INSERT OR IGNORE INTO research_instagram_records
                       (reel_id, observed_at, source_url, status, failure_reason, record_json)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (record.reel_id, record.observed_at, record.source_url,
                     record.status, record.failure_reason, payload),
                )
        except sqlite3.Error as exc:
            raise InstagramResearchError("Reel record persistence failed") from exc

    def latest(self, reel_id: str) -> InstagramReelRecord | None:
        if not _REEL_ID.fullmatch(reel_id):
            raise InstagramResearchError("invalid Reel ID")
        row = self.db.execute(
            "SELECT record_json FROM research_instagram_records WHERE reel_id=? ORDER BY observed_at DESC LIMIT 1",
            (reel_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            value = json.loads(row["record_json"])
            if not isinstance(value, Mapping):
                raise ValueError
            return self._record(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise InstagramResearchError("stored Reel record is invalid") from exc

    @staticmethod
    def _record(data: Mapping[str, object]) -> InstagramReelRecord:
        raw = data.get("audio_segments", ())
        if not isinstance(raw, (list, tuple)):
            raise InstagramResearchError("stored audio transcript is invalid")
        segments: list[TranscriptSegment] = []
        for item in raw:
            if not isinstance(item, Mapping):
                raise InstagramResearchError("stored audio transcript is invalid")
            start_ms = item.get("start_ms"); end_ms = item.get("end_ms")
            text = item.get("text"); source_link = item.get("source_link")
            if type(start_ms) is not int or type(end_ms) is not int or not isinstance(text, str) or not isinstance(source_link, str):
                raise InstagramResearchError("stored audio transcript is invalid")
            segments.append(TranscriptSegment(start_ms, end_ms, text, source_link))
        reel_id = _text(data.get("reel_id"), "Reel ID", 64)
        source_url = _text(data.get("source_url"), "source URL", 2048)
        title = _text(data.get("title", ""), "title", 512, empty=True)
        caption = _text(data.get("caption", ""), "caption", 8192, empty=True)
        observed_at = _text(data.get("observed_at"), "observation timestamp", 64)
        status = _text(data.get("status"), "status", 32)
        failure = data.get("failure_reason")
        if failure is not None:
            failure = _text(failure, "failure reason", 128)
        return InstagramReelRecord(reel_id, source_url, title, caption, observed_at, status, tuple(segments), failure)

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


MetadataTransport = Callable[[str, str], Mapping[str, object]]
AudioTransport = Callable[[str, str], Iterable[Mapping[str, object]]]


class InstagramReelService:
    """Use only injected public-content transports; never creates account sessions."""

    def __init__(
        self,
        store: InstagramReelStore,
        *,
        metadata_transport: MetadataTransport | None = None,
        audio_transport: AudioTransport | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(store, InstagramReelStore):
            raise InstagramResearchError("Reel store is required")
        self.store = store
        self.metadata_transport = metadata_transport
        self.audio_transport = audio_transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def fetch(self, source_url: str) -> InstagramResult:
        observed_at = _timestamp(self.clock)
        try:
            reel_id = instagram_reel_id_from_url(source_url)
        except InstagramResearchError:
            return InstagramResult("blocked", None, "invalid_reel_url")
        if self.metadata_transport is None:
            return self._save(reel_id, source_url, observed_at, "failed", "metadata_unavailable")
        try:
            metadata = self.metadata_transport(reel_id, source_url)
            if not isinstance(metadata, Mapping):
                raise InstagramResearchError("metadata response is invalid")
            if any(bool(metadata.get(key)) for key in ("is_private", "requires_login", "login_required", "access_denied")):
                return self._save(reel_id, source_url, observed_at, "blocked", "private_content_unavailable")
            title = metadata.get("title", "")
            caption = metadata.get("caption", "")
            if not isinstance(title, str) or not isinstance(caption, str):
                raise InstagramResearchError("metadata fields are invalid")
            _text(title, "title", 512, empty=True)
            _text(caption, "caption", 8192, empty=True)
        except PermissionError:
            return self._save(reel_id, source_url, observed_at, "blocked", "private_content_unavailable")
        except TimeoutError:
            return self._save(reel_id, source_url, observed_at, "failed", "provider_timeout")
        except (ConnectionError, OSError):
            return self._save(reel_id, source_url, observed_at, "failed", "provider_unavailable")
        except (TypeError, ValueError, InstagramResearchError):
            return self._save(reel_id, source_url, observed_at, "failed", "provider_invalid")

        if self.audio_transport is None:
            return self._save(reel_id, source_url, observed_at, "partial", "audio_unavailable", title, caption)
        try:
            values = self.audio_transport(reel_id, source_url)
            if isinstance(values, (str, bytes, Mapping)):
                raise InstagramResearchError("audio response is invalid")
            segments = self._segments(values, source_url)
            if not segments:
                return self._save(reel_id, source_url, observed_at, "partial", "audio_empty", title, caption)
        except PermissionError:
            return self._save(reel_id, source_url, observed_at, "partial", "audio_not_permitted", title, caption)
        except TimeoutError:
            return self._save(reel_id, source_url, observed_at, "partial", "provider_timeout", title, caption)
        except (ConnectionError, OSError):
            return self._save(reel_id, source_url, observed_at, "partial", "provider_unavailable", title, caption)
        except (TypeError, ValueError, InstagramResearchError):
            return self._save(reel_id, source_url, observed_at, "failed", "provider_invalid", title, caption)
        return self._save(reel_id, source_url, observed_at, "ok", None, title, caption, segments)

    def _save(self, reel_id: str, source_url: str, observed_at: str, status: str,
              failure: str | None, title: str = "", caption: str = "",
              segments: tuple[TranscriptSegment, ...] = ()) -> InstagramResult:
        record = InstagramReelRecord(reel_id, source_url, title, caption, observed_at, status, segments, failure)
        self.store.save(record)
        return InstagramResult(status, record, failure)

    @staticmethod
    def _segments(values: Iterable[Mapping[str, object]], source_url: str) -> tuple[TranscriptSegment, ...]:
        segments: list[TranscriptSegment] = []
        for item in values:
            if not isinstance(item, Mapping):
                raise InstagramResearchError("audio segment is invalid")
            start_ms = item.get("start_ms"); end_ms = item.get("end_ms"); text = item.get("text")
            if type(start_ms) is not int or type(end_ms) is not int or not isinstance(text, str):
                raise InstagramResearchError("audio segment fields are invalid")
            segments.append(TranscriptSegment(start_ms, end_ms, text, f"{source_url}#t={start_ms / 1000:g}s"))
            if len(segments) > MAX_SEGMENTS:
                raise InstagramResearchError("audio transcript is too large")
        if any(left.start_ms >= right.start_ms for left, right in zip(segments, segments[1:])):
            raise InstagramResearchError("audio offsets are not ordered")
        return tuple(segments)


InstagramAdapter = InstagramReelService
InstagramStore = InstagramReelStore


__all__ = [
    "InstagramAdapter",
    "InstagramReelRecord",
    "InstagramReelService",
    "InstagramReelStore",
    "InstagramResearchError",
    "InstagramResult",
    "InstagramStore",
    "instagram_reel_id_from_url",
]
