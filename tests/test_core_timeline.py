import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import TimelineError
from jarvis_v2.core.queue import TaskQueue


class CoreTimelineTests(unittest.TestCase):
    def test_timeline_joins_sources_states_and_hashed_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="CORE-010", priority="P1", module="core", payload={
                "private": "not returned",
            }, title="timeline")
            session = queue.open_session("CORE-010")
            queue.record_receipt(session["session_id"], "effect-1", {"ok": True})
            event = queue.event_session.emit("CORE-010", "progress", "private detail")
            dispatch = queue.dispatch(
                "CORE-010", "backend", "backend:read", "result", correlation_id="corr-10",
                dispatch_id="dispatch-10",
            )
            claimed = queue.claim_dispatch("dispatch-10", "backend-1", claim_id="claim-10")
            queue.acknowledge_dispatch(
                "dispatch-10", "backend-1", claimed["claim_id"],
                status="completed", result={"receipt": "private result"},
            )
            lease = queue.lease_next()["lease"]
            queue.finish("CORE-010", lease, ok=True, receipt="private receipt")

            view = queue.timeline("CORE-010")
            self.assertEqual(view["task"]["state"], "completed")
            self.assertEqual(view["source_ids"]["task_id"], "CORE-010")
            self.assertIn(event["event_id"], view["source_ids"]["event_ids"])
            self.assertEqual(view["source_ids"]["dispatch_ids"], [dispatch["dispatch_id"]])
            self.assertTrue(view["outcome"]["receipt_present"])
            self.assertTrue(view["outcome"]["receipt_sha256"])
            self.assertEqual(view["outcome"]["dispatch_acknowledgements"], ["completed"])
            self.assertEqual(view["outcome"]["session_receipts"], 1)
            self.assertNotIn("private detail", str(view))
            self.assertNotIn("private result", str(view))
            self.assertNotIn("private receipt", str(view))
            queue.close()

    def test_progress_is_bounded_and_query_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="CORE-010", priority="P1", module="core", payload={})
            before = queue.db.total_changes
            progress = queue.progress("CORE-010")
            after = queue.db.total_changes

            self.assertEqual(before, after)
            self.assertEqual(progress["state"], "pending")
            self.assertEqual(progress["event_kinds"], {"pending": 1})
            with self.assertRaises(TimelineError):
                queue.timeline("missing")
            with self.assertRaises(TimelineError):
                queue.timeline("CORE-010", limit=0)
            queue.close()


if __name__ == "__main__":
    unittest.main()
