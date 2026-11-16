import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import IntentError
from jarvis_v2.core.queue import TaskQueue


def intent(*, request_id="REQ-1", risk="safe", action="inspect", **extra):
    value = {
        "request_id": request_id,
        "module": "core",
        "action": action,
        "risk": risk,
        "priority": "P2",
        "objective": "Inspect the current state",
        "acceptance": ["record a bounded result"],
        "payload": {"source": "owner"},
    }
    value.update(extra)
    return value


class CoreIntentTests(unittest.TestCase):
    def test_safe_owner_intent_is_idempotently_enqueued(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            first = queue.submit_intent(intent())
            second = queue.submit_intent(intent())
            self.assertEqual(first, second)
            self.assertEqual(first["status"], "queued")
            self.assertEqual([item["id"] for item in queue.eligible()], ["REQ-1"])
            queue.close()

    def test_ambiguous_or_sensitive_intent_waits_for_exact_explicit_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            request = intent(request_id="REQ-2", risk="ambiguous", action="deploy")
            pending = queue.submit_intent(request)
            self.assertEqual(pending["status"], "approval_required")
            self.assertEqual(queue.eligible(), [])
            with self.assertRaises(IntentError):
                queue.submit_intent(request, approval={"approval_id": "ap-1", "decision": "APPROVE", "intent_sha": "wrong", "scope": "deploy"})
            approved = queue.submit_intent(request, approval={"approval_id": "ap-1", "decision": "APPROVE", "intent_sha": pending["intent_sha"], "scope": "deploy"})
            self.assertEqual(approved["status"], "queued")
            self.assertEqual(approved["approval"]["decision"], "APPROVE")
            self.assertEqual(queue.eligible()[0]["id"], "REQ-2")
            queue.close()

    def test_rejected_sensitive_intent_is_recorded_without_a_task(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            request = intent(request_id="REQ-3", risk="sensitive", action="delete")
            pending = queue.submit_intent(request)
            result = queue.submit_intent(request, approval={"approval_id": "ap-3", "decision": "REJECT", "intent_sha": pending["intent_sha"], "scope": "delete"})
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(queue.eligible(), [])
            self.assertEqual(queue.intents.get("REQ-3")["approval"]["decision"], "REJECT")
            queue.close()

    def test_intent_conflicts_and_invalid_contracts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.submit_intent(intent())
            with self.assertRaises(IntentError):
                queue.submit_intent(intent(objective="different"))
            with self.assertRaises(IntentError):
                queue.submit_intent(intent(request_id="REQ-4", acceptance=[]))
            queue.close()


if __name__ == "__main__":
    unittest.main()
