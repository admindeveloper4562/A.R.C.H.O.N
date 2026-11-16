import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import (
    MAX_PENDING_EVENTS_PER_CORRELATION,
    EventSessionError,
)
from jarvis_v2.core.queue import TaskQueue


class CoreEventGuardTests(unittest.TestCase):
    def test_duplicate_event_id_is_idempotent_and_storm_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-013", priority="P1", module="core", payload={})
            first = queue.event_session.emit(
                "CORE-013", "progress", "detail", correlation_id="corr-13", event_id="event-13"
            )
            self.assertEqual(
                queue.event_session.emit(
                    "CORE-013", "progress", "detail", correlation_id="corr-13", event_id="event-13"
                ),
                first,
            )
            for index in range(MAX_PENDING_EVENTS_PER_CORRELATION - 1):
                queue.event_session.emit("CORE-013", "progress", f"detail-{index}", correlation_id="corr-13")
            with self.assertRaisesRegex(EventSessionError, "event_backpressure"):
                queue.event_session.emit("CORE-013", "progress", "overflow", correlation_id="corr-13")
            queue.close()

    def test_repeated_failures_quarantine_and_redact_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-013", priority="P1", module="core", payload={})
            for pending in queue.event_session.replay():
                queue.event_session.ack(pending["seq"])
            event = queue.event_session.emit("CORE-013", "work", "event detail", event_id="event-fail")
            first = queue.record_event_failure("event-fail", "worker_error", "private diagnostic")
            second = queue.record_event_failure("event-fail", "worker_error", "private diagnostic")
            third = queue.record_event_failure("event-fail", "worker_error", "private diagnostic")

            self.assertEqual(first["state"], "retry")
            self.assertEqual(second["attempts"], 2)
            self.assertEqual(third["state"], "quarantined")
            self.assertEqual(third["attempts"], 3)
            self.assertNotIn("private diagnostic", str(third))
            self.assertEqual(queue.event_failure(event["event_id"]), third)
            self.assertEqual(queue.event_session.replay(), [])
            chain = queue.event_session.causal_chain("task:CORE-013")
            failed = next(item for item in chain if item["event_id"] == event["event_id"])
            self.assertEqual(failed["failure"], third)
            self.assertEqual(
                queue.record_event_failure("event-fail", "different_code", "new diagnostic"),
                third,
            )
            queue.close()


if __name__ == "__main__":
    unittest.main()
