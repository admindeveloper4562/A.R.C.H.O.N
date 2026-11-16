import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core.queue import TaskQueue


class CorePriorityTests(unittest.TestCase):
    def test_priority_fifo_and_blocked_work(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="BLOCKED", priority="P0", module="core", payload={})
            queue.add(task_id="URGENT", priority="P0", module="core", payload={})
            queue.add(task_id="FIRST", priority="P1", module="core", payload={})
            queue.add(task_id="SECOND", priority="P1", module="core", payload={})
            queue.add(task_id="LAST", priority="P5", module="core", payload={})
            queue.block("BLOCKED", reason="dependency_wait")

            leased = [queue.lease_next() for _ in range(4)]
            self.assertEqual([item["id"] for item in leased], ["URGENT", "FIRST", "SECOND", "LAST"])
            self.assertIsNone(queue.lease_next())
            self.assertEqual(queue.status()[0]["state"], "blocked")
            queue.close()

    def test_leased_block_requires_current_lease_and_can_reenter_fifo(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="TASK", priority="P2", module="core", payload={})
            lease = queue.lease_next()["lease"]
            with self.assertRaises(ValueError):
                queue.block("TASK", reason="dependency_wait", lease="stale")
            queue.block("TASK", reason="dependency_wait", lease=lease)
            with self.assertRaises(ValueError):
                queue.finish("TASK", lease, ok=True, receipt="late")
            queue.unblock("TASK")
            new_lease = queue.lease_next()["lease"]
            queue.finish("TASK", new_lease, ok=True, receipt="done")
            queue.close()


if __name__ == "__main__":
    unittest.main()
