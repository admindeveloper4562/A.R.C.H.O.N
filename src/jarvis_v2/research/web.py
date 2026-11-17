"""Bounded, allowlisted web discovery and retrieval contracts."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from urllib.parse import urlsplit


MAX_QUERY_BYTES = 512
MAX_RESULTS = 50
MAX_CONTENT_BYTES = 512 * 1024
MAX_TITLE_BYTES = 512
MAX_SNIPPET_BYTES = 2 * 1024
MAX_CITATION_BYTES = 1 * 1024
MAX_SOURCE_POLICIES = 32
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_HOST = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,253}[a-z0-9])?$")


class ResearchError(ValueError):
    """Raised when a Research request or source policy is malformed."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ResearchError(f"invalid {label}")
    return value


def _text(value: str, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise ResearchError(f"invalid {label}")
    return value


def _content(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value.encode("utf-8")) > MAX_CONTENT_BYTES
        or any(ord(char) < 32 and char not in "\n\r\t" for char in value)
    ):
        raise ResearchError("invalid content")
    return value


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ResearchError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class SourcePolicy:
    """One exact-host HTTPS allowlist entry; it grants no network capability."""

    source_id: str
    host: str
    access_scope: str

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source id")
        if not isinstance(self.host, str) or not _HOST.fullmatch(self.host.lower()):
            raise ResearchError("invalid source host")
        _identifier(self.access_scope, "access scope")
        object.__setattr__(self, "host", self.host.lower())

    def allows(self, uri: str) -> bool:
        if not isinstance(uri, str) or len(uri.encode("utf-8")) > 2048:
            return False
        try:
            parsed = urlsplit(uri)
            port = parsed.port
        except ValueError:
            return False
        return (
            parsed.scheme.lower() == "https"
            and parsed.hostname == self.host
            and parsed.username is None
            and parsed.password is None
            and port in (None, 443)
            and not parsed.fragment
            and bool(parsed.path)
        )


@dataclass(frozen=True)
class SearchHit:
    """A source-bound search result with separate publication and observation dates."""

    source_id: str
    uri: str
    title: str
    snippet: str
    citation: str
    source_date: str | None
    observed_at: str

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source id")
        _text(self.uri, "source URI", 2048)
        _text(self.title, "title", MAX_TITLE_BYTES, empty=True)
        _text(self.snippet, "snippet", MAX_SNIPPET_BYTES, empty=True)
        _text(self.citation, "citation", MAX_CITATION_BYTES)
        if self.source_date is not None:
            _text(self.source_date, "source date", 64)
        _text(self.observed_at, "observed timestamp", 64)

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "uri": self.uri,
            "title": self.title,
            "snippet": self.snippet,
            "citation": self.citation,
            "source_date": self.source_date,
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class SearchResult:
    """Bounded search outcome; provider failures never expose raw exceptions."""

    status: str
    observed_at: str
    results: tuple[SearchHit, ...] = ()
    failure: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "empty", "partial", "failed", "blocked"}:
            raise ResearchError("invalid search status")
        _text(self.observed_at, "observed timestamp", 64)
        if len(self.results) > MAX_RESULTS or any(not isinstance(item, SearchHit) for item in self.results):
            raise ResearchError("search results exceed the bounded range")
        if self.failure is not None:
            _identifier(self.failure, "search failure")

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "observed_at": self.observed_at,
            "results": [item.as_dict() for item in self.results],
            "failure": self.failure,
        }


@dataclass(frozen=True)
class FetchedDocument:
    """A bounded fetched document; the caller decides whether to persist it."""

    source_id: str
    uri: str
    title: str
    content: str
    citation: str
    source_date: str | None
    observed_at: str
    content_sha256: str

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source id")
        _text(self.uri, "source URI", 2048)
        _text(self.title, "title", MAX_TITLE_BYTES, empty=True)
        _content(self.content)
        _text(self.citation, "citation", MAX_CITATION_BYTES)
        if self.source_date is not None:
            _text(self.source_date, "source date", 64)
        _text(self.observed_at, "observed timestamp", 64)
        if not re.fullmatch(r"[0-9a-f]{64}", self.content_sha256):
            raise ResearchError("invalid content SHA-256")

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "uri": self.uri,
            "title": self.title,
            "content": self.content,
            "citation": self.citation,
            "source_date": self.source_date,
            "observed_at": self.observed_at,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True)
class FetchResult:
    """Bounded fetch outcome with explicit unavailable and rejected states."""

    status: str
    observed_at: str
    document: FetchedDocument | None = None
    failure: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "empty", "failed", "blocked"}:
            raise ResearchError("invalid fetch status")
        _text(self.observed_at, "observed timestamp", 64)
        if self.document is not None and not isinstance(self.document, FetchedDocument):
            raise ResearchError("invalid fetched document")
        if self.failure is not None:
            _identifier(self.failure, "fetch failure")

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "observed_at": self.observed_at,
            "document": None if self.document is None else self.document.as_dict(),
            "failure": self.failure,
        }


SearchTransport = Callable[[str, SourcePolicy, int], Iterable[Mapping[str, object]]]
FetchTransport = Callable[[str, SourcePolicy, int], Mapping[str, object]]


class WebDiscoveryService:
    """Run bounded discovery/fetch through injected, already-authorized transports."""

    def __init__(
        self,
        sources: Iterable[SourcePolicy],
        *,
        search_transport: SearchTransport | None = None,
        fetch_transport: FetchTransport | None = None,
        clock: Callable[[], datetime] | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        if isinstance(sources, (str, bytes)):
            raise ResearchError("sources must be a collection")
        try:
            policies = tuple(sources)
        except TypeError as exc:
            raise ResearchError("sources must be a collection") from exc
        if not 1 <= len(policies) <= MAX_SOURCE_POLICIES or any(
            not isinstance(item, SourcePolicy) for item in policies
        ):
            raise ResearchError("source policies are outside the bounded range")
        if len({item.source_id for item in policies}) != len(policies):
            raise ResearchError("duplicate source policy")
        if search_transport is not None and not callable(search_transport):
            raise ResearchError("search transport must be callable")
        if fetch_transport is not None and not callable(fetch_transport):
            raise ResearchError("fetch transport must be callable")
        if clock is not None and not callable(clock):
            raise ResearchError("clock must be callable")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 60:
            raise ResearchError("timeout is outside the bounded range")
        self.sources = {item.source_id: item for item in policies}
        self.search_transport = search_transport
        self.fetch_transport = fetch_transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, *, source_id: str | None = None, limit: int = 10) -> SearchResult:
        query = _text(query, "query", MAX_QUERY_BYTES)
        if type(limit) is not int or not 1 <= limit <= MAX_RESULTS:
            raise ResearchError("search limit is outside the bounded range")
        observed_at = _timestamp(self.clock)
        policies = self._policies(source_id)
        if not policies:
            return SearchResult("blocked", observed_at, failure="source_not_allowlisted")
        if self.search_transport is None:
            return SearchResult("failed", observed_at, failure="search_unavailable")
        hits: list[SearchHit] = []
        rejected = False
        try:
            for policy in policies:
                values = self.search_transport(query, policy, min(limit, MAX_RESULTS - len(hits)))
                if isinstance(values, (str, bytes, Mapping)):
                    raise ResearchError("search transport returned an invalid collection")
                for item in values:
                    hit = self._hit(item, policy, observed_at)
                    if hit is None:
                        rejected = True
                        continue
                    hits.append(hit)
                    if len(hits) >= limit:
                        break
                if len(hits) >= limit:
                    break
        except TimeoutError:
            return SearchResult("failed", observed_at, failure="provider_timeout")
        except (ConnectionError, OSError):
            return SearchResult("failed", observed_at, failure="provider_unavailable")
        except (ResearchError, TypeError, ValueError):
            return SearchResult("failed", observed_at, failure="provider_invalid")
        if not hits:
            return SearchResult("failed" if rejected else "empty", observed_at,
                                failure="source_not_allowlisted" if rejected else None)
        return SearchResult("partial" if rejected else "ok", observed_at, tuple(hits))

    def fetch(self, source_id: str, uri: str) -> FetchResult:
        source_id = _identifier(source_id, "source id")
        observed_at = _timestamp(self.clock)
        policy = self.sources.get(source_id)
        if policy is None or not policy.allows(uri):
            return FetchResult("blocked", observed_at, failure="source_not_allowlisted")
        if self.fetch_transport is None:
            return FetchResult("failed", observed_at, failure="fetch_unavailable")
        try:
            payload = self.fetch_transport(uri, policy, self.timeout_seconds)
            if not isinstance(payload, Mapping):
                raise ResearchError("fetch transport returned an invalid object")
            content = payload.get("content")
            if not isinstance(content, str) or not content:
                return FetchResult("empty", observed_at, failure="empty_response")
            _content(content)
            title = payload.get("title", "")
            citation = payload.get("citation")
            if not isinstance(title, str) or not isinstance(citation, str):
                raise ResearchError("fetch metadata is incomplete")
            source_date = payload.get("source_date")
            if source_date is not None and not isinstance(source_date, str):
                raise ResearchError("source date is invalid")
            document = FetchedDocument(
                source_id, uri, title, content, citation, source_date, observed_at,
                hashlib.sha256(content.encode("utf-8")).hexdigest(),
            )
            return FetchResult("ok", observed_at, document=document)
        except TimeoutError:
            return FetchResult("failed", observed_at, failure="provider_timeout")
        except (ConnectionError, OSError):
            return FetchResult("failed", observed_at, failure="provider_unavailable")
        except (ResearchError, TypeError, ValueError):
            return FetchResult("failed", observed_at, failure="provider_invalid")

    def _policies(self, source_id: str | None) -> tuple[SourcePolicy, ...]:
        if source_id is None:
            return tuple(self.sources.values())
        source_id = _identifier(source_id, "source id")
        policy = self.sources.get(source_id)
        return () if policy is None else (policy,)

    @staticmethod
    def _hit(item: Mapping[str, object], policy: SourcePolicy, observed_at: str) -> SearchHit | None:
        if not isinstance(item, Mapping):
            raise ResearchError("search result is invalid")
        uri = item.get("uri")
        if not isinstance(uri, str) or not policy.allows(uri):
            return None
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        citation = item.get("citation")
        source_date = item.get("source_date")
        if (
            not isinstance(title, str)
            or not isinstance(snippet, str)
            or not isinstance(citation, str)
        ):
            raise ResearchError("search result metadata is incomplete")
        if source_date is not None and not isinstance(source_date, str):
            raise ResearchError("source date is invalid")
        return SearchHit(policy.source_id, uri, title, snippet, citation, source_date, observed_at)


WebDiscoveryAdapter = WebDiscoveryService
ResearchSourcePolicy = SourcePolicy


__all__ = [
    "FetchResult",
    "FetchedDocument",
    "MAX_CONTENT_BYTES",
    "MAX_QUERY_BYTES",
    "MAX_RESULTS",
    "ResearchError",
    "ResearchSearchResult",
    "ResearchSourcePolicy",
    "SearchHit",
    "SearchResult",
    "SourcePolicy",
    "WebDiscoveryAdapter",
    "WebDiscoveryService",
]


ResearchSearchResult = SearchResult
