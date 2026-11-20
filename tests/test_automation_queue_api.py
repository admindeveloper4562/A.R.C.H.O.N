import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis_v2.automation.queue_api import (
    MAX_LEASE_ATTEMPTS,
    LEGACY_SCHEMA,
    SCHEMA,
    CoordinatorQueue,
    QueueApiError,
    QueueEnvelope,
    QueueSchemaError,
    detect_schema,
)
from tests.queue_admission import enqueue_approved, signed_admission


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
                enqueue_approved(queue, task_id="AUTO-002", priority="P1", module="automation", payload={"n": 1})
            self.assertEqual(detect_schema(path), LEGACY_SCHEMA)
            with CoordinatorQueue.open(path) as queue:
                self.assertEqual(queue.source_schema, LEGACY_SCHEMA)
                self.assertEqual(queue.status()[0]["id"], "AUTO-002")
                self.assertEqual(queue.history("AUTO-002")[0]["kind"], "pending")

    def test_lease_completion_and_duplicate_enqueue_preserve_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                item = enqueue_approved(queue, task_id="AUTO-004", priority="P1", module="automation", payload={})
                with self.assertRaises(ValueError):
                    enqueue_approved(queue, task_id="AUTO-004", priority="P1", module="automation", payload={})
                leased = queue.lease_next()
                self.assertEqual(leased.task_id, item.task_id)
                queue.complete(leased, ok=True, receipt="verified")
                self.assertEqual(queue.status()[0]["state"], "completed")

    def test_reopen_requeues_expired_lease_and_duplicate_receipt_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            now = [100.0]
            queue = CoordinatorQueue.open(path, clock=lambda: now[0])
            enqueue_approved(queue, task_id="AUTO-007", priority="P1", module="automation", payload={})
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
                enqueue_approved(queue, task_id="AUTO-008", priority="P1", module="automation", payload={})
                for attempt in range(MAX_LEASE_ATTEMPTS):
                    leased = queue.lease_next(lease_seconds=1)
                    self.assertIsNotNone(leased)
                    now[0] += 2
                    ready = queue.eligible()
                    self.assertEqual(bool(ready), attempt < MAX_LEASE_ATTEMPTS - 1)
                self.assertEqual(queue.status()[0]["state"], "failed")
                self.assertEqual(queue.history("AUTO-008")[-1]["kind"], "failed")


    def test_bounded_attempts_include_released_handoffs(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                enqueue_approved(queue, task_id="AUTO-011", priority="P1", module="automation", payload={})
                for attempt in range(MAX_LEASE_ATTEMPTS):
                    leased = queue.lease_next()
                    self.assertIsNotNone(leased)
                    queue.release(leased, reason="handoff_retry")
                    self.assertEqual(bool(queue.eligible()), attempt < MAX_LEASE_ATTEMPTS - 1)
                self.assertEqual(queue.status()[0]["state"], "failed")
                self.assertEqual(queue.history("AUTO-011")[-1]["kind"], "failed")


    def test_pending_task_cancellation_is_durable_and_leased_task_is_protected(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                enqueue_approved(queue, task_id="AUTO-009", priority="P1", module="automation", payload={})
                approval = {"approval_id": "owner-cancel", "signature": "signed-document"}
                cancelled = queue.cancel("AUTO-009", approval=approval)
                self.assertEqual(cancelled["state"], "cancelled")
                self.assertEqual(queue.cancel("AUTO-009", approval=approval), cancelled)
                self.assertEqual(queue.status()[0]["state"], "cancelled")
                event = queue.history("AUTO-009")[-1]
                self.assertEqual(event["kind"], "cancelled")
                detail = queue._queue.db.execute(
                    "SELECT detail FROM events WHERE task_id=? AND kind='cancelled'",
                    ("AUTO-009",),
                ).fetchone()[0]
                self.assertEqual(json.loads(detail)["approval"], approval)
                enqueue_approved(queue, task_id="AUTO-010", priority="P1", module="automation", payload={})
                queue.lease_next()
                with self.assertRaisesRegex(ValueError, "only pending tasks"):
                    queue.cancel("AUTO-010", approval=approval)

    def test_enqueue_requires_trusted_signature_bound_to_the_task(self):
        task = {"task_id": "AUTO-012", "priority": "P1", "module": "automation", "payload": {"n": 1}}
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                with self.assertRaisesRegex(QueueApiError, "approval is required"):
                    queue.enqueue(**task)
                approval = signed_admission(**task, trusted_signer=False)
                with self.assertRaisesRegex(QueueApiError, "approval is invalid"):
                    queue.enqueue(**task, approval=approval)
                approval = signed_admission(**task)
                with self.assertRaisesRegex(QueueApiError, "approval is invalid"):
                    queue.enqueue(**{**task, "payload": {"n": 2}}, approval=approval)
                self.assertEqual(queue.status(), [])
                accepted = enqueue_approved(queue, **task)
                self.assertEqual(accepted.task_id, task["task_id"])

    def test_raw_unsigned_queue_insert_is_failed_before_it_can_be_leased(self):
        with tempfile.TemporaryDirectory() as directory:
            with CoordinatorQueue.open(Path(directory) / "queue.sqlite") as queue:
                queue._queue.add(
                    task_id="AUTO-013", priority="P1", module="automation", payload={},
                )
                with patch.dict(os.environ, {}, clear=True):
                    with self.assertRaisesRegex(QueueApiError, "owner key store is not configured"):
                        queue.lease_next()
                    self.assertEqual(queue.status()[0]["state"], "pending")
                self.assertIsNone(queue.lease_next())
                self.assertEqual(queue.status()[0]["state"], "failed")
                detail = queue._queue.db.execute(
                    "SELECT detail FROM events WHERE task_id=? AND kind='failed'",
                    ("AUTO-013",),
                ).fetchone()[0]
                self.assertEqual(detail, "task_admission_invalid")


if __name__ == "__main__":
    unittest.main()
