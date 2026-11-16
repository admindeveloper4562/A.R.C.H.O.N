import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import SessionError, TaskSessionStore
from jarvis_v2.core.queue import TaskQueue


class CoreSessionTests(unittest.TestCase):
    def test_parent_session_reconstructs_decisions_handoffs_and_receipts_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            first = queue.open_session(
                "CORE-004",
                context={"base_sha": "c4d01f3", "scope": ["src/jarvis_v2/core/"]},
            )
            queue.record_decision(first["session_id"], "decision-1", {"choice": "durable"})
            queue.record_handoff(first["session_id"], "handoff-1", {"child": "CORE-004.S03"})
            receipt = queue.record_receipt(
                first["session_id"], "effect-1", {"operation": "tests", "exit_code": 0}
            )
            checkpoint = queue.checkpoint_session(
                first["session_id"],
                checkpoint={"child": "CORE-004.S04", "next_sequence": 4},
            )
            self.assertEqual(first["session_id"], queue.open_session("CORE-004")["session_id"])
            self.assertEqual(checkpoint["checkpoint"]["child"], "CORE-004.S04")
            queue.close()

            reopened = TaskQueue(path)
            restored = reopened.restore_session("CORE-004")
            self.assertEqual(restored["session_id"], first["session_id"])
            self.assertEqual(restored["correlation_id"], first["correlation_id"])
            self.assertEqual(restored["context"]["base_sha"], "c4d01f3")
            self.assertEqual([item["kind"] for item in restored["records"]], [
                "decision", "handoff", "receipt", "checkpoint",
            ])
            self.assertEqual(restored["decisions"][0]["payload"]["choice"], "durable")
            self.assertEqual(restored["handoffs"][0]["payload"]["child"], "CORE-004.S03")
            self.assertEqual(restored["receipts"][0]["record_id"], receipt["record_id"])
            reopened.close()

    def test_receipt_and_checkpoint_replays_are_idempotent_and_conflicts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            session = queue.open_session("CORE-004")
            first = queue.record_receipt(session["session_id"], "effect-1", {"ok": True})
            self.assertEqual(first, queue.record_receipt(session["session_id"], "effect-1", {"ok": True}))
            with self.assertRaises(SessionError):
                queue.record_receipt(session["session_id"], "effect-1", {"ok": False})
            state = {"child": "CORE-004.S03"}
            self.assertEqual(
                queue.checkpoint_session(session["session_id"], checkpoint=state),
                queue.checkpoint_session(session["session_id"], checkpoint=state),
            )
            queue.close()

    def test_store_reuses_an_existing_connection_and_bounds_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            store = TaskSessionStore(queue.db)
            with self.assertRaises(SessionError):
                store.open_session("CORE-004", context={"bad": "x" * 40_000})
            with self.assertRaises(SessionError):
                store.restore_session("CORE-004", session_id="other")
            queue.close()


if __name__ == "__main__":
    unittest.main()
