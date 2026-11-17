"""Bounded offline replay and SQLite restore drills for automation state."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from jarvis_v2.backend.backup import BackupManager, BackupReceipt, RestoreReceipt
from jarvis_v2.backend.event_bus import DeliveryReceipt, EventBus


MAX_REPLAY_EVENTS = 100


class RecoveryDrill:
    """Exercise retained event replay and database restore without live writes."""

    def __init__(self, database: str | Path, *, max_replay_events: int = MAX_REPLAY_EVENTS) -> None:
        if type(max_replay_events) is not int or not 1 <= max_replay_events <= MAX_REPLAY_EVENTS:
            raise ValueError("max_replay_events is outside the bounded policy")
        self.database = Path(database)
        self.max_replay_events = max_replay_events
        self._backups = BackupManager()

    def inspect(self) -> dict[str, Any]:
        """Return bounded, digest-only state for the retained database."""
        return self._backups.inspect(self.database)

    def backup(self, destination: str | Path) -> BackupReceipt:
        """Create a verified backup without overwriting an existing artifact."""
        return self._backups.create(self.database, destination)

    def restore(self, backup: str | Path, destination: str | Path) -> RestoreReceipt:
        """Restore a verified backup into a new destination."""
        return self._backups.restore(backup, destination)

    def replay_pending(
        self,
        consumer: str,
        effect: Callable[[Any], Mapping[str, Any]],
        *,
        limit: int | None = None,
    ) -> list[DeliveryReceipt]:
        """Replay retained events; completed effects remain idempotent no-ops."""
        replay_limit = self.max_replay_events if limit is None else limit
        if type(replay_limit) is not int or not 1 <= replay_limit <= self.max_replay_events:
            raise ValueError("replay limit is outside the bounded policy")
        with EventBus(self.database) as bus:
            events = bus.pending(consumer, limit=replay_limit)
            return [bus.deliver(consumer, event.event_id, effect) for event in events]


__all__ = ["MAX_REPLAY_EVENTS", "RecoveryDrill"]
