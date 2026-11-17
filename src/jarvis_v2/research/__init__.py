"""Bounded ARCHON Research source and retrieval boundaries."""

from .web import (
    FetchResult,
    FetchedDocument,
    MAX_CONTENT_BYTES,
    MAX_QUERY_BYTES,
    MAX_RESULTS,
    ResearchError,
    ResearchSearchResult,
    ResearchSourcePolicy,
    SearchHit,
    SearchResult,
    SourcePolicy,
    WebDiscoveryAdapter,
    WebDiscoveryService,
)

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
