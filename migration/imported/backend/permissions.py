from __future__ import annotations

import hashlib
import ctypes
import os
import re
import secrets
import sqlite3
import stat
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from .storage import connect, ensure_schema
from .deletion_log import append_deletion_event


class ApprovalError(Exception):
    """A requested capability cannot be safely authorized or executed."""


@dataclass(frozen=True)
class FileIdentity:
    path: str
    device: int
    inode: int
    size: int
    mtime_ns: int

    @classmethod
    def capture(cls, target: Path) -> FileIdentity:
        canonical = target.resolve(strict=True)
        stat = canonical.stat()
        if not canonical.is_file() or canonical.is_symlink():
            raise ApprovalError("only regular files may be individually approved")
        return cls(str(canonical), stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)

    def matches(self) -> bool:
        target = Path(self.path)
        try:
            if target.is_symlink() or target.resolve(strict=True) != target:
                return False
            stat = target.stat()
        except OSError:
            return False
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns) == (
            self.device, self.inode, self.size, self.mtime_ns
        )

    def digest(self) -> str:
        value = f"{self.path}\0{self.device}\0{self.inode}\0{self.size}\0{self.mtime_ns}"
        return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    action: str
    reason: str
    identity: FileIdentity
    expires_at: float


class ApprovalBroker:
    """One-use, per-file approval tokens. Execution is deliberately not performed here."""

    ALLOWED_ACTIONS = {"trash_file", "restore_file", "delete_file", "overwrite_file", "move_file"}
    MAX_REASON_LENGTH = 512
    REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,128}$")

    @classmethod
    def _validate_request_id(cls, request_id: object) -> str:
        """Validate opaque approval IDs before any lookup or state mutation."""
        if not isinstance(request_id, str) or not cls.REQUEST_ID_PATTERN.fullmatch(request_id):
            raise ApprovalError("approval request id is malformed")
        return request_id

    def __init__(self, db_path: Path, ttl: int = 300, clock=time.time, trash_root: Path | None = None) -> None:
        self.db_path = db_path
        self.ttl = ttl
        self.clock = clock
        self.trash_root = (trash_root or db_path.parent / ".jarvis-trash").resolve()
        self._requests: dict[str, ApprovalRequest] = {}
        self._decisions: set[str] = set()
        self._approved: set[str] = set()
        self._consumed: set[str] = set()
        ensure_schema(self.db_path)
        with connect(self.db_path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS permission_audit "
                "(id INTEGER PRIMARY KEY, request_id TEXT NOT NULL, actor TEXT NOT NULL, "
                "capability TEXT NOT NULL, target_digest TEXT NOT NULL, decision TEXT NOT NULL, "
                "result TEXT NOT NULL, created REAL NOT NULL)"
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(permission_audit)")}
            if "actor" not in columns:
                db.execute("ALTER TABLE permission_audit ADD COLUMN actor TEXT NOT NULL DEFAULT 'owner'")
            if "capability" not in columns:
                db.execute("ALTER TABLE permission_audit ADD COLUMN capability TEXT NOT NULL DEFAULT 'unknown'")
        with connect(self.db_path) as db:
            rows = db.execute(
                "SELECT request_id, action, reason, path, device, inode, size, mtime_ns, expires_at, state "
                "FROM approval_requests"
            ).fetchall()
        for row in rows:
            # SQLite is local state, but it is still an authorization input:
            # reject tampered or legacy rows before they can populate any
            # approval set.  Loading a malformed opaque ID would otherwise
            # make restart semantics differ from direct broker calls.
            self._validate_request_id(row[0])
            identity = FileIdentity(row[3], row[4], row[5], row[6], row[7])
            request = ApprovalRequest(row[0], row[1], row[2], identity, row[8])
            self._requests[request.request_id] = request
            if row[9] in {"approved", "consumed"}:
                self._approved.add(request.request_id)
            if row[9] in {"denied", "consumed"}:
                self._decisions.add(request.request_id)
            if row[9] == "consumed":
                self._consumed.add(request.request_id)

    def propose(self, target: Path, action: str, reason: str) -> ApprovalRequest:
        # Keep this boundary typed even for non-model callers.  A malformed
        # value must become a policy rejection, not an unhashable-membership
        # TypeError or an AttributeError before approval state is recorded.
        if not isinstance(target, Path):
            raise ApprovalError("approval target must be a pathlib.Path")
        if not isinstance(action, str) or action not in self.ALLOWED_ACTIONS:
            raise ApprovalError("capability is not allowlisted")
        normalized_reason = self._validate_reason(reason)
        identity = FileIdentity.capture(target)
        request = ApprovalRequest(secrets.token_urlsafe(24), action, normalized_reason, identity, self.clock() + self.ttl)
        self._requests[request.request_id] = request
        with connect(self.db_path) as db:
            db.execute(
                "INSERT INTO approval_requests(request_id, action, reason, path, device, inode, size, mtime_ns, expires_at, state) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')",
                (request.request_id, request.action, request.reason, identity.path, identity.device,
                 identity.inode, identity.size, identity.mtime_ns, request.expires_at),
            )
        self._audit(request, "pending", "awaiting_owner")
        return request

    @classmethod
    def _validate_reason(cls, reason: object) -> str:
        """Validate human-controlled approval text before any target lookup."""
        if not isinstance(reason, str) or not reason.strip():
            raise ApprovalError("a human-readable reason is required")
        normalized_reason = reason.strip()
        if any(ord(char) < 0x20 or ord(char) == 0x7f for char in normalized_reason):
            raise ApprovalError("approval reason contains control characters")
        if len(normalized_reason) > cls.MAX_REASON_LENGTH:
            raise ApprovalError("approval reason is too long")
        return normalized_reason

    def propose_directory(self, target: Path, action: str, reason: str) -> None:
        """Reject directory-wide approval; callers must enumerate files individually.

        This explicit entry point prevents a future cleanup adapter from treating
        one directory approval as authorization for recursive child operations.
        """
        raise ApprovalError("directory-wide approval is forbidden; propose each regular file separately")

    def decide(self, request_id: str, approved: bool) -> None:
        request_id = self._validate_request_id(request_id)
        if not isinstance(approved, bool):
            raise ApprovalError("owner decision must be a boolean")
        request = self._requests.get(request_id)
        if not request or request_id in self._decisions:
            raise ApprovalError("approval is unknown or already decided")
        if self.clock() >= request.expires_at:
            self._decisions.add(request_id)
            self._audit(request, "expired", "approval_expired")
            raise ApprovalError("approval expired")
        self._decisions.add(request_id)
        state = "approved" if approved else "denied"
        with connect(self.db_path) as db:
            db.execute("UPDATE approval_requests SET state = ? WHERE request_id = ?", (state, request_id))
        self._audit(request, "approved" if approved else "denied", "owner_decision")
        if not approved:
            raise ApprovalError("owner denied this individual file action")
        self._approved.add(request_id)

    def authorize_execution(self, request_id: str) -> ApprovalRequest:
        request_id = self._validate_request_id(request_id)
        request = self._requests.get(request_id)
        # This is a capability boundary, not merely an approval lookup.  The
        # only enabled filesystem executor is the recoverable Trash primitive;
        # keeping that restriction here prevents a future caller from turning
        # an approved preview for delete/overwrite/move into an executable
        # capability by bypassing the HTTP route's allow-list.
        if not request or request.action != "trash_file" or request_id not in self._approved or request_id in self._consumed:
            raise ApprovalError("owner approval is required")
        if self.clock() >= request.expires_at or not request.identity.matches():
            self._audit(request, "failed", "identity_changed_or_expired")
            raise ApprovalError("file identity changed or approval expired")
        self._consumed.add(request_id)
        with connect(self.db_path) as db:
            db.execute("UPDATE approval_requests SET state = 'consumed' WHERE request_id = ?", (request_id,))
        self._audit(request, "ready", "identity_revalidated")
        return request

    def trash_file(self, request_id: str) -> Path:
        """Move one approved file to JARVIS' local recoverable Trash.

        This is intentionally the only mutation primitive.  It opens both
        directories without following their final symlink, validates the
        source through a descriptor, and uses directory-relative rename.  A
        unique destination prevents overwriting an existing Trash entry.
        """
        request_id = self._validate_request_id(request_id)
        request = self._requests.get(request_id)
        if not request or request.action != "trash_file" or request_id not in self._approved:
            raise ApprovalError("an approved trash_file request is required")
        if request_id in self._consumed or self.clock() >= request.expires_at:
            raise ApprovalError("owner approval is required")
        source = Path(request.identity.path)
        parent = source.parent
        name = source.name
        self.trash_root.mkdir(parents=True, exist_ok=True)
        source_fd = parent_fd = trash_fd = -1
        destination = self.trash_root / f"{request.request_id}-{name}"
        try:
            parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
            source_fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent_fd)
            record = os.fstat(source_fd)
            expected = request.identity
            if not stat.S_ISREG(record.st_mode) or (record.st_dev, record.st_ino, record.st_size, record.st_mtime_ns) != (
                expected.device, expected.inode, expected.size, expected.mtime_ns
            ):
                raise ApprovalError("file identity changed or approval expired")
            trash_fd = os.open(self.trash_root, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
            # A pre-check plus os.rename is not sufficient: an attacker could
            # replace the source pathname after validation, causing rename to
            # remove the wrong file, or replace an existing Trash entry. Linux
            # renameat2(RENAME_NOREPLACE) performs the move and both checks as
            # one filesystem operation. If unavailable, fail closed rather
            # than falling back to a pathname race.
            # A durable local audit entry MUST exist before any approved move.
            # It is private and deliberately not part of the GitHub checkout.
            append_deletion_event(
                self.db_path.parent / "DELETE-LOGS.md",
                approval_id=request_id,
                action="trash_file",
                event="authorized_attempt",
                original_path=source,
                destination=destination,
            )
            self._rename_noreplace(parent_fd, name, trash_fd, destination.name)
            moved = os.stat(destination.name, dir_fd=trash_fd, follow_symlinks=False)
            if (moved.st_dev, moved.st_ino, moved.st_size, moved.st_mtime_ns) != (
                expected.device, expected.inode, expected.size, expected.mtime_ns
            ):
                raise ApprovalError("Trash identity verification failed")
            self._consumed.add(request_id)
            with connect(self.db_path) as db:
                db.execute("UPDATE approval_requests SET state = 'consumed' WHERE request_id = ?", (request_id,))
                checksum = self._checksum_fd(trash_fd, destination.name)
                db.execute(
                    "INSERT INTO trash_manifests(request_id, trash_path, original_path, checksum, device, inode, size, mtime_ns, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (request.request_id, str(destination), expected.path, checksum, expected.device, expected.inode, expected.size, expected.mtime_ns, self.clock()),
                )
            self._audit(request, "completed", "moved_to_trash")
            append_deletion_event(
                self.db_path.parent / "DELETE-LOGS.md",
                approval_id=request_id,
                action="trash_file",
                event="moved_to_trash",
                original_path=source,
                destination=destination,
            )
            return destination
        except ApprovalError:
            self._audit(request, "failed", "identity_changed_or_trash_failed")
            raise
        except (OSError, ValueError) as exc:
            self._audit(request, "failed", "trash_operation_failed")
            raise ApprovalError("file could not be moved safely") from exc
        finally:
            for fd in (source_fd, parent_fd, trash_fd):
                if fd >= 0:
                    os.close(fd)

    def execute_trash_file(self, request_id: str) -> tuple[ApprovalRequest, Path]:
        """Execute exactly one approved Trash capability through a public boundary."""
        request_id = self._validate_request_id(request_id)
        request = self._requests.get(request_id)
        if not request or request.action != "trash_file":
            raise ApprovalError("only an approved trash_file capability is executable")
        return request, self.trash_file(request_id)

    @staticmethod
    def _rename_noreplace(source_dir_fd: int, source_name: str, target_dir_fd: int, target_name: str) -> None:
        """Atomically move one directory entry without replacing the target."""
        if not sys.platform.startswith("linux"):
            raise OSError("atomic no-replace rename is unavailable on this platform")
        libc = ctypes.CDLL(None, use_errno=True)
        syscall = libc.syscall
        syscall.restype = ctypes.c_long
        # SYS_renameat2 is 316 on supported x86_64/aarch64 Linux hosts. The
        # host contract is Ubuntu Linux; unknown architectures fail closed.
        machine = os.uname().machine
        syscall_number = {"x86_64": 316, "aarch64": 276}.get(machine)
        if syscall_number is None:
            raise OSError(f"unsupported Linux architecture: {machine}")
        result = syscall(
            syscall_number,
            source_dir_fd,
            source_name.encode(),
            target_dir_fd,
            target_name.encode(),
            1,  # RENAME_NOREPLACE
        )
        if result != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))

    @contextmanager
    def verified_file(self, request_id: str):
        """Yield a verified read-only descriptor for a single approved file.

        This is deliberately not a mutation primitive.  An eventual Trash or
        delete executor must use the yielded descriptor (and its parent
        directory descriptor) rather than re-resolving the path after this
        check.  ``O_NOFOLLOW`` plus ``fstat`` closes the common symlink and
        replacement gap between pathname validation and opening the target.
        Approval is consumed only after the descriptor has been verified.
        """
        request_id = self._validate_request_id(request_id)
        request = self._requests.get(request_id)
        if not request or request_id not in self._approved or request_id in self._consumed:
            raise ApprovalError("owner approval is required")
        if self.clock() >= request.expires_at:
            self._audit(request, "failed", "identity_changed_or_expired")
            raise ApprovalError("file identity changed or approval expired")
        fd = -1
        try:
            fd = os.open(request.identity.path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
            record = os.fstat(fd)
            expected = request.identity
            if not stat.S_ISREG(record.st_mode) or (record.st_dev, record.st_ino, record.st_size, record.st_mtime_ns) != (
                expected.device, expected.inode, expected.size, expected.mtime_ns
            ):
                raise ApprovalError("file identity changed or approval expired")
            self._consumed.add(request_id)
            with connect(self.db_path) as db:
                db.execute("UPDATE approval_requests SET state = 'consumed' WHERE request_id = ?", (request_id,))
            self._audit(request, "ready", "descriptor_identity_revalidated")
            yield fd, request
        except ApprovalError:
            # Identity failures are security events, not ordinary I/O errors.
            # Keep the approval unconsumed so the caller can request a fresh
            # decision after presenting the changed target to the owner.
            self._audit(request, "failed", "identity_changed_or_expired")
            raise
        except (OSError, ValueError):
            self._audit(request, "failed", "descriptor_open_failed")
            raise ApprovalError("file could not be opened safely")
        finally:
            if fd >= 0:
                os.close(fd)

    @staticmethod
    def _checksum_fd(directory_fd: int | Path, name: str) -> str:
        digest = hashlib.sha256()
        opened_directory = False
        if isinstance(directory_fd, Path):
            directory_fd = os.open(directory_fd, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
            opened_directory = True
        fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
        finally:
            os.close(fd)
            if opened_directory:
                os.close(directory_fd)
        return digest.hexdigest()

    def trash_manifest(self, request_id: str) -> dict[str, object] | None:
        # Keep direct broker callers on the same strict opaque-ID boundary as
        # the HTTP adapter.  Even a read-only lookup must not accept arbitrary
        # model-shaped values or malformed control strings before SQLite.
        request_id = self._validate_request_id(request_id)
        with connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM trash_manifests WHERE request_id = ?", (request_id,)).fetchone()
        return dict(row) if row else None

    def propose_restore(self, request_id: str, reason: str) -> ApprovalRequest:
        request_id = self._validate_request_id(request_id)
        # Reject malformed direct callers before manifest lookup or filesystem
        # inspection.  The lower-level broker must preserve the same ordering
        # guarantees as the authenticated HTTP boundary.
        reason = self._validate_reason(reason)
        manifest = self.trash_manifest(request_id)
        if not manifest or manifest["restored"] is not None:
            raise ApprovalError("Trash entry is unavailable or already restored")
        trash = Path(str(manifest["trash_path"]))
        if not trash.is_file() or trash.is_symlink():
            raise ApprovalError("Trash entry is missing or unsafe")
        request = self.propose(trash, "restore_file", reason)
        with connect(self.db_path) as db:
            db.execute("UPDATE approval_requests SET restore_target = ? WHERE request_id = ?", (manifest["original_path"], request.request_id))
        self._requests[request.request_id] = ApprovalRequest(request.request_id, request.action, request.reason, request.identity, request.expires_at)
        return request

    def restore_file(self, request_id: str) -> Path:
        request_id = self._validate_request_id(request_id)
        request = self._requests.get(request_id)
        if not request or request.action != "restore_file" or request_id not in self._approved or request_id in self._consumed:
            raise ApprovalError("an approved restore_file request is required")
        with connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM trash_manifests WHERE trash_path = ? AND restored IS NULL", (request.identity.path,)).fetchone()
        manifest = dict(row) if row else None
        if not manifest:
            raise ApprovalError("Trash manifest is missing")
        target = Path(str(manifest["original_path"]))
        source = Path(request.identity.path)
        if target.exists() or target.is_symlink():
            raise ApprovalError("restore destination already exists")
        if self.clock() >= request.expires_at:
            raise ApprovalError("owner approval is required")
        source_fd = source_parent_fd = target_parent_fd = -1
        try:
            source_fd = os.open(source, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
            record = os.fstat(source_fd)
            if (record.st_dev, record.st_ino, record.st_size, record.st_mtime_ns) != (request.identity.device, request.identity.inode, request.identity.size, request.identity.mtime_ns):
                raise ApprovalError("Trash identity changed")
            if self._checksum_fd(source.parent, source.name) != manifest["checksum"]:
                raise ApprovalError("Trash checksum changed")
            target.parent.mkdir(parents=True, exist_ok=True)
            source_parent_fd = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
            target_parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
            # The existence check above is only advisory. Use an atomic
            # no-replace move so a destination created after that check can
            # never be overwritten during restore.
            append_deletion_event(
                self.db_path.parent / "DELETE-LOGS.md",
                approval_id=request_id,
                action="restore_file",
                event="authorized_attempt",
                original_path=source,
                destination=target,
            )
            self._rename_noreplace(source_parent_fd, source.name, target_parent_fd, target.name)
            self._consumed.add(request_id)
            with connect(self.db_path) as db:
                db.execute("UPDATE approval_requests SET state = 'consumed' WHERE request_id = ?", (request_id,))
                db.execute("UPDATE trash_manifests SET restored = ? WHERE request_id = ?", (self.clock(), manifest["request_id"]))
            self._audit(request, "completed", "restored_from_trash")
            append_deletion_event(
                self.db_path.parent / "DELETE-LOGS.md",
                approval_id=request_id,
                action="restore_file",
                event="restored_from_trash",
                original_path=source,
                destination=target,
            )
            return target
        except (OSError, ValueError) as exc:
            self._audit(request, "failed", "restore_operation_failed")
            raise ApprovalError("file could not be restored safely") from exc
        finally:
            for fd in (source_fd, source_parent_fd, target_parent_fd):
                if fd >= 0: os.close(fd)

    def audit(self, limit: int = 100) -> list[dict[str, object]]:
        """Return redacted durable records; paths, reasons and tokens never leave the broker."""
        # Keep direct broker callers on a typed, bounded boundary.  In
        # particular, bool is an int subclass but must not silently turn into
        # a one-record audit request, and model-shaped objects must not leak a
        # raw comparison/SQLite exception.
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ApprovalError("audit limit must be an integer")
        bounded = max(1, min(limit, 500))
        with connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT id, request_id, actor, capability, target_digest, decision, result, created "
                "FROM permission_audit ORDER BY id DESC LIMIT ?", (bounded,)
            ).fetchall()
        return [dict(row) for row in rows]

    def emergency_stop(self) -> int:
        """Deny every undecided request; never approves or executes anything."""
        pending = [request for request in self._requests.values()
                   if request.request_id not in self._decisions]
        for request in pending:
            try:
                self.decide(request.request_id, False)
            except ApprovalError:
                # Expiry is already a terminal, fail-closed outcome.
                self._decisions.add(request.request_id)
        return len(pending)

    def _audit(self, request: ApprovalRequest, decision: str, result: str) -> None:
        with connect(self.db_path) as db:
            db.execute(
                "INSERT INTO permission_audit(request_id, actor, capability, target_digest, decision, result, created) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (request.request_id, "owner", request.action, request.identity.digest(), decision, result, self.clock()),
            )
