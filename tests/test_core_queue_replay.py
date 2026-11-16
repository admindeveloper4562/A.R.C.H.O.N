import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core.queue import MAX_EVENT_BATCH, TaskQueue


class CoreQueueReplayTests(unittest.TestCase):
    def test_events_survive_restart_and_are_replayed_once_after_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="CORE-002", priority="P1", module="core", payload={"private": "hidden"})
            lease = queue.lease_next()["lease"]
            queue.finish("CORE-002", lease, ok=True, receipt="receipt")
            queue.close()

            reopened = TaskQueue(path)
            first = reopened.replay_events("core-session")
            self.assertEqual([event["kind"] for event in first], ["pending", "leased", "completed"])
            self.assertTrue(all(set(event) == {"seq", "task_id", "kind"} for event in first))
            self.assertNotIn("hidden", str(first))
            reopened.close()

            after_restart = TaskQueue(path)
            self.assertEqual(after_restart.replay_events("core-session"), first)
            for event in first:
                after_restart.ack_event("core-session", event["seq"])
                after_restart.ack_event("core-session", event["seq"])
            self.assertEqual(after_restart.replay_events("core-session"), [])
            after_restart.close()

    def test_replay_is_consumer_scoped_and_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            for index in range(MAX_EVENT_BATCH + 1):
                queue.add(task_id=f"CORE-{index}", priority="P4", module="core", payload={})
            self.assertEqual(len(queue.replay_events("one", limit=MAX_EVENT_BATCH + 1)), MAX_EVENT_BATCH)
            self.assertEqual(len(queue.replay_events("two", limit=1)), 1)
            with self.assertRaises(ValueError):
                queue.ack_event("one", 999999)
            queue.close()


if __name__ == "__main__":
    unittest.main()
