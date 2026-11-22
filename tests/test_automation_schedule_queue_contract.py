from datetime import date, datetime, time, timezone
from pathlib import Path
import tempfile
import time as wall_clock
import unittest

from jarvis_v2.automation.dispatcher import ReconnectDispatcher
from jarvis_v2.automation.queue_api import CoordinatorQueue, QueueApiError, DEFAULT_LEASE_SECONDS
from jarvis_v2.automation.scheduler import AutomationScheduleStore
from jarvis_v2.backend import NodeRoute
from tests.queue_admission import enqueue_approved

UTC = timezone.utc


class ScheduledQueuePersistenceTests(unittest.TestCase):
    def test_daily_due_dispatch_restart_and_ack_replay_are_idempotent(self):
        schedule_id = "relay-daily-disposable"
        scheduled_for = datetime(2026, 11, 21, 12, 0, tzinfo=UTC)
        task_id = "relay-daily-disposable-20261121T120000Z"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule_path = root / "relay.sqlite"
            queue_path = root / "queue.sqlite"
            effect_path = root / "effect.receipt"
            schedule_clock = lambda: scheduled_for
            with AutomationScheduleStore(schedule_path, clock=schedule_clock) as schedule:
                schedule.schedule_daily(
                    schedule_id,
                    "disposable scheduled work",
                    time(12),
                    timezone_name="UTC",
                    start_date=date(2026, 11, 21),
                )

            with AutomationScheduleStore(schedule_path, clock=schedule_clock) as schedule:
                due = schedule.due(scheduled_for)
                self.assertEqual([item.reminder_id for item in due], [schedule_id])
                occurrence = due[0]

            queue_clock = [wall_clock.time()]
            payload = {
                "job_id": f"job-{task_id}",
                "idempotency_key": f"effect-{task_id}",
                "operation": "summarize",
                "input_sha256": "a" * 64,
                "required_scope": "public_metadata",
                "deadline_at": int(queue_clock[0]) + 600,
                "task_id": task_id,
                "schedule_id": schedule_id,
                "scheduled_for_utc": occurrence.next_due_utc.isoformat(),
            }
            route = lambda job: NodeRoute(
                "routed", "disposable-node", "test-model", "fixture"
            )

            first_claims = []

            def record_effect(item, job, target):
                if not effect_path.exists():
                    effect_path.write_text(job.idempotency_key + "\n", encoding="utf-8")
                return True

            def crash_after_effect(item, job, target):
                first_claims.append(item)
                record_effect(item, job, target)
                raise SystemExit("simulated worker crash after disposable effect")

            with CoordinatorQueue.open(queue_path, clock=lambda: queue_clock[0]) as queue:
                enqueue_approved(
                    queue,
                    task_id=task_id,
                    priority="P3",
                    module="automation",
                    payload=payload,
                )
                dispatcher = ReconnectDispatcher(
                    queue, route=route, handoff=crash_after_effect
                )
                with self.assertRaises(SystemExit):
                    dispatcher.drain(limit=1)
                self.assertEqual(effect_path.read_text(encoding="utf-8").splitlines(), [f"effect-{task_id}"])
                self.assertEqual(queue.status()[0]["state"], "leased")

            with CoordinatorQueue.open(queue_path, clock=lambda: queue_clock[0]) as queue:
                dispatcher = ReconnectDispatcher(queue, route=route, handoff=record_effect)
                self.assertEqual(dispatcher.drain(limit=1), [])
                self.assertEqual(effect_path.read_text(encoding="utf-8").splitlines(), [f"effect-{task_id}"])

            queue_clock[0] += DEFAULT_LEASE_SECONDS + 1
            with CoordinatorQueue.open(queue_path, clock=lambda: queue_clock[0]) as queue:
                dispatcher = ReconnectDispatcher(queue, route=route, handoff=record_effect)
                decisions = dispatcher.drain(limit=1)
                self.assertEqual([decision.status for decision in decisions], ["dispatched"])
                self.assertIsNotNone(decisions[0].item)
                self.assertNotEqual(decisions[0].item.lease, first_claims[0].lease)
                with self.assertRaises(QueueApiError):
                    queue.complete(first_claims[0], ok=True, receipt="stale-effect")
                queue.complete(
                    decisions[0].item,
                    ok=True,
                    receipt=f"effect:{task_id}",
                )
                self.assertEqual(queue.status()[0]["state"], "completed")

            with CoordinatorQueue.open(queue_path, clock=lambda: queue_clock[0]) as queue:
                dispatcher = ReconnectDispatcher(queue, route=route, handoff=record_effect)
                self.assertEqual(dispatcher.drain(limit=1), [])
                self.assertEqual(effect_path.read_text(encoding="utf-8").splitlines(), [f"effect-{task_id}"])

            with AutomationScheduleStore(schedule_path, clock=schedule_clock) as schedule:
                first_ack = schedule.acknowledge(
                    schedule_id, expected_due_utc=occurrence.next_due_utc
                )
            with AutomationScheduleStore(schedule_path, clock=schedule_clock) as schedule:
                replay = schedule.acknowledge(
                    schedule_id, expected_due_utc=occurrence.next_due_utc
                )
                self.assertEqual(replay, first_ack)
                self.assertEqual(schedule.due(scheduled_for), [])


if __name__ == "__main__":
    unittest.main()
