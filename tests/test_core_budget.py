import unittest

from jarvis_v2.core import ResourceBudget, ResourceBudgetError


class CoreBudgetTests(unittest.TestCase):
    def test_global_capacity_and_device_limits(self):
        budget = ResourceBudget(2, device_limits={"gpu": 1}, slots=("cpu", "gpu"))

        self.assertEqual(budget.claim("worker-1", device="gpu", compatible_slots=("gpu",)), "gpu")
        self.assertIsNone(budget.claim("worker-2", device="gpu", compatible_slots=("cpu",)))
        self.assertEqual(budget.claim("worker-2", device="cpu", compatible_slots=("cpu",)), "cpu")
        self.assertIsNone(budget.claim("worker-3", device="cpu"))
        self.assertEqual(budget.device_usage, {"gpu": 1, "cpu": 1})

    def test_guardian_reservation_blocks_lower_priority_without_preemption(self):
        budget = ResourceBudget(2, slots=("cpu", "gpu"))
        self.assertEqual(budget.claim("worker", device="cpu", compatible_slots=("cpu",)), "cpu")
        budget.guardian_request(("gpu",))

        self.assertIsNone(budget.claim("background", device="gpu", compatible_slots=("gpu",)))
        self.assertEqual(budget.claim("guardian", device="gpu", guardian=True), "gpu")
        self.assertEqual(budget.held_slots["cpu"]["owner"], "worker")

    def test_release_is_fenced_and_invalid_configuration_is_rejected(self):
        with self.assertRaises(ResourceBudgetError):
            ResourceBudget(0)
        with self.assertRaises(ResourceBudgetError):
            ResourceBudget(2, slots=("only-one",))

        budget = ResourceBudget(1)
        slot = budget.claim("worker")
        with self.assertRaises(ResourceBudgetError):
            budget.finish("other", slot)
        with self.assertRaises(ResourceBudgetError):
            budget.finish("worker", slot, device="wrong")
        budget.finish("worker", slot)
        self.assertEqual(budget.available_slots, ("slot-0",))


if __name__ == "__main__":
    unittest.main()
