"""Read-only and local deterministic foundation commands. No background agents."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import sysconfig
from .guardian.release import inspect
from .health import HealthError, collect_health
from .system_inventory import InventoryError, collect_inventory, write_inventory

DEFAULT_STATE = Path.home() / ".local" / "state" / "archon"

def _config_file(name: str) -> Path:
    development = Path(__file__).resolve().parents[2] / "config" / name
    if development.is_file():
        return development
    return Path(sysconfig.get_path("data")) / "share" / "jarvis-v2" / name


def _state_directory(path: str | Path, *, create: bool = False) -> Path:
    state = Path(path).expanduser()
    if state.is_symlink():
        raise ValueError("state directory cannot be a symlink")
    if create:
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not state.is_dir():
        raise ValueError("state directory is unavailable")
    details = state.stat()
    if details.st_uid != os.geteuid() or stat.S_IMODE(details.st_mode) & 0o077:
        raise ValueError("state directory must be owned by this user and private")
    return state.resolve(strict=True)


def _initialize_state(path: str | Path) -> dict[str, object]:
    from .backend.storage import StorageManager
    from .native_controller import NativeController

    state = _state_directory(path, create=True)
    database_paths = (state / "runtime.sqlite3", state / "atlas.sqlite3")
    existed = []
    for database in database_paths:
        present = database.exists()
        if database.is_symlink() or (present and not database.is_file()):
            raise ValueError("runtime database is not a regular file")
        if present and stat.S_IMODE(database.stat().st_mode) & 0o077:
            raise ValueError("runtime database permissions are not private")
        existed.append(present)
    with StorageManager(database_paths[0]) as storage:
        migrations = storage.migrate()
    with NativeController(state):
        pass
    for database, present in zip(database_paths, existed):
        if not present:
            os.chmod(database, 0o600)
    return {"status": "initialized", "mode": "native_runtime", "migrations_applied": len(migrations)}


def _submit_task(path: str, task_path: str | Path) -> dict[str, str]:
    from .automation.queue_api import CoordinatorQueue, QueueApiError

    state = _state_directory(path)
    database = state / "atlas.sqlite3"
    if database.is_symlink() or not database.is_file():
        raise ValueError("native task queue is unavailable")
    if stat.S_IMODE(database.stat().st_mode) & 0o077:
        raise ValueError("native task queue permissions are not private")
    if str(task_path) == "-":
        raw = sys.stdin.read()
    else:
        source = Path(task_path).expanduser()
        if source.is_symlink() or not source.is_file() or source.stat().st_size > 256 * 1024:
            raise ValueError("task document is unavailable or too large")
        raw = source.read_text(encoding="utf-8")
    if len(raw.encode("utf-8")) > 256 * 1024:
        raise ValueError("task document is too large")
    task = json.loads(raw)
    if (
        not isinstance(task, dict)
        or set(task) != {"task_id", "priority", "module", "payload"}
        or not isinstance(task["payload"], dict)
    ):
        raise ValueError("task document shape is invalid")
    try:
        with CoordinatorQueue.open(database) as queue:
            envelope = queue.enqueue(
                task_id=task["task_id"],
                priority=task["priority"],
                module=task["module"],
                payload=task["payload"],
            )
    except QueueApiError as exc:
        raise ValueError("task admission failed") from exc
    return {"status": "accepted", "task_id": envelope.task_id}



def _cancel_task(path: str | Path, task_id: str) -> dict[str, str]:
    from .automation.queue_api import CoordinatorQueue, QueueApiError

    state = _state_directory(path)
    database = state / "atlas.sqlite3"
    if database.is_symlink() or not database.is_file():
        raise ValueError("native task queue is unavailable")
    if stat.S_IMODE(database.stat().st_mode) & 0o077:
        raise ValueError("native task queue permissions are not private")
    try:
        with CoordinatorQueue.open(database) as queue:
            return queue.cancel(task_id)
    except QueueApiError as exc:
        raise ValueError("task cancellation failed") from exc


def main(argv=None):
    p=argparse.ArgumentParser(prog="jarvis-v2")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("modules");s.add_parser("identities")
    init=s.add_parser("init");init.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", DEFAULT_STATE)))
    submit=s.add_parser("submit");submit.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", DEFAULT_STATE)));submit.add_argument("--task-file",required=True)
    cancel=s.add_parser("cancel");cancel.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", DEFAULT_STATE)));cancel.add_argument("--task-id",required=True)
    i=s.add_parser("inventory")
    i.add_argument("--root",type=Path,default=Path("/"))
    i.add_argument("--max-entries",type=int,default=10000)
    i.add_argument("--output",type=Path)
    i.add_argument("--resume-cursor",type=Path)
    i.add_argument("--cursor-output",type=Path)
    h=s.add_parser("health")
    h.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", DEFAULT_STATE)))
    h.add_argument("--repo",type=Path,default=Path.cwd())
    x=s.add_parser("guardian-gate");x.add_argument("manifest",type=Path)
    args=p.parse_args(argv)
    if args.command=="init":
        try: print(json.dumps(_initialize_state(args.state),sort_keys=True))
        except (OSError,ValueError) as exc:
            print(f"jarvis-v2 init: {exc}",file=sys.stderr);return 2
    elif args.command=="submit":
        try: print(json.dumps(_submit_task(args.state,args.task_file),sort_keys=True))
        except (OSError,UnicodeError,ValueError) as exc:
            print(f"jarvis-v2 submit: {exc}",file=sys.stderr);return 2
    elif args.command=="cancel":
        try: print(json.dumps(_cancel_task(args.state,args.task_id),sort_keys=True))
        except (OSError,ValueError) as exc:
            print(f"jarvis-v2 cancel: {exc}",file=sys.stderr);return 2
    elif args.command in ("modules","identities"):
        file=_config_file("identities.json" if args.command=="identities" else "modules.json")
        if file.exists(): print(file.read_text(encoding="utf-8"))
        else: print(json.dumps({"status":"no manifest; installed wheel has no repository config"}))
    elif args.command=="inventory":
        try:
            resume_cursor = None
            if args.resume_cursor:
                try:
                    resume_cursor = json.loads(args.resume_cursor.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, ValueError) as exc:
                    raise InventoryError("resume cursor is unreadable") from exc
                if not isinstance(resume_cursor, dict):
                    raise InventoryError("resume cursor must be a JSON object")
            inventory=collect_inventory(
                root=args.root,
                max_entries=args.max_entries,
                resume_cursor=resume_cursor,
            )
            if args.output:
                write_inventory(args.output, inventory)
            if args.cursor_output:
                cursor = inventory["filesystem"]["coverage"]["resume_cursor"]
                write_inventory(
                    args.cursor_output,
                    cursor or {
                        "schema": 1,
                        "root": str(args.root.resolve()),
                        "root_device": args.root.resolve().stat().st_dev,
                        "scanned_entries": inventory["filesystem"]["coverage"]["scanned_entries"],
                        "pending": [],
                    },
                )
            print(json.dumps({
                "inventory_sha256": inventory["inventory_sha256"],
                "entries": inventory["filesystem"]["coverage"]["scanned_entries"],
                "truncated": inventory["filesystem"]["coverage"]["truncated"],
                "permission_denied": len(inventory["filesystem"]["coverage"]["permission_denied"]),
                "skipped_mounts": len(inventory["filesystem"]["coverage"]["skipped_mounts"]),
                "output": str(args.output) if args.output else None,
                "resumable": inventory["filesystem"]["coverage"]["resume_cursor"] is not None,
                "cursor_output": str(args.cursor_output) if args.cursor_output else None,
            }, sort_keys=True))
        except InventoryError as exc:
            print(f"archon inventory: {exc}", file=__import__("sys").stderr)
            return 2
    elif args.command=="health":
        try:
            print(json.dumps(collect_health(state_dir=args.state, repository=args.repo), indent=2, sort_keys=True))
        except HealthError as exc:
            print(f"archon health: {exc}", file=__import__("sys").stderr)
            return 2
    else:print(json.dumps(inspect(args.manifest),indent=2))
    return 0
if __name__ == "__main__": raise SystemExit(main())
