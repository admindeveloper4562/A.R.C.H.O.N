"""Deterministic, non-preemptive model-slot scheduling for AEGIS."""
from __future__ import annotations

from collections.abc import Iterable


class SlotPriority:
    """Allocate compatible model slots in configured order.

    A Guardian request is a reservation at the next free-slot boundary. It
    never changes an existing holder, and while it is pending no ordinary
    requester may claim a slot. ``start`` retains the original boolean API;
    ``claim`` exposes the slot selected for multi-slot callers.
    """

    def __init__(self, slots: Iterable[str] = ("default",)) -> None:
        configured = tuple(slots)
        if (not configured or
                any(not isinstance(slot, str) or not slot for slot in configured) or
                len(set(configured)) != len(configured)):
            raise ValueError("slots must contain unique non-empty names")
        self._slots = configured
        self._held: dict[str, str] = {}
        self._guardian_slots: frozenset[str] | None = None
        self.active: str | None = None
        self.guardian_pending = False

    @property
    def slots(self) -> tuple[str, ...]:
        return self._slots

    @property
    def held_slots(self) -> dict[str, str]:
        """Return a snapshot, so callers cannot mutate scheduler state."""
        return dict(self._held)

    @property
    def available_slots(self) -> tuple[str, ...]:
        return tuple(slot for slot in self._slots if slot not in self._held)

    def guardian_request(self, compatible_slots: Iterable[str] | None = None) -> None:
        """Queue one Guardian reservation without interrupting active work.

        Repeated requests are idempotent. The first valid request determines
        compatibility until that reservation is claimed.
        """
        requested = self._normalize_slots(compatible_slots)
        if requested is not None and not requested:
            raise ValueError("at least one compatible slot is required")
        if self.guardian_pending:
            return
        self._guardian_slots = requested
        self.guardian_pending = True

    def claim(self, name: str, compatible_slots: Iterable[str] | None = None) -> str | None:
        """Claim the first eligible slot in configured order, or ``None``.

        A failed claim has no state effect; a lower-priority claim cannot
        consume a slot reserved for a waiting Guardian.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("requester name required")
        requested = self._normalize_slots(compatible_slots)

        if name == "guardian":
            if not self.guardian_pending:
                return None
            eligible = self._guardian_slots
        else:
            if self.guardian_pending:
                return None
            eligible = requested

        for slot in self._slots:
            if slot in self._held:
                continue
            if eligible is not None and slot not in eligible:
                continue
            self._held[slot] = name
            if name == "guardian":
                self.guardian_pending = False
                self._guardian_slots = None
            self._sync_compatibility_state()
            return slot
        return None

    def start(self, name: str, compatible_slots: Iterable[str] | None = None) -> bool:
        """Compatibility wrapper returning whether ``name`` started."""
        return self.claim(name, compatible_slots) is not None

    def finish(self, name: str, slot: str | None = None) -> None:
        """Release exactly one slot owned by ``name``; never steal or preempt."""
        if not isinstance(name, str) or not name:
            raise ValueError("requester name required")
        if slot is not None:
            if self._held.get(slot) != name:
                raise ValueError("slot is not held by requester")
            del self._held[slot]
        else:
            owned = [held_slot for held_slot, owner in self._held.items()
                     if owner == name]
            if len(owned) != 1:
                raise ValueError("slot is not held by requester or is ambiguous")
            del self._held[owned[0]]
        self._sync_compatibility_state()

    def _normalize_slots(self, slots: Iterable[str] | None) -> frozenset[str] | None:
        if slots is None:
            return None
        if isinstance(slots, str):
            raise ValueError("compatible slots must be an iterable of slot names")
        try:
            normalized = frozenset(slots)
        except TypeError as exc:
            raise ValueError("compatible slots must be an iterable of slot names") from exc
        if any(not isinstance(slot, str) or not slot for slot in normalized):
            raise ValueError("compatible slots must contain non-empty names")
        unknown = normalized.difference(self._slots)
        if unknown:
            raise ValueError(f"unknown model slot(s): {sorted(unknown)}")
        return normalized

    def _sync_compatibility_state(self) -> None:
        self.active = (next(iter(self._held.values()))
                       if len(self._held) == 1 else None)
