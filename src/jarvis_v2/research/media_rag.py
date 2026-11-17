"""Deterministic, bounded media chunking, topics and source-backed summaries."""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .youtube import TranscriptSegment, VideoRecord


MAX_CHUNK_BYTES = 2048
MAX_CHUNKS = 2048
MAX_TOPICS = 32
MAX_SUMMARY_BYTES = 8192
MAX_SOURCE_SPANS = 128
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{3,128}$")
_TOKEN = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
_STOPWORDS = frozenset(
    "a an and are as at be been but by for from had has have he her his i if in is it its me my of on or our she that the their them they this to was we were what when where which who will with you your".split()
)


class MediaRAGError(ValueError):
    """Raised when media indexing or summary evidence is malformed."""


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value if char not in "\n\t")
    ):
        raise MediaRAGError(f"invalid {label}")
    return value


def _id(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise MediaRAGError(f"invalid {label}")
    return value


def _int(value: object, label: str) -> int:
    if type(value) is not int:
        raise MediaRAGError(f"invalid {label}")
    return value


def _offsets(start_ms: object, end_ms: object) -> tuple[int, int]:
    if type(start_ms) is not int or type(end_ms) is not int or not 0 <= start_ms < end_ms:
        raise MediaRAGError("invalid source offsets")
    return start_ms, end_ms


@dataclass(frozen=True)
class SourceSpan:
    """A bounded transcript span retained as summary provenance."""

    video_id: str
    start_ms: int
    end_ms: int
    text: str
    source_link: str

    def __post_init__(self) -> None:
        _id(self.video_id, "video id")
        _offsets(self.start_ms, self.end_ms)
        _text(self.text, "source span text", 4096)
        _text(self.source_link, "source link", 2048)

    def as_dict(self) -> dict[str, object]:
        return {
            "video_id": self.video_id,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "text": self.text,
            "source_link": self.source_link,
        }


@dataclass(frozen=True)
class VideoChunk:
    """One deterministic chunk with the exact source spans used to build it."""

    chunk_id: str
    video_id: str
    index: int
    start_ms: int
    end_ms: int
    text: str
    source_spans: tuple[SourceSpan, ...]

    def __post_init__(self) -> None:
        _id(self.chunk_id, "chunk id")
        _id(self.video_id, "video id")
        if type(self.index) is not int or self.index < 0:
            raise MediaRAGError("invalid chunk index")
        _offsets(self.start_ms, self.end_ms)
        _text(self.text, "chunk text", MAX_CHUNK_BYTES)
        if not self.source_spans or len(self.source_spans) > MAX_SOURCE_SPANS:
            raise MediaRAGError("chunk source spans are outside the bounded range")
        if any(span.video_id != self.video_id for span in self.source_spans):
            raise MediaRAGError("chunk source identity mismatch")

    def as_dict(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "video_id": self.video_id,
            "index": self.index,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "text": self.text,
            "source_spans": [span.as_dict() for span in self.source_spans],
        }


@dataclass(frozen=True)
class Topic:
    """A reproducible lexical topic with source references."""

    term: str
    count: int
    chunk_ids: tuple[str, ...]
    source_spans: tuple[SourceSpan, ...]

    def __post_init__(self) -> None:
        _text(self.term, "topic", 64)
        if self.term != self.term.casefold() or type(self.count) is not int or self.count < 1:
            raise MediaRAGError("invalid topic")
        if not self.chunk_ids or len(self.source_spans) > MAX_SOURCE_SPANS:
            raise MediaRAGError("topic provenance is incomplete")

    def as_dict(self) -> dict[str, object]:
        return {
            "term": self.term,
            "count": self.count,
            "chunk_ids": list(self.chunk_ids),
            "source_spans": [span.as_dict() for span in self.source_spans],
        }


@dataclass(frozen=True)
class IndexedVideo:
    video_id: str
    chunks: tuple[VideoChunk, ...]
    topics: tuple[Topic, ...]

    def __post_init__(self) -> None:
        _id(self.video_id, "video id")
        if any(chunk.video_id != self.video_id for chunk in self.chunks):
            raise MediaRAGError("indexed chunk identity mismatch")
        if any(not isinstance(topic, Topic) for topic in self.topics):
            raise MediaRAGError("indexed topic is invalid")

    def as_dict(self) -> dict[str, object]:
        return {
            "video_id": self.video_id,
            "chunks": [chunk.as_dict() for chunk in self.chunks],
            "topics": [topic.as_dict() for topic in self.topics],
        }


@dataclass(frozen=True)
class VideoSummary:
    summary_id: str
    video_ids: tuple[str, ...]
    observed_at: str
    text: str
    topics: tuple[str, ...]
    source_spans: tuple[SourceSpan, ...]

    def __post_init__(self) -> None:
        _id(self.summary_id, "summary id")
        if not self.video_ids or tuple(sorted(self.video_ids)) != self.video_ids:
            raise MediaRAGError("summary video IDs are not canonical")
        _text(self.observed_at, "summary observation timestamp", 64)
        _text(self.text, "summary text", MAX_SUMMARY_BYTES)
        if any(not isinstance(topic, str) or not topic for topic in self.topics):
            raise MediaRAGError("summary topics are invalid")
        if not self.source_spans or len(self.source_spans) > MAX_SOURCE_SPANS:
            raise MediaRAGError("summary source spans are outside the bounded range")

    def as_dict(self) -> dict[str, object]:
        return {
            "summary_id": self.summary_id,
            "video_ids": list(self.video_ids),
            "observed_at": self.observed_at,
            "text": self.text,
            "topics": list(self.topics),
            "source_spans": [span.as_dict() for span in self.source_spans],
        }


@dataclass(frozen=True)
class MediaRAGResult:
    status: str
    indexed: tuple[IndexedVideo, ...]
    summary: VideoSummary | None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "empty"}:
            raise MediaRAGError("invalid RAG result status")
        if self.status == "ok" and self.summary is None:
            raise MediaRAGError("successful RAG result requires a summary")
        if self.status == "empty" and self.summary is not None:
            raise MediaRAGError("empty RAG result cannot contain a summary")


def _split_text(value: str, maximum: int) -> tuple[str, ...]:
    words = value.split()
    if not words:
        return ()
    parts: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate.encode("utf-8")) <= maximum:
            current = candidate
            continue
        if current:
            parts.append(current)
            current = ""
        if len(word.encode("utf-8")) <= maximum:
            current = word
            continue
        piece = ""
        for char in word:
            candidate = piece + char
            if len(candidate.encode("utf-8")) > maximum:
                if piece:
                    parts.append(piece)
                piece = char
            else:
                piece = candidate
        current = piece
    if current:
        parts.append(current)
    return tuple(parts)


def chunk_video(record: VideoRecord, *, max_bytes: int = MAX_CHUNK_BYTES) -> tuple[VideoChunk, ...]:
    """Group ordered transcript segments into bounded, source-linked chunks."""
    if not isinstance(record, VideoRecord):
        raise MediaRAGError("video record is required")
    if type(max_bytes) is not int or not 256 <= max_bytes <= MAX_CHUNK_BYTES:
        raise MediaRAGError("chunk size is outside the bounded range")
    chunks: list[VideoChunk] = []
    current_text: list[str] = []
    current_spans: list[SourceSpan] = []
    current_bytes = 0

    def flush() -> None:
        nonlocal current_bytes
        if not current_spans:
            return
        text = " ".join(current_text)
        index = len(chunks)
        digest = hashlib.sha256(
            json.dumps(
                {"video_id": record.video_id, "index": index, "text": text,
                 "spans": [span.as_dict() for span in current_spans]},
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:32]
        chunks.append(VideoChunk(
            f"chunk-{digest}", record.video_id, index,
            current_spans[0].start_ms, current_spans[-1].end_ms,
            text, tuple(current_spans),
        ))
        current_text.clear()
        current_spans.clear()
        current_bytes = 0

    for segment in record.transcript:
        if not isinstance(segment, TranscriptSegment):
            raise MediaRAGError("transcript segment is invalid")
        for piece in _split_text(segment.text, max_bytes):
            span = SourceSpan(record.video_id, segment.start_ms, segment.end_ms, piece, segment.source_link)
            piece_bytes = len(piece.encode("utf-8"))
            separator = 1 if current_text else 0
            if current_text and current_bytes + separator + piece_bytes > max_bytes:
                flush()
            current_text.append(piece)
            current_spans.append(span)
            current_bytes += (1 if len(current_text) > 1 else 0) + piece_bytes
            if len(chunks) >= MAX_CHUNKS:
                raise MediaRAGError("video produces too many chunks")
    flush()
    return tuple(chunks)


def extract_topics(chunks: Iterable[VideoChunk], *, limit: int = MAX_TOPICS) -> tuple[Topic, ...]:
    """Return stable frequency topics, retaining the chunks that supplied them."""
    if type(limit) is not int or not 1 <= limit <= MAX_TOPICS:
        raise MediaRAGError("topic limit is outside the bounded range")
    values = tuple(chunks)
    if any(not isinstance(chunk, VideoChunk) for chunk in values):
        raise MediaRAGError("topic chunks are invalid")
    counts: Counter[str] = Counter()
    sources: dict[str, list[VideoChunk]] = defaultdict(list)
    for chunk in values:
        seen: set[str] = set()
        for match in _TOKEN.finditer(chunk.text.casefold()):
            term = match.group(0).replace("’", "'")
            if len(term) < 3 or term in _STOPWORDS or term.isdigit():
                continue
            counts[term] += 1
            seen.add(term)
        for term in seen:
            sources[term].append(chunk)
    result: list[Topic] = []
    for term, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        chunks_for_term = sources[term]
        spans: list[SourceSpan] = []
        for chunk in chunks_for_term:
            spans.extend(chunk.source_spans)
        result.append(Topic(term, count, tuple(chunk.chunk_id for chunk in chunks_for_term), tuple(spans[:MAX_SOURCE_SPANS])))
    return tuple(result)


def _sentences(text: str) -> tuple[str, ...]:
    values = tuple(part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip())
    return values or (text.strip(),)


class MediaRAGStore:
    """Append-only SQLite storage for indexed chunks and summaries."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        if isinstance(database, sqlite3.Connection):
            self.db = database
            self._owns_connection = False
        else:
            self.db = sqlite3.connect(str(database))
            self._owns_connection = True
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS research_video_chunks (
            chunk_id TEXT PRIMARY KEY, video_id TEXT NOT NULL, chunk_index INTEGER NOT NULL,
            chunk_json TEXT NOT NULL
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS research_video_summaries (
            summary_id TEXT PRIMARY KEY, observed_at TEXT NOT NULL, summary_json TEXT NOT NULL
        )""")
        self.db.commit()

    def __enter__(self) -> "MediaRAGStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save_chunks(self, chunks: Iterable[VideoChunk]) -> None:
        values = tuple(chunks)
        for chunk in values:
            payload = json.dumps(chunk.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            with self.db:
                self.db.execute(
                    "INSERT OR IGNORE INTO research_video_chunks(chunk_id,video_id,chunk_index,chunk_json) VALUES(?,?,?,?)",
                    (chunk.chunk_id, chunk.video_id, chunk.index, payload),
                )

    def save_summary(self, summary: VideoSummary) -> None:
        payload = json.dumps(summary.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO research_video_summaries(summary_id,observed_at,summary_json) VALUES(?,?,?)",
                (summary.summary_id, summary.observed_at, payload),
            )

    def chunks_for(self, video_id: str) -> tuple[VideoChunk, ...]:
        _id(video_id, "video id")
        rows = self.db.execute(
            "SELECT chunk_json FROM research_video_chunks WHERE video_id=? ORDER BY chunk_index", (video_id,)
        ).fetchall()
        return tuple(_chunk_from_dict(json.loads(row["chunk_json"])) for row in rows)

    def summary(self, summary_id: str) -> VideoSummary | None:
        _id(summary_id, "summary id")
        row = self.db.execute(
            "SELECT summary_json FROM research_video_summaries WHERE summary_id=?", (summary_id,)
        ).fetchone()
        return None if row is None else _summary_from_dict(json.loads(row["summary_json"]))

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


def _span_from_dict(value: Mapping[str, object]) -> SourceSpan:
    return SourceSpan(
        _id(value.get("video_id"), "video id"), _int(value.get("start_ms"), "start offset"),
        _int(value.get("end_ms"), "end offset"),
        _text(value.get("text"), "source span text", 4096), _text(value.get("source_link"), "source link", 2048),
    )


def _chunk_from_dict(value: Mapping[str, object]) -> VideoChunk:
    raw = value.get("source_spans")
    if not isinstance(raw, list):
        raise MediaRAGError("stored chunk spans are invalid")
    if any(not isinstance(item, Mapping) for item in raw):
        raise MediaRAGError("stored chunk spans are invalid")
    return VideoChunk(
        _id(value.get("chunk_id"), "chunk id"), _id(value.get("video_id"), "video id"),
        _int(value.get("index"), "chunk index"), _int(value.get("start_ms"), "start offset"),
        _int(value.get("end_ms"), "end offset"),
        _text(value.get("text"), "chunk text", MAX_CHUNK_BYTES), tuple(_span_from_dict(item) for item in raw),
    )


def _summary_from_dict(value: Mapping[str, object]) -> VideoSummary:
    ids = value.get("video_ids"); topics = value.get("topics"); raw = value.get("source_spans")
    if not isinstance(ids, list) or not isinstance(topics, list) or not isinstance(raw, list):
        raise MediaRAGError("stored summary is invalid")
    if any(not isinstance(item, str) for item in ids + topics) or any(not isinstance(item, Mapping) for item in raw):
        raise MediaRAGError("stored summary is invalid")
    return VideoSummary(
        _id(value.get("summary_id"), "summary id"), tuple(_id(item, "video id") for item in ids),
        _text(value.get("observed_at"), "summary observation timestamp", 64),
        _text(value.get("text"), "summary text", MAX_SUMMARY_BYTES),
        tuple(_text(item, "topic", 64) for item in topics), tuple(_span_from_dict(item) for item in raw),
    )


class MediaRAGService:
    """Index records and create reproducible extractive cross-video summaries."""

    def __init__(self, store: MediaRAGStore | None = None):
        if store is not None and not isinstance(store, MediaRAGStore):
            raise MediaRAGError("RAG store is invalid")
        self.store = store

    def index(self, record: VideoRecord) -> IndexedVideo:
        chunks = chunk_video(record)
        indexed = IndexedVideo(record.video_id, chunks, extract_topics(chunks))
        if self.store is not None:
            self.store.save_chunks(chunks)
        return indexed

    def summarize(self, records: Iterable[VideoRecord]) -> MediaRAGResult:
        values = tuple(records)
        if any(not isinstance(record, VideoRecord) for record in values):
            raise MediaRAGError("summary records are invalid")
        if not values:
            return MediaRAGResult("empty", (), None)
        if len(values) > 128 or len({record.video_id for record in values}) != len(values):
            raise MediaRAGError("summary video set is outside the bounded range")
        indexed = tuple(sorted((self.index(record) for record in values), key=lambda item: item.video_id))
        all_chunks = tuple(chunk for item in indexed for chunk in item.chunks)
        topics = extract_topics(all_chunks, limit=8)
        lines: list[str] = []
        spans: list[SourceSpan] = []
        observed = tuple(sorted(record.observed_at for record in values))[-1]
        for item in indexed:
            selected_sentences: list[str] = []
            selected_spans: list[SourceSpan] = []
            for chunk in item.chunks:
                sentences = _sentences(chunk.text)
                selected_sentences.extend(sentences[: 2 - len(selected_sentences)])
                selected_spans.extend(chunk.source_spans)
                if len(selected_sentences) >= 2:
                    break
            if selected_sentences:
                lines.append(f"{item.video_id}: {' '.join(selected_sentences)}")
                spans.extend(selected_spans)
        if topics:
            lines.append("Topics: " + ", ".join(topic.term for topic in topics))
            for topic in topics:
                spans.extend(topic.source_spans)
        text = "\n".join(lines)
        if not text:
            return MediaRAGResult("empty", indexed, None)
        text = _text(text, "summary text", MAX_SUMMARY_BYTES)
        unique_spans: list[SourceSpan] = []
        seen: set[tuple[str, int, int, str]] = set()
        for span in spans:
            key = (span.video_id, span.start_ms, span.end_ms, span.source_link)
            if key not in seen:
                seen.add(key)
                unique_spans.append(span)
            if len(unique_spans) >= MAX_SOURCE_SPANS:
                break
        digest = hashlib.sha256(
            json.dumps({"video_ids": [item.video_id for item in indexed], "text": text,
                        "spans": [span.as_dict() for span in unique_spans]},
                       sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:32]
        summary = VideoSummary(
            f"summary-{digest}", tuple(item.video_id for item in indexed), observed, text,
            tuple(topic.term for topic in topics), tuple(unique_spans),
        )
        if self.store is not None:
            self.store.save_summary(summary)
        return MediaRAGResult("ok", indexed, summary)


MediaRAG = MediaRAGService


__all__ = [
    "MAX_CHUNK_BYTES",
    "MAX_CHUNKS",
    "MAX_SOURCE_SPANS",
    "MAX_SUMMARY_BYTES",
    "MAX_TOPICS",
    "IndexedVideo",
    "MediaRAG",
    "MediaRAGError",
    "MediaRAGResult",
    "MediaRAGService",
    "MediaRAGStore",
    "SourceSpan",
    "Topic",
    "VideoChunk",
    "VideoSummary",
    "chunk_video",
    "extract_topics",
]
