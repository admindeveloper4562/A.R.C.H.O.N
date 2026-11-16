"""Scope-filtered, source-grounded document retrieval backed by SQLite FTS5."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import sqlite3
from typing import Any


MAX_DOCUMENT_BYTES = 512 * 1024
MAX_METADATA_BYTES = 4 * 1024
MAX_QUERY_BYTES = 512
MAX_RESULTS = 50
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class RetrievalError(ValueError):
    """Raised when a document or retrieval request is outside policy."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise RetrievalError(f"invalid {label}")
    return value


def _text(value: str, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > limit:
        raise RetrievalError(f"invalid {label}")
    if any(ord(char) < 32 for char in value):
        raise RetrievalError(f"invalid {label}")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class DocumentStore:
    """Persist bounded documents and return only scope-authorized citations."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        try:
            self.db.executescript(
                """
                CREATE TABLE IF NOT EXISTS retrieval_documents (
                    document_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    source_uri TEXT NOT NULL,
                    access_scope TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    citation TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS retrieval_fts USING fts5(
                    document_id UNINDEXED,
                    source_id UNINDEXED,
                    source_uri UNINDEXED,
                    access_scope UNINDEXED,
                    observed_at UNINDEXED,
                    citation UNINDEXED,
                    title,
                    content
                );
                """
            )
            self.db.commit()
        except sqlite3.OperationalError as exc:
            self.db.rollback()
            raise RetrievalError("SQLite FTS5 is unavailable") from exc

    def __enter__(self) -> "DocumentStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def add_document(
        self,
        document_id: str,
        content: str,
        *,
        source_id: str,
        source_uri: str,
        access_scope: str,
        citation: str,
        title: str = "",
        observed_at: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        document_id = _identifier(document_id, "document id")
        source_id = _text(source_id, "source id", 256)
        source_uri = _text(source_uri, "source URI", 1024)
        access_scope = _identifier(access_scope, "access scope")
        citation = _text(citation, "citation", 1024)
        title = "" if title == "" else _text(title, "title", 512)
        if not isinstance(content, str) or not content or len(content.encode("utf-8")) > MAX_DOCUMENT_BYTES:
            raise RetrievalError("document content is outside the bounded range")
        if "\x00" in content:
            raise RetrievalError("document content contains NUL")
        observed_at_provided = observed_at is not None
        observed_at = _now() if observed_at is None else _text(observed_at, "observation timestamp", 64)
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, Mapping):
            raise RetrievalError("document metadata must be an object")
        try:
            import json
            metadata_json = json.dumps(dict(metadata), ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise RetrievalError("document metadata must be bounded JSON") from exc
        if len(metadata_json.encode("utf-8")) > MAX_METADATA_BYTES:
            raise RetrievalError("document metadata exceeds bounded size")
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        expected = {
            "source_id": source_id,
            "source_uri": source_uri,
            "access_scope": access_scope,
            "observed_at": observed_at,
            "citation": citation,
            "title": title,
            "content_sha256": content_sha256,
            "metadata_json": metadata_json,
        }
        try:
            with self.db:
                existing = self.db.execute(
                    "SELECT * FROM retrieval_documents WHERE document_id=?", (document_id,)
                ).fetchone()
                if existing is not None:
                    if any(
                        existing[key] != value
                        for key, value in expected.items()
                        if key != "observed_at" or observed_at_provided
                    ):
                        raise RetrievalError("document identity conflict")
                    return self._snapshot(existing)
                now = _now()
                self.db.execute(
                    """INSERT INTO retrieval_documents
                       (document_id, source_id, source_uri, access_scope, observed_at,
                        citation, title, content_sha256, metadata_json, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (document_id, source_id, source_uri, access_scope, observed_at,
                     citation, title, content_sha256, metadata_json, now),
                )
                self.db.execute(
                    """INSERT INTO retrieval_fts
                       (document_id, source_id, source_uri, access_scope, observed_at,
                        citation, title, content)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (document_id, source_id, source_uri, access_scope, observed_at,
                     citation, title, content),
                )
                return self._snapshot(
                    self.db.execute(
                        "SELECT * FROM retrieval_documents WHERE document_id=?", (document_id,)
                    ).fetchone()
                )
        except (sqlite3.Error, RetrievalError) as exc:
            self.db.rollback()
            if isinstance(exc, RetrievalError):
                raise
            raise RetrievalError("document indexing failed") from exc

    def search(
        self,
        query: str,
        *,
        access_scope: str,
        source_id: str | None = None,
        limit: int = 10,
        reranker: Any | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip() or len(query.encode("utf-8")) > MAX_QUERY_BYTES:
            raise RetrievalError("retrieval query is outside the bounded range")
        if any(ord(char) < 32 for char in query):
            raise RetrievalError("retrieval query contains control characters")
        access_scope = _identifier(access_scope, "access scope")
        if source_id is not None:
            source_id = _text(source_id, "source id", 256)
        if type(limit) is not int or not 1 <= limit <= MAX_RESULTS:
            raise RetrievalError("retrieval limit is outside the bounded range")
        match_query = '"' + query.replace('"', '""') + '"'
        clauses = ["retrieval_fts MATCH ?", "access_scope=?"]
        args: list[Any] = [match_query, access_scope]
        if source_id is not None:
            clauses.append("source_id=?")
            args.append(source_id)
        args.append(limit)
        rows = self.db.execute(
            f"""SELECT document_id, source_id, source_uri, access_scope,
                       observed_at, citation,
                       snippet(retrieval_fts, 7, '', '', ' … ', 16) AS snippet
                FROM retrieval_fts WHERE {' AND '.join(clauses)}
                ORDER BY rank LIMIT ?""",
            args,
        )
        results = [dict(row) for row in rows]
        if reranker is None:
            return results
        try:
            ranked = reranker.rerank(query, results)
            return [dict(item) for item in ranked]
        except (AttributeError, TypeError, ValueError) as exc:
            raise RetrievalError("invalid reranker") from exc

    retrieve = search

    def get(self, document_id: str) -> dict[str, Any]:
        document_id = _identifier(document_id, "document id")
        row = self.db.execute(
            "SELECT * FROM retrieval_documents WHERE document_id=?", (document_id,)
        ).fetchone()
        if row is None:
            raise RetrievalError("unknown document")
        return self._snapshot(row)

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> dict[str, Any]:
        import json
        try:
            metadata = json.loads(row["metadata_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise RetrievalError("stored document metadata is invalid") from exc
        if not isinstance(metadata, dict):
            raise RetrievalError("stored document metadata is not an object")
        return {
            "document_id": row["document_id"],
            "source_id": row["source_id"],
            "source_uri": row["source_uri"],
            "access_scope": row["access_scope"],
            "observed_at": row["observed_at"],
            "citation": row["citation"],
            "title": row["title"],
            "content_sha256": row["content_sha256"],
            "metadata": metadata,
            "updated_at": row["updated_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


RAGStore = DocumentStore
SourceRetriever = DocumentStore


__all__ = [
    "DocumentStore",
    "MAX_DOCUMENT_BYTES",
    "MAX_METADATA_BYTES",
    "MAX_QUERY_BYTES",
    "MAX_RESULTS",
    "RAGStore",
    "RetrievalError",
    "SourceRetriever",
]
