from __future__ import annotations

import hashlib
import re
import os
import sqlite3
import stat
import time
from dataclasses import dataclass
from pathlib import Path
from .storage import connect

VIRTUAL = {"/proc", "/sys", "/dev", "/run", "/snap"}
SENSITIVE_NAMES = {
    ".ssh", ".gnupg", ".password-store", ".mozilla", "google-chrome",
    "chromium", "keyrings", "browser-profiles",
}
EXCLUDED_DIR_NAMES = {".git", "__pycache__", ".cache", "keyrings"}
VIRTUAL_FS = {"proc", "sysfs", "devtmpfs", "devpts", "tmpfs", "cgroup", "cgroup2", "overlay", "squashfs", "pstore", "debugfs"}


def mounted_volumes(proc_mounts: Path = Path("/proc/mounts")) -> list[dict[str, object]]:
    """Return sanitized, read-only volume provenance and capacity facts."""
    volumes: list[dict[str, object]] = []
    try:
        lines = proc_mounts.read_text().splitlines()
    except OSError:
        return volumes
    for line in lines:
        fields = line.split()
        if len(fields) < 3 or fields[2] in VIRTUAL_FS:
            continue
        mountpoint = fields[1].replace("\\040", " ")
        if not mountpoint.startswith("/"):
            continue
        try:
            usage = os.statvfs(mountpoint)
            total = usage.f_blocks * usage.f_frsize
            free = usage.f_bavail * usage.f_frsize
        except OSError:
            continue
        if total > 0:
            volumes.append({"mountpoint": mountpoint, "filesystem": fields[2],
                            "total_bytes": total, "free_bytes": free})
    return volumes


def _is_secret_name(name: str) -> bool:
    """Match secret files without treating ordinary names as secrets."""
    return name == ".env" or name.startswith(".env.")


@dataclass(frozen=True)
class FileRecord:
    path: str
    kind: str
    size: int
    mtime: float
    mount: str


def is_allowed(path: Path) -> bool:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return False
    text = str(resolved)
    if any(text == root or text.startswith(root + "/") for root in VIRTUAL):
        return False
    parts = set(resolved.parts)
    if any(name in parts for name in SENSITIVE_NAMES):
        return False
    return not any(_is_secret_name(part) for part in resolved.parts)


def default_roots() -> list[Path]:
    roots: list[Path] = []
    for name in ("XDG_DOCUMENTS_DIR", "XDG_DOWNLOAD_DIR", "XDG_PICTURES_DIR", "XDG_DESKTOP_DIR"):
        value = os.environ.get(name)
        if value:
            roots.append(Path(value).expanduser())
    home = Path.home()
    for name in ("Documents", "Downloads", "Pictures", "Desktop", "Projects"):
        roots.append(home / name)
    return list(dict.fromkeys(p for p in roots if p.is_dir() and is_allowed(p)))


def configured_roots(db_path: Path) -> list[Path]:
    """Return only roots explicitly selected by the owner in local storage."""
    with connect(db_path) as db:
        rows = db.execute("SELECT path FROM scan_roots ORDER BY path").fetchall()
    roots: list[Path] = []
    for (raw,) in rows:
        candidate = Path(raw)
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved.is_dir() and not resolved.is_symlink() and is_allowed(resolved):
            roots.append(resolved)
    return roots


def _open_git_metadata(directory_fd: int) -> int:
    """Open a repository's Git metadata, including linked-worktree pointers."""
    git_fd = os.open(".git", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
    info = os.fstat(git_fd)
    if stat.S_ISDIR(info.st_mode):
        return git_fd
    if not stat.S_ISREG(info.st_mode) or info.st_size > 4096:
        os.close(git_fd)
        raise OSError("invalid git metadata pointer")
    try:
        pointer = os.read(git_fd, 4097).decode("utf-8").strip()
    finally:
        os.close(git_fd)
    if not pointer.startswith("gitdir: "):
        raise OSError("invalid git metadata pointer")
    target = Path(pointer[8:]).expanduser()
    if not target.is_absolute():
        target = Path(os.readlink(f"/proc/self/fd/{directory_fd}")) / target
    return os.open(target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)


def _git_branch(directory_fd: int) -> str:
    """Read a small Git HEAD through no-follow descriptors, without invoking Git."""
    try:
        git_fd = _open_git_metadata(directory_fd)
        try:
            head_fd = os.open("HEAD", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=git_fd)
            try:
                info = os.fstat(head_fd)
                if not stat.S_ISREG(info.st_mode) or info.st_size > 256:
                    return "unknown"
                value = os.read(head_fd, 257).decode("ascii").strip()
            finally:
                os.close(head_fd)
        finally:
            os.close(git_fd)
    except (OSError, UnicodeError):
        return "unknown"
    if value.startswith("ref: refs/heads/"):
        name = value.removeprefix("ref: refs/heads/")
        if re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", name):
            return name
    return "unknown"


def _git_checkpoint(directory_fd: int) -> str:
    """Return a safe Git checkpoint hash, or ``unknown``.

    This deliberately reads only ``HEAD`` and a direct branch ref through
    no-follow descriptors. It never invokes Git or evaluates repository data.
    """
    try:
        git_fd = _open_git_metadata(directory_fd)
        try:
            head_fd = os.open("HEAD", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=git_fd)
            try:
                head = os.read(head_fd, 257).decode("ascii").strip()
            finally:
                os.close(head_fd)
            if re.fullmatch(r"[0-9a-fA-F]{40}", head):
                return head.lower()
            if not head.startswith("ref: refs/heads/"):
                return "unknown"
            ref = head.removeprefix("ref: refs/heads/")
            if not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", ref):
                return "unknown"
            refs_fd = os.open("refs", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=git_fd)
            try:
                for part in ("heads", *ref.split("/")):
                    next_fd = os.open(part, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=refs_fd)
                    os.close(refs_fd)
                    refs_fd = next_fd
                commit = os.read(refs_fd, 257).decode("ascii").strip()
            finally:
                os.close(refs_fd)
            return commit.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", commit) else "unknown"
        finally:
            os.close(git_fd)
    except (OSError, UnicodeError):
        return "unknown"


def discover_projects(db_path: Path, limit: int = 100) -> list[dict[str, object]]:
    """Discover local Git workspaces below owner-selected roots, read-only.

    Only repository directories themselves are returned; no file contents,
    remotes, credentials, or Git commands that can mutate state are inspected.
    """
    if type(limit) is not int or limit < 1 or limit > 500:
        raise ValueError("project limit is invalid")
    projects: list[dict[str, object]] = []

    # Task evidence is deliberately opt-in: only a payload field naming the
    # canonical repository can associate a durable local task with a project.
    # This keeps unrelated assistant tasks out of the Projects view and does
    # not inspect repositories, invoke Git, or authorize any worker action.
    evidence: dict[str, list[dict[str, object]]] = {}
    try:
        with connect(db_path) as db:
            rows = db.execute(
                "SELECT kind, state, result, error, payload FROM tasks "
                "ORDER BY updated DESC LIMIT 200"
            ).fetchall()
        import json
        for kind, state, result, error, payload_text in rows:
            try:
                payload = json.loads(payload_text)
            except (TypeError, ValueError):
                continue
            if not isinstance(payload, dict):
                continue
            raw_path = payload.get("project_path")
            if not isinstance(raw_path, str) or not raw_path:
                continue
            try:
                project_path = str(Path(raw_path).expanduser().resolve(strict=False))
            except OSError:
                continue
            evidence.setdefault(project_path, []).append({
                "kind": kind, "state": state, "result": result,
                "error": error,
            })
    except sqlite3.Error:
        # A project inventory remains useful if an older/read-only database
        # has no task tables yet.
        evidence = {}
    deadline = time.monotonic() + 1.0
    inspected = 0
    entries_seen = 0
    for root in configured_roots(db_path):
        stack = [root]
        visited: set[tuple[int, int]] = set()
        try:
            root_device = root.stat().st_dev
        except OSError:
            continue
        while stack and len(projects) < limit and inspected < 2000 and entries_seen < 10000 and time.monotonic() < deadline:
            current = stack.pop()
            try:
                if not is_allowed(current) or not current.resolve(strict=True).is_relative_to(root):
                    continue
                fd = os.open(current, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    info = os.fstat(fd)
                    if info.st_dev != root_device:
                        continue
                    identity = (info.st_dev, info.st_ino)
                    if identity in visited:
                        continue
                    visited.add(identity)
                    inspected += 1
                    branch = None
                    checkpoint = "unknown"
                    children = []
                    with os.scandir(fd) as entries:
                        for entry in entries:
                            entries_seen += 1
                            if entries_seen > 10000 or time.monotonic() >= deadline:
                                break
                            if entry.is_symlink():
                                continue
                            if entry.name == ".git" and not entry.is_symlink() and (
                                    entry.is_dir(follow_symlinks=False) or
                                    entry.is_file(follow_symlinks=False)):
                                branch = _git_branch(fd)
                                checkpoint = _git_checkpoint(fd)
                            elif entry.name not in EXCLUDED_DIR_NAMES and entry.is_dir(follow_symlinks=False):
                                if entry.stat(follow_symlinks=False).st_dev == root_device:
                                    children.append(current / entry.name)
                finally:
                    os.close(fd)
                if branch is not None:
                    project_path = str(current.resolve(strict=False))
                    project_tasks = evidence.get(project_path, [])
                    test_tasks = [item for item in project_tasks
                                  if "test" in str(item["kind"]).lower()]
                    codex_tasks = [item for item in project_tasks
                                   if "codex" in str(item["kind"]).lower()]
                    projects.append({"path": project_path, "branch": branch,
                                     "status": "local repository", "mutations": False,
                                     "checkpoint": checkpoint,
                                     "test_result": (test_tasks[0]["state"]
                                                     if test_tasks else "not recorded"),
                                     "codex_progress": (codex_tasks[0]["state"]
                                                         if codex_tasks else "not connected"),
                                     "task_milestones": project_tasks[:20]})
                    continue
                stack.extend(children)
            except OSError:
                continue
        if inspected >= 2000 or entries_seen >= 10000 or time.monotonic() >= deadline:
            break
    return sorted(projects, key=lambda item: str(item["path"]))


def add_configured_root(path: Path, db_path: Path) -> Path:
    """Persist one canonical, readable, non-sensitive directory as a scan root."""
    try:
        resolved = path.expanduser().resolve(strict=True)
    except OSError as exc:
        raise ValueError("scan root must be an allowed real directory") from exc
    if not resolved.is_dir() or resolved.is_symlink() or not is_allowed(resolved):
        raise ValueError("scan root must be an allowed real directory")
    with connect(db_path) as db:
        db.execute("INSERT OR IGNORE INTO scan_roots(path, created) VALUES (?, ?)",
                   (str(resolved), time.time()))
    return resolved


def scan(roots: list[Path], limit: int = 2000) -> tuple[list[FileRecord], bool]:
    records: list[FileRecord] = []
    visited: set[tuple[int, int]] = set()
    for root in roots:
        if len(records) >= limit or not is_allowed(root):
            continue
        try:
            if root.is_symlink():
                continue
            canonical_root = root.resolve(strict=True)
            if not canonical_root.is_dir() or canonical_root.is_symlink():
                continue
            root_stat = canonical_root.stat()
            stack = [(canonical_root, root_stat.st_dev)]
        except OSError:
            continue
        while stack and len(records) < limit:
            current, device = stack.pop()
            try:
                if not is_allowed(current):
                    continue
                current_stat = current.stat()
                identity = (current_stat.st_dev, current_stat.st_ino)
                if identity in visited:
                    continue
                visited.add(identity)
                with os.scandir(current) as entries:
                    for entry in entries:
                        if len(records) >= limit:
                            break
                        child = Path(entry.path)
                        if entry.is_symlink() or not is_allowed(child):
                            continue
                        try:
                            stat = entry.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name in EXCLUDED_DIR_NAMES or stat.st_dev != device:
                                continue
                            stack.append((child, device))
                            kind = "directory"
                        elif entry.is_file(follow_symlinks=False):
                            kind = "file"
                        else:
                            continue
                        mount = "/" if stat.st_dev == root_stat.st_dev else "unknown"
                        records.append(FileRecord(str(child), kind, stat.st_size, stat.st_mtime, mount))
            except OSError:
                continue
    return records, len(records) >= limit


def store(records: list[FileRecord], db_path: Path, roots: list[Path] | None = None) -> int:
    """Reconcile metadata records, pruning stale rows only inside *roots*.

    The pruning is local SQLite maintenance, never filesystem deletion.  A
    caller must provide the explicit owner-selected roots to enable it; the
    legacy ``None`` form only upserts records and therefore cannot widen the
    cleanup scope accidentally.
    """
    with connect(db_path) as db:
        if roots:
            seen = {record.path for record in records}
            for root in roots:
                canonical = root.expanduser().resolve(strict=False)
                # Do not express the scope as SQL LIKE: '%' and '_' are valid
                # path characters and would turn an owner-selected root into
                # a wildcard that can prune unrelated records.  Fetch the
                # bounded metadata paths and apply the exact canonical,
                # descendant check in Python instead.
                candidates = db.execute("SELECT path FROM file_index").fetchall()
                stale = []
                for (raw_path,) in candidates:
                    try:
                        candidate = Path(raw_path).resolve(strict=False)
                        in_scope = candidate != canonical and candidate.is_relative_to(canonical)
                    except (OSError, ValueError):
                        in_scope = False
                    if in_scope and raw_path not in seen:
                        stale.append((raw_path,))
                if stale:
                    db.executemany("DELETE FROM file_index WHERE path = ?", stale)
        db.executemany("DELETE FROM file_index WHERE path = ?", [(r.path,) for r in records])
        db.executemany("INSERT INTO file_index(path, kind, size, mtime, mount) VALUES (?, ?, ?, ?, ?)",
                       [(r.path, r.kind, r.size, r.mtime, r.mount) for r in records])
    return len(records)


def refresh(roots: list[Path], db_path: Path, *, limit: int = 2000,
            now: float | None = None) -> dict[str, object]:
    """Perform one bounded, metadata-only refresh of owner-selected roots.

    The scan timestamp is durable per root so callers can display freshness and
    schedule the next bounded refresh without inferring that an old index is
    current. Empty roots are recorded as complete too; the filesystem is never
    modified by this operation.
    """
    if not roots:
        return {"records": 0, "limited": False, "roots": 0, "last_seen": None}
    records, limited = scan(roots, limit)
    count = store(records, db_path, roots)
    timestamp = time.time() if now is None else now
    with connect(db_path) as db:
        for root in roots:
            canonical = str(root.expanduser().resolve(strict=False))
            db.execute(
                "INSERT INTO inventory_scans(path,last_seen,record_count,complete) VALUES(?,?,?,?) "
                "ON CONFLICT(path) DO UPDATE SET last_seen=excluded.last_seen, "
                "record_count=excluded.record_count, complete=excluded.complete",
                (canonical, timestamp, count, int(not limited)),
            )
    return {"records": count, "limited": limited, "roots": len(roots), "last_seen": timestamp}


def refresh_status(db_path: Path) -> list[dict[str, object]]:
    """Return durable freshness facts without touching the filesystem."""
    with connect(db_path) as db:
        rows = db.execute("SELECT path,last_seen,record_count,complete FROM inventory_scans ORDER BY path").fetchall()
    return [{"path": row[0], "last_seen": row[1], "record_count": row[2], "complete": bool(row[3])}
            for row in rows]


def search(query: str, db_path: Path, limit: int = 50) -> list[dict]:
    # FTS5 treats punctuation and operators as query syntax.  File search is
    # user input, not an administrator-authored MATCH expression.  Tokenize
    # ordinary natural-language input and quote each token, so phrases such as
    # "find my tax receipts" become a safe AND query rather than an FTS command.
    # Empty/punctuation-only input is a normal no-match.
    stop_words = {"a", "an", "find", "for", "in", "my", "of", "the", "to", "with"}
    tokens = [token for token in re.findall(r"[\w]+", query, flags=re.UNICODE)
              if token.casefold() not in stop_words]
    tokens = list(dict.fromkeys(token for token in tokens if len(token) <= 80))[:12]
    if not tokens:
        return []
    expression = " AND ".join('"' + token.replace('"', '""') + '"' for token in tokens)
    with connect(db_path) as db:
        rows = db.execute(
            "SELECT path, kind, size, mtime, mount FROM file_index "
            "WHERE file_index MATCH ? ORDER BY rank LIMIT ?", (expression, limit)
        ).fetchall()
    results = []
    for row in rows:
        item = dict(zip(("path", "kind", "size", "mtime", "mount"), row))
        # A search result is only as current as the last metadata scan.  Check
        # the exact indexed identity with lstat, without following links or
        # opening content.  Missing/replaced entries remain visible but are
        # explicitly marked stale so callers cannot present old paths as live.
        current = None
        try:
            current = os.lstat(str(item["path"]))
        except OSError:
            pass
        if current is None:
            item["stale"] = True
            item["stale_reason"] = "path is missing or inaccessible"
        else:
            current_kind = "directory" if os.path.isdir(str(item["path"])) else "file" if os.path.isfile(str(item["path"])) else "other"
            changed = (current_kind != item["kind"] or int(current.st_size) != int(item["size"])
                       or float(current.st_mtime) != float(item["mtime"]))
            item["stale"] = changed
            item["stale_reason"] = "filesystem metadata differs from the index" if changed else ""
        lowered_path = str(item["path"]).casefold()
        matched = sum(token.casefold() in lowered_path for token in tokens)
        item["confidence"] = round(matched / len(tokens), 2)
        item["match_basis"] = "all query terms matched in indexed metadata"
        results.append(item)
    return results


def duplicate_groups(db_path: Path, limit: int = 50) -> list[dict[str, object]]:
    """Return bounded duplicate *candidates* using metadata only.

    Equal size is only a hash candidate, never proof of duplicate content.  No
    file is opened and no action is implied by this read-only report.
    """
    bounded = max(1, min(int(limit), 200))
    with connect(db_path) as db:
        rows = db.execute(
            "SELECT size, GROUP_CONCAT(path, char(10)) FROM file_index "
            "WHERE kind='file' GROUP BY size HAVING COUNT(*) > 1 "
            "ORDER BY size DESC LIMIT ?", (bounded,)
        ).fetchall()
    groups = []
    for size, paths in rows:
        members = paths.split("\n") if paths else []
        groups.append({"size": size, "paths": members, "verified": False,
                       "basis": "same metadata size; content hash not computed"})
    return groups


def verified_duplicate_groups(db_path: Path, limit: int = 50,
                              max_file_bytes: int = 64 * 1024 * 1024) -> list[dict[str, object]]:
    """Hash bounded same-size candidates only after an explicit caller opt-in.

    The index is metadata-only by default.  This function is the narrow,
    read-only exception: it opens regular files, refuses symlinks and files
    whose indexed size/mtime changed, and reports SHA-256 groups without
    authorizing any cleanup action.
    """
    bounded = max(1, min(int(limit), 200))
    with connect(db_path) as db:
        rows = db.execute(
            "SELECT size, path, mtime FROM file_index WHERE kind='file' "
            "AND size <= ? ORDER BY size DESC, path LIMIT ?",
            (max_file_bytes, bounded * 20),
        ).fetchall()
    by_size: dict[int, list[tuple[str, float]]] = {}
    for size, path, mtime in rows:
        by_size.setdefault(int(size), []).append((path, float(mtime)))
    result: list[dict[str, object]] = []
    bytes_read = 0
    max_total_bytes = 128 * 1024 * 1024
    deadline = time.monotonic() + 5
    for size, members in by_size.items():
        if time.monotonic() >= deadline:
            break
        if len(members) < 2:
            continue
        by_hash: dict[str, list[tuple[str, int, int]]] = {}
        for path, indexed_mtime in members:
            if time.monotonic() >= deadline:
                break
            candidate = Path(path)
            try:
                if not is_allowed(candidate) or bytes_read + size > max_total_bytes:
                    continue
                before = candidate.lstat()
                if not stat.S_ISREG(before.st_mode) or before.st_size != size or before.st_mtime != indexed_mtime:
                    continue
                fd = os.open(candidate, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
                digest = hashlib.sha256()
                try:
                    opened = os.fstat(fd)
                    if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino) or opened.st_size != size or opened.st_mtime != indexed_mtime:
                        continue
                    while True:
                        chunk = os.read(fd, 1024 * 1024)
                        if not chunk:
                            break
                        bytes_read += len(chunk)
                        if bytes_read > max_total_bytes:
                            break
                        digest.update(chunk)
                    after = os.fstat(fd)
                finally:
                    os.close(fd)
                current_path = candidate.lstat()
                if bytes_read > max_total_bytes or (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns) or (current_path.st_dev, current_path.st_ino) != (opened.st_dev, opened.st_ino) or not stat.S_ISREG(current_path.st_mode):
                    continue
                by_hash.setdefault(digest.hexdigest(), []).append((path, opened.st_dev, opened.st_ino))
            except OSError:
                continue
        for digest, matches in by_hash.items():
            if len(matches) > 1:
                identities: dict[tuple[int, int], list[str]] = {}
                for path, device, inode in matches:
                    identities.setdefault((device, inode), []).append(path)
                hardlink_groups = [members for members in identities.values() if len(members) > 1]
                result.append({"size": size, "sha256": digest, "paths": [path for path, _, _ in matches],
                               "verified": True,
                               "hardlink_groups": hardlink_groups,
                               "basis": "explicit SHA-256 content match; hardlink identity reported"})
                if len(result) >= bounded:
                    return result
    return result


def cleanup_preview(db_path: Path, limit: int = 50) -> dict[str, object]:
    """Build a non-destructive preview from duplicate candidates.

    The first path is retained only as a display convention; nothing is
    deleted, moved, or approved, and the preview must not be treated as an
    authorization request.
    """
    groups = duplicate_groups(db_path, limit)
    candidates = [{"path": path, "size": group["size"], "reason": "unverified duplicate candidate; review manually"}
                  for group in groups for path in group["paths"][1:]]
    return {"dry_run": True, "mutations": "disabled", "groups": groups,
            "candidates": candidates, "estimated_bytes": sum(item["size"] for item in candidates)}


def organization_preview(db_path: Path, limit: int = 50) -> dict[str, object]:
    """Build an exact, metadata-only plan; no move or approval is performed."""
    cleanup = cleanup_preview(db_path, limit)
    plans = []
    for item in cleanup["candidates"]:
        source = Path(str(item["path"]))
        destination = source.parent / ".jarvis-review" / source.name
        collision = destination.exists()
        plans.append({
            "before": str(source), "after": str(destination), "size": item["size"],
            "collision": collision,
            "impact": "would require a separate owner-approved move" if not collision
                      else "blocked: destination already exists",
            "mutation": "disabled",
        })
    return {"dry_run": True, "mutations": "disabled", "plans": plans,
            "estimated_bytes": sum(int(item["size"]) for item in plans if not item["collision"])}
