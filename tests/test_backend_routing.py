import unittest

from jarvis_v2.backend import (
    CircuitBreaker,
    CircuitState,
    GatewayRouter,
    ProviderCapability,
    ProviderRegistry,
    ProviderRequirements,
    StickyRouter,
    UsageBudget,
)


def capability(provider_id="codex", *, available=True, quota_remaining=100):
    return ProviderCapability(
        provider_id=provider_id,
        model="gpt-5.6-luna",
        context_window=32_000,
        tools=frozenset(),
        privacy_scopes=frozenset({"public_metadata"}),
        locality="remote",
        quota_remaining=quota_remaining,
        available=available,
    )


def requirements(**changes):
    values = {
        "context_tokens": 1_000,
        "tools": frozenset(),
        "privacy_scope": "public_metadata",
        "locality": "remote",
        "quota_units": 1,
    }
    values.update(changes)
    return ProviderRequirements(**values)


class BackendRoutingTests(unittest.TestCase):
    def test_sticky_route_requires_explicit_handoff(self):
        router = GatewayRouter(ProviderRegistry([capability("codex"), capability("local")] ), sticky=StickyRouter())
        first = router.route("conversation-1", requirements(requested_provider="codex"))
        self.assertEqual((first.status, first.provider_id), ("routed", "codex"))
        held = router.route("conversation-1", requirements(requested_provider="local"))
        self.assertEqual((held.status, held.reason), ("paused", "sticky_provider_required"))
        handed = router.route(
            "conversation-1", requirements(), allow_handoff=True, handoff_provider="local"
        )
        self.assertEqual((handed.status, handed.provider_id), ("routed", "local"))

    def test_budget_blocks_without_selecting_another_provider(self):
        router = GatewayRouter(
            ProviderRegistry([capability("codex"), capability("local")]),
            budgets={"codex": UsageBudget(1), "local": UsageBudget(10)},
        )
        self.assertEqual(router.route("task-1", requirements(requested_provider="codex")).status, "routed")
        blocked = router.route("task-2", requirements(requested_provider="codex"))
        self.assertEqual((blocked.status, blocked.reason), ("paused", "usage_budget_exhausted"))
        handed = router.route(
            "task-2", requirements(requested_provider="codex"),
            allow_handoff=True, handoff_provider="local",
        )
        self.assertEqual((handed.status, handed.provider_id), ("routed", "local"))

    def test_circuit_opens_and_allows_one_timed_probe(self):
        now = [0.0]
        breaker = CircuitBreaker(failure_threshold=2, reset_timeout=5, clock=lambda: now[0])
        self.assertTrue(breaker.allow())
        breaker.record_failure()
        breaker.record_failure()
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertFalse(breaker.allow())
        now[0] = 5.0
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        self.assertTrue(breaker.allow())
        self.assertFalse(breaker.allow())
        breaker.record_success()
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_budget_reservation_can_be_released(self):
        budget = UsageBudget(3)
        self.assertTrue(budget.reserve(2))
        self.assertEqual((budget.remaining, budget.reserved), (1, 2))
        budget.release(2)
        self.assertEqual((budget.remaining, budget.reserved), (3, 0))
        self.assertFalse(budget.consume(4))

    def test_registry_quota_becomes_a_consumable_default_budget(self):
        router = GatewayRouter(ProviderRegistry([capability("codex", quota_remaining=1)]))
        self.assertEqual(router.route("task-1", requirements(requested_provider="codex")).status, "routed")
        blocked = router.route("task-2", requirements(requested_provider="codex"))
        self.assertEqual((blocked.status, blocked.reason), ("paused", "usage_budget_exhausted"))


if __name__ == "__main__":
    unittest.main()
