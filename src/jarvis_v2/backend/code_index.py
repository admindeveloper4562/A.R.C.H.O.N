"""Provenance-bound AST and SQLite FTS5 indexing for repository source."""
from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
import hashlib
from pathlib import PurePosixPath
import re
import sqlite3
from pathlib import Path
from typing import Any


MAX_SOURCE_BYTES = 512 * 1024
MAX_QUERY_BYTES = 512
MAX_RESULTS = 100
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SENSITIVE_PATH = re.compile(
    r"(?:^|/)(?:\.env(?:\..*)?|credentials(?:\..*)?|secrets(?:\..*)?|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)(?:\..*)?|[^/]+\.(?:pem|key))$",
    re.IGNORECASE,
)
_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|"
    r"client[_-]?secret|private[_-]?key)\s*[:=]\s*[^\s#]+"
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class CodeIndexError(ValueError):
    """Raised when source cannot be safely indexed or searched."""


def _sha(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SHA1.fullmatch(value):
        raise CodeIndexError(f"invalid {label}")
    return value


def _path(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise CodeIndexError("invalid source path")
    normalized = value.replace("\\", "/")
    parsed = PurePosixPath(normalized)
    if parsed.is_absolute() or ".." in parsed.parts or str(parsed) != normalized:
        raise CodeIndexError("source path must be repository-relative")
    return str(parsed)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _content(value: str | bytes) -> str:
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CodeIndexError("source must be UTF-8 text") from exc
    if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise CodeIndexError("source exceeds bounded size")
    if "\x00" in value:
        raise CodeIndexError("source contains NUL")
    return value


def _language(path: str, value: str | None) -> str:
    result = value or ("python" if path.endswith((".py", ".pyi")) else "text")
    if not isinstance(result, str) or not _IDENTIFIER.fullmatch(result):
        raise CodeIndexError("invalid source language")
    return result


def _sensitive(path: str, content: str) -> bool:
    return bool(_SENSITIVE_PATH.search(path) or _SENSITIVE_ASSIGNMENT.search(content))


def _symbols(path: str, content: str, language: str) -> list[dict[str, Any]]:
    if language != "python":
        return []
    try:
        tree = ast.parse(content, filename=path)
    except SyntaxError as exc:
        raise CodeIndexError("python source is not syntactically valid") from exc
    result: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            if isinstance(node, ast.AsyncFunctionDef):
                kind = "async_function"
            if node.name.startswith("test_"):
                kind = "test"
            result.append({"name": node.name, "qualified_name": node.name, "kind": kind, "line": node.lineno})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result.append({"name": alias.asname or alias.name, "qualified_name": alias.name, "kind": "import", "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                qualified = f"{module}.{alias.name}" if module else alias.name
                result.append({"name": alias.asname or alias.name, "qualified_name": qualified, "kind": "import", "line": node.lineno})
    return sorted(result, key=lambda item: (item["line"], item["kind"], item["qualified_name"]))


class RepositoryIndex:
    """Index repository text and Python symbols in a caller-owned SQLite DB."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        try:
            self.db.executescript(
                """
                CREATE TABLE IF NOT EXISTS code_index_documents (
                    path TEXT NOT NULL,
                    source_sha TEXT NOT NULL,
                    blob_sha TEXT NOT NULL,
                    language TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    PRIMARY KEY (source_sha, path)
                );
                CREATE TABLE IF NOT EXISTS code_index_symbols (
                    source_sha TEXT NOT NULL,
                    path TEXT NOT NULL,
                    blob_sha TEXT NOT NULL,
                    name TEXT NOT NULL,
                    qualified_name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    line INTEGER NOT NULL,
                    FOREIGN KEY (source_sha, path)
                      REFERENCES code_index_documents(source_sha, path)
                      ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_code_index_symbols_name
                    ON code_index_symbols(name, qualified_name);
                CREATE VIRTUAL TABLE IF NOT EXISTS code_index_fts USING fts5(
                    path UNINDEXED,
                    source_sha UNINDEXED,
                    blob_sha UNINDEXED,
                    symbols,
                    content
                );
                """
            )
            self.db.commit()
        except sqlite3.OperationalError as exc:
            self.db.rollback()
            raise CodeIndexError("SQLite FTS5 is unavailable") from exc

    def __enter__(self) -> "RepositoryIndex":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def index_file(
        self,
        path: str,
        content: str | bytes,
        *,
        blob_sha: str,
        source_sha: str,
        language: str | None = None,
    ) -> dict[str, Any]:
        path = _path(path)
        blob_sha = _sha(blob_sha, "blob SHA")
        source_sha = _sha(source_sha, "source SHA")
        content = _content(content)
        language = _language(path, language)
        if _sensitive(path, content):
            return {"indexed": False, "excluded": True, "path": path, "reason": "sensitive_source"}
        symbols = _symbols(path, content, language)
        symbols_text = " ".join(
            f"{item['name']} {item['qualified_name']} {item['kind']}" for item in symbols
        )
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        try:
            with self.db:
                self.db.execute(
                    "DELETE FROM code_index_fts WHERE path=? AND source_sha=?", (path, source_sha)
                )
                self.db.execute(
                    "DELETE FROM code_index_symbols WHERE path=? AND source_sha=?", (path, source_sha)
                )
                self.db.execute(
                    "DELETE FROM code_index_documents WHERE path=? AND source_sha=?", (path, source_sha)
                )
                self.db.execute(
                    """INSERT INTO code_index_documents
                       (path, source_sha, blob_sha, language, content_sha256, indexed_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (path, source_sha, blob_sha, language, content_sha256, _now()),
                )
                self.db.executemany(
                    """INSERT INTO code_index_symbols
                       (source_sha, path, blob_sha, name, qualified_name, kind, line)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [
                        (source_sha, path, blob_sha, item["name"], item["qualified_name"], item["kind"], item["line"])
                        for item in symbols
                    ],
                )
                self.db.execute(
                    "INSERT INTO code_index_fts(path, source_sha, blob_sha, symbols, content) VALUES (?, ?, ?, ?, ?)",
                    (path, source_sha, blob_sha, symbols_text, content),
                )
        except sqlite3.Error as exc:
            raise CodeIndexError("source indexing failed") from exc
        return {
            "indexed": True,
            "excluded": False,
            "path": path,
            "source_sha": source_sha,
            "blob_sha": blob_sha,
            "symbol_count": len(symbols),
            "content_sha256": content_sha256,
        }

    index = index_file

    def search(self, query: str, *, limit: int = 20, source_sha: str | None = None) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip() or len(query.encode("utf-8")) > MAX_QUERY_BYTES:
            raise CodeIndexError("search query is outside the bounded range")
        if any(ord(char) < 32 for char in query):
            raise CodeIndexError("search query contains control characters")
        if type(limit) is not int or not 1 <= limit <= MAX_RESULTS:
            raise CodeIndexError("search limit is outside the bounded range")
        # Quote user text so punctuation cannot become FTS5 operators.
        match_query = '"' + query.replace('"', '""') + '"'
        args: list[Any] = [match_query]
        clause = "code_index_fts MATCH ?"
        if source_sha is not None:
            args.append(_sha(source_sha, "source SHA"))
            clause += " AND source_sha=?"
        args.append(limit)
        rows = self.db.execute(
            f"""SELECT path, source_sha, blob_sha,
                       snippet(code_index_fts, 4, '', '', ' … ', 12) AS snippet
                FROM code_index_fts WHERE {clause} ORDER BY rank LIMIT ?""",
            args,
        )
        return [dict(row) for row in rows]

    def symbols(self, *, path: str | None = None, source_sha: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        args: list[Any] = []
        if path is not None:
            clauses.append("path=?"); args.append(_path(path))
        if source_sha is not None:
            clauses.append("source_sha=?"); args.append(_sha(source_sha, "source SHA"))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return [dict(row) for row in self.db.execute(
            "SELECT source_sha,path,blob_sha,name,qualified_name,kind,line "
            f"FROM code_index_symbols{where} ORDER BY path,line,qualified_name", args
        )]

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


CodeIndex = RepositoryIndex
ASTFTSIndex = RepositoryIndex


__all__ = [
    "ASTFTSIndex",
    "CodeIndex",
    "CodeIndexError",
    "MAX_QUERY_BYTES",
    "MAX_RESULTS",
    "MAX_SOURCE_BYTES",
    "RepositoryIndex",
]
