"""Deterministic dependency checks for the Core task queue."""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping


class DependencyError(ValueError):
    """Raised for an invalid dependency declaration."""


class DependencyOrchestrator:
    """Keep pending work behind completed parent dependencies."""

    def __init__(self, database: sqlite3.Connection):
        self.db = database
        self.db.row_factory = sqlite3.Row

    @staticmethod
    def dependencies(payload: Mapping[str, object]) -> tuple[str, ...]:
        if not isinstance(payload, Mapping):
            raise DependencyError("task payload must be an object")
        declared = payload.get("depends_on", payload.get("dependencies", ()))
        if declared is None:
            return ()
        if not isinstance(declared, (list, tuple)):
            raise DependencyError("dependencies must be a list")
        if any(type(item) is not str or not item for item in declared):
            raise DependencyError("dependencies must contain non-empty strings")
        if len(set(declared)) != len(declared):
            raise DependencyError("dependencies must be unique")
        return tuple(declared)

    def ready(self, payload: Mapping[str, object]) -> bool:
        try:
            dependencies = self.dependencies(payload)
        except DependencyError:
            return False
        if not dependencies:
            return True
        placeholders = ",".join("?" for _ in dependencies)
        rows = self.db.execute(
            f"SELECT id,state FROM tasks WHERE id IN ({placeholders})", dependencies
        ).fetchall()
        states = {row["id"]: row["state"] for row in rows}
        return len(states) == len(dependencies) and all(
            states[dependency] == "completed" for dependency in dependencies
        )

    def dependent_ids(self, task_id: str) -> list[str]:
        rows = self.db.execute("SELECT id,payload FROM tasks ORDER BY created_id").fetchall()
        result = []
        for row in rows:
            try:
                payload = json.loads(row["payload"])
                if task_id in self.dependencies(payload):
                    result.append(row["id"])
            except (DependencyError, json.JSONDecodeError):
                continue
        return result
