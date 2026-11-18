"""Quota-aware, Guardian-compatible local inference generation admission."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass

from jarvis_v2.core.budget import ResourceBudget


PRIORITIES = ("P0", "P1", "P2", "P3", "P4", "P5")
MODES = frozenset({"interactive", "batch"})


class GenerationSchedulerError(ValueError):
    """Raised when a generation request violates scheduler fencing."""


@dataclass(frozen=True)
class GenerationRequest:
    task_id: str
    generation: int
    priority: str = "P3"
    mode: str = "batch"
    device: str = "default"
    guardian: bool = False
    compatible_slots: tuple[str, ...] | None = None


@dataclass(frozen=True)
class GenerationLease:
    request_id: str
    task_id: str
    generation: int
    priority: str
    mode: str
    device: str
    slot: str
    guardian: bool


class GenerationScheduler:
    """Admit at most one active generation per task under shared capacity.

    Interactive and batch work share ``ResourceBudget``.  P0 is selected before
    lower priorities, interactive work breaks equal-priority ties, and a
    pending Guardian reservation remains compatible with the same policy.
    """

    def __init__(
        self,
        quota_units: int,
        *,
        slots: Iterable[str] = ("cpu",),
        device_limits: Mapping[str, int] | None = None,
    ) -> None:
        if type(quota_units) is not int or quota_units < 0:
            raise GenerationSchedulerError("quota must be a non-negative integer")
        configured_slots = tuple(slots)
        self._budget = ResourceBudget(len(configured_slots), slots=configured_slots, device_limits=device_limits)
        self._quota_remaining = quota_units
        self._pending: dict[str, GenerationRequest] = {}
        self._active: dict[str, GenerationLease] = {}

    @property
    def quota_remaining(self) -> int:
        return self._quota_remaining

    def submit(self, request: GenerationRequest) -> str:
        self._validate_request(request)
        request_id = f"{request.task_id}:g{request.generation}"
        existing = self._pending.get(request_id) or self._active.get(request_id)
        if existing is not None:
            if existing != request and not isinstance(existing, GenerationLease):
                raise GenerationSchedulerError("generation request conflicts with existing work")
            return request_id
        for item in (*self._pending.values(), *self._active.values()):
            if item.task_id == request.task_id and item.generation != request.generation:
                raise GenerationSchedulerError("only one generation may be active per task")
        self._pending[request_id] = request
        if request.guardian:
            self._budget.guardian_request(request.compatible_slots)
        return request_id

    def claim_next(self) -> GenerationLease | None:
        if self._quota_remaining < 1:
            return None
        ordered = sorted(
            self._pending.items(),
            key=lambda item: (PRIORITIES.index(item[1].priority), item[1].mode != "interactive", item[0]),
        )
        for request_id, request in ordered:
            owner = request_id
            slot = self._budget.claim(
                owner,
                device=request.device,
                compatible_slots=request.compatible_slots,
                guardian=request.guardian,
            )
            if slot is None:
                continue
            lease = GenerationLease(
                request_id=request_id,
                task_id=request.task_id,
                generation=request.generation,
                priority=request.priority,
                mode=request.mode,
                device=request.device,
                slot=slot,
                guardian=request.guardian,
            )
            del self._pending[request_id]
            self._active[request_id] = lease
            self._quota_remaining -= 1
            return lease
        return None

    def finish(self, lease: GenerationLease) -> None:
        if not isinstance(lease, GenerationLease) or self._active.get(lease.request_id) != lease:
            raise GenerationSchedulerError("stale generation lease")
        self._budget.finish(lease.request_id, lease.slot, device=lease.device)
        del self._active[lease.request_id]

    def snapshot(self) -> dict[str, object]:
        return {
            "quota_remaining": self._quota_remaining,
            "pending": [asdict(item) for item in self._pending.values()],
            "active": [asdict(item) for item in self._active.values()],
            "guardian_pending": self._budget.guardian_pending,
        }

    @staticmethod
    def _validate_request(request: GenerationRequest) -> None:
        if not isinstance(request, GenerationRequest):
            raise GenerationSchedulerError("generation request is required")
        if not isinstance(request.task_id, str) or not request.task_id or any(ord(c) < 32 for c in request.task_id):
            raise GenerationSchedulerError("task id is invalid")
        if type(request.generation) is not int or request.generation < 1:
            raise GenerationSchedulerError("generation is invalid")
        if request.priority not in PRIORITIES or request.mode not in MODES:
            raise GenerationSchedulerError("priority or mode is invalid")
        if not isinstance(request.device, str) or not request.device:
            raise GenerationSchedulerError("device is invalid")
        if request.compatible_slots is not None and isinstance(request.compatible_slots, str):
            raise GenerationSchedulerError("compatible slots are invalid")


__all__ = ["GenerationLease", "GenerationRequest", "GenerationScheduler", "GenerationSchedulerError"]
