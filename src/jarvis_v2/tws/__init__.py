"""Persistent, module-owned storage for the Twelve-Winged quest boundary.

Progression is derived from independently accepted proof records.  Companion
dialogue is never an input to cultivation or skill adaptation.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from ..backend.event_bus import PRIVACY_SCOPES
from ..backend.storage import DEFAULT_MIGRATIONS, Migration, StorageError, StorageManager


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
    Migration(
        module="tws",
        version=3,
        name="tws-quest-catalog-fields",
        tables=("tws_quests",),
        up_sql=(
            "ALTER TABLE tws_quests ADD COLUMN kind TEXT NOT NULL DEFAULT 'skill'",
            "ALTER TABLE tws_quests ADD COLUMN cadence TEXT NOT NULL DEFAULT 'once'",
        ),
        down_sql=(
            "ALTER TABLE tws_quests DROP COLUMN cadence",
            "ALTER TABLE tws_quests DROP COLUMN kind",
        ),
    ),
    Migration(
        module="tws",
        version=4,
        name="tws-proof-review-scope",
        tables=("tws_proofs",),
        up_sql=(
            "ALTER TABLE tws_proofs ADD COLUMN privacy_scope TEXT NOT NULL DEFAULT 'internal_metadata'",
            "ALTER TABLE tws_proofs ADD COLUMN reviewer_id TEXT NOT NULL DEFAULT ''",
        ),
        down_sql=(
            "ALTER TABLE tws_proofs DROP COLUMN reviewer_id",
            "ALTER TABLE tws_proofs DROP COLUMN privacy_scope",
        ),
    ),
    Migration(
        module="tws",
        version=5,
        name="tws-xp-rewards-and-realm-gates",
        tables=("tws_realms", "tws_realm_progress", "tws_xp_rewards"),
        up_sql=(
            "CREATE TABLE tws_realms ("
            "realm_id TEXT PRIMARY KEY, name TEXT NOT NULL, min_xp INTEGER NOT NULL CHECK(min_xp >= 0), "
            "prerequisites_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL"
            ")",
            "CREATE TABLE tws_realm_progress ("
            "profile_id TEXT NOT NULL, realm_id TEXT NOT NULL, unlocked_at TEXT NOT NULL, "
            "PRIMARY KEY(profile_id, realm_id), FOREIGN KEY(realm_id) REFERENCES tws_realms(realm_id)"
            ")",
            "CREATE TABLE tws_xp_rewards ("
            "reward_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, quest_id TEXT NOT NULL, "
            "proof_id TEXT NOT NULL, sync_id TEXT NOT NULL, xp INTEGER NOT NULL CHECK(xp > 0), "
            "awarded_at TEXT NOT NULL, UNIQUE(profile_id, quest_id), UNIQUE(profile_id, sync_id), "
            "FOREIGN KEY(quest_id) REFERENCES tws_quests(quest_id), "
            "FOREIGN KEY(proof_id) REFERENCES tws_proofs(proof_id)"
            ")",
        ),
        down_sql=(
            "DROP TABLE tws_xp_rewards",
            "DROP TABLE tws_realm_progress",
            "DROP TABLE tws_realms",
        ),
    ),
    Migration(
        module="tws",
        version=6,
        name="tws-verified-cultivation-progress",
        tables=("tws_cultivation_achievements", "tws_skill_adaptations"),
        up_sql=(
            "CREATE TABLE tws_cultivation_achievements ("
            "achievement_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, skill_id TEXT NOT NULL, "
            "pattern TEXT NOT NULL, quest_id TEXT NOT NULL, proof_id TEXT NOT NULL, "
            "sync_id TEXT NOT NULL, evidence_sha256 TEXT NOT NULL, recorded_at TEXT NOT NULL, "
            "UNIQUE(profile_id, quest_id), UNIQUE(profile_id, sync_id), "
            "FOREIGN KEY(quest_id) REFERENCES tws_quests(quest_id), "
            "FOREIGN KEY(proof_id) REFERENCES tws_proofs(proof_id)"
            ")",
            "CREATE INDEX tws_cultivation_by_profile_skill "
            "ON tws_cultivation_achievements(profile_id, skill_id, pattern)",
            "CREATE TABLE tws_skill_adaptations ("
            "adaptation_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, skill_id TEXT NOT NULL, "
            "pattern TEXT NOT NULL, basis_sha256 TEXT NOT NULL, created_at TEXT NOT NULL, "
            "UNIQUE(profile_id, skill_id, basis_sha256)"
            ")",
        ),
        down_sql=(
            "DROP TABLE tws_skill_adaptations",
            "DROP INDEX tws_cultivation_by_profile_skill",
            "DROP TABLE tws_cultivation_achievements",
        ),
    ),
    Migration(
        module="tws",
        version=7,
        name="tws-aurelia-dialogue-state",
        tables=("tws_aurelia_states", "tws_aurelia_turns"),
        up_sql=(
            "CREATE TABLE tws_aurelia_states ("
            "profile_id TEXT PRIMARY KEY, personality TEXT NOT NULL, mood TEXT NOT NULL, "
            "narrative_node TEXT NOT NULL, updated_at TEXT NOT NULL"
            ")",
            "CREATE TABLE tws_aurelia_turns ("
            "turn_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, mood TEXT NOT NULL, "
            "narrative_node TEXT NOT NULL, line_sha256 TEXT NOT NULL, created_at TEXT NOT NULL, "
            "UNIQUE(profile_id, turn_id), FOREIGN KEY(profile_id) REFERENCES tws_aurelia_states(profile_id)"
            ")",
            "CREATE INDEX tws_aurelia_turns_by_profile "
            "ON tws_aurelia_turns(profile_id, created_at, turn_id)",
        ),
        down_sql=(
            "DROP INDEX tws_aurelia_turns_by_profile",
            "DROP TABLE tws_aurelia_turns",
            "DROP TABLE tws_aurelia_states",
        ),
    ),
)

TWS_SCHEMA_VERSION = 7
_QUEST_KINDS = frozenset({"daily", "weekly", "skill", "story", "trial"})
_CADENCES = frozenset({"once", "daily", "weekly"})
_AURELIA_MOODS = frozenset({"calm", "curious", "encouraging", "reflective", "playful", "concerned"})
_STATE_ALIASES = {"submitted": "proof_submitted"}
_TRANSITIONS = {
    "draft": frozenset({"offered", "rejected", "expired"}),
    "offered": frozenset({"accepted", "rejected", "expired"}),
    "accepted": frozenset({"in_progress", "proof_submitted", "rejected", "expired"}),
    "in_progress": frozenset({"proof_submitted", "rejected", "expired", "disputed"}),
    "proof_submitted": frozenset({"verified", "rejected", "disputed"}),
    "verified": frozenset({"rewarded"}),
    "rewarded": frozenset({"archived"}),
    "rejected": frozenset(),
    "expired": frozenset(),
    "disputed": frozenset(),
    "archived": frozenset(),
}


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

    def create_quest(
        self,
        quest_id: str,
        wing_id: str,
        title: str,
        *,
        kind: str = "skill",
        cadence: str = "once",
    ) -> dict[str, Any]:
        quest_id = _identifier(quest_id, "quest id")
        wing_id = _identifier(wing_id, "wing id")
        title = _text(title, "quest title")
        if kind not in _QUEST_KINDS:
            raise TWSStoreError("invalid quest kind")
        if cadence not in _CADENCES:
            raise TWSStoreError("invalid quest cadence")
        if self._one("SELECT * FROM tws_wings WHERE wing_id=?", (wing_id,)) is None:
            raise TWSStoreError("quest references an unknown wing")
        existing = self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,))
        if existing is not None:
            if (
                existing["wing_id"] != wing_id
                or existing["title"] != title
                or existing["kind"] != kind
                or existing["cadence"] != cadence
            ):
                raise TWSStoreError("quest identity conflict")
            return existing
        now = _now()
        self.storage.module("tws").insert(
            "tws_quests",
            {"quest_id": quest_id, "wing_id": wing_id, "title": title,
             "state": "draft", "created_at": now, "updated_at": now,
             "kind": kind, "cadence": cadence},
        )
        return self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,)) or {}

    def transition_quest(self, quest_id: str, state: str) -> dict[str, Any]:
        """Advance one quest through the approved lifecycle exactly once."""
        quest_id = _identifier(quest_id, "quest id")
        state = _STATE_ALIASES.get(state, state)
        if state not in _TRANSITIONS:
            raise TWSStoreError("invalid quest state")
        existing = self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,))
        if existing is None:
            raise TWSStoreError("unknown quest")
        if state not in _TRANSITIONS[existing["state"]]:
            raise TWSStoreError("invalid quest state transition")
        if state == "proof_submitted" and not self.proofs(quest_id):
            raise TWSStoreError("quest requires proof before submission")
        if state == "verified" and self._one(
            "SELECT 1 FROM tws_proofs WHERE quest_id=? AND review_state='accepted'",
            (quest_id,),
        ) is None:
            raise TWSStoreError("quest requires accepted proof before verification")
        with self.db:
            self.db.execute(
                "UPDATE tws_quests SET state=?, updated_at=? WHERE quest_id=? AND state=?",
                (state, _now(), quest_id, existing["state"]),
            )
        return self._one("SELECT * FROM tws_quests WHERE quest_id=?", (quest_id,)) or {}

    def catalog(
        self, *, kind: str | None = None, state: str | None = None
    ) -> list[dict[str, Any]]:
        if kind is not None and kind not in _QUEST_KINDS:
            raise TWSStoreError("invalid quest kind")
        if state is not None:
            state = _STATE_ALIASES.get(state, state)
            if state not in _TRANSITIONS:
                raise TWSStoreError("invalid quest state")
        clauses: list[str] = []
        values: list[object] = []
        if kind is not None:
            clauses.append("kind=?")
            values.append(kind)
        if state is not None:
            clauses.append("state=?")
            values.append(state)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return [
            dict(row) for row in self.db.execute(
                "SELECT * FROM tws_quests" + where + " ORDER BY created_at, quest_id",
                tuple(values),
            )
        ]

    def append_proof(
        self,
        proof_id: str,
        quest_id: str,
        evidence: Mapping[str, object],
        *,
        privacy_scope: str = "internal_metadata",
    ) -> dict[str, Any]:
        proof_id = _identifier(proof_id, "proof id")
        quest_id = _identifier(quest_id, "quest id")
        if privacy_scope not in PRIVACY_SCOPES:
            raise TWSStoreError("invalid privacy scope")
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
             "reviewed_at": None, "privacy_scope": privacy_scope, "reviewer_id": ""},
        )
        return self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,)) or {}

    def review_proof(self, proof_id: str, decision: str, reviewer_id: str) -> dict[str, Any]:
        """Record one independent proof decision; repeated same decisions are idempotent."""
        proof_id = _identifier(proof_id, "proof id")
        reviewer_id = _identifier(reviewer_id, "reviewer id")
        if decision not in {"accepted", "rejected"}:
            raise TWSStoreError("invalid proof review decision")
        existing = self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,))
        if existing is None:
            raise TWSStoreError("unknown proof")
        if existing["review_state"] == decision:
            return existing
        if existing["review_state"] != "submitted":
            raise TWSStoreError("proof review is already final")
        with self.db:
            self.db.execute(
                "UPDATE tws_proofs SET review_state=?, reviewed_at=?, reviewer_id=? WHERE proof_id=? AND review_state='submitted'",
                (decision, _now(), reviewer_id, proof_id),
            )
        return self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,)) or {}

    def define_realm(
        self,
        realm_id: str,
        name: str,
        *,
        min_xp: int = 0,
        prerequisites: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        realm_id = _identifier(realm_id, "realm id")
        name = _text(name, "realm name")
        if type(min_xp) is not int or min_xp < 0:
            raise TWSStoreError("invalid realm XP threshold")
        if not isinstance(prerequisites, (tuple, list)):
            raise TWSStoreError("realm prerequisites must be ordered identifiers")
        prerequisite_ids = tuple(_identifier(item, "realm prerequisite") for item in prerequisites)
        if len(prerequisite_ids) != len(set(prerequisite_ids)) or realm_id in prerequisite_ids:
            raise TWSStoreError("invalid realm prerequisites")
        for prerequisite in prerequisite_ids:
            if self._one("SELECT 1 FROM tws_realms WHERE realm_id=?", (prerequisite,)) is None:
                raise TWSStoreError("unknown realm prerequisite")
        encoded = json.dumps(prerequisite_ids, separators=(",", ":"))
        existing = self._one("SELECT * FROM tws_realms WHERE realm_id=?", (realm_id,))
        if existing is not None:
            if (
                existing["name"] != name
                or existing["min_xp"] != min_xp
                or json.loads(existing["prerequisites_json"]) != list(prerequisite_ids)
            ):
                raise TWSStoreError("realm identity conflict")
            return existing
        now = _now()
        self.storage.module("tws").insert(
            "tws_realms",
            {"realm_id": realm_id, "name": name, "min_xp": min_xp,
             "prerequisites_json": encoded, "created_at": now, "updated_at": now},
        )
        return self._one("SELECT * FROM tws_realms WHERE realm_id=?", (realm_id,)) or {}

    def xp_total(self, profile_id: str) -> int:
        profile_id = _identifier(profile_id, "profile id")
        return int(self.db.execute(
            "SELECT COALESCE(SUM(xp), 0) FROM tws_xp_rewards WHERE profile_id=?",
            (profile_id,),
        ).fetchone()[0])

    def award_xp(
        self,
        profile_id: str,
        reward_id: str,
        quest_id: str,
        proof_id: str,
        xp: int,
        sync_id: str,
    ) -> dict[str, Any]:
        """Append one reward only after reviewed proof and verified quest state."""
        profile_id = _identifier(profile_id, "profile id")
        reward_id = _identifier(reward_id, "reward id")
        quest_id = _identifier(quest_id, "quest id")
        proof_id = _identifier(proof_id, "proof id")
        sync_id = _identifier(sync_id, "sync id")
        if type(xp) is not int or xp <= 0:
            raise TWSStoreError("invalid XP amount")
        existing = self._one("SELECT * FROM tws_xp_rewards WHERE reward_id=?", (reward_id,))
        by_sync = self._one(
            "SELECT * FROM tws_xp_rewards WHERE profile_id=? AND sync_id=?",
            (profile_id, sync_id),
        )
        by_quest = self._one(
            "SELECT * FROM tws_xp_rewards WHERE profile_id=? AND quest_id=?",
            (profile_id, quest_id),
        )
        for prior in (existing, by_sync, by_quest):
            if prior is None:
                continue
            if (
                prior["profile_id"] != profile_id
                or prior["quest_id"] != quest_id
                or prior["proof_id"] != proof_id
                or prior["xp"] != xp
            ):
                raise TWSStoreError("reward identity conflict")
            return prior
        quest = self.quest(quest_id)
        proof = self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,))
        if quest is None or proof is None or proof["quest_id"] != quest_id:
            raise TWSStoreError("reward references do not match")
        if quest["state"] != "verified" or proof["review_state"] != "accepted":
            raise TWSStoreError("proof is not independently accepted")
        if proof["privacy_scope"] not in PRIVACY_SCOPES:
            raise TWSStoreError("proof privacy scope is invalid")
        try:
            self.storage.module("tws").insert(
                "tws_xp_rewards",
                {"reward_id": reward_id, "profile_id": profile_id, "quest_id": quest_id,
                 "proof_id": proof_id, "sync_id": sync_id, "xp": xp, "awarded_at": _now()},
            )
        except StorageError as exc:
            prior = self._one(
                "SELECT * FROM tws_xp_rewards WHERE profile_id=? AND (sync_id=? OR quest_id=?)",
                (profile_id, sync_id, quest_id),
            )
            if prior is not None and prior["quest_id"] == quest_id and prior["proof_id"] == proof_id and prior["xp"] == xp:
                return prior
            raise TWSStoreError("reward identity conflict") from exc
        return self._one("SELECT * FROM tws_xp_rewards WHERE reward_id=?", (reward_id,)) or {}

    def unlock_realm(self, profile_id: str, realm_id: str) -> dict[str, Any]:
        profile_id = _identifier(profile_id, "profile id")
        realm_id = _identifier(realm_id, "realm id")
        realm = self._one("SELECT * FROM tws_realms WHERE realm_id=?", (realm_id,))
        if realm is None:
            raise TWSStoreError("unknown realm")
        existing = self._one(
            "SELECT * FROM tws_realm_progress WHERE profile_id=? AND realm_id=?",
            (profile_id, realm_id),
        )
        if existing is not None:
            return existing
        if self.xp_total(profile_id) < realm["min_xp"]:
            raise TWSStoreError("realm XP prerequisite is not met")
        for prerequisite in json.loads(realm["prerequisites_json"]):
            if self._one(
                "SELECT 1 FROM tws_realm_progress WHERE profile_id=? AND realm_id=?",
                (profile_id, prerequisite),
            ) is None:
                raise TWSStoreError("realm prerequisite is not unlocked")
        self.storage.module("tws").insert(
            "tws_realm_progress",
            {"profile_id": profile_id, "realm_id": realm_id, "unlocked_at": _now()},
        )
        return self._one(
            "SELECT * FROM tws_realm_progress WHERE profile_id=? AND realm_id=?",
            (profile_id, realm_id),
        ) or {}

    def record_achievement(
        self,
        profile_id: str,
        achievement_id: str,
        skill_id: str,
        pattern: str,
        quest_id: str,
        proof_id: str,
        sync_id: str,
    ) -> dict[str, Any]:
        """Record progression only from an independently accepted quest proof."""
        profile_id = _identifier(profile_id, "profile id")
        achievement_id = _identifier(achievement_id, "achievement id")
        skill_id = _identifier(skill_id, "skill id")
        pattern = _identifier(pattern, "achievement pattern")
        quest_id = _identifier(quest_id, "quest id")
        proof_id = _identifier(proof_id, "proof id")
        sync_id = _identifier(sync_id, "sync id")
        existing = self._one(
            "SELECT * FROM tws_cultivation_achievements WHERE achievement_id=?",
            (achievement_id,),
        )
        by_quest = self._one(
            "SELECT * FROM tws_cultivation_achievements WHERE profile_id=? AND quest_id=?",
            (profile_id, quest_id),
        )
        by_sync = self._one(
            "SELECT * FROM tws_cultivation_achievements WHERE profile_id=? AND sync_id=?",
            (profile_id, sync_id),
        )
        for prior in (existing, by_quest, by_sync):
            if prior is None:
                continue
            if any(
                prior[field] != value
                for field, value in {
                    "profile_id": profile_id,
                    "skill_id": skill_id,
                    "pattern": pattern,
                    "quest_id": quest_id,
                    "proof_id": proof_id,
                    "sync_id": sync_id,
                }.items()
            ):
                raise TWSStoreError("achievement identity conflict")
            return prior
        quest = self.quest(quest_id)
        proof = self._one("SELECT * FROM tws_proofs WHERE proof_id=?", (proof_id,))
        if quest is None or proof is None or proof["quest_id"] != quest_id:
            raise TWSStoreError("achievement references do not match")
        if proof["review_state"] != "accepted" or not proof["reviewer_id"]:
            raise TWSStoreError("achievement requires independently accepted proof")
        if proof["privacy_scope"] not in PRIVACY_SCOPES:
            raise TWSStoreError("achievement proof privacy scope is invalid")
        if quest["state"] not in {"verified", "rewarded", "archived"}:
            raise TWSStoreError("achievement requires a verified quest")
        self.storage.module("tws").insert(
            "tws_cultivation_achievements",
            {
                "achievement_id": achievement_id,
                "profile_id": profile_id,
                "skill_id": skill_id,
                "pattern": pattern,
                "quest_id": quest_id,
                "proof_id": proof_id,
                "sync_id": sync_id,
                "evidence_sha256": proof["evidence_sha256"],
                "recorded_at": _now(),
            },
        )
        return self._one(
            "SELECT * FROM tws_cultivation_achievements WHERE achievement_id=?",
            (achievement_id,),
        ) or {}

    def achievements(
        self, profile_id: str, *, skill_id: str | None = None
    ) -> list[dict[str, Any]]:
        profile_id = _identifier(profile_id, "profile id")
        values: list[object] = [profile_id]
        where = "profile_id=?"
        if skill_id is not None:
            skill_id = _identifier(skill_id, "skill id")
            where += " AND skill_id=?"
            values.append(skill_id)
        return [
            dict(row)
            for row in self.db.execute(
                "SELECT achievement_id, profile_id, skill_id, pattern, quest_id, proof_id, "
                "sync_id, evidence_sha256, recorded_at "
                "FROM tws_cultivation_achievements "
                f"WHERE {where} ORDER BY recorded_at, achievement_id",
                tuple(values),
            )
        ]

    def cultivation_progress(self, profile_id: str, skill_id: str) -> dict[str, Any]:
        """Summarize verified progress without exposing proof contents."""
        profile_id = _identifier(profile_id, "profile id")
        skill_id = _identifier(skill_id, "skill id")
        rows = self.achievements(profile_id, skill_id=skill_id)
        pattern_counts: dict[str, int] = {}
        for row in rows:
            pattern_counts[row["pattern"]] = pattern_counts.get(row["pattern"], 0) + 1
        xp = int(self.db.execute(
            "SELECT COALESCE(SUM(r.xp), 0) FROM tws_xp_rewards r "
            "JOIN tws_cultivation_achievements a ON a.quest_id=r.quest_id "
            "WHERE a.profile_id=? AND a.skill_id=?",
            (profile_id, skill_id),
        ).fetchone()[0])
        return {
            "profile_id": profile_id,
            "skill_id": skill_id,
            "verified_achievements": len(rows),
            "pattern_counts": dict(sorted(pattern_counts.items())),
            "xp": xp,
        }

    def adapt_skill(
        self,
        profile_id: str,
        adaptation_id: str,
        skill_id: str,
        *,
        pattern: str | None = None,
    ) -> dict[str, Any]:
        """Persist a deterministic adaptation selected from verified patterns."""
        profile_id = _identifier(profile_id, "profile id")
        adaptation_id = _identifier(adaptation_id, "adaptation id")
        skill_id = _identifier(skill_id, "skill id")
        if pattern is not None:
            pattern = _identifier(pattern, "adaptation pattern")
        rows = self.achievements(profile_id, skill_id=skill_id)
        if not rows:
            raise TWSStoreError("skill adaptation requires verified achievement")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["pattern"]] = counts.get(row["pattern"], 0) + 1
        if pattern is None:
            pattern = min(counts, key=lambda item: (-counts[item], item))
        elif pattern not in counts:
            raise TWSStoreError("adaptation pattern has no verified achievement")
        basis = json.dumps(
            [
                (row["achievement_id"], row["quest_id"], row["evidence_sha256"])
                for row in rows
            ],
            separators=(",", ":"),
        )
        basis_sha256 = hashlib.sha256(basis.encode("utf-8")).hexdigest()
        existing = self._one(
            "SELECT * FROM tws_skill_adaptations WHERE adaptation_id=?",
            (adaptation_id,),
        )
        if existing is not None:
            if (
                existing["profile_id"] != profile_id
                or existing["skill_id"] != skill_id
                or existing["pattern"] != pattern
                or existing["basis_sha256"] != basis_sha256
            ):
                raise TWSStoreError("skill adaptation identity conflict")
            return existing
        prior = self._one(
            "SELECT * FROM tws_skill_adaptations WHERE profile_id=? AND skill_id=? AND basis_sha256=?",
            (profile_id, skill_id, basis_sha256),
        )
        if prior is not None:
            if prior["pattern"] != pattern:
                raise TWSStoreError("skill adaptation identity conflict")
            return prior
        self.storage.module("tws").insert(
            "tws_skill_adaptations",
            {
                "adaptation_id": adaptation_id,
                "profile_id": profile_id,
                "skill_id": skill_id,
                "pattern": pattern,
                "basis_sha256": basis_sha256,
                "created_at": _now(),
            },
        )
        return self._one(
            "SELECT * FROM tws_skill_adaptations WHERE adaptation_id=?",
            (adaptation_id,),
        ) or {}

    def set_aurelia_state(
        self,
        profile_id: str,
        *,
        personality: str = "aurelia",
        mood: str = "calm",
        narrative_node: str = "sanctuary",
    ) -> dict[str, Any]:
        """Update dialogue state only; it has no XP or finance side effects."""
        profile_id = _identifier(profile_id, "profile id")
        personality = _identifier(personality, "personality")
        mood = _identifier(mood, "dialogue mood")
        narrative_node = _identifier(narrative_node, "narrative node")
        if mood not in _AURELIA_MOODS:
            raise TWSStoreError("invalid dialogue mood")
        existing = self._one(
            "SELECT * FROM tws_aurelia_states WHERE profile_id=?", (profile_id,)
        )
        if existing is None:
            self.storage.module("tws").insert(
                "tws_aurelia_states",
                {
                    "profile_id": profile_id,
                    "personality": personality,
                    "mood": mood,
                    "narrative_node": narrative_node,
                    "updated_at": _now(),
                },
            )
        else:
            with self.db:
                self.db.execute(
                    "UPDATE tws_aurelia_states SET personality=?, mood=?, narrative_node=?, updated_at=? "
                    "WHERE profile_id=?",
                    (personality, mood, narrative_node, _now(), profile_id),
                )
        return self._one(
            "SELECT * FROM tws_aurelia_states WHERE profile_id=?", (profile_id,)
        ) or {}

    def record_aurelia_turn(
        self,
        profile_id: str,
        turn_id: str,
        line: str,
        *,
        personality: str = "aurelia",
        mood: str = "calm",
        narrative_node: str = "sanctuary",
    ) -> dict[str, Any]:
        """Record only a bounded hash of dialogue content and its narrative state."""
        profile_id = _identifier(profile_id, "profile id")
        turn_id = _identifier(turn_id, "dialogue turn id")
        line = _text(line, "dialogue line")
        line_sha256 = hashlib.sha256(line.encode("utf-8")).hexdigest()
        personality = _identifier(personality, "personality")
        mood = _identifier(mood, "dialogue mood")
        narrative_node = _identifier(narrative_node, "narrative node")
        if mood not in _AURELIA_MOODS:
            raise TWSStoreError("invalid dialogue mood")
        existing = self._one(
            "SELECT * FROM tws_aurelia_turns WHERE turn_id=?", (turn_id,)
        )
        if existing is not None:
            if (
                existing["profile_id"] != profile_id
                or existing["mood"] != mood
                or existing["narrative_node"] != narrative_node
                or existing["line_sha256"] != line_sha256
            ):
                raise TWSStoreError("dialogue turn identity conflict")
            return existing
        self.set_aurelia_state(
            profile_id,
            personality=personality,
            mood=mood,
            narrative_node=narrative_node,
        )
        self.storage.module("tws").insert(
            "tws_aurelia_turns",
            {
                "turn_id": turn_id,
                "profile_id": profile_id,
                "mood": mood,
                "narrative_node": narrative_node,
                "line_sha256": line_sha256,
                "created_at": _now(),
            },
        )
        return self._one(
            "SELECT * FROM tws_aurelia_turns WHERE turn_id=?", (turn_id,)
        ) or {}

    def aurelia_state(self, profile_id: str) -> dict[str, Any] | None:
        return self._one(
            "SELECT * FROM tws_aurelia_states WHERE profile_id=?",
            (_identifier(profile_id, "profile id"),),
        )

    def aurelia_turns(self, profile_id: str) -> list[dict[str, Any]]:
        profile_id = _identifier(profile_id, "profile id")
        return [
            dict(row)
            for row in self.db.execute(
                "SELECT turn_id, profile_id, mood, narrative_node, line_sha256, created_at "
                "FROM tws_aurelia_turns WHERE profile_id=? ORDER BY created_at, turn_id",
                (profile_id,),
            )
        ]

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


class AureliaDialogue:
    """Narrow dialogue façade; XP and finance APIs are intentionally absent."""

    def __init__(self, store: QuestStore) -> None:
        self._store = store

    def record_turn(
        self,
        profile_id: str,
        turn_id: str,
        line: str,
        *,
        personality: str = "aurelia",
        mood: str = "calm",
        narrative_node: str = "sanctuary",
    ) -> dict[str, Any]:
        return self._store.record_aurelia_turn(
            profile_id,
            turn_id,
            line,
            personality=personality,
            mood=mood,
            narrative_node=narrative_node,
        )

    def state(self, profile_id: str) -> dict[str, Any] | None:
        return self._store.aurelia_state(profile_id)

    def turns(self, profile_id: str) -> list[dict[str, Any]]:
        return self._store.aurelia_turns(profile_id)


__all__ = [
    "AureliaDialogue",
    "QuestStore",
    "TWS_MIGRATIONS",
    "TWS_SCHEMA_VERSION",
    "TWSStoreError",
]
