import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.queue_api import (
    MAX_LEASE_ATTEMPTS,
    LEGACY_SCHEMA,
    SCHEMA,
    CoordinatorQueue,
    QueueEnvelope,
    QueueSchemaError,
    detect_schema,
)


class CoordinatorQueueTests(unittest.TestCase):
    def test_versioned_envelope_round_trip_and_unknown_fields_are_rejected(self):
        item = QueueEnvelope("AUTO-002", "P1", "automation", {"scope": "local"})
        self.assertEqual(QueueEnvelope.loads(item.dumps()), item)
        self.assertEqual(item.to_dict()["schema"], SCHEMA)
        with self.assertRaises(QueueSchemaError):
            QueueEnvelope.from_dict({**item.to_dict(), "schema": "archon-coordinator-queue/2"})
        with self.assertRaises(QueueSchemaError):
            QueueEnvelope.from_dict({**item.to_dict(), "unexpected": True})

    def test_existing_task_queue_reopens_without_migration_or_data_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            with CoordinatorQueue.open(path) as queue:
                queue.enqueue(task_id="AUTO-002", priority="P1", module="automation", payload={"n": 1})
            self.assertEqual(detect_schema(path), LEGACY_SCHEMA)
            with CoordinatorQueue.open(path) as queue:
                self.assertEqual(queue.source_schema, LEGACY_SCHEMA)
                self.assertEqual(queue.status()[0]["id"], "AUTO-002")
                self.assertEqual(queue.history("AUTO-002")[0]["kind"], "pending")

    def test_lease_completion_and_duplicate_enqueue_preserve_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                item = queue.enqueue(task_id="AUTO-004", priority="P1", module="automation", payload={})
                with self.assertRaises(ValueError):
                    queue.enqueue(task_id="AUTO-004", priority="P1", module="automation", payload={})
                leased = queue.lease_next()
                self.assertEqual(leased.task_id, item.task_id)
                queue.complete(leased, ok=True, receipt="verified")
                self.assertEqual(queue.status()[0]["state"], "completed")

    def test_reopen_requeues_expired_lease_and_duplicate_receipt_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            now = [100.0]
            queue = CoordinatorQueue.open(path, clock=lambda: now[0])
            queue.enqueue(task_id="AUTO-007", priority="P1", module="automation", payload={})
            self.assertIsNotNone(queue.lease_next(lease_seconds=10))
            queue.close()

            now[0] = 111.0
            with CoordinatorQueue.open(path, clock=lambda: now[0]) as reopened:
                self.assertEqual(reopened.eligible()[0].task_id, "AUTO-007")
                resumed = reopened.lease_next()
                self.assertEqual(resumed.task_id, "AUTO-007")
                reopened.complete(resumed, ok=True, receipt="verified")
                self.assertEqual(
                    reopened.complete(resumed, ok=True, receipt="verified")["state"],
                    "completed",
                )


    def test_expired_leases_fail_after_bounded_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            now = [100.0]
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite", clock=lambda: now[0]) as queue:
                queue.enqueue(task_id="AUTO-008", priority="P1", module="automation", payload={})
                for attempt in range(MAX_LEASE_ATTEMPTS):
                    leased = queue.lease_next(lease_seconds=1)
                    self.assertIsNotNone(leased)
                    now[0] += 2
                    ready = queue.eligible()
                    self.assertEqual(bool(ready), attempt < MAX_LEASE_ATTEMPTS - 1)
                self.assertEqual(queue.status()[0]["state"], "failed")
                self.assertEqual(queue.history("AUTO-008")[-1]["kind"], "failed")


    def test_pending_task_cancellation_is_durable_and_leased_task_is_protected(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                queue.enqueue(task_id="AUTO-009", priority="P1", module="automation", payload={})
                cancelled = queue.cancel("AUTO-009")
                self.assertEqual(cancelled["state"], "cancelled")
                self.assertEqual(queue.cancel("AUTO-009"), cancelled)
                self.assertEqual(queue.status()[0]["state"], "cancelled")
                self.assertEqual(queue.history("AUTO-009")[-1]["kind"], "cancelled")
                queue.enqueue(task_id="AUTO-010", priority="P1", module="automation", payload={})
                queue.lease_next()
                with self.assertRaisesRegex(ValueError, "only pending tasks"):
                    queue.cancel("AUTO-010")


if __name__ == "__main__":
    unittest.main()
