import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import DispatchError
from jarvis_v2.core.queue import TaskQueue


class CoreDispatchTests(unittest.TestCase):
    def test_dispatch_contains_scope_acceptance_and_correlation_and_reconstructs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="CORE-006", priority="P1", module="core", payload={})
            dispatch = queue.dispatch(
                "CORE-006",
                "backend",
                ["backend:read"],
                ["result is acknowledged"],
                correlation_id="corr-6",
                input_refs={"source_sha": "04f9c5e"},
                dispatch_id="dispatch-1",
            )
            self.assertEqual(dispatch["scope"], ["backend:read"])
            self.assertEqual(dispatch["acceptance"], ["result is acknowledged"])
            self.assertEqual(dispatch["correlation_id"], "corr-6")
            queue.close()

            reopened = TaskQueue(path)
            restored = reopened.restore_dispatch("dispatch-1")
            self.assertEqual(restored["status"], "queued")
            self.assertEqual(restored["input_refs"]["source_sha"], "04f9c5e")
            reopened.close()

    def test_one_claim_and_one_ack_are_fenced_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-006", priority="P1", module="core", payload={})
            dispatch = queue.dispatch("CORE-006", "backend", "backend:read", "ack", correlation_id="corr-6", dispatch_id="dispatch-1")
            claimed = queue.claim_dispatch("dispatch-1", "backend-worker", claim_id="claim-1")
            self.assertEqual(queue.claim_dispatch("dispatch-1", "backend-worker", claim_id="claim-1"), claimed)
            with self.assertRaises(DispatchError):
                queue.claim_dispatch("dispatch-1", "other-worker", claim_id="claim-2")
            completed = queue.acknowledge_dispatch(
                "dispatch-1", "backend-worker", "claim-1", status="completed", result={"receipt": "r1"}
            )
            self.assertEqual(
                queue.acknowledge_dispatch(
                    "dispatch-1", "backend-worker", "claim-1", status="completed", result={"receipt": "r1"}
                ),
                completed,
            )
            with self.assertRaises(DispatchError):
                queue.acknowledge_dispatch(
                    "dispatch-1", "backend-worker", "claim-1", status="failed", result={"receipt": "r2"}
                )
            self.assertEqual(queue.restore_dispatch("dispatch-1")["ack"]["status"], "completed")
            queue.close()

    def test_dispatch_payload_conflicts_and_unbounded_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-006", priority="P1", module="core", payload={})
            queue.dispatch("CORE-006", "backend", ["backend:read"], "ack", correlation_id="corr-6", dispatch_id="dispatch-1")
            with self.assertRaises(DispatchError):
                queue.dispatch("CORE-006", "backend", ["backend:write"], "ack", correlation_id="corr-6", dispatch_id="dispatch-1")
            with self.assertRaises(DispatchError):
                queue.dispatch("CORE-006", "backend", "x" * 20_000, "ack", correlation_id="corr-6")
            queue.close()


if __name__ == "__main__":
    unittest.main()
