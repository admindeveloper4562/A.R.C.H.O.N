"""Bounded public-source ingestion with durable WIC provenance."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit

from jarvis_v2.research.web import SourcePolicy


MAX_FEED_ITEMS = 100
MAX_RECORD_BYTES = 128 * 1024
MAX_TITLE_BYTES = 512
MAX_URL_BYTES = 2048
MAX_SOURCE_POLICIES = 32
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_PUBLIC_SCOPES = frozenset({"public_metadata", "public_read"})


class WICError(ValueError):
    """Raised when a WIC source or observation is malformed."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise WICError(f"invalid {label}")
    return value


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise WICError(f"invalid {label}")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise WICError(f"invalid {label}")
    return value


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _url(value: object, label: str) -> str:
    value = _text(value, label, MAX_URL_BYTES)
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise WICError(f"invalid {label}") from exc
    if (
        parsed.scheme.lower() != "https"
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
        or not parsed.path
    ):
        raise WICError(f"invalid {label}")
    return value


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WICError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _stored_timestamp(value: object, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    value = _text(value, label, 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WICError(f"invalid {label}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WICError(f"invalid {label}")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class SourceObservation:
    """One immutable, source-bound feed observation."""

    observation_id: str
    source_id: str
    feed_url: str
    article_url: str
    fetched_at: str
    published_at: str | None = None
    source_updated_at: str | None = None
    title: str = ""

    def __post_init__(self) -> None:
        _identifier(self.observation_id, "observation id")
        _identifier(self.source_id, "source id")
        _url(self.feed_url, "feed URL")
        _url(self.article_url, "article URL")
        _stored_timestamp(self.fetched_at, "fetched timestamp")
        _stored_timestamp(self.published_at, "published timestamp", optional=True)
        _stored_timestamp(self.source_updated_at, "source updated timestamp", optional=True)
        _text(self.title, "title", MAX_TITLE_BYTES, empty=True)

    def as_dict(self) -> dict[str, object]:
        return {
            "observation_id": self.observation_id,
            "source_id": self.source_id,
            "feed_url": self.feed_url,
            "article_url": self.article_url,
            "fetched_at": self.fetched_at,
            "published_at": self.published_at,
            "source_updated_at": self.source_updated_at,
            "title": self.title,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "SourceObservation":
        if not isinstance(data, Mapping):
            raise WICError("stored observation is invalid")
        keys = (
            "observation_id", "source_id", "feed_url", "article_url", "fetched_at",
            "published_at", "source_updated_at", "title",
        )
        values = {key: data.get(key) for key in keys}
        if values["published_at"] is None:
            values.pop("published_at")
        if values["source_updated_at"] is None:
            values.pop("source_updated_at")
        if values["title"] is None:
            values["title"] = ""
        observation_id = _string(values["observation_id"], "observation id")
        source_id = _string(values["source_id"], "source id")
        feed_url = _string(values["feed_url"], "feed URL")
        article_url = _string(values["article_url"], "article URL")
        fetched_at = _string(values["fetched_at"], "fetched timestamp")
        title = _string(values["title"], "title")
        published_at = _optional_string(values.get("published_at"), "published timestamp")
        source_updated_at = _optional_string(values.get("source_updated_at"), "source updated timestamp")
        return cls(
            observation_id, source_id, feed_url, article_url, fetched_at,
            published_at, source_updated_at, title,
        )


@dataclass(frozen=True)
class IngestionResult:
    """Bounded ingestion result with explicit rejection and outage states."""

    status: str
    fetched_at: str
    observations: tuple[SourceObservation, ...] = ()
    rejected_items: int = 0
    failure: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "partial", "empty", "failed", "blocked"}:
            raise WICError("invalid ingestion status")
        _stored_timestamp(self.fetched_at, "fetched timestamp")
        if len(self.observations) > MAX_FEED_ITEMS or any(
            not isinstance(item, SourceObservation) for item in self.observations
        ):
            raise WICError("observations exceed the bounded range")
        if type(self.rejected_items) is not int or not 0 <= self.rejected_items <= MAX_FEED_ITEMS:
            raise WICError("invalid rejected item count")
        if self.failure is not None:
            _identifier(self.failure, "failure")

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "fetched_at": self.fetched_at,
            "observations": [item.as_dict() for item in self.observations],
            "rejected_items": self.rejected_items,
            "failure": self.failure,
        }


class SourceStore:
    """Persist immutable WIC observations without replacing earlier fetches."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        if isinstance(database, sqlite3.Connection):
            self._owns_connection = False
            self.db = database
        else:
            self._owns_connection = True
            self.db = sqlite3.connect(str(database))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS wic_source_observations (
                observation_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                feed_url TEXT NOT NULL,
                article_url TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                published_at TEXT,
                source_updated_at TEXT,
                title TEXT NOT NULL,
                record_json TEXT NOT NULL,
                UNIQUE(source_id, article_url, fetched_at)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "SourceStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save(self, observation: SourceObservation) -> bool:
        if not isinstance(observation, SourceObservation):
            raise WICError("observation is required")
        payload = json.dumps(observation.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise WICError("observation exceeds the bounded size")
        try:
            with self.db:
                cursor = self.db.execute(
                    """INSERT OR IGNORE INTO wic_source_observations
                       (observation_id, source_id, feed_url, article_url, fetched_at,
                        published_at, source_updated_at, title, record_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        observation.observation_id, observation.source_id, observation.feed_url,
                        observation.article_url, observation.fetched_at, observation.published_at,
                        observation.source_updated_at, observation.title, payload,
                    ),
                )
            return cursor.rowcount == 1
        except sqlite3.Error as exc:
            raise WICError("observation persistence failed") from exc

    def observations(self, source_id: str | None = None) -> tuple[SourceObservation, ...]:
        if source_id is not None:
            source_id = _identifier(source_id, "source id")
            rows = self.db.execute(
                "SELECT record_json FROM wic_source_observations WHERE source_id=? ORDER BY fetched_at, article_url",
                (source_id,),
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT record_json FROM wic_source_observations ORDER BY fetched_at, article_url"
            ).fetchall()
        result: list[SourceObservation] = []
        for row in rows:
            try:
                value = json.loads(row["record_json"])
                result.append(SourceObservation.from_dict(value))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise WICError("stored observation is invalid") from exc
        return tuple(result)

    def latest(self, article_url: str) -> SourceObservation | None:
        article_url = _url(article_url, "article URL")
        row = self.db.execute(
            "SELECT record_json FROM wic_source_observations WHERE article_url=? ORDER BY fetched_at DESC LIMIT 1",
            (article_url,),
        ).fetchone()
        if row is None:
            return None
        try:
            return SourceObservation.from_dict(json.loads(row["record_json"]))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored observation is invalid") from exc

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


FeedTransport = Callable[[str, SourcePolicy, int], Iterable[Mapping[str, object]]]


class PublicSourceIngestion:
    """Ingest authorized public feed metadata through an injected transport."""

    def __init__(
        self,
        store: SourceStore,
        sources: Iterable[SourcePolicy],
        *,
        feed_transport: FeedTransport | None = None,
        clock: Callable[[], datetime] | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        if not isinstance(store, SourceStore):
            raise WICError("source store is required")
        if isinstance(sources, (str, bytes)):
            raise WICError("sources must be a collection")
        try:
            policies = tuple(sources)
        except TypeError as exc:
            raise WICError("sources must be a collection") from exc
        if not 1 <= len(policies) <= MAX_SOURCE_POLICIES or any(
            not isinstance(item, SourcePolicy) for item in policies
        ):
            raise WICError("source policies are outside the bounded range")
        if len({item.source_id for item in policies}) != len(policies):
            raise WICError("duplicate source policy")
        if any(item.access_scope not in _PUBLIC_SCOPES for item in policies):
            raise WICError("source policy is not public")
        if feed_transport is not None and not callable(feed_transport):
            raise WICError("feed transport must be callable")
        if clock is not None and not callable(clock):
            raise WICError("clock must be callable")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 60:
            raise WICError("timeout is outside the bounded range")
        self.store = store
        self.sources = {item.source_id: item for item in policies}
        self.feed_transport = feed_transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.timeout_seconds = timeout_seconds

    def ingest(self, source_id: str, feed_url: str) -> IngestionResult:
        source_id = _identifier(source_id, "source id")
        fetched_at = _timestamp(self.clock)
        policy = self.sources.get(source_id)
        if policy is None or not policy.allows(feed_url):
            return IngestionResult("blocked", fetched_at, failure="source_not_allowlisted")
        if self.feed_transport is None:
            return IngestionResult("failed", fetched_at, failure="feed_unavailable")
        try:
            values = self.feed_transport(feed_url, policy, self.timeout_seconds)
            if isinstance(values, (str, bytes, Mapping)):
                raise WICError("feed response is invalid")
            observations: list[SourceObservation] = []
            rejected = 0
            for item in values:
                if len(observations) + rejected >= MAX_FEED_ITEMS:
                    raise WICError("feed contains too many items")
                try:
                    observation = self._observation(item, policy, feed_url, fetched_at)
                except (TypeError, ValueError, WICError):
                    rejected += 1
                    continue
                self.store.save(observation)
                observations.append(observation)
        except TimeoutError:
            return IngestionResult("failed", fetched_at, failure="provider_timeout")
        except (ConnectionError, OSError):
            return IngestionResult("failed", fetched_at, failure="provider_unavailable")
        except (TypeError, ValueError, WICError):
            return IngestionResult("failed", fetched_at, failure="provider_invalid")
        if not observations:
            return IngestionResult(
                "failed" if rejected else "empty", fetched_at, rejected_items=rejected,
                failure="feed_item_rejected" if rejected else None,
            )
        return IngestionResult(
            "partial" if rejected else "ok", fetched_at, tuple(observations), rejected,
            "feed_item_rejected" if rejected else None,
        )

    @staticmethod
    def _observation(
        item: Mapping[str, object], policy: SourcePolicy, feed_url: str, fetched_at: str,
    ) -> SourceObservation:
        if not isinstance(item, Mapping):
            raise WICError("feed item is invalid")
        article_url = item.get("article_url")
        if not isinstance(article_url, str) or not policy.allows(article_url):
            raise WICError("article URL is not allowlisted")
        published_at = _stored_timestamp(item.get("published_at"), "published timestamp", optional=True)
        source_updated_at = _stored_timestamp(item.get("updated_at"), "source updated timestamp", optional=True)
        title = item.get("title", "")
        if not isinstance(title, str):
            raise WICError("title is invalid")
        _text(title, "title", MAX_TITLE_BYTES, empty=True)
        identity = "|".join((policy.source_id, feed_url, article_url, fetched_at, source_updated_at or ""))
        observation_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
        return SourceObservation(
            observation_id, policy.source_id, _url(feed_url, "feed URL"), _url(article_url, "article URL"),
            fetched_at, published_at, source_updated_at, title,
        )


PublicNewsIngestion = PublicSourceIngestion
WICSourceStore = SourceStore


__all__ = [
    "FeedTransport",
    "IngestionResult",
    "MAX_FEED_ITEMS",
    "MAX_RECORD_BYTES",
    "MAX_SOURCE_POLICIES",
    "PublicNewsIngestion",
    "PublicSourceIngestion",
    "SourceObservation",
    "SourcePolicy",
    "SourceStore",
    "WICError",
    "WICSourceStore",
]
