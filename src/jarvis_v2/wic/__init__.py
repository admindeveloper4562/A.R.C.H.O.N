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
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jarvis_v2.research.web import SourcePolicy


MAX_FEED_ITEMS = 100
MAX_RECORD_BYTES = 128 * 1024
MAX_TITLE_BYTES = 512
MAX_URL_BYTES = 2048
MAX_SOURCE_POLICIES = 32
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_PUBLIC_SCOPES = frozenset({"public_metadata", "public_read"})
_TRACKING_QUERY_KEYS = frozenset({"fbclid", "gclid", "mc_cid", "mc_eid"})
_CATEGORY_NAMES = frozenset({"geography", "technology", "politics", "economics", "science", "thailand"})
_MAX_SUMMARY_SEGMENTS = 32


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


def _categories(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise WICError("categories must be a collection")
    try:
        result = tuple(sorted(set(values)))
    except (TypeError, ValueError) as exc:
        raise WICError("categories must be a collection") from exc
    if not result or len(result) > len(_CATEGORY_NAMES) or any(
        not isinstance(value, str) or value not in _CATEGORY_NAMES for value in result
    ):
        raise WICError("invalid WIC category")
    return result


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


def normalize_url(value: str) -> str:
    """Normalize one already-allowlisted article URL without changing attribution."""
    value = _url(value, "article URL")
    parsed = urlsplit(value)
    hostname = parsed.hostname
    if hostname is None:
        raise WICError("invalid article URL")
    query = [
        (key, item) for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() not in _TRACKING_QUERY_KEYS and not key.casefold().startswith("utm_")
    ]
    query.sort()
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit(("https", hostname.casefold(), path, urlencode(query), ""))


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


@dataclass(frozen=True)
class StoryCluster:
    """A deduplicated incident view that retains every source observation."""

    cluster_id: str
    cluster_key: str
    observation_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    article_urls: tuple[str, ...]
    normalized_article_urls: tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.cluster_id, "cluster id")
        _text(self.cluster_key, "cluster key", MAX_URL_BYTES)
        if not self.observation_ids or len(self.observation_ids) > MAX_FEED_ITEMS:
            raise WICError("cluster observations are outside the bounded range")
        if len(self.observation_ids) != len(set(self.observation_ids)):
            raise WICError("cluster observations are duplicated")
        if len(self.source_ids) != len(set(self.source_ids)) or not self.source_ids:
            raise WICError("cluster sources are invalid")
        if len(self.article_urls) != len(self.normalized_article_urls):
            raise WICError("cluster URL lists are inconsistent")
        for value in self.observation_ids:
            _identifier(value, "observation id")
        for value in self.source_ids:
            _identifier(value, "source id")
        for value in self.article_urls:
            _url(value, "article URL")
        for value in self.normalized_article_urls:
            _url(value, "normalized article URL")

    def as_dict(self) -> dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "cluster_key": self.cluster_key,
            "observation_ids": list(self.observation_ids),
            "source_ids": list(self.source_ids),
            "article_urls": list(self.article_urls),
            "normalized_article_urls": list(self.normalized_article_urls),
        }


class StoryClusterStore:
    """Persist cluster membership while keeping original source URLs intact."""

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
            """CREATE TABLE IF NOT EXISTS wic_story_clusters (
                cluster_id TEXT PRIMARY KEY,
                cluster_key TEXT NOT NULL UNIQUE
            )"""
        )
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS wic_story_cluster_members (
                cluster_id TEXT NOT NULL REFERENCES wic_story_clusters(cluster_id),
                observation_id TEXT NOT NULL UNIQUE,
                source_id TEXT NOT NULL,
                article_url TEXT NOT NULL,
                normalized_url TEXT NOT NULL,
                PRIMARY KEY (cluster_id, observation_id)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "StoryClusterStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def add(self, cluster_key: str, observations: Iterable[SourceObservation]) -> StoryCluster:
        cluster_key = _text(cluster_key, "cluster key", MAX_URL_BYTES)
        values = tuple(observations)
        if not values or len(values) > MAX_FEED_ITEMS or any(
            not isinstance(item, SourceObservation) for item in values
        ):
            raise WICError("cluster observations are outside the bounded range")
        if len({item.observation_id for item in values}) != len(values):
            raise WICError("cluster observations are duplicated")
        cluster_id = hashlib.sha256(cluster_key.encode("utf-8")).hexdigest()[:32]
        try:
            with self.db:
                self.db.execute(
                    "INSERT OR IGNORE INTO wic_story_clusters (cluster_id, cluster_key) VALUES (?, ?)",
                    (cluster_id, cluster_key),
                )
                existing = self.db.execute(
                    "SELECT cluster_id FROM wic_story_cluster_members WHERE observation_id IN ({})".format(
                        ",".join("?" for _ in values)
                    ),
                    tuple(item.observation_id for item in values),
                ).fetchall()
                if any(row["cluster_id"] != cluster_id for row in existing):
                    raise WICError("observation already belongs to another cluster")
                for item in values:
                    self.db.execute(
                        """INSERT OR IGNORE INTO wic_story_cluster_members
                           (cluster_id, observation_id, source_id, article_url, normalized_url)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            cluster_id, item.observation_id, item.source_id,
                            item.article_url, normalize_url(item.article_url),
                        ),
                    )
        except sqlite3.Error as exc:
            raise WICError("cluster persistence failed") from exc
        return self.get(cluster_key)  # type: ignore[return-value]

    def get(self, cluster_key: str) -> StoryCluster | None:
        cluster_key = _text(cluster_key, "cluster key", MAX_URL_BYTES)
        row = self.db.execute(
            "SELECT cluster_id, cluster_key FROM wic_story_clusters WHERE cluster_key=?",
            (cluster_key,),
        ).fetchone()
        if row is None:
            return None
        members = self.db.execute(
            """SELECT observation_id, source_id, article_url, normalized_url
               FROM wic_story_cluster_members WHERE cluster_id=?
               ORDER BY observation_id""",
            (row["cluster_id"],),
        ).fetchall()
        return StoryCluster(
            row["cluster_id"], row["cluster_key"],
            tuple(item["observation_id"] for item in members),
            tuple(sorted({item["source_id"] for item in members})),
            tuple(item["article_url"] for item in members),
            tuple(item["normalized_url"] for item in members),
        )

    def clusters(self) -> tuple[StoryCluster, ...]:
        result: list[StoryCluster] = []
        for row in self.db.execute("SELECT cluster_key FROM wic_story_clusters ORDER BY cluster_key"):
            cluster = self.get(row["cluster_key"])
            if cluster is not None:
                result.append(cluster)
        return tuple(result)

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


class StoryClusterer:
    """Group observations by an explicit incident key or normalized URL."""

    def __init__(self, store: StoryClusterStore):
        if not isinstance(store, StoryClusterStore):
            raise WICError("story cluster store is required")
        self.store = store

    def cluster(
        self, observations: Iterable[SourceObservation], *, incident_key: str | None = None,
    ) -> StoryCluster:
        values = tuple(observations)
        if not values:
            raise WICError("at least one observation is required")
        if any(not isinstance(item, SourceObservation) for item in values):
            raise WICError("cluster observations are invalid")
        if incident_key is None:
            normalized = {normalize_url(item.article_url) for item in values}
            if len(normalized) != 1:
                raise WICError("incident key is required for different URLs")
            cluster_key = "url:" + next(iter(normalized))
        else:
            incident_key = _text(incident_key, "incident key", 512)
            cluster_key = "incident:" + incident_key
        return self.store.add(cluster_key, values)


@dataclass(frozen=True)
class ClaimRecord:
    """One bounded claim revision with explicit verification state."""

    claim_id: str
    cluster_id: str
    statement_digest: str
    status: str
    confidence: float | None
    observation_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    revision: int
    updated_at: str
    reason: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.claim_id, "claim id")
        _identifier(self.cluster_id, "cluster id")
        if not re.fullmatch(r"[0-9a-f]{64}", self.statement_digest):
            raise WICError("invalid statement digest")
        if self.status not in {"uncertain", "supported", "verified", "corrected", "retracted"}:
            raise WICError("invalid claim status")
        if self.confidence is not None and (
            type(self.confidence) is not float or not 0.0 <= self.confidence <= 1.0
        ):
            raise WICError("invalid claim confidence")
        if not self.observation_ids or len(self.observation_ids) != len(set(self.observation_ids)):
            raise WICError("claim observations are invalid")
        if not self.source_ids or len(self.source_ids) != len(set(self.source_ids)):
            raise WICError("claim sources are invalid")
        for value in self.observation_ids:
            _identifier(value, "observation id")
        for value in self.source_ids:
            _identifier(value, "source id")
        if type(self.revision) is not int or self.revision < 1:
            raise WICError("invalid claim revision")
        _stored_timestamp(self.updated_at, "claim timestamp")
        if self.reason is not None:
            _text(self.reason, "claim reason", 512)

    def as_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "cluster_id": self.cluster_id,
            "statement_digest": self.statement_digest,
            "status": self.status,
            "confidence": self.confidence,
            "observation_ids": list(self.observation_ids),
            "source_ids": list(self.source_ids),
            "revision": self.revision,
            "updated_at": self.updated_at,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ClaimRecord":
        if not isinstance(data, Mapping):
            raise WICError("stored claim is invalid")
        observation_ids = data.get("observation_ids")
        source_ids = data.get("source_ids")
        if (
            not isinstance(observation_ids, list) or not all(isinstance(item, str) for item in observation_ids)
            or not isinstance(source_ids, list) or not all(isinstance(item, str) for item in source_ids)
        ):
            raise WICError("stored claim sources are invalid")
        claim_id = _string(data.get("claim_id"), "claim id")
        cluster_id = _string(data.get("cluster_id"), "cluster id")
        statement_digest = _string(data.get("statement_digest"), "statement digest")
        status = _string(data.get("status"), "claim status")
        confidence = data.get("confidence")
        if confidence is not None and type(confidence) is not float:
            raise WICError("stored claim confidence is invalid")
        revision = data.get("revision")
        if type(revision) is not int:
            raise WICError("stored claim revision is invalid")
        updated_at = _string(data.get("updated_at"), "claim timestamp")
        reason = data.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise WICError("stored claim reason is invalid")
        return cls(
            claim_id, cluster_id, statement_digest, status, confidence,
            tuple(observation_ids), tuple(source_ids), revision, updated_at, reason,
        )


class ClaimLedger:
    """Append-only claim history that cannot promote uncertainty directly."""

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
            "CREATE TABLE IF NOT EXISTS wic_claims (claim_id TEXT PRIMARY KEY, record_json TEXT NOT NULL)"
        )
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS wic_claim_revisions (
                claim_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                record_json TEXT NOT NULL,
                PRIMARY KEY (claim_id, revision)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "ClaimLedger":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def create(
        self, claim_id: str, cluster: StoryCluster, statement_digest: str,
        recorded_at: str, confidence: float | None = None,
    ) -> ClaimRecord:
        claim_id = _identifier(claim_id, "claim id")
        if not isinstance(cluster, StoryCluster):
            raise WICError("story cluster is required")
        _stored_timestamp(recorded_at, "claim timestamp")
        status = "supported" if len(cluster.source_ids) >= 2 and confidence is not None else "uncertain"
        record = ClaimRecord(
            claim_id, cluster.cluster_id, statement_digest, status, confidence,
            cluster.observation_ids, cluster.source_ids, 1, recorded_at,
        )
        return self._insert_new(record)

    def corroborate(
        self, claim_id: str, cluster: StoryCluster, recorded_at: str,
        confidence: float | None,
    ) -> ClaimRecord:
        current = self.get(claim_id)
        if current is None:
            raise WICError("claim is not recorded")
        if current.status == "retracted":
            raise WICError("retracted claim requires correction")
        _stored_timestamp(recorded_at, "claim timestamp")
        sources = tuple(sorted(set(cluster.source_ids)))
        observations = tuple(sorted(set(cluster.observation_ids)))
        status = "supported" if len(sources) >= 2 and confidence is not None else "uncertain"
        record = ClaimRecord(
            current.claim_id, cluster.cluster_id, current.statement_digest, status, confidence,
            observations, sources, current.revision + 1, recorded_at,
        )
        return self._append(record)

    def verify(self, claim_id: str, recorded_at: str) -> ClaimRecord:
        current = self.get(claim_id)
        if current is None:
            raise WICError("claim is not recorded")
        if current.status != "supported" or len(current.source_ids) < 2 or current.confidence is None:
            raise WICError("uncertain claim cannot be verified")
        _stored_timestamp(recorded_at, "claim timestamp")
        return self._append(
            ClaimRecord(
                current.claim_id, current.cluster_id, current.statement_digest, "verified",
                current.confidence, current.observation_ids, current.source_ids,
                current.revision + 1, recorded_at,
            )
        )

    def retract(self, claim_id: str, reason: str, recorded_at: str) -> ClaimRecord:
        current = self.get(claim_id)
        if current is None:
            raise WICError("claim is not recorded")
        _stored_timestamp(recorded_at, "claim timestamp")
        return self._append(
            ClaimRecord(
                current.claim_id, current.cluster_id, current.statement_digest, "retracted",
                None, current.observation_ids, current.source_ids, current.revision + 1,
                recorded_at, _text(reason, "claim reason", 512),
            )
        )

    def correct(
        self, claim_id: str, cluster: StoryCluster, statement_digest: str,
        reason: str, recorded_at: str, confidence: float | None = None,
    ) -> ClaimRecord:
        current = self.get(claim_id)
        if current is None:
            raise WICError("claim is not recorded")
        _stored_timestamp(recorded_at, "claim timestamp")
        return self._append(
            ClaimRecord(
                current.claim_id, cluster.cluster_id, statement_digest, "corrected", confidence,
                cluster.observation_ids, cluster.source_ids, current.revision + 1,
                recorded_at, _text(reason, "claim reason", 512),
            )
        )

    def get(self, claim_id: str) -> ClaimRecord | None:
        claim_id = _identifier(claim_id, "claim id")
        row = self.db.execute("SELECT record_json FROM wic_claims WHERE claim_id=?", (claim_id,)).fetchone()
        if row is None:
            return None
        try:
            return ClaimRecord.from_dict(json.loads(row["record_json"]))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored claim is invalid") from exc

    def history(self, claim_id: str) -> tuple[ClaimRecord, ...]:
        claim_id = _identifier(claim_id, "claim id")
        rows = self.db.execute(
            "SELECT record_json FROM wic_claim_revisions WHERE claim_id=? ORDER BY revision",
            (claim_id,),
        ).fetchall()
        try:
            return tuple(ClaimRecord.from_dict(json.loads(row["record_json"])) for row in rows)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored claim history is invalid") from exc

    def _insert_new(self, record: ClaimRecord) -> ClaimRecord:
        payload = self._payload(record)
        try:
            with self.db:
                self.db.execute(
                    "INSERT INTO wic_claims (claim_id, record_json) VALUES (?, ?)",
                    (record.claim_id, payload),
                )
                self.db.execute(
                    "INSERT INTO wic_claim_revisions (claim_id, revision, record_json) VALUES (?, ?, ?)",
                    (record.claim_id, record.revision, payload),
                )
        except sqlite3.IntegrityError as exc:
            raise WICError("claim already exists") from exc
        except sqlite3.Error as exc:
            raise WICError("claim persistence failed") from exc
        return record

    def _append(self, record: ClaimRecord) -> ClaimRecord:
        payload = self._payload(record)
        try:
            with self.db:
                self.db.execute(
                    "UPDATE wic_claims SET record_json=? WHERE claim_id=?",
                    (payload, record.claim_id),
                )
                self.db.execute(
                    "INSERT INTO wic_claim_revisions (claim_id, revision, record_json) VALUES (?, ?, ?)",
                    (record.claim_id, record.revision, payload),
                )
        except sqlite3.Error as exc:
            raise WICError("claim history persistence failed") from exc
        return record

    @staticmethod
    def _payload(record: ClaimRecord) -> str:
        payload = json.dumps(record.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise WICError("claim exceeds the bounded size")
        return payload

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


@dataclass(frozen=True)
class CategoryAssignment:
    """Current WIC categories for one story cluster."""

    cluster_id: str
    categories: tuple[str, ...]
    revision: int
    status: str
    recorded_at: str
    reason: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.cluster_id, "cluster id")
        if self.categories != _categories(self.categories):
            raise WICError("categories are not canonical")
        if type(self.revision) is not int or self.revision < 1:
            raise WICError("invalid category revision")
        if self.status not in {"active", "corrected"}:
            raise WICError("invalid category status")
        _stored_timestamp(self.recorded_at, "category timestamp")
        if self.reason is not None:
            _text(self.reason, "category reason", 512)

    def as_dict(self) -> dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "categories": list(self.categories),
            "revision": self.revision,
            "status": self.status,
            "recorded_at": self.recorded_at,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CategoryAssignment":
        if not isinstance(data, Mapping):
            raise WICError("stored category assignment is invalid")
        raw_categories = data.get("categories")
        if not isinstance(raw_categories, list) or not all(isinstance(item, str) for item in raw_categories):
            raise WICError("stored categories are invalid")
        cluster_id = _string(data.get("cluster_id"), "cluster id")
        revision = data.get("revision")
        if type(revision) is not int:
            raise WICError("stored category revision is invalid")
        status = _string(data.get("status"), "category status")
        recorded_at = _string(data.get("recorded_at"), "category timestamp")
        reason = data.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise WICError("stored category reason is invalid")
        return cls(cluster_id, tuple(raw_categories), revision, status, recorded_at, reason)


class CategoryStore:
    """Persist searchable category snapshots and their correction history."""

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
            """CREATE TABLE IF NOT EXISTS wic_category_assignments (
                cluster_id TEXT PRIMARY KEY,
                record_json TEXT NOT NULL
            )"""
        )
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS wic_category_revisions (
                cluster_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                record_json TEXT NOT NULL,
                PRIMARY KEY (cluster_id, revision)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "CategoryStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def assign(self, cluster_id: str, categories: Iterable[str], recorded_at: str) -> CategoryAssignment:
        cluster_id = _identifier(cluster_id, "cluster id")
        _stored_timestamp(recorded_at, "category timestamp")
        record = CategoryAssignment(cluster_id, _categories(categories), 1, "active", recorded_at)
        return self._insert_new(record)

    def correct(
        self, cluster_id: str, categories: Iterable[str], reason: str, recorded_at: str,
    ) -> CategoryAssignment:
        current = self.get(cluster_id)
        if current is None:
            raise WICError("category assignment is not recorded")
        _stored_timestamp(recorded_at, "category timestamp")
        record = CategoryAssignment(
            current.cluster_id, _categories(categories), current.revision + 1,
            "corrected", recorded_at, _text(reason, "category reason", 512),
        )
        return self._append(record)

    def get(self, cluster_id: str) -> CategoryAssignment | None:
        cluster_id = _identifier(cluster_id, "cluster id")
        row = self.db.execute(
            "SELECT record_json FROM wic_category_assignments WHERE cluster_id=?",
            (cluster_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            return CategoryAssignment.from_dict(json.loads(row["record_json"]))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored category assignment is invalid") from exc

    def search(self, category: str) -> tuple[CategoryAssignment, ...]:
        category = _string(category, "category")
        if category not in _CATEGORY_NAMES:
            raise WICError("invalid WIC category")
        result: list[CategoryAssignment] = []
        for row in self.db.execute("SELECT record_json FROM wic_category_assignments ORDER BY cluster_id"):
            try:
                assignment = CategoryAssignment.from_dict(json.loads(row["record_json"]))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise WICError("stored category assignment is invalid") from exc
            if category in assignment.categories:
                result.append(assignment)
        return tuple(result)

    def history(self, cluster_id: str) -> tuple[CategoryAssignment, ...]:
        cluster_id = _identifier(cluster_id, "cluster id")
        rows = self.db.execute(
            "SELECT record_json FROM wic_category_revisions WHERE cluster_id=? ORDER BY revision",
            (cluster_id,),
        ).fetchall()
        try:
            return tuple(CategoryAssignment.from_dict(json.loads(row["record_json"])) for row in rows)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored category history is invalid") from exc

    def _insert_new(self, record: CategoryAssignment) -> CategoryAssignment:
        payload = self._payload(record)
        try:
            with self.db:
                self.db.execute(
                    "INSERT INTO wic_category_assignments (cluster_id, record_json) VALUES (?, ?)",
                    (record.cluster_id, payload),
                )
                self.db.execute(
                    "INSERT INTO wic_category_revisions (cluster_id, revision, record_json) VALUES (?, ?, ?)",
                    (record.cluster_id, record.revision, payload),
                )
        except sqlite3.IntegrityError as exc:
            raise WICError("category assignment already exists") from exc
        except sqlite3.Error as exc:
            raise WICError("category assignment persistence failed") from exc
        return record

    def _append(self, record: CategoryAssignment) -> CategoryAssignment:
        payload = self._payload(record)
        try:
            with self.db:
                self.db.execute(
                    "UPDATE wic_category_assignments SET record_json=? WHERE cluster_id=?",
                    (payload, record.cluster_id),
                )
                self.db.execute(
                    "INSERT INTO wic_category_revisions (cluster_id, revision, record_json) VALUES (?, ?, ?)",
                    (record.cluster_id, record.revision, payload),
                )
        except sqlite3.Error as exc:
            raise WICError("category history persistence failed") from exc
        return record

    @staticmethod
    def _payload(record: CategoryAssignment) -> str:
        payload = json.dumps(record.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise WICError("category assignment exceeds the bounded size")
        return payload

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


StoryCategoryStore = CategoryStore
WICCategoryStore = CategoryStore


@dataclass(frozen=True)
class SummarySegment:
    """One cited statement that can be safely included in a summary."""

    claim_id: str
    text: str
    citation_url: str
    certainty: str
    observed_at: str
    uncertainty_note: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.claim_id, "claim id")
        _text(self.text, "summary text", 2048)
        _url(self.citation_url, "citation URL")
        if self.certainty not in {"verified", "supported", "uncertain"}:
            raise WICError("invalid summary certainty")
        _stored_timestamp(self.observed_at, "observation timestamp")
        if self.certainty == "uncertain" and self.uncertainty_note is None:
            raise WICError("uncertain summary requires a note")
        if self.uncertainty_note is not None:
            _text(self.uncertainty_note, "uncertainty note", 512)

    def as_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "citation_url": self.citation_url,
            "certainty": self.certainty,
            "observed_at": self.observed_at,
            "uncertainty_note": self.uncertainty_note,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "SummarySegment":
        if not isinstance(data, Mapping):
            raise WICError("stored summary segment is invalid")
        claim_id = _string(data.get("claim_id"), "claim id")
        text = _string(data.get("text"), "summary text")
        citation_url = _string(data.get("citation_url"), "citation URL")
        certainty = _string(data.get("certainty"), "summary certainty")
        observed_at = _string(data.get("observed_at"), "observation timestamp")
        uncertainty_note = data.get("uncertainty_note")
        if uncertainty_note is not None and not isinstance(uncertainty_note, str):
            raise WICError("stored uncertainty note is invalid")
        return cls(claim_id, text, citation_url, certainty, observed_at, uncertainty_note)


@dataclass(frozen=True)
class SituationSummary:
    """A dated summary whose text is assembled only from cited segments."""

    summary_id: str
    text: str
    segments: tuple[SummarySegment, ...]
    citations: tuple[str, ...]
    status: str
    freshness: str
    created_at: str

    def __post_init__(self) -> None:
        _identifier(self.summary_id, "summary id")
        _text(self.text, "summary text", MAX_RECORD_BYTES)
        if not self.segments or len(self.segments) > _MAX_SUMMARY_SEGMENTS:
            raise WICError("summary segments are outside the bounded range")
        if self.status not in {"verified", "supported", "uncertain"}:
            raise WICError("invalid summary status")
        if self.freshness not in {"dated", "stale"}:
            raise WICError("live freshness requires fresh verified evidence")
        _stored_timestamp(self.created_at, "summary timestamp")
        if not self.citations or len(self.citations) != len(set(self.citations)):
            raise WICError("summary citations are invalid")
        for citation in self.citations:
            _url(citation, "citation URL")
        expected = "uncertain" if any(item.certainty == "uncertain" for item in self.segments) else (
            "verified" if all(item.certainty == "verified" for item in self.segments) else "supported"
        )
        if self.status != expected:
            raise WICError("summary status does not match evidence")

    def as_dict(self) -> dict[str, object]:
        return {
            "summary_id": self.summary_id,
            "text": self.text,
            "segments": [item.as_dict() for item in self.segments],
            "citations": list(self.citations),
            "status": self.status,
            "freshness": self.freshness,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "SituationSummary":
        if not isinstance(data, Mapping):
            raise WICError("stored summary is invalid")
        raw_segments = data.get("segments")
        raw_citations = data.get("citations")
        if not isinstance(raw_segments, list) or not isinstance(raw_citations, list):
            raise WICError("stored summary evidence is invalid")
        segments = tuple(SummarySegment.from_dict(item) for item in raw_segments)
        if not all(isinstance(item, str) for item in raw_citations):
            raise WICError("stored summary citations are invalid")
        return cls(
            _string(data.get("summary_id"), "summary id"),
            _string(data.get("text"), "summary text"),
            segments, tuple(raw_citations), _string(data.get("status"), "summary status"),
            _string(data.get("freshness"), "summary freshness"),
            _string(data.get("created_at"), "summary timestamp"),
        )


class CitedSummaryComposer:
    """Compose dated summaries without accepting unsupported live assertions."""

    def compose(
        self, summary_id: str, segments: Iterable[SummarySegment], created_at: str,
        *, freshness: str = "dated",
    ) -> SituationSummary:
        values = tuple(segments)
        if not values or len(values) > _MAX_SUMMARY_SEGMENTS or any(
            not isinstance(item, SummarySegment) for item in values
        ):
            raise WICError("summary segments are outside the bounded range")
        _stored_timestamp(created_at, "summary timestamp")
        if freshness not in {"dated", "stale"}:
            raise WICError("live freshness requires fresh verified evidence")
        status = "uncertain" if any(item.certainty == "uncertain" for item in values) else (
            "verified" if all(item.certainty == "verified" for item in values) else "supported"
        )
        text_parts = []
        citations: list[str] = []
        for index, item in enumerate(values, 1):
            note = f" (uncertain: {item.uncertainty_note})" if item.uncertainty_note else ""
            text_parts.append(f"{item.text}{note} [{index}]")
            if item.citation_url not in citations:
                citations.append(item.citation_url)
        return SituationSummary(
            summary_id, " ".join(text_parts), values, tuple(citations), status, freshness, created_at,
        )


class SummaryStore:
    """Persist bounded cited summaries for dated retrieval."""

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
            "CREATE TABLE IF NOT EXISTS wic_summaries (summary_id TEXT PRIMARY KEY, record_json TEXT NOT NULL)"
        )
        self.db.commit()

    def __enter__(self) -> "SummaryStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def save(self, summary: SituationSummary) -> bool:
        if not isinstance(summary, SituationSummary):
            raise WICError("summary is required")
        payload = json.dumps(summary.as_dict(), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_RECORD_BYTES:
            raise WICError("summary exceeds the bounded size")
        try:
            with self.db:
                cursor = self.db.execute(
                    "INSERT OR IGNORE INTO wic_summaries (summary_id, record_json) VALUES (?, ?)",
                    (summary.summary_id, payload),
                )
            return cursor.rowcount == 1
        except sqlite3.Error as exc:
            raise WICError("summary persistence failed") from exc

    def get(self, summary_id: str) -> SituationSummary | None:
        summary_id = _identifier(summary_id, "summary id")
        row = self.db.execute("SELECT record_json FROM wic_summaries WHERE summary_id=?", (summary_id,)).fetchone()
        if row is None:
            return None
        try:
            return SituationSummary.from_dict(json.loads(row["record_json"]))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise WICError("stored summary is invalid") from exc

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


CitedSituationSummary = CitedSummaryComposer
WICSummaries = SummaryStore


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
    "CategoryAssignment",
    "CategoryStore",
    "CitedSituationSummary",
    "CitedSummaryComposer",
    "ClaimLedger",
    "ClaimRecord",
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
    "StoryCluster",
    "StoryClusterStore",
    "StoryClusterer",
    "StoryCategoryStore",
    "SituationSummary",
    "SummarySegment",
    "SummaryStore",
    "WICError",
    "WICCategoryStore",
    "WICSummaries",
    "WICSourceStore",
    "normalize_url",
]
