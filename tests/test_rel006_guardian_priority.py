from __future__ import annotations

import unittest

from jarvis_v2.core import ResourceBudget


class GuardianPriorityQualificationTests(unittest.TestCase):
    """Exercise the real Core budget and Guardian reservation boundary."""

    def test_guardian_uses_next_slot_without_preempting_active_inference(self) -> None:
        budget = ResourceBudget(2, slots=("slot-0", "slot-1"))

        active_slot = budget.claim(
            "core-inference", device="local", compatible_slots=("slot-0",)
        )
        self.assertEqual(active_slot, "slot-0")

        budget.guardian_request()
        self.assertEqual(
            budget.held_slots,
            {"slot-0": {"owner": "core-inference", "device": "local"}},
        )
        self.assertIsNone(
            budget.claim(
                "new-worker-inference",
                device="local",
                compatible_slots=("slot-1",),
            )
        )

        guardian_slot = budget.claim("guardian", device="local", guardian=True)
        self.assertEqual(guardian_slot, "slot-1")
        self.assertEqual(budget.held_slots["slot-0"]["owner"], "core-inference")

        budget.finish("core-inference", "slot-0", device="local")
        self.assertIsNone(
            budget.claim(
                "new-worker-inference",
                device="local",
                compatible_slots=("slot-1",),
            )
        )

        budget.finish("guardian", guardian_slot, device="local")
        self.assertEqual(
            budget.claim(
                "new-worker-inference",
                device="local",
                compatible_slots=("slot-1",),
            ),
            "slot-1",
        )


if __name__ == "__main__":
    unittest.main()
