import hashlib
import unittest

from jarvis_v2.automation.device_registry import AuthenticatedDeviceRegistry, DeviceAuthError
from jarvis_v2.backend import LocalAgentJob, NodeManifest, WindowsAgentRegistry


OLD_KEY = b"old-device-key-" + b"a" * 32
NEW_KEY = b"new-device-key-" + b"b" * 32
INPUT_SHA = "a" * 64
RESULT_SHA = "b" * 64


def manifest() -> NodeManifest:
    return NodeManifest(
        node_id="windows-1",
        agent_version="1.0.0",
        model="qwen3-8b",
        capabilities=frozenset({"summarize"}),
        data_scopes=frozenset({"public_metadata"}),
    )


def job(job_id: str = "job-1") -> LocalAgentJob:
    return LocalAgentJob(
        job_id=job_id,
        idempotency_key=job_id,
        operation="summarize",
        input_sha256=INPUT_SHA,
        required_scope="public_metadata",
        deadline_at=1_000,
        task_id="AUTO-003",
    )


class AuthenticatedDeviceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = AuthenticatedDeviceRegistry(
            WindowsAgentRegistry(clock=lambda: 100.0, heartbeat_age_seconds=30)
        )
        self.registry.register(manifest(), OLD_KEY)
        self.registry.heartbeat(
            "windows-1",
            "key-1",
            AuthenticatedDeviceRegistry.make_proof(OLD_KEY, "heartbeat:windows-1:online"),
        )

    def test_registration_is_idempotent_and_snapshot_contains_only_digest(self):
        first = self.registry.register(manifest(), OLD_KEY)
        self.assertEqual(first.generation, 1)
        snapshot = self.registry.snapshot("windows-1")
        self.assertEqual(snapshot["device"]["key_sha256"], hashlib.sha256(OLD_KEY).hexdigest())
        self.assertNotIn(OLD_KEY.decode(), str(snapshot))

    def test_claim_requires_authentication_and_online_device(self):
        self.registry.submit(job())
        with self.assertRaises(DeviceAuthError):
            self.registry.claim("job-1", "windows-1", "key-1", "00" * 32)
        proof = AuthenticatedDeviceRegistry.make_proof(OLD_KEY, "claim:job-1")
        lease = self.registry.claim("job-1", "windows-1", "key-1", proof)
        self.assertEqual(lease.node_id, "windows-1")

    def test_revoked_device_cannot_claim_even_with_old_proof(self):
        self.registry.submit(job())
        self.registry.revoke("windows-1")
        proof = AuthenticatedDeviceRegistry.make_proof(OLD_KEY, "claim:job-1")
        with self.assertRaises(DeviceAuthError):
            self.registry.claim("job-1", "windows-1", "key-1", proof)

    def test_rotation_requires_current_key_and_fences_old_key(self):
        next_digest = hashlib.sha256(NEW_KEY).hexdigest()
        message = AuthenticatedDeviceRegistry.rotation_message("windows-1", "key-1", "key-2", next_digest)
        proof = AuthenticatedDeviceRegistry.make_proof(OLD_KEY, message)
        rotated = self.registry.rotate("windows-1", "key-1", "key-2", NEW_KEY, proof)
        self.assertEqual((rotated.key_id, rotated.generation), ("key-2", 2))
        with self.assertRaises(DeviceAuthError):
            self.registry.authenticate("windows-1", "key-1", "claim:job-1", proof)
        new_proof = AuthenticatedDeviceRegistry.make_proof(NEW_KEY, "claim:job-1")
        self.registry.submit(job())
        self.assertEqual(self.registry.claim("job-1", "windows-1", "key-2", new_proof).node_id, "windows-1")

    def test_complete_is_bound_to_authenticated_device_lease(self):
        self.registry.submit(job())
        lease = self.registry.claim(
            "job-1", "windows-1", "key-1",
            AuthenticatedDeviceRegistry.make_proof(OLD_KEY, "claim:job-1"),
        )
        proof = AuthenticatedDeviceRegistry.make_proof(
            OLD_KEY, AuthenticatedDeviceRegistry.complete_message("job-1", lease.lease_id, RESULT_SHA)
        )
        result = self.registry.complete("job-1", "windows-1", "key-1", proof, lease.lease_id, result_sha256=RESULT_SHA)
        self.assertEqual(result["status"], "completed")


if __name__ == "__main__":
    unittest.main()
