import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core.queue import TaskQueue


class AtlasCoreEventHistoryTests(unittest.TestCase):
    def test_history_is_ordered_bounded_and_excludes_private_values(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(
                task_id="CORE-301",
                priority="P2",
                module="core",
                payload={"private": "model prompt"},
            )
            leased = queue.lease_next()
            queue.finish("CORE-301", leased["lease"], ok=True, receipt="private receipt")

            history = queue.history("CORE-301", limit=2)

            self.assertEqual([entry["kind"] for entry in history], ["pending", "leased"])
            self.assertEqual([entry["seq"] for entry in history], sorted(entry["seq"] for entry in history))
            self.assertEqual(set(history[0]), {"seq", "task_id", "kind"})
            self.assertNotIn("private", str(history))
            self.assertNotIn("receipt", str(history))
            queue.close()

    def test_history_for_unknown_task_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            self.assertEqual(queue.history("missing"), [])
            queue.close()

    def test_duplicate_completion_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-301", priority="P2", module="core", payload={})
            leased = queue.lease_next()
            queue.finish("CORE-301", leased["lease"], ok=True, receipt="receipt")
            with self.assertRaises(ValueError):
                queue.finish("CORE-301", leased["lease"], ok=True, receipt="duplicate")
            queue.close()


if __name__ == "__main__":
    unittest.main()
