import unittest

from jarvis_v2.guardian.isolation import IsolationController, IsolationError


class GuardianIsolationTests(unittest.TestCase):
    def test_drain_reconciles_effects_and_preserves_unaffected_modules(self):
        controller = IsolationController(("module-a", "module-b"))
        controller.begin_effect("module-a", "effect-a")
        controller.begin_effect("module-b", "effect-b")

        draining = controller.drain("module-a")
        self.assertEqual(draining.state, "draining")
        with self.assertRaises(IsolationError):
            controller.begin_effect("module-a", "effect-new")

        controller.begin_effect("module-b", "effect-b-2")
        controller.complete_effect("module-b", "effect-b")
        controller.complete_effect("module-b", "effect-b-2")
        with self.assertRaises(IsolationError):
            controller.quiesce("module-a")

        controller.reconcile_effect(
            "module-a", "effect-a", status="completed", evidence_ref="receipt-a"
        )
        self.assertEqual(controller.quiesce("module-a").state, "quiesced")
        isolated = controller.isolate("module-a", reason="component_failure")
        self.assertEqual(isolated.state, "isolated")
        self.assertEqual(controller.snapshot("module-b").state, "running")

    def test_unknown_effect_blocks_resume_until_resolved(self):
        controller = IsolationController(("module-a",))
        started = controller.begin_effect("module-a", "effect-a")
        controller.drain("module-a")
        controller.complete_effect(
            "module-a", "effect-a", status="unknown", generation=started.generation + 1
        )
        controller.isolate("module-a", reason="unknown_outcome")
        with self.assertRaises(IsolationError):
            controller.resume("module-a")
        controller.complete_effect("module-a", "effect-a", status="completed")
        self.assertEqual(controller.resume("module-a").state, "running")

    def test_stale_generation_and_duplicate_effects_are_rejected(self):
        controller = IsolationController(("module-a",))
        started = controller.begin_effect("module-a", "effect-a")
        with self.assertRaises(IsolationError):
            controller.begin_effect("module-a", "effect-a")
        controller.drain("module-a")
        with self.assertRaises(IsolationError):
            controller.complete_effect(
                "module-a", "effect-a", generation=started.generation
            )
        self.assertEqual(controller.snapshot("module-a").in_flight, ("effect-a",))

    def test_invalid_transition_does_not_mutate_other_state(self):
        controller = IsolationController(("module-a", "module-b"))
        with self.assertRaises(IsolationError):
            controller.isolate("module-a", reason="not_drained")
        with self.assertRaises(IsolationError):
            controller.begin_effect("module-c", "effect-c")
        self.assertEqual(controller.snapshot("module-a").state, "running")
        self.assertEqual(controller.snapshot("module-b").state, "running")


if __name__ == "__main__":
    unittest.main()
