import json
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.authorization import AuthorizationServer
from jarvis_v2.backend.event_bus import EventBus
from jarvis_v2.core.dispatch import DispatchStore
from jarvis_v2.core.registry import ModuleRegistry
from jarvis_v2.runtime import RuntimeService


ROOT = Path(__file__).parents[1]


class RuntimeServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        path = Path(self.temp.name) / "runtime.sqlite"
        registry = ModuleRegistry.from_config(ROOT / "config/modules.json")
        authorization = AuthorizationServer(registry)
        identity = authorization.register_identity("runtime-client", "runtime")
        authorization.grant(
            identity.identity_id,
            "runtime",
            ("runtime:read", "runtime:health"),
            grant_id="runtime-grant",
        )
        self.service = RuntimeService(
            registry, authorization, DispatchStore(path), EventBus(path)
        )

    def tearDown(self):
        self.service.close()
        self.temp.cleanup()

    @staticmethod
    def request(path, scope="runtime:read", **extra):
        return {
            "method": extra.pop("method", "GET"),
            "path": path,
            "identity_id": extra.pop("identity_id", "runtime-client"),
            "scope": scope,
            **extra,
        }

    def test_authenticated_health_and_scope_denial(self):
        healthy = self.service.handle(self.request("/health", "runtime:health"))
        self.assertEqual(healthy.status, 200)
        self.assertEqual(healthy.body["module"], "runtime")
        self.assertEqual(self.service.handle(self.request("/health")).status, 403)
        self.assertEqual(
            self.service.handle(self.request("/health", "runtime:health", identity_id="unknown")).status,
            403,
        )
        self.assertEqual(
            self.service.handle({"method": "GET", "path": "/health"}).status,
            400,
        )

    def test_task_handoff_claim_ack_and_event_stream(self):
        created = self.service.handle(self.request(
            "/tasks",
            method="POST",
            body={
                "task_id": "runtime-task-1",
                "target_module": "core",
                "scope": "core:read",
                "acceptance": ["dispatch is acknowledged"],
                "correlation_id": "runtime-correlation-1",
                "input_refs": {"source": "fixture-ref"},
            },
        ))
        self.assertEqual(created.status, 201)
        dispatch_id = created.body["dispatch"]["dispatch_id"]
        event_id = created.body["event_id"]

        claimed = self.service.handle(self.request(
            f"/tasks/{dispatch_id}/claim",
            method="POST",
            body={"executor_id": "core-executor", "claim_id": "claim-1"},
        ))
        self.assertEqual(claimed.status, 200)
        acknowledged = self.service.handle(self.request(
            f"/tasks/{dispatch_id}/ack",
            method="POST",
            body={
                "executor_id": "core-executor",
                "claim_id": "claim-1",
                "status": "completed",
                "result": {"state": "done"},
            },
        ))
        self.assertEqual(acknowledged.status, 200)
        self.assertEqual(acknowledged.body["dispatch"]["status"], "completed")

        events = self.service.handle(self.request(
            "/events", consumer="runtime-events", limit=10
        ))
        self.assertEqual(events.status, 200)
        self.assertEqual([item["event_id"] for item in events.body["events"]], [event_id])
        self.assertEqual(events.body["events"][0]["payload"]["dispatch_id"], dispatch_id)

    def test_duplicate_handoff_is_idempotent_and_foreign_scope_is_rejected(self):
        body = {
            "task_id": "runtime-task-2",
            "target_module": "core",
            "scope": "core:read",
            "acceptance": "one result",
            "correlation_id": "runtime-correlation-2",
            "dispatch_id": "stable-dispatch-2",
        }
        first = self.service.handle(self.request("/tasks", method="POST", body=body))
        second = self.service.handle(self.request("/tasks", method="POST", body=body))
        self.assertEqual(first.status, 201)
        self.assertEqual(second.status, 201)
        self.assertEqual(first.body, second.body)
        denied = dict(body, scope="core:admin")
        self.assertEqual(
            self.service.handle(self.request("/tasks", method="POST", body=denied)).status,
            403,
        )

    def test_invalid_target_and_ack_claim_are_fail_closed(self):
        invalid = self.service.handle(self.request(
            "/tasks", method="POST", body={
                "task_id": "runtime-task-3", "target_module": "business",
                "scope": "business:read", "acceptance": "no", "correlation_id": "corr-3",
            }
        ))
        self.assertEqual(invalid.status, 400)
        bad_ack = self.service.handle(self.request(
            "/tasks/unknown/ack", method="POST", body={
                "executor_id": "core-executor", "claim_id": "wrong",
                "status": "completed", "result": {},
            }
        ))
        self.assertEqual(bad_ack.status, 409)


if __name__ == "__main__":
    unittest.main()
