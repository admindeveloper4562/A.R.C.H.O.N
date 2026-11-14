"""Bounded acceptance coverage for deterministic AEGIS slot scheduling."""
import random
import unittest

from jarvis_v2.guardian.priority import SlotPriority


class AegisSlotTests(unittest.TestCase):
    def test_in_flight_work_is_not_preempted(self):
        slots = SlotPriority(("local", "remote"))
        self.assertEqual(slots.claim("worker", ("local",)), "local")
        slots.guardian_request(("local",))
        self.assertIsNone(slots.claim("guardian"))
        self.assertEqual(slots.held_slots, {"local": "worker"})
        self.assertIsNone(slots.claim("background", ("remote",)))
        slots.finish("worker", "local")
        self.assertEqual(slots.claim("guardian"), "local")

    def test_guardian_blocks_lower_priority_until_next_compatible_slot(self):
        slots = SlotPriority(("cpu", "gpu"))
        self.assertEqual(slots.claim("worker", ("cpu",)), "cpu")
        slots.guardian_request(("gpu",))
        self.assertEqual(slots.available_slots, ("gpu",))
        self.assertIsNone(slots.claim("research", ("gpu",)))
        self.assertEqual(slots.claim("guardian"), "gpu")

    def test_guardian_uses_stable_configured_slot_order(self):
        slots = SlotPriority(("cpu-1", "gpu", "cpu-2"))
        slots.guardian_request(("cpu-2", "cpu-1"))
        self.assertEqual(slots.claim("guardian"), "cpu-1")

    def test_request_sequence_is_idempotent_and_release_is_strict(self):
        slots = SlotPriority(("cpu", "gpu"))
        self.assertTrue(slots.start("worker"))
        slots.guardian_request(("gpu",))
        slots.guardian_request(("cpu",))  # retry cannot rewrite first request
        self.assertEqual(slots.claim("guardian"), "gpu")
        with self.assertRaises(ValueError):
            slots.finish("worker", "gpu")
        slots.finish("guardian", "gpu")
        slots.finish("worker", "cpu")
        self.assertEqual(slots.available_slots, slots.slots)

    def test_invalid_request_does_not_change_state(self):
        slots = SlotPriority(("cpu",))
        with self.assertRaises(ValueError):
            slots.guardian_request(())
        with self.assertRaises(ValueError):
            slots.guardian_request(("gpu",))
        self.assertFalse(slots.guardian_pending)
        self.assertEqual(slots.held_slots, {})

    def test_bounded_sequences_do_not_leak_or_starve_guardian(self):
        for seed in range(32):
            rng = random.Random(seed)
            slots = SlotPriority(("cpu", "gpu"))
            requested = False
            for _ in range(48):
                action = rng.randrange(4)
                if action == 0:
                    slots.guardian_request(("gpu",))
                    requested = True
                elif action == 1:
                    slots.claim("worker", ("cpu",))
                elif action == 2:
                    slots.claim("guardian")
                elif slots.held_slots:
                    slot, owner = next(iter(slots.held_slots.items()))
                    slots.finish(owner, slot)

                held = slots.held_slots
                self.assertLessEqual(len(held), len(slots.slots))
                self.assertTrue(set(held).issubset(slots.slots))
                if requested and slots.guardian_pending:
                    self.assertIsNone(slots.claim("lower", ("gpu",)))

            # A finite sequence gets a finite drain at safe boundaries.
            for slot, owner in tuple(slots.held_slots.items()):
                slots.finish(owner, slot)
            if slots.guardian_pending:
                self.assertEqual(slots.claim("guardian"), "gpu")
                slots.finish("guardian", "gpu")
            self.assertEqual(slots.held_slots, {})
            self.assertEqual(slots.available_slots, slots.slots)
            self.assertFalse(slots.guardian_pending)


if __name__ == "__main__":
    unittest.main()
