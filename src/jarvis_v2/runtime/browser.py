"""Persistent, allowlisted browser profiles without exposing private session data."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from typing import Callable, Protocol


MAX_ACTIONS = 64
MAX_TARGET_BYTES = 512
MAX_REF_BYTES = 128
MAX_TOOL_RESULT_BYTES = 16 * 1024
MAX_FORM_FIELDS = 32
PROFILE_STATUSES = frozenset({"login_required", "awaiting_human", "ready", "revoked"})
HANDOFF_STATUSES = frozenset({"awaiting_human", "completed"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SITE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$")
_ACTION = re.compile(r"^[a-z][a-z0-9_.:-]{0,63}$")
_OPAQUE_REF = re.compile(r"^ref:[A-Za-z0-9_.:-]{1,120}$")
_TARGET_REF = re.compile(r"^[A-Za-z0-9_.:/#-]{1,256}$")
_FIELD = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,63}$")
_SENSITIVE_FIELD = re.compile(r"(?:auth|cookie|credential|pass|secret|session|token)", re.IGNORECASE)


class BrowserProfileError(ValueError):
    """Raised when a browser profile or action cannot be admitted safely."""


class BrowserToolError(ValueError):
    """Raised when a typed browser operation cannot be safely executed."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise BrowserProfileError(f"invalid {label}")
    return value


def _site(value: str) -> str:
    if not isinstance(value, str) or not _SITE.fullmatch(value):
        raise BrowserProfileError("invalid site")
    return value.lower()


def _actions(values: Iterable[str], label: str = "actions") -> tuple[str, ...]:
    if isinstance(values, (str, bytes, Mapping)):
        raise BrowserProfileError(f"{label} must be a collection")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise BrowserProfileError(f"{label} must be a collection") from exc
    if not 1 <= len(normalized) <= MAX_ACTIONS or len(set(normalized)) != len(normalized):
        raise BrowserProfileError(f"{label} are outside the bounded range")
    if any(not isinstance(value, str) or not _ACTION.fullmatch(value) for value in normalized):
        raise BrowserProfileError(f"{label} contain an invalid action")
    return tuple(sorted(normalized))


def _json(value: object, label: str) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise BrowserProfileError(f"{label} must be JSON serializable") from exc


def _now(clock: Callable[[], float]) -> str:
    value = clock()
    if not isinstance(value, (int, float)) or value < 0:
        raise BrowserProfileError("invalid clock")
    return datetime.fromtimestamp(value, timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BrowserProfile:
    """Persisted profile metadata; the profile directory is adapter-only data."""

    profile_id: str
    site: str
    allowed_actions: tuple[str, ...]
    status: str
    profile_path: str
    updated_at: str

    def model_context(self) -> dict[str, object]:
        """Return safe model metadata without a local path or session material."""
        return {
            "profile_id": self.profile_id,
            "site": self.site,
            "allowed_actions": list(self.allowed_actions),
            "status": self.status,
        }


@dataclass(frozen=True)
class LoginHandoff:
    """Human-login state; no raw session value is retained or returned."""

    handoff_id: str
    profile_id: str
    site: str
    status: str
    updated_at: str

    def model_context(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "profile_id": self.profile_id,
            "site": self.site,
            "status": self.status,
        }


@dataclass(frozen=True)
class BrowserActionReceipt:
    """A bounded authorization receipt for a trusted browser adapter."""

    request_id: str
    profile_id: str
    site: str
    action: str
    target_sha256: str
    confirmed: bool
    created_at: str

    def model_context(self) -> dict[str, object]:
        """Expose outcome metadata only; target and profile path stay outside model context."""
        return {
            "request_id": self.request_id,
            "profile_id": self.profile_id,
            "site": self.site,
            "action": self.action,
            "status": "authorized",
            "confirmed": self.confirmed,
        }


class BrowserAdapter(Protocol):
    """Trusted adapter surface; arbitrary command execution is not part of it."""

    def navigate(self, profile_dir: str, target_ref: str) -> Mapping[str, object]: ...

    def read(self, profile_dir: str, target_ref: str) -> Mapping[str, object]: ...

    def click(self, profile_dir: str, target_ref: str) -> Mapping[str, object]: ...

    def form(
        self, profile_dir: str, target_ref: str, fields: Mapping[str, str]
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class BrowserToolResult:
    """Bounded adapter output explicitly marked as untrusted page data."""

    request_id: str
    operation: str
    data: Mapping[str, object]

    def model_context(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "operation": self.operation,
            "untrusted_page_data": True,
            "data": dict(self.data),
        }


class BrowserToolService:
    """Expose four typed browser operations through the profile policy."""

    def __init__(self, profiles: "BrowserProfileService", adapter: BrowserAdapter) -> None:
        if not isinstance(profiles, BrowserProfileService):
            raise BrowserToolError("browser profiles are required")
        self.profiles = profiles
        self.adapter = adapter

    def navigate(
        self, profile_id: str, request_id: str, *, target_ref: str, confirmed: bool = False
    ) -> BrowserToolResult:
        return self._run(
            profile_id, request_id, "navigate", target_ref, confirmed,
            lambda directory: self.adapter.navigate(directory, target_ref),
        )

    def read(
        self, profile_id: str, request_id: str, *, target_ref: str
    ) -> BrowserToolResult:
        return self._run(
            profile_id, request_id, "read", target_ref, False,
            lambda directory: self.adapter.read(directory, target_ref),
        )

    def click(
        self, profile_id: str, request_id: str, *, target_ref: str, confirmed: bool = False
    ) -> BrowserToolResult:
        return self._run(
            profile_id, request_id, "click", target_ref, confirmed,
            lambda directory: self.adapter.click(directory, target_ref),
        )

    def form(
        self,
        profile_id: str,
        request_id: str,
        *,
        target_ref: str,
        fields: Mapping[str, str],
        confirmed: bool = False,
    ) -> BrowserToolResult:
        safe_fields = self._fields(fields)
        return self._run(
            profile_id, request_id, "form", target_ref, confirmed,
            lambda directory: self.adapter.form(directory, target_ref, safe_fields),
        )

    def _run(
        self,
        profile_id: str,
        request_id: str,
        operation: str,
        target_ref: str,
        confirmed: bool,
        call: Callable[[str], Mapping[str, object]],
    ) -> BrowserToolResult:
        try:
            self.profiles.authorize_action(
                profile_id, request_id, action=operation, target_ref=target_ref, confirmed=confirmed
            )
            context = self.profiles.adapter_context(profile_id)
        except BrowserProfileError as exc:
            raise BrowserToolError(str(exc)) from exc
        try:
            result = call(str(context["profile_dir"]))
        except Exception as exc:
            raise BrowserToolError("browser adapter execution failed") from exc
        return BrowserToolResult(request_id, operation, self._result(result))

    @staticmethod
    def _fields(fields: Mapping[str, str]) -> dict[str, str]:
        if not isinstance(fields, Mapping) or len(fields) > MAX_FORM_FIELDS:
            raise BrowserToolError("form fields are outside the bounded range")
        normalized: dict[str, str] = {}
        for name, value in fields.items():
            if not isinstance(name, str) or not _FIELD.fullmatch(name) or _SENSITIVE_FIELD.search(name):
                raise BrowserToolError("sensitive or invalid form field")
            if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_TARGET_BYTES:
                raise BrowserToolError("form value is outside the bounded range")
            if any(ord(char) < 32 for char in value):
                raise BrowserToolError("form value contains control data")
            normalized[name] = value
        return normalized

    @staticmethod
    def _result(result: Mapping[str, object]) -> Mapping[str, object]:
        if not isinstance(result, Mapping):
            raise BrowserToolError("browser adapter result must be an object")
        try:
            encoded = json.dumps(
                dict(result), ensure_ascii=True, allow_nan=False, separators=(",", ":")
            )
            if len(encoded.encode("utf-8")) > MAX_TOOL_RESULT_BYTES:
                raise BrowserToolError("browser adapter result is too large")
            normalized = json.loads(encoded)
        except BrowserToolError:
            raise
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BrowserToolError("browser adapter result is invalid") from exc
        if not isinstance(normalized, dict):
            raise BrowserToolError("browser adapter result is invalid")
        return normalized


class BrowserProfileService:
    """Persist scoped browser profiles and human handoffs without browser I/O."""

    def __init__(
        self,
        database: str | Path | sqlite3.Connection,
        profile_root: str | Path,
        *,
        site_actions: Mapping[str, Iterable[str]],
        read_only_actions: Iterable[str] = ("read", "search", "view", "list", "status"),
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db: sqlite3.Connection = (
            database if isinstance(database, sqlite3.Connection) else sqlite3.connect(str(database))
        )
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self._clock = clock
        self._policies = self._normalize_policies(site_actions)
        self._read_only_actions = frozenset(_actions(read_only_actions, "read-only actions"))
        self.profile_root = Path(profile_root).expanduser().resolve()
        self.profile_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS browser_profiles (
                profile_id TEXT PRIMARY KEY,
                site TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                profile_dir TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('login_required','awaiting_human','ready','revoked')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS browser_login_handoffs (
                handoff_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('awaiting_human','completed')),
                proof_sha256 TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES browser_profiles(profile_id)
            );
            CREATE TABLE IF NOT EXISTS browser_action_receipts (
                request_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL,
                site TEXT NOT NULL,
                action TEXT NOT NULL,
                target_sha256 TEXT NOT NULL,
                confirmed INTEGER NOT NULL CHECK(confirmed IN (0,1)),
                created_at TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES browser_profiles(profile_id)
            );
            """
        )
        self.db.commit()

    def __enter__(self) -> "BrowserProfileService":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def create_profile(
        self, profile_id: str, site: str, *, allowed_actions: Iterable[str] | None = None
    ) -> BrowserProfile:
        profile_id = _identifier(profile_id, "profile id")
        site = _site(site)
        try:
            policy_actions = self._policies[site]
        except KeyError as exc:
            raise BrowserProfileError("site is not allowlisted") from exc
        actions = policy_actions if allowed_actions is None else _actions(allowed_actions)
        if not set(actions) <= set(policy_actions):
            raise BrowserProfileError("profile action exceeds site policy")
        profile_dir = (self.profile_root / profile_id).resolve()
        if profile_dir.parent != self.profile_root:
            raise BrowserProfileError("profile path escapes profile root")
        existing = self.db.execute(
            "SELECT * FROM browser_profiles WHERE profile_id=?", (profile_id,)
        ).fetchone()
        if existing is not None:
            if existing["site"] != site or tuple(json.loads(existing["actions_json"])) != actions:
                raise BrowserProfileError("profile registration conflict")
            return self._profile(existing)
        profile_dir.mkdir(mode=0o700)
        now = _now(self._clock)
        with self.db:
            self.db.execute(
                "INSERT INTO browser_profiles(profile_id,site,actions_json,profile_dir,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (profile_id, site, _json(list(actions), "profile actions"), str(profile_dir), "login_required", now, now),
            )
        return self.get_profile(profile_id)

    def begin_login(self, profile_id: str, handoff_id: str) -> LoginHandoff:
        profile_id = _identifier(profile_id, "profile id")
        handoff_id = _identifier(handoff_id, "handoff id")
        profile = self.get_profile(profile_id)
        if profile.status == "revoked":
            raise BrowserProfileError("profile is revoked")
        existing = self.db.execute(
            "SELECT * FROM browser_login_handoffs WHERE handoff_id=?", (handoff_id,)
        ).fetchone()
        if existing is not None:
            if existing["profile_id"] != profile_id:
                raise BrowserProfileError("handoff registration conflict")
            return self._handoff(existing, profile.site)
        now = _now(self._clock)
        with self.db:
            self.db.execute(
                "INSERT INTO browser_login_handoffs(handoff_id,profile_id,status,proof_sha256,created_at,updated_at) "
                "VALUES(?,?, 'awaiting_human', NULL, ?, ?)",
                (handoff_id, profile_id, now, now),
            )
            self.db.execute(
                "UPDATE browser_profiles SET status='awaiting_human', updated_at=? WHERE profile_id=?",
                (now, profile_id),
            )
        return self._handoff(self.db.execute(
            "SELECT * FROM browser_login_handoffs WHERE handoff_id=?", (handoff_id,)
        ).fetchone(), profile.site)

    def complete_login(self, profile_id: str, handoff_id: str, *, proof_ref: str) -> LoginHandoff:
        profile_id = _identifier(profile_id, "profile id")
        handoff_id = _identifier(handoff_id, "handoff id")
        if not isinstance(proof_ref, str) or len(proof_ref.encode("utf-8")) > MAX_REF_BYTES or not _OPAQUE_REF.fullmatch(proof_ref):
            raise BrowserProfileError("login reference is invalid")
        row = self.db.execute(
            "SELECT * FROM browser_login_handoffs WHERE handoff_id=?", (handoff_id,)
        ).fetchone()
        if row is None or row["profile_id"] != profile_id:
            raise BrowserProfileError("unknown login handoff")
        profile = self.get_profile(profile_id)
        if profile.status == "revoked":
            raise BrowserProfileError("profile is revoked")
        proof_sha256 = _digest(proof_ref)
        if row["status"] == "completed" and row["proof_sha256"] != proof_sha256:
            raise BrowserProfileError("login handoff completion conflict")
        now = _now(self._clock)
        with self.db:
            self.db.execute(
                "UPDATE browser_login_handoffs SET status='completed', proof_sha256=?, updated_at=? WHERE handoff_id=?",
                (proof_sha256, now, handoff_id),
            )
            self.db.execute(
                "UPDATE browser_profiles SET status='ready', updated_at=? WHERE profile_id=?",
                (now, profile_id),
            )
        return self._handoff(self.db.execute(
            "SELECT * FROM browser_login_handoffs WHERE handoff_id=?", (handoff_id,)
        ).fetchone(), profile.site)

    def revoke_profile(self, profile_id: str) -> BrowserProfile:
        profile_id = _identifier(profile_id, "profile id")
        self.get_profile(profile_id)
        now = _now(self._clock)
        with self.db:
            self.db.execute(
                "UPDATE browser_profiles SET status='revoked', updated_at=? WHERE profile_id=?",
                (now, profile_id),
            )
        return self.get_profile(profile_id)

    def authorize_action(
        self,
        profile_id: str,
        request_id: str,
        *,
        action: str,
        target_ref: str,
        confirmed: bool = False,
    ) -> BrowserActionReceipt:
        profile_id = _identifier(profile_id, "profile id")
        request_id = _identifier(request_id, "request id")
        if not isinstance(action, str) or not _ACTION.fullmatch(action):
            raise BrowserProfileError("invalid action")
        if not isinstance(target_ref, str) or not _TARGET_REF.fullmatch(target_ref):
            raise BrowserProfileError("target must be an opaque bounded reference")
        profile = self.get_profile(profile_id)
        if profile.status != "ready":
            raise BrowserProfileError("profile login is not ready")
        if action not in profile.allowed_actions:
            raise BrowserProfileError("action is not allowlisted")
        if action not in self._read_only_actions and confirmed is not True:
            raise BrowserProfileError("confirmation is required")
        target_sha256 = _digest(target_ref)
        existing = self.db.execute(
            "SELECT * FROM browser_action_receipts WHERE request_id=?", (request_id,)
        ).fetchone()
        if existing is not None:
            if any(existing[key] != value for key, value in {
                "profile_id": profile_id,
                "site": profile.site,
                "action": action,
                "target_sha256": target_sha256,
                "confirmed": int(confirmed),
            }.items()):
                raise BrowserProfileError("action request conflict")
            return self._receipt(existing)
        now = _now(self._clock)
        with self.db:
            self.db.execute(
                "INSERT INTO browser_action_receipts(request_id,profile_id,site,action,target_sha256,confirmed,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (request_id, profile_id, profile.site, action, target_sha256, int(confirmed), now),
            )
        return self._receipt(self.db.execute(
            "SELECT * FROM browser_action_receipts WHERE request_id=?", (request_id,)
        ).fetchone())

    def get_profile(self, profile_id: str) -> BrowserProfile:
        profile_id = _identifier(profile_id, "profile id")
        row = self.db.execute(
            "SELECT * FROM browser_profiles WHERE profile_id=?", (profile_id,)
        ).fetchone()
        if row is None:
            raise BrowserProfileError("unknown browser profile")
        return self._profile(row)

    def adapter_context(self, profile_id: str) -> dict[str, object]:
        """Return profile path only for a trusted browser adapter, never a model."""
        profile = self.get_profile(profile_id)
        if profile.status != "ready":
            raise BrowserProfileError("profile login is not ready")
        return {
            "profile_id": profile.profile_id,
            "site": profile.site,
            "profile_dir": profile.profile_path,
            "allowed_actions": list(profile.allowed_actions),
        }

    @staticmethod
    def _normalize_policies(site_actions: Mapping[str, Iterable[str]]) -> dict[str, tuple[str, ...]]:
        if not isinstance(site_actions, Mapping) or not site_actions:
            raise BrowserProfileError("site policy is required")
        normalized: dict[str, tuple[str, ...]] = {}
        for site, actions in site_actions.items():
            normalized[_site(site)] = _actions(actions, "site actions")
        return normalized

    def _profile(self, row: sqlite3.Row) -> BrowserProfile:
        status = row["status"]
        if status not in PROFILE_STATUSES:
            raise BrowserProfileError("stored profile status is invalid")
        profile_path = Path(row["profile_dir"]).resolve()
        if profile_path.parent != self.profile_root:
            raise BrowserProfileError("stored profile path escapes profile root")
        return BrowserProfile(
            profile_id=row["profile_id"], site=row["site"],
            allowed_actions=tuple(json.loads(row["actions_json"])), status=status,
            profile_path=str(profile_path), updated_at=row["updated_at"],
        )

    @staticmethod
    def _handoff(row: sqlite3.Row, site: str) -> LoginHandoff:
        if row["status"] not in HANDOFF_STATUSES:
            raise BrowserProfileError("stored handoff status is invalid")
        return LoginHandoff(row["handoff_id"], row["profile_id"], site, row["status"], row["updated_at"])

    @staticmethod
    def _receipt(row: sqlite3.Row) -> BrowserActionReceipt:
        return BrowserActionReceipt(
            request_id=row["request_id"], profile_id=row["profile_id"], site=row["site"],
            action=row["action"], target_sha256=row["target_sha256"],
            confirmed=bool(row["confirmed"]), created_at=row["created_at"],
        )

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


__all__ = [
    "BrowserActionReceipt",
    "BrowserAdapter",
    "BrowserProfile",
    "BrowserProfileError",
    "BrowserProfileService",
    "BrowserToolError",
    "BrowserToolResult",
    "BrowserToolService",
    "LoginHandoff",
    "MAX_ACTIONS",
]
