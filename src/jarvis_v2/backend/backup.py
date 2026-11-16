"""Bounded SQLite backup and restore with WAL and integrity fencing.

The backup path is deliberately provider-neutral.  Plain backups are protected
by exclusive creation and owner-only permissions.  Encrypted artifacts require
an explicit caller-supplied cipher with ``seal`` and ``unseal`` methods; this
module never invents cryptography or silently downgrades to plaintext.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, asdict
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from typing import Any, Protocol
from urllib.parse import quote


MAX_BACKUP_BYTES = 512 * 1024 * 1024
_SQLITE_SUFFIXES = ("-wal", "-shm")


class BackupError(RuntimeError):
    """Raised when a backup or restore cannot be completed safely."""


class BackupCipher(Protocol):
    """Explicit encryption boundary supplied by an approved crypto provider."""

    def seal(self, payload: bytes) -> bytes:
        ...

    def unseal(self, payload: bytes) -> bytes:
        ...


@dataclass(frozen=True)
class BackupReceipt:
    """Digest-only evidence for one verified backup."""

    source_path: str
    destination_path: str
    source_sha256: str
    backup_sha256: str
    source_state_sha256: str
    size_bytes: int
    schema_version: int
    journal_mode: str
    wal_present: bool
    wal_bytes: int
    integrity: str
    encrypted: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RestoreReceipt:
    """Digest-only evidence for one verified restore."""

    backup_path: str
    destination_path: str
    backup_sha256: str
    restored_sha256: str
    size_bytes: int
    schema_version: int
    journal_mode: str
    integrity: str
    encrypted: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _path(value: str | Path, label: str) -> Path:
    if not isinstance(value, (str, Path)):
        raise BackupError(f"{label} must be a path")
    return Path(value)


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bounded_bytes(path: Path, limit: int) -> bytes:
    size = path.stat().st_size
    if size > limit:
        raise BackupError("backup exceeds bounded size")
    return path.read_bytes()


def _sqlite_uri(path: Path) -> str:
    return "file:" + quote(str(path.resolve()), safe="/:\\") + "?mode=ro"


def _sidecar(path: Path, suffix: str) -> Path:
    return Path(f"{path}{suffix}")


def _validate_cipher(cipher: BackupCipher | None) -> None:
    if cipher is None:
        return
    if not callable(getattr(cipher, "seal", None)) or not callable(getattr(cipher, "unseal", None)):
        raise BackupError("cipher must provide seal and unseal")


def _seal(cipher: BackupCipher, payload: bytes) -> bytes:
    try:
        sealed = cipher.seal(payload)
    except Exception as exc:  # provider boundary: do not leak implementation details
        raise BackupError("backup encryption failed") from exc
    if not isinstance(sealed, bytes) or not sealed:
        raise BackupError("cipher returned invalid sealed data")
    return sealed


def _unseal(cipher: BackupCipher, payload: bytes) -> bytes:
    try:
        opened = cipher.unseal(payload)
    except Exception as exc:  # provider boundary: do not leak implementation details
        raise BackupError("backup decryption failed") from exc
    if not isinstance(opened, bytes) or not opened:
        raise BackupError("cipher returned invalid opened data")
    return opened


def _exclusive_write(path: Path, payload: bytes) -> None:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise BackupError("destination already exists") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    os.chmod(path, 0o600)


class BackupManager:
    """Create and restore bounded SQLite artifacts without overwriting files."""

    def __init__(self, *, max_backup_bytes: int = MAX_BACKUP_BYTES) -> None:
        if type(max_backup_bytes) is not int or not 1 <= max_backup_bytes <= MAX_BACKUP_BYTES:
            raise BackupError("invalid backup size limit")
        self.max_backup_bytes = max_backup_bytes

    def inspect(self, database: str | Path) -> dict[str, Any]:
        """Check integrity, schema version and WAL sidecars without writing."""
        path = _path(database, "database")
        if not path.is_file():
            raise BackupError("database does not exist")
        if path.stat().st_size > self.max_backup_bytes:
            raise BackupError("database exceeds bounded size")
        wal = _sidecar(path, "-wal")
        shm = _sidecar(path, "-shm")
        try:
            with sqlite3.connect(_sqlite_uri(path), uri=True) as db:
                db.execute("PRAGMA query_only=ON")
                journal_mode = str(db.execute("PRAGMA journal_mode").fetchone()[0]).lower()
                integrity = str(db.execute("PRAGMA integrity_check").fetchone()[0])
                if integrity != "ok":
                    raise BackupError("database integrity check failed")
                if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                    raise BackupError("database foreign-key check failed")
                schema_version = int(db.execute("PRAGMA user_version").fetchone()[0])
        except sqlite3.Error as exc:
            raise BackupError("database inspection failed") from exc

        wal_file = wal.is_file()
        shm_file = shm.is_file()
        wal_present = wal_file and wal.stat().st_size > 0
        shm_present = shm_file and shm.stat().st_size > 0
        if journal_mode == "wal":
            # SQLite may remove/recreate the transient -shm index while a
            # valid -wal snapshot remains.  A shared-memory file without its
            # WAL, however, cannot describe a recoverable WAL state.
            if shm_file and not wal_file:
                raise BackupError("WAL sidecars are inconsistent")
        elif wal_present or shm_present:
            raise BackupError("journal sidecar does not match journal mode")
        state = {
            "path": str(path),
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
            "schema_version": schema_version,
            "journal_mode": journal_mode,
            "wal_present": wal_present,
            "wal_bytes": wal.stat().st_size if wal_present else 0,
            "shm_bytes": shm.stat().st_size if shm_present else 0,
            "integrity": integrity,
        }
        state["state_sha256"] = hashlib.sha256(
            json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return state

    def _copy_sqlite(self, source: Path, destination: Path) -> None:
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
            with sqlite3.connect(_sqlite_uri(source), uri=True) as source_db:
                with sqlite3.connect(destination) as destination_db:
                    source_db.backup(destination_db)
                    destination_db.commit()
        except FileExistsError as exc:
            raise BackupError("destination already exists") from exc
        except sqlite3.Error as exc:
            destination.unlink(missing_ok=True)
            raise BackupError("SQLite backup failed") from exc
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        os.chmod(destination, 0o600)

    def create(
        self,
        source: str | Path,
        destination: str | Path,
        *,
        cipher: BackupCipher | None = None,
    ) -> BackupReceipt:
        """Create a verified backup; the destination is never overwritten."""
        source_path = _path(source, "source")
        destination_path = _path(destination, "destination")
        if _same_path(source_path, destination_path):
            raise BackupError("source and destination must differ")
        if not source_path.is_file():
            raise BackupError("source database does not exist")
        _validate_cipher(cipher)
        before = self.inspect(source_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path = Path(tempfile.mkstemp(prefix=".archon-backup-", dir=destination_path.parent)[1])
        raw_path.unlink()
        try:
            self._copy_sqlite(source_path, raw_path)
            raw = self.inspect(raw_path)
            if raw["schema_version"] != before["schema_version"]:
                raise BackupError("schema changed during backup")
            after = self.inspect(source_path)
            if before["state_sha256"] != after["state_sha256"]:
                raise BackupError("source changed during backup")
            raw_bytes = _bounded_bytes(raw_path, self.max_backup_bytes)
            if cipher is None:
                try:
                    os.link(raw_path, destination_path)
                except FileExistsError as exc:
                    raise BackupError("destination already exists") from exc
                os.chmod(destination_path, 0o600)
            else:
                _exclusive_write(destination_path, _seal(cipher, raw_bytes))
            receipt = BackupReceipt(
                source_path=str(source_path),
                destination_path=str(destination_path),
                source_sha256=before["sha256"],
                backup_sha256=_sha256(destination_path),
                source_state_sha256=before["state_sha256"],
                size_bytes=destination_path.stat().st_size,
                schema_version=raw["schema_version"],
                journal_mode=before["journal_mode"],
                wal_present=before["wal_present"],
                wal_bytes=before["wal_bytes"],
                integrity=raw["integrity"],
                encrypted=cipher is not None,
            )
            return receipt
        finally:
            raw_path.unlink(missing_ok=True)

    def restore(
        self,
        backup: str | Path,
        destination: str | Path,
        *,
        cipher: BackupCipher | None = None,
        expected_sha256: str | None = None,
        expected_schema_version: int | None = None,
    ) -> RestoreReceipt:
        """Restore a backup into a new path and verify its schema and integrity."""
        backup_path = _path(backup, "backup")
        destination_path = _path(destination, "destination")
        if _same_path(backup_path, destination_path):
            raise BackupError("backup and destination must differ")
        if not backup_path.is_file():
            raise BackupError("backup does not exist")
        _validate_cipher(cipher)
        backup_sha256 = _sha256(backup_path)
        if expected_sha256 is not None and backup_sha256 != expected_sha256:
            raise BackupError("backup digest does not match expected value")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path: Path | None = None
        try:
            if cipher is None:
                raw_path = backup_path
                encrypted = False
            else:
                raw_path = Path(tempfile.mkstemp(prefix=".archon-restore-", dir=destination_path.parent)[1])
                os.chmod(raw_path, 0o600)
                raw_path.write_bytes(_unseal(cipher, _bounded_bytes(backup_path, self.max_backup_bytes)))
                if raw_path.stat().st_size > self.max_backup_bytes:
                    raise BackupError("opened backup exceeds bounded size")
                encrypted = True
            inspection = self.inspect(raw_path)
            if expected_schema_version is not None and inspection["schema_version"] != expected_schema_version:
                raise BackupError("restored schema version does not match expected value")
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_destination = Path(
                tempfile.mkstemp(prefix=".archon-restored-", dir=destination_path.parent)[1]
            )
            temporary_destination.unlink()
            try:
                self._copy_sqlite(raw_path, temporary_destination)
                restored = self.inspect(temporary_destination)
                os.link(temporary_destination, destination_path)
                os.chmod(destination_path, 0o600)
            except FileExistsError as exc:
                raise BackupError("destination already exists") from exc
            finally:
                temporary_destination.unlink(missing_ok=True)
            return RestoreReceipt(
                backup_path=str(backup_path),
                destination_path=str(destination_path),
                backup_sha256=backup_sha256,
                restored_sha256=_sha256(destination_path),
                size_bytes=destination_path.stat().st_size,
                schema_version=restored["schema_version"],
                journal_mode=restored["journal_mode"],
                integrity=restored["integrity"],
                encrypted=encrypted,
            )
        finally:
            if raw_path is not None and raw_path != backup_path:
                raw_path.unlink(missing_ok=True)


SQLiteBackup = BackupManager
SafeBackupManager = BackupManager


__all__ = [
    "BackupCipher",
    "BackupError",
    "BackupManager",
    "BackupReceipt",
    "MAX_BACKUP_BYTES",
    "RestoreReceipt",
    "SQLiteBackup",
    "SafeBackupManager",
]
