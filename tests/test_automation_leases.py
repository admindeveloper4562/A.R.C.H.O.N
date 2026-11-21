import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.queue_api import CoordinatorQueue, QueueApiError, QueueEnvelope
from tests.queue_admission import enqueue_approved


class CoordinatorLeaseTests(unittest.TestCase):
    def setUp(self):
        self.now = [100.0]

    def test_renewal_extends_a_live_lease_and_completion_is_idempotent(self):
        with CoordinatorQueue.open(Path(tempfile.mkdtemp()) / "queue.sqlite", clock=lambda: self.now[0]) as queue:
            enqueue_approved(queue, task_id="AUTO-004", priority="P1", module="automation", payload={})
            item = queue.lease_next(lease_seconds=5)
            renewed = queue.renew(item, lease_seconds=20)
            self.now[0] += 10
            first = queue.complete(renewed, ok=True, receipt="done")
            self.assertEqual(queue.complete(renewed, ok=True, receipt="done"), first)

    def test_expired_lease_is_requeued_and_old_owner_cannot_complete(self):
        with CoordinatorQueue.open(Path(tempfile.mkdtemp()) / "queue.sqlite", clock=lambda: self.now[0]) as queue:
            enqueue_approved(queue, task_id="AUTO-004", priority="P1", module="automation", payload={})
            item = queue.lease_next(lease_seconds=5)
            self.now[0] += 6
            with self.assertRaises(QueueApiError):
                queue.complete(item, ok=True, receipt="late")
            replacement = queue.lease_next(lease_seconds=5)
            self.assertNotEqual(replacement.lease, item.lease)

    def test_stale_or_invalid_renewals_do_not_change_the_queue(self):
        with CoordinatorQueue.open(Path(tempfile.mkdtemp()) / "queue.sqlite", clock=lambda: self.now[0]) as queue:
            enqueue_approved(queue, task_id="AUTO-004", priority="P1", module="automation", payload={})
            item = queue.lease_next(lease_seconds=5)
            with self.assertRaises(QueueApiError):
                queue.renew(item, lease_seconds=0)
            with self.assertRaises(QueueApiError):
                queue.complete(
                    QueueEnvelope(item.task_id, item.priority, item.module, item.payload, "foreign-lease"),
                    ok=True,
                    receipt="wrong",
                )
            self.assertEqual(queue.status()[0]["state"], "leased")


if __name__ == "__main__":
    unittest.main()
