import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.authorization import AuthorizationServer
from jarvis_v2.backend.event_bus import EventBus
from jarvis_v2.backend.event_bus import EventBusError
from jarvis_v2.core.dispatch import DispatchStore
from jarvis_v2.core.registry import ModuleRegistry
from jarvis_v2.runtime import RuntimeService


ROOT = Path(__file__).parents[1]
SOURCE_SHA = "50db90ccd2421621585e39eb128745ed8916f9ce"


class Rel003CoreSdaDelegationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "rel003.sqlite"
        registry = ModuleRegistry.from_config(ROOT / "config/modules.json")
        authorization = AuthorizationServer(registry)
        identity = authorization.register_identity("rel003-runtime", "runtime")
        authorization.grant(
            identity.identity_id,
            "runtime",
            ("runtime:read", "runtime:health"),
            grant_id="rel003-runtime-grant",
        )
        self.service = RuntimeService(
            registry, authorization, DispatchStore(self.path), EventBus(self.path)
        )

    def tearDown(self):
        if self.service is not None:
            self.service.close()
        self.temp.cleanup()

    @staticmethod
    def request(path, scope="runtime:read", **extra):
        return {
            "method": extra.pop("method", "GET"),
            "path": path,
            "identity_id": extra.pop("identity_id", "rel003-runtime"),
            "scope": scope,
            **extra,
        }

    def _delegate(self):
        created = self.service.handle(self.request(
            "/tasks",
            method="POST",
            body={
                "task_id": "REL-003-core-sda",
                "target_module": "core",
                "scope": "core:read",
                "acceptance": ["Core records the SDA project completion result"],
                "correlation_id": "rel003-correlation",
                "input_refs": {
                    "project_id": "ARCHON-JARVIS-V2",
                    "source_sha": SOURCE_SHA,
                },
                "dispatch_id": "rel003-dispatch",
            },
        ))
        self.assertEqual(created.status, 201)
        dispatch_id = created.body["dispatch"]["dispatch_id"]
        handoff_event_id = created.body["event_id"]
        claimed = self.service.handle(self.request(
            f"/tasks/{dispatch_id}/claim",
            method="POST",
            body={"executor_id": "core-executor", "claim_id": "rel003-claim"},
        ))
        self.assertEqual(claimed.status, 200)
        acknowledged = self.service.handle(self.request(
            f"/tasks/{dispatch_id}/ack",
            method="POST",
            body={
                "executor_id": "core-executor",
                "claim_id": "rel003-claim",
                "status": "completed",
                "result": {
                    "project_id": "ARCHON-JARVIS-V2",
                    "state": "verified",
                    "integration_sha": SOURCE_SHA,
                    "child_receipts": 5,
                },
            },
        ))
        self.assertEqual(acknowledged.status, 200)
        self.assertEqual(acknowledged.body["dispatch"]["status"], "completed")
        completion = self.service.events.publish(
            "core.project.completed",
            "core",
            dispatch_id,
            2,
            {
                "task_id": "REL-003-core-sda",
                "project_id": "ARCHON-JARVIS-V2",
                "state": "verified",
                "integration_sha": SOURCE_SHA,
                "child_receipts": 5,
            },
            correlation_id="rel003-correlation",
            causation_id=handoff_event_id,
            idempotency_key="rel003-completion",
        )
        return dispatch_id, completion

    def test_single_builder_delegates_to_core_and_records_completion_event(self):
        dispatch_id, completion = self._delegate()
        self.assertEqual(completion.event_type, "core.project.completed")
        self.assertEqual(completion.causation_id, self.service.events.pending("rel003-events")[0].event_id)
        self.assertEqual(completion.payload["integration_sha"], SOURCE_SHA)
        self.assertEqual(completion.payload["child_receipts"], 5)
        self.assertEqual(self.service.dispatch.get(dispatch_id)["ack"]["status"], "completed")

    def test_restart_preserves_result_and_delivery_is_idempotent(self):
        dispatch_id, completion = self._delegate()
        self.service.close()
        self.service = None

        events = EventBus(self.path)
        dispatch = DispatchStore(self.path)
        restored = dispatch.get(dispatch_id)
        self.assertEqual(restored["status"], "completed")
        self.assertEqual(restored["ack"]["result"]["project_id"], "ARCHON-JARVIS-V2")
        calls = []

        def consume(event):
            calls.append(event.event_id)
            return {"accepted": True}

        first = events.deliver("core-consumer", completion.event_id, consume)
        second = events.deliver("core-consumer", completion.event_id, consume)
        self.assertEqual(first, second)
        self.assertEqual(calls, [completion.event_id])
        dispatch.close()
        events.close()

    def test_scope_claim_and_completion_idempotency_fail_closed(self):
        denied = self.service.handle(self.request(
            "/tasks",
            method="POST",
            body={
                "task_id": "REL-003-denied",
                "target_module": "core",
                "scope": "core:admin",
                "acceptance": ["not admitted"],
                "correlation_id": "rel003-denied",
            },
        ))
        self.assertEqual(denied.status, 403)
        dispatch_id, completion = self._delegate()
        wrong_claim = self.service.handle(self.request(
            f"/tasks/{dispatch_id}/claim",
            method="POST",
            body={"executor_id": "other-executor", "claim_id": "other-claim"},
        ))
        self.assertEqual(wrong_claim.status, 409)
        with self.assertRaises(EventBusError):
            self.service.events.publish(
                "core.project.completed",
                "core",
                dispatch_id,
                2,
                {"state": "tampered"},
                correlation_id="rel003-correlation",
                causation_id=completion.causation_id,
                idempotency_key="rel003-completion",
            )


if __name__ == "__main__":
    unittest.main()
