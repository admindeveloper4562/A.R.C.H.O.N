import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.event_bus import DeliveryError, EventBus, EventBusError


class BackendEventBusTests(unittest.TestCase):
    def test_publish_is_durable_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.sqlite"
            with EventBus(path) as bus:
                first = bus.publish(
                    "task.completed", "core", "task-1", 1, {"state": "done"},
                    correlation_id="corr-1", idempotency_key="effect-1",
                )
                replay = bus.publish(
                    "task.completed", "core", "task-1", 1, {"state": "done"},
                    correlation_id="corr-1", idempotency_key="effect-1",
                )
                self.assertEqual(first.event_id, replay.event_id)
                self.assertEqual([item.event_id for item in bus.pending("backend")], [first.event_id])
            with EventBus(path) as reopened:
                self.assertEqual(reopened.pending("backend")[0].payload, {"state": "done"})

    def test_conflicting_idempotency_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with EventBus(Path(directory) / "events.sqlite") as bus:
                bus.publish("task.updated", "core", "task-1", 1, {"value": 1}, correlation_id="corr", idempotency_key="same")
                with self.assertRaises(EventBusError):
                    bus.publish("task.updated", "core", "task-1", 1, {"value": 2}, correlation_id="corr", idempotency_key="same")

    def test_successful_effect_receipt_prevents_duplicate_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            with EventBus(Path(directory) / "events.sqlite") as bus:
                event = bus.publish("task.completed", "core", "task-1", 1, {"state": "done"}, correlation_id="corr")
                calls = []

                def effect(received):
                    calls.append(received.event_id)
                    return {"accepted": True}

                first = bus.deliver("backend-worker", event.event_id, effect)
                second = bus.deliver("backend-worker", event.event_id, effect)
                self.assertEqual(first, second)
                self.assertEqual(calls, [event.event_id])
                self.assertEqual(bus.pending("backend-worker"), [])

    def test_failed_effect_is_retryable_then_completes(self):
        with tempfile.TemporaryDirectory() as directory:
            with EventBus(Path(directory) / "events.sqlite") as bus:
                event = bus.publish("task.completed", "core", "task-1", 1, {"state": "done"}, correlation_id="corr")
                calls = []

                def failing(received):
                    calls.append(received.event_id)
                    raise RuntimeError("temporary")

                with self.assertRaises(DeliveryError):
                    bus.deliver("backend-worker", event.event_id, failing)
                self.assertEqual([item.event_id for item in bus.pending("backend-worker")], [event.event_id])
                receipt = bus.deliver("backend-worker", event.event_id, lambda received: {"retry": True})
                self.assertEqual(receipt.status, "completed")
                self.assertEqual(calls, [event.event_id])

    def test_invalid_envelopes_are_rejected_before_outbox_write(self):
        with tempfile.TemporaryDirectory() as directory:
            with EventBus(Path(directory) / "events.sqlite") as bus:
                with self.assertRaises(EventBusError):
                    bus.publish("bad event", "core", "task-1", 1, {}, correlation_id="corr")
                with self.assertRaises(EventBusError):
                    bus.publish("event", "core", "task-1", 0, {}, correlation_id="corr")
                with self.assertRaises(EventBusError):
                    bus.publish("event", "core", "task-1", 1, {}, correlation_id="corr", privacy_scope="write")
                self.assertEqual(bus.pending("backend"), [])


if __name__ == "__main__":
    unittest.main()
