import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import EventSessionError
from jarvis_v2.core.queue import TaskQueue


class CoreEventSessionTests(unittest.TestCase):
    def test_event_session_is_separate_and_reconstructs_causal_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="CORE-005", priority="P1", module="core", payload={})
            task_session = queue.open_session("CORE-005")
            first = queue.event_session.emit(
                "CORE-005", "decision", "private detail", correlation_id="corr-1"
            )
            second = queue.event_session.emit(
                "CORE-005", "handoff", "another private detail", correlation_id="corr-1"
            )
            self.assertNotEqual(task_session["session_id"], first["session_id"])
            self.assertEqual(second["causation_id"], first["event_id"])
            self.assertNotIn("private detail", str(queue.event_session.causal_chain("corr-1")))
            queue.close()

            reopened = TaskQueue(path)
            chain = reopened.event_session.causal_chain("corr-1")
            self.assertEqual([item["event_id"] for item in chain], [first["event_id"], second["event_id"]])
            self.assertEqual(chain[1]["causation_id"], chain[0]["event_id"])
            reopened.close()

    def test_event_replay_ack_is_durable_and_event_ids_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-005", priority="P1", module="core", payload={})
            event = queue.event_session.emit("CORE-005", "decision", "detail", event_id="event-1")
            self.assertEqual(queue.event_session.emit("CORE-005", "decision", "detail", event_id="event-1"), event)
            pending = queue.event_session.interpret()
            self.assertIn(event["event_id"], [item["event_id"] for item in pending])
            for item in pending:
                queue.event_session.ack(item["seq"])
                queue.event_session.ack(item["seq"])
            self.assertEqual(queue.event_session.replay(), [])
            with self.assertRaises(EventSessionError):
                queue.event_session.emit("CORE-005", "decision", "different", event_id="event-1")
            queue.close()

    def test_event_session_rejects_unbounded_detail_and_invalid_replay_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-005", priority="P1", module="core", payload={})
            with self.assertRaises(EventSessionError):
                queue.event_session.emit("CORE-005", "decision", "x" * 20_000)
            with self.assertRaises(EventSessionError):
                queue.event_session.replay(limit=0)
            queue.close()


if __name__ == "__main__":
    unittest.main()
