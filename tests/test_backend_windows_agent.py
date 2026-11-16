import unittest
from typing import cast

from jarvis_v2.backend import (
    LocalAgentJob,
    NodeManifest,
    WindowsAgentError,
    WindowsAgentRegistry,
)


INPUT_SHA = "a" * 64
RESULT_SHA = "b" * 64


def node(**changes):
    values = {
        "node_id": "windows-1",
        "agent_version": "1.0.0",
        "model": "qwen3-8b",
        "capabilities": frozenset({"summarize", "classify"}),
        "data_scopes": frozenset({"public_metadata", "internal_metadata"}),
    }
    values.update(changes)
    return NodeManifest(**values)


def job(**changes):
    values = {
        "job_id": "job-1",
        "idempotency_key": "idem-1",
        "operation": "summarize",
        "input_sha256": INPUT_SHA,
        "required_scope": "public_metadata",
        "deadline_at": 1_000,
        "task_id": "BACK-021",
    }
    values.update(changes)
    return LocalAgentJob(**values)


class BackendWindowsAgentTests(unittest.TestCase):
    def setUp(self):
        self.now = [100.0]
        self.registry = WindowsAgentRegistry(clock=lambda: self.now[0], heartbeat_age_seconds=30)
        self.registry.register_node(node())
        self.registry.heartbeat("windows-1", cpu_percent=42.0, memory_bytes=1024, free_vram_bytes=2048)

    def test_identity_heartbeat_and_capability_routing(self):
        route = self.registry.route("summarize", "public_metadata")
        self.assertEqual((route.status, route.node_id, route.model), ("routed", "windows-1", "qwen3-8b"))
        snapshot = self.registry.node_snapshot("windows-1")
        heartbeat = cast(dict[str, object], snapshot["heartbeat"])
        self.assertEqual(heartbeat["status"], "online")
        self.assertEqual(heartbeat["free_vram_bytes"], 2048)

    def test_stale_or_incompatible_nodes_are_not_used(self):
        self.now[0] = 131.0
        self.assertEqual(self.registry.route("summarize", "public_metadata").status, "blocked")
        self.now[0] = 100.0
        self.registry.heartbeat("windows-1", status="draining")
        self.assertEqual(self.registry.route("summarize", "public_metadata").reason, "no_compatible_node")
        with self.assertRaises(WindowsAgentError):
            self.registry.heartbeat("missing")

    def test_bounded_job_idempotency_lease_and_checksum_completion(self):
        first = self.registry.submit(job())
        self.assertIs(self.registry.submit(job()), first)
        lease = self.registry.lease(first.job_id, "windows-1")
        result = self.registry.complete(first.job_id, "windows-1", lease.lease_id, result_sha256=RESULT_SHA)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            self.registry.complete(first.job_id, "windows-1", lease.lease_id, result_sha256=RESULT_SHA),
            result,
        )
        with self.assertRaises(WindowsAgentError):
            self.registry.complete(first.job_id, "other-node", lease.lease_id, result_sha256=RESULT_SHA)
        snapshot = self.registry.job_snapshot(first.job_id)
        result_snapshot = cast(dict[str, object], snapshot["result"])
        self.assertEqual(snapshot["status"], "completed")
        self.assertEqual(result_snapshot["result_sha256"], RESULT_SHA)
        with self.assertRaises(WindowsAgentError):
            self.registry.lease(first.job_id, "windows-1")

    def test_disconnect_requeues_and_duplicate_or_foreign_leases_fail(self):
        first = self.registry.submit(job())
        lease = self.registry.lease(first.job_id, "windows-1")
        with self.assertRaises(WindowsAgentError):
            self.registry.complete(first.job_id, "other-node", lease.lease_id, result_sha256=RESULT_SHA)
        self.registry.heartbeat("windows-1", status="offline")
        self.assertEqual(self.registry.reconcile(), 1)
        self.assertEqual(self.registry.job_snapshot(first.job_id)["status"], "queued")

    def test_invalid_manifest_and_job_schema_fail_closed(self):
        with self.assertRaises(WindowsAgentError):
            node(platform="linux")
        with self.assertRaises(WindowsAgentError):
            node(capabilities=frozenset({"execute_shell"}))
        with self.assertRaises(WindowsAgentError):
            job(input_sha256="not-a-digest")
        with self.assertRaises(WindowsAgentError):
            job(required_scope="unknown")
        self.registry.submit(job())
        with self.assertRaises(WindowsAgentError):
            self.registry.submit(job(idempotency_key="idem-1", job_id="different", deadline_at=1001))


if __name__ == "__main__":
    unittest.main()
