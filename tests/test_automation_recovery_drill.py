import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.recovery_drill import RecoveryDrill
from jarvis_v2.backend import EventBus


class RecoveryDrillTests(unittest.TestCase):
    def test_restored_completed_event_is_not_applied_twice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "events.sqlite"
            backup = root / "events.backup.sqlite"
            restored = root / "events.restored.sqlite"
            with EventBus(database) as bus:
                event = bus.publish(
                    "automation.job", "automation", "job-1", 1, {"state": "retained"},
                    correlation_id="corr-1", idempotency_key="job-1",
                )
                calls: list[str] = []

                def effect(received):
                    calls.append(received.event_id)
                    return {"accepted": True}

                bus.deliver("automation-worker", event.event_id, effect)
            drill = RecoveryDrill(database)
            source_state = drill.inspect()["state_sha256"]
            backup_receipt = drill.backup(backup)
            restore_receipt = drill.restore(backup, restored)
            self.assertEqual(backup_receipt.integrity, "ok")
            self.assertEqual(restore_receipt.integrity, "ok")
            self.assertEqual(drill.inspect()["state_sha256"], source_state)
            self.assertEqual(
                RecoveryDrill(restored).replay_pending(
                    "automation-worker", effect,
                ),
                [],
            )
            self.assertEqual(calls, [event.event_id])

    def test_replay_after_restore_keeps_effect_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "events.sqlite"
            backup = root / "events.backup.sqlite"
            restored = root / "events.restored.sqlite"
            with EventBus(database) as bus:
                bus.publish(
                    "automation.job", "automation", "job-2", 1, {"state": "retained"},
                    correlation_id="corr-2", idempotency_key="job-2",
                )
            drill = RecoveryDrill(database)
            drill.backup(backup)
            drill.restore(backup, restored)
            calls: list[str] = []
            receipts = RecoveryDrill(restored).replay_pending(
                "automation-worker",
                lambda received: calls.append(received.event_id) or {"accepted": True},
            )
            self.assertEqual(len(receipts), 1)
            self.assertEqual(len(calls), 1)
            self.assertEqual(
                RecoveryDrill(restored).replay_pending(
                    "automation-worker",
                    lambda received: calls.append(received.event_id) or {"accepted": True},
                ),
                [],
            )
            self.assertEqual(len(calls), 1)

    def test_replay_limit_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "events.sqlite"
            with EventBus(database) as bus:
                bus.publish("automation.job", "automation", "job-3", 1, {}, correlation_id="corr-3")
            with self.assertRaises(ValueError):
                RecoveryDrill(database, max_replay_events=1).replay_pending(
                    "automation-worker", lambda _: {"accepted": True}, limit=2
                )


if __name__ == "__main__":
    unittest.main()
