"""Durable, provider-neutral conversation turns for Backend-owned storage."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any
from uuid import uuid4


MAX_METADATA_BYTES = 8 * 1024
MAX_TURN_CONTENT_BYTES = 32 * 1024
MAX_TOOL_EFFECTS = 32
MAX_TOOL_EFFECT_BYTES = 16 * 1024
MAX_CONVERSATION_TURNS = 10_000
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_ROLES = frozenset({"system", "developer", "user", "assistant", "tool"})


class ConversationStoreError(ValueError):
    """Raised when a conversation operation is invalid or cannot be persisted."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ConversationStoreError(f"invalid {label}")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _json(value: object, *, limit: int, label: str) -> str:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ConversationStoreError(f"{label} must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > limit:
        raise ConversationStoreError(f"{label} exceeds bounded size")
    return encoded


def _mapping(value: Mapping[str, object] | None, label: str) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ConversationStoreError(f"{label} must be an object")
    return dict(value)


def _effects(value: Sequence[Mapping[str, object]] | None) -> tuple[list[dict[str, object]], str]:
    if value is None:
        items: list[dict[str, object]] = []
    else:
        if isinstance(value, (str, bytes)):
            raise ConversationStoreError("tool_effects must be objects")
        items = []
        for item in value:
            if not isinstance(item, Mapping):
                raise ConversationStoreError("tool_effects must be objects")
            items.append(dict(item))
    if len(items) > MAX_TOOL_EFFECTS:
        raise ConversationStoreError("too many tool effects")
    encoded = _json(items, limit=MAX_TOOL_EFFECT_BYTES, label="tool_effects")
    return items, encoded


class ConversationStore:
    """Persist conversations and ordered turns on a local SQLite database.

    The store keeps provider/model identifiers and structured tool-effect
    receipts as data, so the conversation contract does not depend on one AI
    provider. Callers are responsible for passing redacted effect metadata;
    values are bounded before they reach SQLite.
    """

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                status TEXT NOT NULL CHECK(status IN ('active','completed','archived')),
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS conversation_turns (
                turn_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                sequence INTEGER NOT NULL CHECK(sequence > 0),
                role TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_effects_json TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE,
                UNIQUE(conversation_id, sequence),
                UNIQUE(conversation_id, idempotency_key)
            );
            CREATE INDEX IF NOT EXISTS idx_conversation_turns_sequence
                ON conversation_turns(conversation_id, sequence);
            """
        )
        self.db.commit()

    def __enter__(self) -> "ConversationStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()

    def create_conversation(
        self,
        conversation_id: str | None = None,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Create a conversation, or return the identical explicit one on replay."""
        conversation_id = _identifier(conversation_id or uuid4().hex, "conversation_id")
        metadata_dict = _mapping(metadata, "metadata")
        metadata_json = _json(metadata_dict, limit=MAX_METADATA_BYTES, label="metadata")
        now = _now()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
            ).fetchone()
            if existing is not None:
                if existing["metadata_json"] != metadata_json:
                    raise ConversationStoreError("conversation metadata conflict")
                self.db.commit()
                return self._conversation(existing, include_turns=False)
            self.db.execute(
                "INSERT INTO conversations(conversation_id,status,metadata_json,created_at,updated_at) "
                "VALUES (?,?,?,?,?)",
                (conversation_id, "active", metadata_json, now, now),
            )
            self.db.commit()
            return self._conversation(
                self.db.execute(
                    "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
                ).fetchone(),
                include_turns=False,
            )
        except (sqlite3.Error, ConversationStoreError) as exc:
            self.db.rollback()
            if isinstance(exc, ConversationStoreError):
                raise
            raise ConversationStoreError("conversation creation failed") from exc

    def open_conversation(
        self,
        conversation_id: str,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Open an existing conversation or create it with an explicit ID."""
        if metadata is None:
            conversation_id = _identifier(conversation_id, "conversation_id")
            row = self.db.execute(
                "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
            ).fetchone()
            if row is not None:
                return self._conversation(row, include_turns=False)
        return self.create_conversation(conversation_id, metadata=metadata)

    def append_turn(
        self,
        conversation_id: str,
        *,
        role: str,
        provider: str,
        content: str,
        model: str = "",
        tool_effects: Sequence[Mapping[str, object]] | None = None,
        idempotency_key: str | None = None,
        turn_id: str | None = None,
    ) -> dict[str, Any]:
        """Append one ordered turn and return the existing row on safe replay."""
        conversation_id = _identifier(conversation_id, "conversation_id")
        if role not in _ROLES:
            raise ConversationStoreError("invalid turn role")
        provider = _identifier(provider, "provider")
        if not isinstance(model, str) or len(model.encode("utf-8")) > 256:
            raise ConversationStoreError("invalid model")
        if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_TURN_CONTENT_BYTES:
            raise ConversationStoreError("content exceeds bounded size")
        _effect_items, effects_json = _effects(tool_effects)
        turn_id = _identifier(turn_id or uuid4().hex, "turn_id")
        idempotency_key = _identifier(idempotency_key or turn_id, "idempotency_key")
        now = _now()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            if self.db.execute(
                "SELECT 1 FROM conversations WHERE conversation_id=?", (conversation_id,)
            ).fetchone() is None:
                raise ConversationStoreError("unknown conversation")
            existing = self.db.execute(
                "SELECT * FROM conversation_turns WHERE conversation_id=? AND idempotency_key=?",
                (conversation_id, idempotency_key),
            ).fetchone()
            if existing is not None:
                if not self._same_turn(
                    existing, role, provider, model, content, effects_json
                ):
                    raise ConversationStoreError("turn idempotency conflict")
                self.db.commit()
                return self._turn(existing)
            count = self.db.execute(
                "SELECT COUNT(*) FROM conversation_turns WHERE conversation_id=?", (conversation_id,)
            ).fetchone()[0]
            if count >= MAX_CONVERSATION_TURNS:
                raise ConversationStoreError("conversation turn limit exceeded")
            sequence = self.db.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 FROM conversation_turns WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()[0]
            self.db.execute(
                "INSERT INTO conversation_turns "
                "(turn_id,conversation_id,sequence,role,provider,model,content,tool_effects_json,idempotency_key,created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    turn_id, conversation_id, sequence, role, provider, model, content,
                    effects_json, idempotency_key, now,
                ),
            )
            self.db.execute(
                "UPDATE conversations SET updated_at=? WHERE conversation_id=?",
                (now, conversation_id),
            )
            self.db.commit()
            return self._turn(
                self.db.execute("SELECT * FROM conversation_turns WHERE turn_id=?", (turn_id,)).fetchone()
            )
        except (sqlite3.Error, ConversationStoreError) as exc:
            self.db.rollback()
            if isinstance(exc, ConversationStoreError):
                raise
            raise ConversationStoreError("turn persistence failed") from exc

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        conversation_id = _identifier(conversation_id, "conversation_id")
        row = self.db.execute(
            "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
        ).fetchone()
        if row is None:
            raise ConversationStoreError("unknown conversation")
        return self._conversation(row, include_turns=True)

    def list_turns(self, conversation_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        conversation_id = _identifier(conversation_id, "conversation_id")
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ConversationStoreError("invalid turn limit")
        if self.db.execute(
            "SELECT 1 FROM conversations WHERE conversation_id=?", (conversation_id,)
        ).fetchone() is None:
            raise ConversationStoreError("unknown conversation")
        rows = self.db.execute(
            "SELECT * FROM conversation_turns WHERE conversation_id=? ORDER BY sequence LIMIT ?",
            (conversation_id, limit),
        )
        return [self._turn(row) for row in rows]

    @staticmethod
    def _same_turn(
        row: sqlite3.Row,
        role: str,
        provider: str,
        model: str,
        content: str,
        effects_json: str,
    ) -> bool:
        return (
            row["role"] == role
            and row["provider"] == provider
            and row["model"] == model
            and row["content"] == content
            and row["tool_effects_json"] == effects_json
        )

    @staticmethod
    def _turn(row: sqlite3.Row) -> dict[str, Any]:
        try:
            effects = json.loads(row["tool_effects_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ConversationStoreError("stored tool effects are invalid") from exc
        if not isinstance(effects, list):
            raise ConversationStoreError("stored tool effects are not a list")
        return {
            "turn_id": row["turn_id"],
            "conversation_id": row["conversation_id"],
            "sequence": row["sequence"],
            "role": row["role"],
            "provider": row["provider"],
            "model": row["model"],
            "content": row["content"],
            "tool_effects": effects,
            "idempotency_key": row["idempotency_key"],
            "created_at": row["created_at"],
        }

    def _conversation(self, row: sqlite3.Row, *, include_turns: bool) -> dict[str, Any]:
        try:
            metadata = json.loads(row["metadata_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ConversationStoreError("stored conversation metadata is invalid") from exc
        if not isinstance(metadata, dict):
            raise ConversationStoreError("stored conversation metadata is not an object")
        result: dict[str, Any] = {
            "conversation_id": row["conversation_id"],
            "status": row["status"],
            "metadata": metadata,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        if include_turns:
            result["turns"] = self.list_turns(row["conversation_id"], limit=1000)
        return result


__all__ = [
    "ConversationStore",
    "ConversationStoreError",
    "MAX_CONVERSATION_TURNS",
    "MAX_METADATA_BYTES",
    "MAX_TOOL_EFFECT_BYTES",
    "MAX_TOOL_EFFECTS",
    "MAX_TURN_CONTENT_BYTES",
]
