import json
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.authorization import AuthorizationServer
from jarvis_v2.backend.event_bus import EVENT_SCHEMA, EventBus
from jarvis_v2.core.registry import ModuleRegistry


ROOT = Path(__file__).parents[1]


class ReleaseCrossModuleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = json.loads((ROOT / "config/modules.json").read_text(encoding="utf-8"))
        cls.registry = ModuleRegistry.from_config(ROOT / "config/modules.json")

    def test_every_configured_module_has_a_valid_identity_and_permission_fixture(self):
        entries = self.modules["modules"]
        self.assertFalse(self.modules["business_module_enabled"])
        self.assertEqual(len(entries), 10)

        auth = AuthorizationServer(self.registry)
        for entry in entries:
            key = entry["key"]
            capability = self.registry.resolve(entry["id"])
            self.assertEqual(capability.key, key)
            self.assertTrue(entry["name"])
            identity = auth.register_identity(f"{key}-fixture", capability.key)
            auth.grant(
                identity.identity_id,
                capability.key,
                (f"{key}:read", f"{key}:health"),
                grant_id=f"grant-{key}",
            )
            self.assertTrue(auth.authorize(identity.identity_id, key, f"{key}:read"))
            self.assertTrue(auth.authorize(identity.identity_id, key, f"{key}:health"))

            other = "backend" if key != "backend" else "core"
            self.assertFalse(auth.authorize(identity.identity_id, other, f"{other}:read"))

    def test_each_module_can_publish_and_deliver_the_versioned_event_fixture(self):
        keys = [entry["key"] for entry in self.modules["modules"]]
        with tempfile.TemporaryDirectory() as directory:
            with EventBus(Path(directory) / "events.sqlite") as bus:
                events = [
                    bus.publish(
                        "module.health",
                        key,
                        f"health-{key}",
                        1,
                        {"module": key, "state": "fixture"},
                        correlation_id=f"fixture-{key}",
                        idempotency_key=f"health-{key}",
                    )
                    for key in keys
                ]
                self.assertEqual({event.schema for event in events}, {EVENT_SCHEMA})
                self.assertEqual({event.producer for event in events}, set(keys))
                self.assertEqual(
                    {event.event_id for event in bus.pending("release-qc")},
                    {event.event_id for event in events},
                )

                delivered = []
                for event in events:
                    receipt = bus.deliver(
                        "release-qc",
                        event.event_id,
                        lambda received: delivered.append(received.producer) or {"accepted": True},
                    )
                    self.assertEqual(receipt.status, "completed")
                self.assertEqual(delivered, keys)
                self.assertEqual(bus.pending("release-qc"), [])


if __name__ == "__main__":
    unittest.main()
