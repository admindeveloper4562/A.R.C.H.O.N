import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import DispatchError
from jarvis_v2.core.queue import TaskQueue


class CoreFaultInjectionTests(unittest.TestCase):
    def test_committed_completion_survives_reopen_without_phantom_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="COMMITTED", priority="P1", module="core", payload={})
            queue.add(task_id="NEXT", priority="P1", module="core", payload={})
            lease = queue.lease_next()["lease"]
            queue.finish("COMMITTED", lease, ok=True, receipt="committed")
            queue.close()

            reopened = TaskQueue(path)
            self.assertEqual(reopened.status()[0]["state"], "completed")
            with self.assertRaises(ValueError):
                reopened.finish("COMMITTED", lease, ok=True, receipt="duplicate")
            self.assertEqual(reopened.lease_next()["id"], "NEXT")
            reopened.close()

    def test_priority_fifo_is_stable_after_a_failed_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            for task_id, priority in (("P1-A", "P1"), ("P0", "P0"), ("P1-B", "P1")):
                queue.add(task_id=task_id, priority=priority, module="core", payload={})
            first = queue.lease_next()
            self.assertEqual(first["id"], "P0")
            queue.finish(first["id"], first["lease"], ok=False, receipt="injected_failure")
            self.assertEqual(queue.lease_next()["id"], "P1-A")
            self.assertEqual(queue.lease_next()["id"], "P1-B")
            queue.close()

    def test_dispatch_claim_is_isolated_and_wrong_executor_cannot_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="TASK-A", priority="P1", module="core", payload={})
            queue.add(task_id="TASK-B", priority="P1", module="core", payload={})
            queue.dispatch("TASK-A", "backend", "read", "ack", correlation_id="corr-a", dispatch_id="dispatch-a")
            claimed = queue.claim_dispatch("dispatch-a", "executor-a", claim_id="claim-a")
            with self.assertRaises(DispatchError):
                queue.acknowledge_dispatch(
                    "dispatch-a", "executor-b", "claim-a", status="completed", result={}
                )
            acknowledged = queue.acknowledge_dispatch(
                "dispatch-a", "executor-a", claimed["claim_id"], status="completed", result={"ok": True}
            )
            self.assertEqual(acknowledged["ack"]["status"], "completed")
            self.assertEqual(queue.restore_dispatch("dispatch-a")["task_id"], "TASK-A")
            queue.close()


if __name__ == "__main__":
    unittest.main()
