"""Non-preemptive inference resource reservation for a local Guardian."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class SlotPriority:
    active: str | None = None
    guardian_pending: bool = False

    def guardian_request(self):
        """Reserve the *next* model slot; never terminate an active generation."""
        self.guardian_pending = True

    def start(self, name: str) -> bool:
        if self.active is not None: return False
        if self.guardian_pending and name != "guardian": return False
        if not name: raise ValueError("requester name required")
        if name == "guardian" and not self.guardian_pending: return False
        self.active = name
        if name == "guardian": self.guardian_pending=False
        return True

    def finish(self, name: str) -> None:
        if self.active != name: raise ValueError("slot is not held by requester")
        self.active = None
