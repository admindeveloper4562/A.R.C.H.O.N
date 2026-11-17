from hashlib import sha256
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.wic import AlertPolicy, AlertStore, WICError


OBSERVED = "2026-11-17T01:00:00Z"


def digest(value):
    return sha256(value.encode()).hexdigest()


class WICAlertTests(unittest.TestCase):
    def policy(self, **changes):
        values = {
            "policy_id": "policy-1",
            "owner_id": "owner-1",
            "topics": ("science",),
            "cadence_seconds": 3600,
            "timezone_name": "Asia/Bangkok",
        }
        values.update(changes)
        return AlertPolicy(**values)

    def test_material_change_is_queued_once_and_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "alerts.sqlite"
            with AlertStore(path) as store:
                store.save_policy(self.policy(), requester_id="owner-1")
                first = store.evaluate(
                    "policy-1", digest("one"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-17T01:00:00Z",
                )
                duplicate = store.evaluate(
                    "policy-1", digest("one"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-17T02:00:01Z",
                )
                self.assertEqual(first.status, "queued")
                self.assertEqual(duplicate.status, "duplicate")
            with AlertStore(path) as store:
                self.assertEqual(len(store.history("policy-1", requester_id="owner-1")), 1)

    def test_non_material_change_does_not_create_alert(self):
        with tempfile.TemporaryDirectory() as directory:
            with AlertStore(Path(directory) / "alerts.sqlite") as store:
                store.save_policy(self.policy(), requester_id="owner-1")
                result = store.evaluate(
                    "policy-1", digest("same"), OBSERVED, material_change=False,
                    requester_id="owner-1", evaluated_at="2026-11-17T01:00:00Z",
                )
                self.assertEqual((result.status, result.reason), ("suppressed", "not_material"))
                self.assertEqual(store.history("policy-1", requester_id="owner-1"), ())

    def test_quiet_hours_and_cadence_suppress_without_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            with AlertStore(Path(directory) / "alerts.sqlite") as store:
                store.save_policy(
                    self.policy(quiet_start_minute=120, quiet_end_minute=360),
                    requester_id="owner-1",
                )
                quiet = store.evaluate(
                    "policy-1", digest("quiet"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-16T20:00:00Z",
                )
                first = store.evaluate(
                    "policy-1", digest("first"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-17T01:00:00Z",
                )
                throttled = store.evaluate(
                    "policy-1", digest("second"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-17T01:30:00Z",
                )
                self.assertEqual(quiet.reason, "quiet_hours")
                self.assertEqual(first.status, "queued")
                self.assertEqual(throttled.reason, "cadence")
                self.assertEqual(len(store.history("policy-1", requester_id="owner-1")), 1)

    def test_owner_scope_and_disabled_policy_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with AlertStore(Path(directory) / "alerts.sqlite") as store:
                store.save_policy(self.policy(enabled=False), requester_id="owner-1")
                with self.assertRaises(WICError):
                    store.get_policy("policy-1", requester_id="other-owner")
                result = store.evaluate(
                    "policy-1", digest("disabled"), OBSERVED, material_change=True,
                    requester_id="owner-1", evaluated_at="2026-11-17T01:00:00Z",
                )
                self.assertEqual(result.reason, "disabled")


if __name__ == "__main__":
    unittest.main()
