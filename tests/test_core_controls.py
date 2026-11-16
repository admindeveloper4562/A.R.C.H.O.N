import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import ControlError
from jarvis_v2.core.queue import TaskQueue


class CoreControlTests(unittest.TestCase):
    def test_stop_blocks_dispatch_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            queue.add(task_id="CORE-012", priority="P1", module="core", payload={})
            self.assertEqual(queue.stop(reason="owner_stop")["state"], "stopped")
            self.assertIsNone(queue.lease_next())
            self.assertEqual(queue.status()[0]["state"], "pending")
            queue.close()

            reopened = TaskQueue(path)
            self.assertEqual(reopened.control_status()["state"], "stopped")
            self.assertIsNone(reopened.lease_next())
            reopened.resume()
            self.assertIsNotNone(reopened.lease_next())
            reopened.close()

    def test_pause_and_resume_preserve_pending_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite"
            queue = TaskQueue(path)
            request = {
                "request_id": "REQ-012",
                "module": "core",
                "action": "deploy",
                "risk": "ambiguous",
                "priority": "P1",
                "objective": "Review deployment",
                "acceptance": ["record review"],
            }
            pending = queue.submit_intent(request)
            self.assertEqual(pending["status"], "approval_required")
            queue.pause(reason="owner_pause")
            queue.close()

            reopened = TaskQueue(path)
            self.assertEqual(reopened.intents.get("REQ-012")["status"], "approval_required")
            self.assertEqual(reopened.control_status()["state"], "paused")
            reopened.resume()
            approved = reopened.submit_intent(request, approval={
                "approval_id": "approval-012",
                "decision": "APPROVE",
                "intent_sha": pending["intent_sha"],
                "scope": "deploy",
            })
            self.assertEqual(approved["status"], "queued")
            self.assertEqual(reopened.lease_next()["id"], "REQ-012")
            reopened.close()

    def test_control_reason_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            with self.assertRaises(ControlError):
                queue.stop(reason="owner stop")
            queue.close()


if __name__ == "__main__":
    unittest.main()
