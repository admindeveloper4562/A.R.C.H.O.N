"""Bounded dispatcher for explicitly registered, read-only task kinds.

Task persistence is deliberately separate from capability authorization.  A
worker may only run a registered function, and registration rejects anything
marked as mutating.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from .inventory import configured_roots, refresh
from .tasks import Task, TaskStore

ReadOnlyHandler = Callable[[dict[str, Any], asyncio.Event], Awaitable[dict[str, Any]]]
InputValidator = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    kind: str
    handler: ReadOnlyHandler
    risk: str = "read_only"
    provenance: str = "local.read_only"
    validate: InputValidator | None = None


class WorkerDispatcher:
    def __init__(self, tasks: TaskStore) -> None:
        self.tasks = tasks
        self._tools: dict[str, ToolSpec] = {}
        self._cancel: dict[str, asyncio.Event] = {}

    def register(self, spec: ToolSpec) -> None:
        if not spec.kind.strip() or spec.risk != "read_only":
            raise ValueError("only named read_only tools may be registered")
        if spec.kind in self._tools:
            raise ValueError("tool already registered")
        self._tools[spec.kind] = spec

    def registered(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def spec(self, kind: str) -> ToolSpec | None:
        return self._tools.get(kind)

    def validate(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        spec = self._tools.get(kind)
        if spec is None:
            raise ValueError("task kind is not registered")
        if not isinstance(payload, dict):
            raise ValueError("task payload must be an object")
        return spec.validate(payload) if spec.validate else payload

    async def run(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        spec = self._tools.get(task.kind)
        if spec is None:
            return self.tasks.transition(task_id, "blocked", error="tool kind is not registered")
        if task.state != "queued":
            raise ValueError("only queued tasks can be dispatched")
        cancel = asyncio.Event()
        self._cancel[task_id] = cancel
        self.tasks.transition(task_id, "running")
        try:
            result = await spec.handler(task.payload, cancel)
            if cancel.is_set():
                current = self.tasks.get(task_id)
                return current if current.state == "cancelled" else self.tasks.cancel(task_id)
            return self.tasks.transition(task_id, "done", result=result)
        except asyncio.CancelledError:
            cancel.set()
            if self.tasks.get(task_id).state not in {"cancelled", "done", "failed"}:
                return self.tasks.cancel(task_id)
            raise
        except Exception as exc:  # worker failures are durable, not process-fatal
            return self.tasks.transition(task_id, "failed", error=str(exc)[:500])
        finally:
            self._cancel.pop(task_id, None)

    def cancel(self, task_id: str) -> bool:
        event = self._cancel.get(task_id)
        if event is None:
            return False
        event.set()
        return True


async def inventory_scan_tool(payload: dict[str, Any], cancel: asyncio.Event) -> dict[str, Any]:
    """Read metadata only; never accepts arbitrary roots from task payload."""
    limit = max(1, min(int(payload.get("limit", 2000)), 2000))
    db_path = payload.get("db_path")
    if not isinstance(db_path, str) or not db_path:
        raise ValueError("inventory scan requires an internal database path")
    db = __import__("pathlib").Path(db_path)
    roots = configured_roots(db)
    result = await asyncio.to_thread(refresh, roots, db, limit=limit)
    if cancel.is_set():
        return {"cancelled": True}
    return result


def validate_inventory_scan(payload: dict[str, Any]) -> dict[str, Any]:
    """Accept only bounded scan controls; the database path is server-owned."""
    unknown = set(payload) - {"limit", "db_path"}
    if unknown:
        raise ValueError("unsupported inventory.scan fields")
    if "db_path" not in payload:
        raise ValueError("inventory scan requires an internal database path")
    try:
        limit = int(payload.get("limit", 2000))
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if not 1 <= limit <= 2000:
        raise ValueError("limit must be between 1 and 2000")
    return {"limit": limit, "db_path": payload["db_path"]}


def default_dispatcher(tasks: TaskStore) -> WorkerDispatcher:
    dispatcher = WorkerDispatcher(tasks)
    dispatcher.register(ToolSpec("inventory.scan", inventory_scan_tool, validate=validate_inventory_scan))
    return dispatcher
