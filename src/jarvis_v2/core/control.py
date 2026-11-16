"""Durable Core dispatch controls shared by queue instances."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


CONTROL_STATES = frozenset({"running", "paused", "stopped"})
_REASON = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")


class ControlError(ValueError):
    """Raised when a Core control transition is invalid."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class CoreControls:
    """Persist the owner control that gates new task dispatch."""

    def __init__(self, database: Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(Path(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS core_controls (
                control_id INTEGER PRIMARY KEY CHECK (control_id = 1),
                state TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )"""
        )
        self.db.execute(
            """INSERT OR IGNORE INTO core_controls(control_id, state, reason, updated_at)
               VALUES (1, 'running', '', ?)""",
            (_now(),),
        )
        self.db.commit()

    def status(self) -> dict[str, str]:
        row = self.db.execute(
            "SELECT state, reason, updated_at FROM core_controls WHERE control_id=1"
        ).fetchone()
        if row is None:
            raise ControlError("control state is missing")
        return dict(row)

    def allows_dispatch(self) -> bool:
        return self.status()["state"] == "running"

    def stop(self, *, reason: str = "owner_stop") -> dict[str, str]:
        return self._set("stopped", reason)

    def pause(self, *, reason: str = "owner_pause") -> dict[str, str]:
        return self._set("paused", reason)

    def resume(self) -> dict[str, str]:
        return self._set("running", "")

    def _set(self, state: str, reason: str) -> dict[str, str]:
        if state not in CONTROL_STATES:
            raise ControlError("invalid control state")
        if not isinstance(reason, str) or (reason and not _REASON.fullmatch(reason)):
            raise ControlError("invalid control reason")
        with self.db:
            self.db.execute(
                "UPDATE core_controls SET state=?, reason=?, updated_at=? WHERE control_id=1",
                (state, reason, _now()),
            )
        return self.status()

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


__all__ = ["CONTROL_STATES", "ControlError", "CoreControls"]
