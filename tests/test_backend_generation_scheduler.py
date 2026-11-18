import unittest

from jarvis_v2.backend import (
    GenerationRequest,
    GenerationScheduler,
    GenerationSchedulerError,
)


class GenerationSchedulerTests(unittest.TestCase):
    def test_priority_interactive_and_single_generation_fencing(self):
        scheduler = GenerationScheduler(2, slots=("cpu", "gpu"))
        scheduler.submit(GenerationRequest("batch-task", 1, priority="P2", mode="batch"))
        scheduler.submit(GenerationRequest("interactive-task", 1, priority="P2", mode="interactive"))
        first = scheduler.claim_next()
        self.assertEqual(first.task_id, "interactive-task")
        with self.assertRaisesRegex(GenerationSchedulerError, "one generation"):
            scheduler.submit(GenerationRequest("interactive-task", 2, mode="interactive"))
        second = scheduler.claim_next()
        self.assertEqual(second.task_id, "batch-task")
        self.assertEqual(scheduler.quota_remaining, 0)

    def test_guardian_reservation_and_finish_are_fenced(self):
        scheduler = GenerationScheduler(2, slots=("cpu", "gpu"))
        scheduler.submit(GenerationRequest("guardian-task", 1, priority="P0", guardian=True, compatible_slots=("gpu",)))
        scheduler.submit(GenerationRequest("batch-task", 1, priority="P1", compatible_slots=("gpu",)))
        guardian = scheduler.claim_next()
        self.assertEqual((guardian.task_id, guardian.slot), ("guardian-task", "gpu"))
        scheduler.finish(guardian)
        with self.assertRaisesRegex(GenerationSchedulerError, "stale"):
            scheduler.finish(guardian)
        self.assertEqual(scheduler.claim_next().task_id, "batch-task")

    def test_quota_and_invalid_requests_fail_closed(self):
        scheduler = GenerationScheduler(0)
        scheduler.submit(GenerationRequest("task", 1))
        self.assertIsNone(scheduler.claim_next())
        with self.assertRaises(GenerationSchedulerError):
            scheduler.submit(GenerationRequest("other", 1, mode="stream"))


if __name__ == "__main__":
    unittest.main()
