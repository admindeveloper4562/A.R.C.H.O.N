import json
import unittest
from pathlib import Path

from jarvis_v2.guardian.isolation import IsolationController, IsolationError


ROOT = Path(__file__).parents[1]


class ReleaseFaultIsolationTests(unittest.TestCase):
    def test_one_fault_isolated_without_stopping_the_other_nine_modules(self):
        modules = json.loads((ROOT / "config/modules.json").read_text(encoding="utf-8"))["modules"]
        component_ids = tuple(entry["key"] for entry in modules)
        self.assertEqual(len(component_ids), 10)

        controller = IsolationController(component_ids)
        for component_id in component_ids:
            controller.begin_effect(component_id, f"initial-{component_id}")

        target = "runtime"
        controller.drain(target)
        generation = controller.snapshot(target).generation
        controller.complete_effect(target, f"initial-{target}", generation=generation)
        controller.quiesce(target)
        self.assertEqual(controller.isolate(target, reason="fault_injection").state, "isolated")

        for component_id in component_ids:
            if component_id == target:
                with self.assertRaises(IsolationError):
                    controller.begin_effect(component_id, "blocked-after-isolation")
                continue
            self.assertEqual(controller.snapshot(component_id).state, "running")
            self.assertTrue(controller.can_accept_effect(component_id))
            controller.begin_effect(component_id, f"followup-{component_id}")

        for component_id in component_ids:
            if component_id != target:
                controller.complete_effect(component_id, f"initial-{component_id}")
                controller.complete_effect(component_id, f"followup-{component_id}")

        self.assertEqual(controller.resume(target).state, "running")
        self.assertTrue(controller.can_accept_effect(target))


if __name__ == "__main__":
    unittest.main()
