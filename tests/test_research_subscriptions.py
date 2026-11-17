import tempfile
import unittest
from pathlib import Path

from jarvis_v2.research import (
    MIN_CADENCE_SECONDS,
    Subscription,
    SubscriptionError,
    SubscriptionService,
    SubscriptionStore,
)


class ResearchSubscriptionTests(unittest.TestCase):
    def service(self, path: Path, clock):
        return SubscriptionService(SubscriptionStore(path), clock=clock)

    def test_follow_is_stable_and_enforces_provider_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "subscriptions.sqlite"
            service = self.service(path, lambda: 100)
            first = service.follow("youtube", "channel-1", "archon", MIN_CADENCE_SECONDS)
            replay = service.follow("youtube", "channel-1", "archon", MIN_CADENCE_SECONDS)
            self.assertEqual(first, replay)
            with self.assertRaises(SubscriptionError):
                service.follow("youtube", "channel-2", "archon", MIN_CADENCE_SECONDS - 1)
            with self.assertRaises(SubscriptionError):
                Subscription(
                    "sub-invalid", "youtube", "channel-3", "private", "private",
                    MIN_CADENCE_SECONDS, 100,
                )

    def test_only_due_subscriptions_refresh_and_next_cadence_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "subscriptions.sqlite"
            now = [100]
            service = self.service(path, lambda: now[0])
            subscription = service.follow("rss", "channel-1", "topic", MIN_CADENCE_SECONDS)
            calls = []
            first = service.refresh_due(lambda item: calls.append(item.subscription_id) or {"updated": 1})
            self.assertEqual(len(first), 1)
            self.assertEqual(calls, [subscription.subscription_id])
            self.assertEqual(service.refresh_due(lambda item: calls.append(item.subscription_id) or {}), ())
            now[0] = 100 + MIN_CADENCE_SECONDS
            second = service.refresh_due(lambda item: calls.append(item.subscription_id) or {"updated": 2})
            self.assertEqual(len(second), 1)
            self.assertEqual(len(calls), 2)
            self.assertEqual(service.store.get(subscription.subscription_id).last_status, "refreshed")

    def test_provider_failure_is_bounded_and_does_not_leak_exception_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "subscriptions.sqlite"
            service = self.service(path, lambda: 100)
            subscription = service.follow("rss", "channel-1", "topic", MIN_CADENCE_SECONDS)

            def unavailable(_item):
                raise TimeoutError("provider internals")

            result = service.refresh_due(unavailable)[0]
            self.assertEqual((result.status, result.failure), ("failed", "provider_timeout"))
            saved = service.store.get(subscription.subscription_id)
            self.assertEqual(saved.last_error, "provider_timeout")
            self.assertNotIn("provider internals", str(saved.as_dict()))

    def test_disabled_subscription_is_not_refreshed_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "subscriptions.sqlite"
            service = self.service(path, lambda: 100)
            subscription = service.follow("rss", "channel-1", "topic", MIN_CADENCE_SECONDS)
            service.store.disable(subscription.subscription_id)
            with SubscriptionStore(path) as store:
                self.assertEqual(store.due(100), [])


if __name__ == "__main__":
    unittest.main()
