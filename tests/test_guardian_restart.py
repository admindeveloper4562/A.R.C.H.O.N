import unittest

from jarvis_v2.guardian.restart import RestartBudget, RestartBudgetError


class GuardianRestartTests(unittest.TestCase):
    def setUp(self):
        self.now = [0.0]
        self.budget = RestartBudget(
            "atlas-sda", max_attempts=2, cooldown_seconds=10, clock=lambda: self.now[0]
        )

    def test_cooldown_and_repeated_failures_escalate_without_replay(self):
        first = self.budget.request(reason="probe_failed", evidence_ref="probe-1")
        self.assertTrue(first.allowed)
        self.assertEqual(first.state, "cooldown")
        self.budget.record_outcome(first.attempt, "failed", evidence_ref="result-1")

        self.now[0] = 1
        self.assertEqual(self.budget.request(reason="probe_failed").reason, "restart_cooldown_active")
        self.now[0] = 10
        second = self.budget.request(reason="probe_failed", evidence_ref="probe-2")
        self.assertTrue(second.allowed)
        self.budget.record_outcome(second.attempt, "failed", evidence_ref="result-2")

        self.now[0] = 20
        exhausted = self.budget.request(reason="probe_failed")
        self.assertFalse(exhausted.allowed)
        self.assertEqual(exhausted.state, "escalated")
        self.assertEqual([record.outcome for record in self.budget.history], ["failed", "failed"])
        self.assertEqual([record.evidence_ref for record in self.budget.history], ["result-1", "result-2"])

    def test_pending_attempt_is_fenced_until_outcome_is_recorded(self):
        first = self.budget.request(reason="timeout", evidence_ref="probe-1")
        self.now[0] = 10
        blocked = self.budget.request(reason="timeout")
        self.assertFalse(blocked.allowed)
        self.assertEqual(blocked.reason, "restart_attempt_unreconciled")
        self.budget.record_outcome(first.attempt, "unknown", evidence_ref="unknown-1")
        self.assertEqual(self.budget.snapshot().state, "needs_reconciliation")
        with self.assertRaises(RestartBudgetError):
            self.budget.new_generation()
        self.budget.resolve_unknown(first.attempt, "failed", evidence_ref="result-1")
        self.assertEqual(self.budget.snapshot().state, "ready")

    def test_success_requires_explicit_generation_reset_and_preserves_history(self):
        first = self.budget.request(reason="crash", evidence_ref="probe-1")
        self.budget.record_outcome(first.attempt, "succeeded", evidence_ref="result-1")
        self.now[0] = 10
        self.assertEqual(self.budget.request(reason="crash").reason, "generation_reset_required")
        reset = self.budget.new_generation()
        self.assertEqual(reset.generation, 1)
        self.assertEqual(reset.attempts, 0)
        self.assertEqual(len(self.budget.history), 1)
        self.assertTrue(self.budget.request(reason="crash").allowed)

    def test_disabled_and_invalid_policies_fail_closed(self):
        disabled = RestartBudget("atlas-sda", enabled=False)
        decision = disabled.request(reason="failure")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "restart_disabled")
        with self.assertRaises(RestartBudgetError):
            RestartBudget("atlas-sda", max_attempts=6)
        with self.assertRaises(RestartBudgetError):
            RestartBudget("atlas-sda", cooldown_seconds=0)


if __name__ == "__main__":
    unittest.main()
