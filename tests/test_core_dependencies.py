import tempfile
import unittest
from pathlib import Path

from jarvis_v2.core import DependencyError, DependencyOrchestrator
from jarvis_v2.core.queue import TaskQueue


class CoreDependencyTests(unittest.TestCase):
    def test_pending_dependency_does_not_block_ready_work_and_resumes_after_result(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="DEPENDENT", priority="P0", module="backend", payload={"depends_on": ["ROOT"]})
            queue.add(task_id="ROOT", priority="P1", module="core", payload={})
            self.assertEqual([item["id"] for item in queue.eligible()], ["ROOT"])
            lease = queue.lease_next()["lease"]
            queue.finish("ROOT", lease, ok=True, receipt="root-complete")
            self.assertEqual(queue.lease_next()["id"], "DEPENDENT")
            queue.close()

    def test_missing_and_cyclic_dependencies_are_not_claimed(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="MISSING", priority="P0", module="core", payload={"dependencies": ["NOPE"]})
            queue.add(task_id="A", priority="P1", module="core", payload={"depends_on": ["B"]})
            queue.add(task_id="B", priority="P1", module="core", payload={"depends_on": ["A"]})
            self.assertEqual(queue.eligible(), [])
            self.assertIsNone(queue.lease_next())
            queue.close()

    def test_dependency_declarations_are_validated_and_dependents_are_discoverable(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = TaskQueue(Path(directory) / "queue.sqlite")
            queue.add(task_id="ROOT", priority="P1", module="core", payload={})
            queue.add(task_id="CHILD", priority="P1", module="core", payload={"depends_on": ["ROOT"]})
            self.assertEqual(queue.dependencies.dependent_ids("ROOT"), ["CHILD"])
            with self.assertRaises(DependencyError):
                DependencyOrchestrator.dependencies({"depends_on": ["ROOT", "ROOT"]})
            queue.close()


if __name__ == "__main__":
    unittest.main()
