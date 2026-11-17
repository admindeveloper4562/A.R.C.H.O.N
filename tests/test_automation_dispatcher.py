import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.dispatcher import ReconnectDispatcher
from jarvis_v2.automation.queue_api import CoordinatorQueue
from jarvis_v2.backend import NodeRoute


def payload(task_id: str) -> dict[str, object]:
    return {
        "job_id": f"job-{task_id}",
        "idempotency_key": f"idem-{task_id}",
        "operation": "summarize",
        "input_sha256": "a" * 64,
        "required_scope": "public_metadata",
        "deadline_at": 1_000,
        "task_id": task_id,
    }


class ReconnectDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "queue.sqlite"
        self.queue = CoordinatorQueue.open(self.path, clock=lambda: 100.0)
        self.queue.enqueue(task_id="AUTO-007-job", priority="P1", module="automation", payload=payload("AUTO-007"))
        self.calls = []

    def tearDown(self):
        self.queue.close()

    def test_offline_host_leaves_job_pending_without_handoff(self):
        dispatcher = ReconnectDispatcher(
            self.queue,
            route=lambda job: NodeRoute("blocked", None, None, "no_compatible_node"),
            handoff=lambda *args: self.calls.append(args) or True,
        )
        result = dispatcher.drain()
        self.assertEqual((result[0].status, result[0].reason), ("deferred", "no_compatible_node"))
        self.assertEqual(self.calls, [])
        self.assertEqual(self.queue.status()[0]["state"], "pending")

    def test_online_host_with_capacity_is_the_only_dispatch_path(self):
        dispatcher = ReconnectDispatcher(
            self.queue,
            route=lambda job: NodeRoute("routed", "windows-1", "qwen3-8b", "capabilities_satisfied"),
            handoff=lambda item, job, target: self.calls.append((item, job, target)) or True,
        )
        result = dispatcher.drain()
        self.assertEqual((result[0].status, result[0].node_id), ("dispatched", "windows-1"))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.queue.status()[0]["state"], "leased")

    def test_failed_handoff_is_requeued_and_can_retry(self):
        dispatcher = ReconnectDispatcher(
            self.queue,
            route=lambda job: NodeRoute("routed", "windows-1", "qwen3-8b", "capabilities_satisfied"),
            handoff=lambda *args: False,
        )
        result = dispatcher.drain()
        self.assertEqual((result[0].status, result[0].reason), ("deferred", "handoff_retry"))
        self.assertEqual(self.queue.status()[0]["state"], "pending")

    def test_invalid_job_payload_is_not_claimed(self):
        self.queue.enqueue(task_id="AUTO-007-invalid", priority="P2", module="automation", payload={})
        dispatcher = ReconnectDispatcher(
            self.queue,
            route=lambda job: NodeRoute("routed", "windows-1", "qwen3-8b", "capabilities_satisfied"),
            handoff=lambda *args: True,
        )
        result = dispatcher.drain(limit=2)
        self.assertEqual(result[1].reason, "invalid_job_payload")
        self.assertEqual(self.queue.status()[1]["state"], "pending")


if __name__ == "__main__":
    unittest.main()
