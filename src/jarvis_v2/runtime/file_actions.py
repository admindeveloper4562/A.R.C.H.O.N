"""Per-file, recoverable file actions with explicit approval and local audit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import hashlib
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import sys
import time
from typing import Callable


MAX_REASON_BYTES = 512
MAX_AUDIT_ROWS = 1000
REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
PROTECTED_NAMES = frozenset({
    ".ssh", ".gnupg", ".password-store", ".mozilla", "google-chrome",
    "chromium", "keyrings", "browser-profiles", ".aws", ".config",
})
VIRTUAL_ROOTS = (Path("/proc"), Path("/sys"), Path("/dev"), Path("/run"), Path("/snap"))
DELETE_LOG_HEADER = (
    "# ARCHON local DELETE-LOGS.md\n\n"
    "Private local audit; do not commit or upload this file.\n\n"
    "| UTC | Approval ID | Action | Event | Original file | Destination |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)


class FileActionError(ValueError):
    """Raised when a per-file operation cannot be admitted safely."""


@dataclass(frozen=True)
class FileIdentity:
    path: str
    device: int
    inode: int
    size: int
    mtime_ns: int

    def digest(self) -> str:
        value = f"{self.path}\0{self.device}\0{self.inode}\0{self.size}\0{self.mtime_ns}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FileActionRequest:
    request_id: str
    action: str
    target_digest: str
    state: str
    expires_at: float
    path: str
    restore_target: str | None = None

    def model_context(self) -> dict[str, object]:
        """Return receipt metadata without local paths or human reasons."""
        return {
            "request_id": self.request_id,
            "action": self.action,
            "target_digest": self.target_digest,
            "state": self.state,
            "expires_at": self.expires_at,
        }


class FileActionService:
    """Provide only individually approved, recoverable file moves."""

    def __init__(
        self,
        database: str | Path,
        *,
        allowed_roots: tuple[Path, ...] | list[Path],
        trash_root: str | Path,
        audit_log: str | Path,
        ttl_seconds: int = 300,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 3600:
            raise FileActionError("approval TTL is outside the bounded range")
        if not allowed_roots:
            raise FileActionError("at least one owner-selected root is required")
        self._clock = clock
        self.ttl_seconds = ttl_seconds
        self.allowed_roots = self._normalize_roots(allowed_roots)
        self.trash_root = Path(trash_root).expanduser().resolve()
        if self._is_protected(self.trash_root):
            raise FileActionError("Trash root is protected")
        self.audit_log = Path(audit_log).expanduser().resolve()
        if self.audit_log.name != "DELETE-LOGS.md":
            raise FileActionError("audit log must be DELETE-LOGS.md")
        self._owns_connection = True
        self.db: sqlite3.Connection = sqlite3.connect(str(database))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS file_action_requests (
                request_id TEXT PRIMARY KEY,
                action TEXT NOT NULL CHECK(action IN ('trash_file','restore_file')),
                reason TEXT NOT NULL,
                path TEXT NOT NULL,
                target_digest TEXT NOT NULL,
                device INTEGER NOT NULL,
                inode INTEGER NOT NULL,
                size INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                expires_at REAL NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('pending','approved','denied','consumed')),
                restore_target TEXT,
                created REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS file_action_audit (
                id INTEGER PRIMARY KEY,
                request_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target_digest TEXT NOT NULL,
                decision TEXT NOT NULL,
                result TEXT NOT NULL,
                created REAL NOT NULL,
                FOREIGN KEY(request_id) REFERENCES file_action_requests(request_id)
            );
            CREATE TABLE IF NOT EXISTS file_trash_manifests (
                request_id TEXT PRIMARY KEY,
                trash_path TEXT NOT NULL UNIQUE,
                original_path TEXT NOT NULL,
                checksum TEXT NOT NULL,
                device INTEGER NOT NULL,
                inode INTEGER NOT NULL,
                size INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                created REAL NOT NULL,
                restored REAL,
                FOREIGN KEY(request_id) REFERENCES file_action_requests(request_id)
            );
            CREATE INDEX IF NOT EXISTS file_action_audit_created
                ON file_action_audit(created);
            """
        )
        self.db.commit()

    def __enter__(self) -> "FileActionService":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def preview(self, target: Path) -> dict[str, object]:
        """Inspect one allowed regular file without changing it."""
        identity = self._capture_allowed_file(target)
        return {
            "path": identity.path,
            "size": identity.size,
            "mtime_ns": identity.mtime_ns,
            "device": identity.device,
            "inode": identity.inode,
            "action": "trash_file",
            "mutation": "requires_individual_owner_approval",
        }

    def propose_trash(self, target: Path, reason: str) -> FileActionRequest:
        identity = self._capture_allowed_file(target)
        reason = self._reason(reason)
        return self._insert_request("trash_file", identity, reason)

    def propose_directory(self, target: Path, reason: str) -> None:
        """Reject directory-wide approval; each regular file needs its own request."""
        raise FileActionError("directory-wide approval is forbidden")

    def decide(self, request_id: str, approved: bool) -> FileActionRequest:
        request_id = self._request_id(request_id)
        if type(approved) is not bool:
            raise FileActionError("owner decision must be boolean")
        row = self._row(request_id)
        if row["state"] != "pending":
            raise FileActionError("approval is unknown or already decided")
        if self._clock() >= row["expires_at"]:
            with self.db:
                self.db.execute("UPDATE file_action_requests SET state='denied' WHERE request_id=?", (request_id,))
                self._audit_db(row, "expired", "approval_expired")
            raise FileActionError("approval expired")
        state = "approved" if approved else "denied"
        result = "owner_decision" if approved else "owner_denied"
        with self.db:
            self.db.execute("UPDATE file_action_requests SET state=? WHERE request_id=?", (state, request_id))
            self._audit_db(row, state, result)
        return self.get_request(request_id)

    def trash_file(self, request_id: str) -> Path:
        request_id = self._request_id(request_id)
        row = self._authorized(request_id, "trash_file")
        expected = self._identity(row)
        source = Path(expected.path)
        self._assert_identity(source, expected)
        self.trash_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.trash_root.is_symlink() or not self.trash_root.is_dir():
            raise FileActionError("Trash root is unsafe")
        destination = self.trash_root / f"{request_id}-{source.name}"
        if destination.exists() or destination.is_symlink():
            raise FileActionError("Trash destination already exists")
        self._audit_db(row, "authorized_attempt", "identity_revalidated")
        self._append_log(request_id, "trash_file", "authorized_attempt", source, destination)
        parent_fd = source_fd = trash_fd = -1
        moved = False
        try:
            parent_fd = self._open_directory(source.parent)
            source_fd = os.open(source.name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent_fd)
            self._assert_fd_identity(source_fd, expected)
            trash_fd = self._open_directory(self.trash_root)
            self._rename_noreplace(parent_fd, source.name, trash_fd, destination.name)
            moved = True
            moved_stat = os.stat(destination.name, dir_fd=trash_fd, follow_symlinks=False)
            if (moved_stat.st_dev, moved_stat.st_ino, moved_stat.st_size, moved_stat.st_mtime_ns) != (
                expected.device, expected.inode, expected.size, expected.mtime_ns
            ):
                raise FileActionError("Trash identity verification failed")
            checksum = self._checksum_at(trash_fd, destination.name)
            self._append_log(request_id, "trash_file", "moved_to_trash", source, destination)
            with self.db:
                self.db.execute("UPDATE file_action_requests SET state='consumed' WHERE request_id=?", (request_id,))
                self.db.execute(
                    "INSERT INTO file_trash_manifests(request_id,trash_path,original_path,checksum,device,inode,size,mtime_ns,created) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (request_id, str(destination), expected.path, checksum, expected.device, expected.inode, expected.size, expected.mtime_ns, self._clock()),
                )
                self._audit_db(row, "completed", "moved_to_trash")
            return destination
        except (OSError, sqlite3.Error, FileActionError) as exc:
            if moved:
                self._restore_move(destination, source)
            self._audit_db(row, "failed", "trash_operation_failed")
            if isinstance(exc, FileActionError):
                raise
            raise FileActionError("file could not be moved safely") from exc
        finally:
            for fd in (source_fd, parent_fd, trash_fd):
                if fd >= 0:
                    os.close(fd)

    def propose_restore(self, trash_request_id: str, reason: str) -> FileActionRequest:
        trash_request_id = self._request_id(trash_request_id)
        reason = self._reason(reason)
        row = self.db.execute(
            "SELECT * FROM file_trash_manifests WHERE request_id=? AND restored IS NULL", (trash_request_id,)
        ).fetchone()
        if row is None:
            raise FileActionError("Trash entry is unavailable")
        trash = Path(row["trash_path"])
        if not self._inside(trash, (self.trash_root,)) or trash.is_symlink() or not trash.is_file():
            raise FileActionError("Trash entry is unsafe")
        target = Path(row["original_path"])
        self._validate_restore_target(target)
        stat_result = trash.stat()
        identity = FileIdentity(str(trash), stat_result.st_dev, stat_result.st_ino, stat_result.st_size, stat_result.st_mtime_ns)
        return self._insert_request("restore_file", identity, reason, restore_target=str(target))

    def restore_file(self, request_id: str) -> Path:
        request_id = self._request_id(request_id)
        row = self._authorized(request_id, "restore_file")
        if not row["restore_target"]:
            raise FileActionError("restore target is missing")
        source = Path(row["path"])
        target = Path(row["restore_target"])
        self._validate_restore_target(target)
        manifest = self.db.execute(
            "SELECT * FROM file_trash_manifests WHERE trash_path=? AND restored IS NULL", (str(source),)
        ).fetchone()
        if manifest is None:
            raise FileActionError("Trash manifest is missing")
        expected = self._identity(row)
        if not source.is_file() or source.is_symlink():
            raise FileActionError("Trash source is missing or unsafe")
        self._assert_identity(source, expected)
        if self._checksum_path(source) != manifest["checksum"]:
            raise FileActionError("Trash checksum changed")
        if target.exists() or target.is_symlink():
            raise FileActionError("restore destination already exists")
        self._audit_db(row, "authorized_attempt", "identity_revalidated")
        self._append_log(request_id, "restore_file", "authorized_attempt", source, target)
        source_fd = source_parent_fd = target_parent_fd = -1
        moved = False
        try:
            source_parent_fd = self._open_directory(source.parent)
            source_fd = os.open(source.name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=source_parent_fd)
            self._assert_fd_identity(source_fd, expected)
            target_parent_fd = self._open_directory(target.parent)
            self._rename_noreplace(source_parent_fd, source.name, target_parent_fd, target.name)
            moved = True
            self._append_log(request_id, "restore_file", "restored_from_trash", source, target)
            with self.db:
                self.db.execute("UPDATE file_action_requests SET state='consumed' WHERE request_id=?", (request_id,))
                self.db.execute("UPDATE file_trash_manifests SET restored=? WHERE request_id=?", (self._clock(), manifest["request_id"]))
                self._audit_db(row, "completed", "restored_from_trash")
            return target
        except (OSError, sqlite3.Error, FileActionError) as exc:
            if moved:
                self._restore_move(target, source)
            self._audit_db(row, "failed", "restore_operation_failed")
            if isinstance(exc, FileActionError):
                raise
            raise FileActionError("file could not be restored safely") from exc
        finally:
            for fd in (source_fd, source_parent_fd, target_parent_fd):
                if fd >= 0:
                    os.close(fd)

    def get_request(self, request_id: str) -> FileActionRequest:
        return self._request_from_row(self._row(self._request_id(request_id)))

    def trash_manifest(self, request_id: str) -> dict[str, object] | None:
        request_id = self._request_id(request_id)
        row = self.db.execute("SELECT * FROM file_trash_manifests WHERE request_id=?", (request_id,)).fetchone()
        return dict(row) if row else None

    def audit(self, limit: int = 100) -> list[dict[str, object]]:
        if type(limit) is not int or not 1 <= limit <= MAX_AUDIT_ROWS:
            raise FileActionError("audit limit is outside the bounded range")
        rows = self.db.execute(
            "SELECT request_id,action,target_digest,decision,result,created FROM file_action_audit ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in rows]

    def _insert_request(
        self, action: str, identity: FileIdentity, reason: str, *, restore_target: str | None = None
    ) -> FileActionRequest:
        request_id = secrets.token_urlsafe(24)
        expires_at = self._clock() + self.ttl_seconds
        now = self._clock()
        with self.db:
            self.db.execute(
                "INSERT INTO file_action_requests(request_id,action,reason,path,target_digest,device,inode,size,mtime_ns,expires_at,state,restore_target,created) "
                "VALUES(?,?,?,?,?,?,?,?,?,?, 'pending', ?, ?)",
                (request_id, action, reason, identity.path, identity.digest(), identity.device, identity.inode, identity.size, identity.mtime_ns, expires_at, restore_target, now),
            )
            self._audit_db({"request_id": request_id, "action": action, "target_digest": identity.digest()}, "pending", "awaiting_owner")
        return self.get_request(request_id)

    def _authorized(self, request_id: str, action: str) -> sqlite3.Row:
        row = self._row(request_id)
        if row["action"] != action or row["state"] != "approved":
            raise FileActionError("individual owner approval is required")
        if self._clock() >= row["expires_at"]:
            raise FileActionError("owner approval expired")
        return row

    def _row(self, request_id: str) -> sqlite3.Row:
        row = self.db.execute("SELECT * FROM file_action_requests WHERE request_id=?", (request_id,)).fetchone()
        if row is None:
            raise FileActionError("unknown approval request")
        return row

    @staticmethod
    def _request_from_row(row: sqlite3.Row) -> FileActionRequest:
        return FileActionRequest(
            request_id=row["request_id"], action=row["action"], target_digest=row["target_digest"],
            state=row["state"], expires_at=row["expires_at"], path=row["path"],
            restore_target=row["restore_target"],
        )

    @staticmethod
    def _identity(row: sqlite3.Row) -> FileIdentity:
        return FileIdentity(row["path"], row["device"], row["inode"], row["size"], row["mtime_ns"])

    @staticmethod
    def _request_id(value: object) -> str:
        if not isinstance(value, str) or not REQUEST_ID.fullmatch(value):
            raise FileActionError("approval request id is malformed")
        return value

    @staticmethod
    def _reason(value: object) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > MAX_REASON_BYTES:
            raise FileActionError("a bounded human-readable reason is required")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
            raise FileActionError("approval reason contains control data")
        return value.strip()

    def _capture_allowed_file(self, target: Path) -> FileIdentity:
        if not isinstance(target, Path):
            raise FileActionError("target must be a pathlib.Path")
        raw = target.expanduser()
        if raw.is_symlink():
            raise FileActionError("symlink targets are not allowed")
        try:
            resolved = raw.resolve(strict=True)
        except OSError as exc:
            raise FileActionError("target does not exist") from exc
        if not self._inside(resolved, self.allowed_roots) or self._is_protected(resolved):
            raise FileActionError("target is outside an allowed root")
        info = resolved.stat()
        if not stat.S_ISREG(info.st_mode) or resolved.is_symlink():
            raise FileActionError("only regular files may be individually approved")
        return FileIdentity(str(resolved), info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)

    def _validate_restore_target(self, target: Path) -> None:
        try:
            parent = target.parent.resolve(strict=True)
        except OSError as exc:
            raise FileActionError("restore parent is unavailable") from exc
        if target.is_symlink() or not self._inside(parent, self.allowed_roots):
            raise FileActionError("restore target is outside an allowed root")
        if self._is_protected(target):
            raise FileActionError("restore target is protected")
        if not target.parent.is_dir() or target.parent.is_symlink():
            raise FileActionError("restore parent is unavailable")

    def _assert_identity(self, path: Path, expected: FileIdentity) -> None:
        if path.is_symlink() or path.resolve(strict=True) != path:
            raise FileActionError("file identity changed")
        info = path.stat()
        if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) != (
            expected.device, expected.inode, expected.size, expected.mtime_ns
        ):
            raise FileActionError("file identity changed")

    @staticmethod
    def _assert_fd_identity(fd: int, expected: FileIdentity) -> None:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) != (
            expected.device, expected.inode, expected.size, expected.mtime_ns
        ):
            raise FileActionError("file identity changed")

    @staticmethod
    def _normalize_roots(roots: tuple[Path, ...] | list[Path]) -> tuple[Path, ...]:
        normalized = []
        for root in roots:
            if not isinstance(root, Path) or root.is_symlink():
                raise FileActionError("allowed root must be a real directory")
            try:
                resolved = root.expanduser().resolve(strict=True)
            except OSError as exc:
                raise FileActionError("allowed root is unavailable") from exc
            if not resolved.is_dir() or FileActionService._is_protected(resolved):
                raise FileActionError("allowed root is unsafe")
            normalized.append(resolved)
        return tuple(dict.fromkeys(normalized))

    @staticmethod
    def _inside(path: Path, roots: tuple[Path, ...]) -> bool:
        try:
            return any(path == root or root in path.parents for root in roots)
        except (OSError, ValueError):
            return False

    @staticmethod
    def _is_protected(path: Path) -> bool:
        text = str(path)
        if any(text == str(root) or text.startswith(str(root) + "/") for root in VIRTUAL_ROOTS):
            return True
        return bool(set(path.parts) & PROTECTED_NAMES or path.name == ".env" or path.name.startswith(".env."))

    @staticmethod
    def _open_directory(path: Path) -> int:
        return os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)

    @staticmethod
    def _checksum_at(directory_fd: int, name: str) -> str:
        digest = hashlib.sha256()
        fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
        finally:
            os.close(fd)
        return digest.hexdigest()

    @classmethod
    def _checksum_path(cls, path: Path) -> str:
        parent = cls._open_directory(path.parent)
        try:
            return cls._checksum_at(parent, path.name)
        finally:
            os.close(parent)

    @classmethod
    def _rename_noreplace(cls, source_dir_fd: int, source_name: str, target_dir_fd: int, target_name: str) -> None:
        if not sys.platform.startswith("linux"):
            raise OSError("atomic no-replace rename is unavailable")
        libc = ctypes.CDLL(None, use_errno=True)
        syscall = libc.syscall
        syscall.restype = ctypes.c_long
        number = {"x86_64": 316, "aarch64": 276}.get(os.uname().machine)
        if number is None:
            raise OSError("unsupported Linux architecture")
        result = syscall(number, source_dir_fd, source_name.encode(), target_dir_fd, target_name.encode(), 1)
        if result != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))

    @classmethod
    def _restore_move(cls, source: Path, target: Path) -> None:
        try:
            source_parent = cls._open_directory(source.parent)
            target_parent = cls._open_directory(target.parent)
            try:
                cls._rename_noreplace(source_parent, source.name, target_parent, target.name)
            finally:
                os.close(source_parent)
                os.close(target_parent)
        except OSError:
            pass

    def _audit_db(self, row: sqlite3.Row | dict[str, object], decision: str, result: str) -> None:
        self.db.execute(
            "INSERT INTO file_action_audit(request_id,action,target_digest,decision,result,created) VALUES(?,?,?,?,?,?)",
            (row["request_id"], row["action"], row["target_digest"], decision, result, self._clock()),
        )
        self.db.commit()

    def _append_log(self, request_id: str, action: str, event: str, original: Path, destination: Path) -> None:
        if event not in {"authorized_attempt", "moved_to_trash", "restored_from_trash"}:
            raise FileActionError("invalid audit event")
        self.audit_log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_CLOEXEC | os.O_NOFOLLOW
        fd = os.open(self.audit_log, flags, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("audit log is not a regular file")
            os.fchmod(fd, 0o600)
            if os.fstat(fd).st_size == 0:
                self._write_all(fd, DELETE_LOG_HEADER.encode("utf-8"))
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            values = [timestamp, request_id, action, event, original, destination]
            cells = [str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", "\\n") for value in values]
            self._write_all(fd, ("| " + " | ".join(cells) + " |\n").encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        while data:
            written = os.write(fd, data)
            if written <= 0:
                raise OSError("audit log write failed")
            data = data[written:]

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


__all__ = ["FileActionError", "FileActionRequest", "FileActionService", "FileIdentity"]
