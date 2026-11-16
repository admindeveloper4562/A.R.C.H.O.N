"""Atomic, module-owned SQLite migrations for the Backend boundary.

The manager is deliberately local and transport-neutral.  Domain modules
provide migrations for their own tables; Backend records the applied digest
and fences writes so a module cannot write another module's table.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from .module_manifest import ACTIVE_MODULE_KEYS


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
_NAME = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
_RESERVED_TABLES = frozenset({"backend_schema_migrations", "backend_table_owners"})


class StorageError(RuntimeError):
    """Base error for bounded Backend storage operations."""


class MigrationError(StorageError):
    """Raised when a migration cannot be applied or rolled back safely."""


class OwnershipError(StorageError):
    """Raised when a module accesses a table it does not own."""


@dataclass(frozen=True)
class Migration:
    """One deterministic, reversible migration owned by one module."""

    module: str
    version: int
    name: str
    tables: tuple[str, ...]
    up_sql: tuple[str, ...]
    down_sql: tuple[str, ...]

    def digest(self) -> str:
        """Return the definition digest persisted with the applied migration."""
        payload = {
            "module": self.module,
            "version": self.version,
            "name": self.name,
            "tables": self.tables,
            "up_sql": self.up_sql,
            "down_sql": self.down_sql,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


DEFAULT_MIGRATIONS = (
    Migration(
        module="backend",
        version=1,
        name="backend-records",
        tables=("backend_records",),
        up_sql=(
            "CREATE TABLE backend_records ("
            "record_id TEXT PRIMARY KEY, "
            "kind TEXT NOT NULL, "
            "payload_json TEXT NOT NULL, "
            "created_at TEXT NOT NULL, "
            "updated_at TEXT NOT NULL"
            ")",
        ),
        down_sql=("DROP TABLE backend_records",),
    ),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise StorageError(f"invalid {label}")
    return value


def _quote_identifier(value: str, label: str) -> str:
    return '"' + _identifier(value, label).replace('"', '""') + '"'


class ModuleStore:
    """Write/read view restricted to one module's registered tables."""

    def __init__(self, manager: "StorageManager", module: str) -> None:
        if module not in ACTIVE_MODULE_KEYS:
            raise OwnershipError("unknown module owner")
        self._manager = manager
        self.module = module

    def insert(self, table: str, values: Mapping[str, Any]) -> None:
        self._manager.insert(self.module, table, values)

    def rows(self, table: str) -> list[dict[str, Any]]:
        return self._manager.rows(self.module, table)


class StorageManager:
    """Apply reversible migrations and enforce table ownership in SQLite."""

    def __init__(
        self,
        path: str | Path,
        *,
        migrations: Sequence[Migration] = DEFAULT_MIGRATIONS,
    ) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self._migrations = tuple(migrations)
        self._validate_plan()

    def __enter__(self) -> "StorageManager":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        self.db.close()

    def module(self, module: str) -> ModuleStore:
        return ModuleStore(self, module)

    def _validate_plan(self) -> None:
        versions: dict[str, set[int]] = {}
        table_owners: dict[str, str] = {}
        for migration in self._migrations:
            if not isinstance(migration, Migration):
                raise MigrationError("migration plan contains a non-migration")
            if migration.module not in ACTIVE_MODULE_KEYS:
                raise MigrationError("migration has an unknown module")
            if type(migration.version) is not int or migration.version < 1:
                raise MigrationError("migration version must be positive")
            if not _NAME.fullmatch(migration.name):
                raise MigrationError("migration name is invalid")
            if not migration.up_sql or not migration.down_sql:
                raise MigrationError("migration must define up and down SQL")
            if not isinstance(migration.tables, tuple) or len(set(migration.tables)) != len(migration.tables):
                raise MigrationError("migration tables must be unique")
            for table in migration.tables:
                _identifier(table, "migration table")
                if table in _RESERVED_TABLES:
                    raise MigrationError("migration cannot own Backend metadata")
                prior = table_owners.setdefault(table, migration.module)
                if prior != migration.module:
                    raise MigrationError("table has multiple module owners")
            for statement in (*migration.up_sql, *migration.down_sql):
                if not isinstance(statement, str) or not statement.strip() or "\x00" in statement:
                    raise MigrationError("migration SQL is invalid")
                if len(statement.encode("utf-8")) > 64_000:
                    raise MigrationError("migration SQL is too large")
            versions.setdefault(migration.module, set()).add(migration.version)
        for module, values in versions.items():
            expected = set(range(1, max(values) + 1))
            if values != expected:
                raise MigrationError(f"migration versions for {module} are not contiguous")
        if len({(item.module, item.version) for item in self._migrations}) != len(self._migrations):
            raise MigrationError("duplicate module migration version")

    def _bootstrap(self) -> None:
        try:
            self.db.executescript(
                """
                CREATE TABLE IF NOT EXISTS backend_schema_migrations (
                    module TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    digest TEXT NOT NULL,
                    applied_at TEXT NOT NULL,
                    PRIMARY KEY (module, version)
                );
                CREATE TABLE IF NOT EXISTS backend_table_owners (
                    table_name TEXT PRIMARY KEY,
                    module TEXT NOT NULL,
                    migration_version INTEGER NOT NULL,
                    FOREIGN KEY (module, migration_version)
                      REFERENCES backend_schema_migrations(module, version)
                );
                """
            )
            self.db.commit()
            required = {
                row[1] for row in self.db.execute("PRAGMA table_info(backend_schema_migrations)")
            }
            if not {"module", "version", "name", "digest", "applied_at"} <= required:
                raise MigrationError("migration ledger schema is incompatible")
        except (sqlite3.Error, MigrationError) as exc:
            self.db.rollback()
            if isinstance(exc, MigrationError):
                raise
            raise MigrationError("migration ledger is unavailable") from exc

    def _applied(self) -> dict[tuple[str, int], sqlite3.Row]:
        try:
            return {
                (row["module"], row["version"]): row
                for row in self.db.execute(
                    "SELECT module,version,name,digest,applied_at "
                    "FROM backend_schema_migrations ORDER BY module,version"
                )
            }
        except sqlite3.Error as exc:
            raise MigrationError("migration ledger cannot be read") from exc

    def _plan_by_key(self) -> dict[tuple[str, int], Migration]:
        return {(item.module, item.version): item for item in self._migrations}

    def _validate_applied(self, applied: Mapping[tuple[str, int], sqlite3.Row]) -> None:
        plan = self._plan_by_key()
        for key, row in applied.items():
            migration = plan.get(key)
            if migration is None:
                raise MigrationError("database contains an unknown migration")
            if row["name"] != migration.name or row["digest"] != migration.digest():
                raise MigrationError("applied migration definition changed")
        for module in {key[0] for key in applied}:
            versions = {version for owner, version in applied if owner == module}
            if versions != set(range(1, max(versions) + 1)):
                raise MigrationError("applied migration versions are not contiguous")

    def _integrity_check(self) -> None:
        result = self.db.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok" or self.db.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise MigrationError("database integrity check failed")

    def _table_exists(self, table: str) -> bool:
        return self.db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone() is not None

    def _apply_one(self, migration: Migration) -> None:
        try:
            self.db.execute("BEGIN IMMEDIATE")
            for statement in migration.up_sql:
                self.db.execute(statement)
            self.db.execute(
                "INSERT INTO backend_schema_migrations(module,version,name,digest,applied_at) "
                "VALUES (?,?,?,?,?)",
                (migration.module, migration.version, migration.name, migration.digest(), _utc_now()),
            )
            for table in migration.tables:
                existing = self.db.execute(
                    "SELECT module FROM backend_table_owners WHERE table_name=?", (table,)
                ).fetchone()
                if existing is not None and existing[0] != migration.module:
                    raise MigrationError("table ownership conflict")
                self.db.execute(
                    "INSERT INTO backend_table_owners(table_name,module,migration_version) VALUES(?,?,?) "
                    "ON CONFLICT(table_name) DO UPDATE SET module=excluded.module, migration_version=excluded.migration_version",
                    (table, migration.module, migration.version),
                )
                if not self._table_exists(table):
                    raise MigrationError("migration did not create its owned table")
            self._integrity_check()
            self.db.commit()
        except (sqlite3.Error, MigrationError) as exc:
            self.db.rollback()
            if isinstance(exc, MigrationError):
                raise
            raise MigrationError(f"migration apply failed: {migration.module}:{migration.version}") from exc

    def migrate(self) -> list[dict[str, Any]]:
        """Apply pending migrations atomically, or leave the DB unchanged."""
        self._bootstrap()
        applied = self._applied()
        self._validate_applied(applied)
        for migration in sorted(self._migrations, key=lambda item: (item.module, item.version)):
            key = (migration.module, migration.version)
            if key in applied:
                continue
            current = max(
                (version for module, version in applied if module == migration.module),
                default=0,
            )
            if migration.version != current + 1:
                raise MigrationError("migration dependency is not applied")
            self._apply_one(migration)
            applied = self._applied()
        return self.applied_migrations()

    def rollback(self, module: str, *, target_version: int = 0) -> list[dict[str, Any]]:
        """Roll one module back to a prior version, preserving failed state."""
        if module not in ACTIVE_MODULE_KEYS:
            raise MigrationError("unknown rollback module")
        if type(target_version) is not int or target_version < 0:
            raise MigrationError("invalid rollback target")
        self._bootstrap()
        applied = self._applied()
        self._validate_applied(applied)
        versions = sorted(version for owner, version in applied if owner == module)
        if target_version > (versions[-1] if versions else 0):
            raise MigrationError("rollback target is ahead of database")
        plan = self._plan_by_key()
        for version in reversed([item for item in versions if item > target_version]):
            migration = plan[(module, version)]
            try:
                self.db.execute("BEGIN IMMEDIATE")
                for statement in migration.down_sql:
                    self.db.execute(statement)
                remaining_tables = {
                    table
                    for (owner, prior_version), prior in plan.items()
                    if owner == module and prior_version < version and prior_version <= target_version
                    for table in prior.tables
                }
                for table in migration.tables:
                    if table in remaining_tables:
                        if not self._table_exists(table):
                            raise MigrationError("rollback removed a required table")
                        continue
                    if self._table_exists(table):
                        raise MigrationError("rollback left an owned table")
                    self.db.execute("DELETE FROM backend_table_owners WHERE table_name=?", (table,))
                self.db.execute(
                    "DELETE FROM backend_schema_migrations WHERE module=? AND version=?",
                    (module, version),
                )
                self._integrity_check()
                self.db.commit()
            except (sqlite3.Error, MigrationError) as exc:
                self.db.rollback()
                if isinstance(exc, MigrationError):
                    raise
                raise MigrationError(f"migration rollback failed: {module}:{version}") from exc
        return self.applied_migrations()

    def applied_migrations(self) -> list[dict[str, Any]]:
        self._bootstrap()
        return [dict(row) for row in self.db.execute(
            "SELECT module,version,name,digest,applied_at "
            "FROM backend_schema_migrations ORDER BY module,version"
        )]

    def table_owner(self, table: str) -> str | None:
        table = _identifier(table, "table")
        self._bootstrap()
        row = self.db.execute(
            "SELECT module FROM backend_table_owners WHERE table_name=?", (table,)
        ).fetchone()
        return row[0] if row else None

    def _assert_owner(self, module: str, table: str) -> str:
        if module not in ACTIVE_MODULE_KEYS:
            raise OwnershipError("unknown module owner")
        table = _identifier(table, "table")
        owner = self.table_owner(table)
        if owner != module:
            raise OwnershipError("module does not own table")
        if not self._table_exists(table):
            raise StorageError("owned table is unavailable")
        return table

    def insert(self, module: str, table: str, values: Mapping[str, Any]) -> None:
        """Insert one row using parameter binding and the module ownership fence."""
        table = self._assert_owner(module, table)
        if not isinstance(values, Mapping) or not values:
            raise StorageError("insert values are required")
        columns = tuple(values)
        if any(not isinstance(column, str) or not _IDENTIFIER.fullmatch(column) for column in columns):
            raise StorageError("insert column is invalid")
        quoted_table = _quote_identifier(table, "table")
        quoted_columns = ",".join(_quote_identifier(column, "column") for column in columns)
        placeholders = ",".join("?" for _ in columns)
        try:
            with self.db:
                self.db.execute(
                    f"INSERT INTO {quoted_table} ({quoted_columns}) VALUES ({placeholders})",
                    tuple(values[column] for column in columns),
                )
        except sqlite3.Error as exc:
            raise StorageError("module insert failed") from exc

    def rows(self, module: str, table: str) -> list[dict[str, Any]]:
        table = self._assert_owner(module, table)
        try:
            return [dict(row) for row in self.db.execute(f"SELECT * FROM {_quote_identifier(table, 'table')}")]
        except sqlite3.Error as exc:
            raise StorageError("module read failed") from exc


__all__ = [
    "DEFAULT_MIGRATIONS",
    "Migration",
    "MigrationError",
    "ModuleStore",
    "OwnershipError",
    "StorageError",
    "StorageManager",
]
