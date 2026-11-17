"""Persistent, module-owned storage for the Twelve-Winged quest boundary.

The store is intentionally limited to the data foundation.  Quest lifecycle
transitions and reward policy belong to later TWS tasks; this layer preserves
wings and submitted proofs across the versioned SQLite migrations.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from ..backend.storage import DEFAULT_MIGRATIONS, Migration, StorageManager


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MAX_TEXT_BYTES = 4096
_MAX_EVIDENCE_BYTES = 64 * 1024


class TWSStoreError(ValueError):
    """Raised when a TWS record is invalid or conflicts with existing data."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise TWSStoreError(f"invalid {label}")
    return value


def _text(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value.encode("utf-8")) > _MAX_TEXT_BYTES
        or any(ord(char) < 32 for char in value)
    ):
        raise TWSStoreError(f"invalid {label}")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _evidence(value: object) -> tuple[str, str]:
    if not isinstance(value, Mapping):
        raise TWSStoreError("proof evidence must be an object")
    try:
        encoded = json.dumps(
            dict(value), sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise TWSStoreError("proof evidence must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > _MAX_EVIDENCE_BYTES:
        raise TWSStoreError("proof evidence is too large")
    return encoded, hashlib.sha256(encoded.encode("utf-8")).hexdigest()


TWS_MIGRATIONS = DEFAULT_MIGRATIONS + (
    Migration(
        module="tws",
        version=1,
        name="tws-quest-proof-foundation",
        tables=("tws_wings", "tws_quests", "tws_proofs"),
        up_sql=(
            "CREATE TABLE tws_wings ("
            "wing_id TEXT PRIMARY KEY, name TEXT NOT NULL, state TEXT NOT NULL, "
            "created_at TEXT NOT NULL, updated_at TEXT NOT NULL"
            ")",
            "CREATE TABLE tws_quests ("
            "quest_id TEXT PRIMARY KEY, wing_id TEXT NOT NULL, title TEXT NOT NULL, "
            "state TEXT NOT NULL CHECK(state IN ('draft','offered','accepted','in_progress',"
            "'proof_submitted','verified','rewarded','archived','rejected','expired','disputed')), "
            "created_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
            "FOREIGN KEY(wing_id) REFERENCES tws_wings(wing_id)"
            ")",
            "CREATE TABLE tws_proofs ("
            "proof_id TEXT PRIMARY KEY, quest_id TEXT NOT NULL, evidence_json TEXT NOT NULL, "
            "evidence_sha256 TEXT NOT NULL, review_state TEXT NOT NULL CHECK(review_state IN "
            "('submitted','accepted','rejected')), submitted_at TEXT NOT NULL, reviewed_at TEXT, "
            "FOREIGN KEY(quest_id) REFERENCES tws_quests(quest_id)"
            ")",
        ),
        down_sql=(
            "DROP TABLE tws_proofs",
            "DROP TABLE tws_quests",
            "DROP TABLE tws_wings",
        ),
    ),
    Migration(
        module="tws",
        version=2,
        name="tws-quest-proof-lookup-indexes",
        tables=("tws_quests", "tws_proofs"),
        up_sql=(
            "CREATE INDEX tws_quests_by_wing_state ON tws_quests(wing_id,state)",
            "CREATE UNIQUE INDEX tws_proofs_quest_evidence "
            "ON tws_proofs(quest_id,evidence_sha256)",
        ),
        down_sql=(
            "DROP INDEX tws_proofs_quest_evidence",
            "DROP INDEX tws_quests_by_wing_state",
        ),
    ),
)

TWS_SCHEMA_VERSION = 2


class QuestStore:
    """Persist TWS wings, quests and append-only proof submissions."""

    def __init__(self, database: str | Path) -> None:
        self.storage = StorageManager(database, migrations=TWS_MIGRATIONS)
        self.storage.migrate()
        self.db = self.storage.db

    def __enter__(self) -> "QuestStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        self.storage.close()

    @property
    def schema_version(self) -> int:
        row = self.db.execute(
            "SELECT MAX(version) FROM backend_schema_migrations WHERE module='tws'"
        ).fetchone()
        return int(row[0] or 0)

    def applied_migrations(self) -> list[dict[str, Any]]:
        return [
            item for item in self.storage.applied_migrations()
            if item["module"] == "tws"
        ]

    def _one(self, query: str, values: tuple[object, ...]) -> dict[str, Any] | None:
        row = self.db.execute(query, values).fetchone()
        return dict(row) if row is not None else None

    def add_wing(self, wing_id: str, name: str, *, state: str = "active") -> dict[str, Any]:
        wing_id = _identifier(wing_id, "wing id")
        name = _text(name, "wing name")
        state = _text(state, "wing state")
        existing = self._one("SELECT * FROM tws_wings WHERE wing_id=?", (wing_id,))
        if existing is not None:
            if existing["name"] != name or existing["state"] != state:
                raise TWSStoreError("wing identity conflict")
            return existing
        now = _now()
        self.storage.module("tws").insert(
            "tws_wings",
            {"wing_id": wing_id, "name": name, "state": state,
             "created_at": now, "updated_at": now},
        )
        return self._one("SELECT * FROM tws_wings WHERE wing_id=?", (wing_id,)) or {}

    def create_quest(self, quest_id: str, wing_id: str, title: str) -> dict[str, Any]:
        quest_id = _identifier(quest_id, "quest id")
        wing_id = _identifier(wing_id, "wing id")
        title = _text(title, "quest title")
        if self._one("SELECT * FROM tws_wings WHERE wing_id=?", (wing_id,)) is None:
            raise TWSStoreError("quest references an unknown wing")
        existing = self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,))
        if existing is not None:
            if existing["wing_id"] != wing_id or existing["title"] != title:
                raise TWSStoreError("quest identity conflict")
            return existing
        now = _now()
        self.storage.module("tws").insert(
            "tws_quests",
            {"quest_id": quest_id, "wing_id": wing_id, "title": title,
             "state": "draft", "created_at": now, "updated_at": now},
        )
        return self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,)) or {}

    def append_proof(
        self, proof_id: str, quest_id: str, evidence: Mapping[str, object]
    ) -> dict[str, Any]:
        proof_id = _identifier(proof_id, "proof id")
        quest_id = _identifier(quest_id, "quest id")
        evidence_json, evidence_sha256 = _evidence(evidence)
        if self._one("SELECT 1 FROM tws_quests WHERE quest_id=?", (quest_id,)) is None:
            raise TWSStoreError("proof references an unknown quest")
        existing = self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,))
        if existing is not None:
            if existing["quest_id"] != quest_id or existing["evidence_sha256"] != evidence_sha256:
                raise TWSStoreError("proof identity conflict")
            return existing
        duplicate = self._one(
            "SELECT * FROM tws_proofs WHERE quest_id=? AND evidence_sha256=?",
            (quest_id, evidence_sha256),
        )
        if duplicate is not None:
            raise TWSStoreError("duplicate proof submission")
        self.storage.module("tws").insert(
            "tws_proofs",
            {"proof_id": proof_id, "quest_id": quest_id,
             "evidence_json": evidence_json, "evidence_sha256": evidence_sha256,
             "review_state": "submitted", "submitted_at": _now(),
             "reviewed_at": None},
        )
        return self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,)) or {}

    def wing(self, wing_id: str) -> dict[str, Any] | None:
        return self._one("SELECT * FROM tws_wings WHERE wing_id=?", (_identifier(wing_id, "wing id"),))

    def quest(self, quest_id: str) -> dict[str, Any] | None:
        return self._one("SELECT * FROM tws_quests WHERE quest_id=?", (_identifier(quest_id, "quest id"),))

    def proofs(self, quest_id: str) -> list[dict[str, Any]]:
        quest_id = _identifier(quest_id, "quest id")
        return [
            dict(row) for row in self.db.execute(
                "SELECT * FROM tws_proofs WHERE quest_id=? ORDER BY submitted_at, proof_id",
                (quest_id,),
            )
        ]


__all__ = [
    "QuestStore",
    "TWS_MIGRATIONS",
    "TWS_SCHEMA_VERSION",
    "TWSStoreError",
]
