"""Bounded reconnect dispatch for approved online local agents."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from jarvis_v2.automation.queue_api import CoordinatorQueue, QueueApiError, QueueEnvelope
from jarvis_v2.backend.windows_agent import LocalAgentJob, NodeRoute


MAX_DRAIN_ITEMS = 100


@dataclass(frozen=True)
class DispatchDecision:
    task_id: str
    status: str
    reason: str
    node_id: str | None = None
    item: QueueEnvelope | None = None


def _job(item: QueueEnvelope) -> LocalAgentJob:
    payload: Mapping[str, Any] = item.payload
    job_id = payload.get("job_id", item.task_id)
    idempotency_key = payload.get("idempotency_key", item.task_id)
    task_id = payload.get("task_id", item.task_id)
    return LocalAgentJob(
        job_id=job_id,
        idempotency_key=idempotency_key,
        operation=payload["operation"],
        input_sha256=payload["input_sha256"],
        required_scope=payload["required_scope"],
        deadline_at=payload["deadline_at"],
        task_id=task_id,
        requested_model=payload.get("requested_model"),
    )


class ReconnectDispatcher:
    """Lease queued work only when an approved host is online and has capacity."""

    def __init__(
        self,
        queue: CoordinatorQueue,
        *,
        route: Callable[[LocalAgentJob], NodeRoute],
        handoff: Callable[[QueueEnvelope, LocalAgentJob, NodeRoute], bool],
    ) -> None:
        self.queue = queue
        self.route = route
        self.handoff = handoff

    def drain(self, *, limit: int = 10) -> list[DispatchDecision]:
        if type(limit) is not int or not 1 <= limit <= MAX_DRAIN_ITEMS:
            raise QueueApiError("drain limit is outside the bounded policy")
        decisions: list[DispatchDecision] = []
        for item in self.queue.eligible()[:limit]:
            try:
                job = _job(item)
            except (KeyError, TypeError, ValueError) as exc:
                decisions.append(DispatchDecision(item.task_id, "deferred", "invalid_job_payload"))
                continue
            target = self.route(job)
            if target.status != "routed" or not target.node_id:
                decisions.append(DispatchDecision(item.task_id, "deferred", target.reason))
                continue
            leased = self.queue.lease_next(allowed_modules={item.module})
            if leased is None or leased.task_id != item.task_id:
                decisions.append(DispatchDecision(item.task_id, "deferred", "queue_not_available"))
                continue
            try:
                accepted = self.handoff(leased, job, target)
            except Exception:
                accepted = False
            if not accepted:
                self.queue.release(leased)
                decisions.append(DispatchDecision(item.task_id, "deferred", "handoff_retry", target.node_id))
                continue
            decisions.append(DispatchDecision(item.task_id, "dispatched", "host_online", target.node_id, leased))
        return decisions


__all__ = ["DispatchDecision", "MAX_DRAIN_ITEMS", "ReconnectDispatcher"]
