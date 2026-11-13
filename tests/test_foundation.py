import json
import tempfile
import unittest
from pathlib import Path
from jarvis_v2.core.queue import TaskQueue
from jarvis_v2.guardian.priority import SlotPriority
from jarvis_v2.guardian.release import inspect
from jarvis_v2.sda.handoff import HandoffEvidence

class FoundationTests(unittest.TestCase):
    def test_fifo_same_priority(self):
        with tempfile.TemporaryDirectory() as d:
            q=TaskQueue(Path(d)/"db.sqlite")
            q.add(task_id="B",priority="P4",module="runtime",payload={})
            q.add(task_id="A",priority="P4",module="runtime",payload={})
            self.assertEqual(q.lease_next()["id"],"B")
            self.assertEqual(q.lease_next()["id"],"A")
            q.close()
    def test_priority(self):
        with tempfile.TemporaryDirectory() as d:
            q=TaskQueue(Path(d)/"db.sqlite")
            q.add(task_id="low",priority="P5",module="research",payload={})
            q.add(task_id="high",priority="P0",module="guardian",payload={})
            self.assertEqual(q.lease_next()["id"],"high")
            q.close()
    def test_lease_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            q=TaskQueue(Path(d)/"db.sqlite")
            q.add(task_id="t1",priority="P3",module="sda",payload={})
            item=q.lease_next()
            with self.assertRaises(ValueError):q.finish("t1","stale",ok=True,receipt="proof")
            q.finish("t1",item["lease"],ok=True,receipt="proof")
            with self.assertRaises(ValueError):q.finish("t1",item["lease"],ok=True,receipt="duplicate")
            self.assertEqual(q.status()[0]["state"],"completed")
            q.close()
    def test_guardian_waits_for_active(self):
        s=SlotPriority()
        self.assertTrue(s.start("worker"))
        s.guardian_request()
        self.assertFalse(s.start("guardian"))
        s.finish("worker")
        self.assertFalse(s.start("worker"))
        self.assertTrue(s.start("guardian"))
        s.finish("guardian")
        self.assertTrue(s.start("worker"))
    def test_guardian_waiting_blocks_background_claim(self):
        with tempfile.TemporaryDirectory() as d:
            q=TaskQueue(Path(d)/"db.sqlite")
            q.add(task_id="t2",priority="P5",module="runtime",payload={})
            q.add(task_id="g1",priority="P1",module="guardian",payload={})
            self.assertEqual(q.lease_next(guardian_waiting=True)["id"],"g1")
            self.assertIsNone(q.lease_next(guardian_waiting=True))
            q.close()
    def test_release_example_blocked(self):
        f=Path(__file__).resolve().parents[1]/"examples/release-candidate.example.json"
        result=inspect(f)
        self.assertFalse(result["eligible_for_independent_review"])
        self.assertFalse(result["deployment_performed"])
    def test_handoff_requires_every_gate(self):
        self.assertFalse(HandoffEvidence().report()["ready_for_controlled_cutover"])
        self.assertTrue(HandoffEvidence(*([True]*8)).report()["ready_for_controlled_cutover"])
        self.assertFalse(HandoffEvidence(*([True]*8)).report()["actual_cutover_performed"])
if __name__=="__main__":unittest.main()
