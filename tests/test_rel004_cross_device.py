import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import (
    EffectJournal,
    GatewayRouter,
    HandoffError,
    HandoffStore,
    LocalAgentJob,
    NodeManifest,
    ProviderCapability,
    ProviderRegistry,
    ProviderRequirements,
    WindowsAgentRegistry,
)


class Rel004CrossDeviceTests(unittest.TestCase):
    def test_context_handoff_and_tool_effects_reconstruct_without_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "rel004.sqlite"
            handoff_args = {
                "source_provider": "codex",
                "target_provider": "ollama",
                "permission_scopes": ["backend:read"],
                "tool_effects": [{"effect_id": "read-1", "status": "accepted"}],
                "context": {"checkpoint": "rel004-c1", "task_id": "REL-004"},
            }
            with HandoffStore(database) as store:
                store.handoff("REL-004", "rel004-handoff", **handoff_args)
            with HandoffStore(database) as reopened:
                restored = reopened.get("rel004-handoff")
                replay = reopened.handoff("REL-004", "rel004-handoff", **handoff_args)
                self.assertEqual(restored, replay)
                self.assertEqual(restored["context"]["task_id"], "REL-004")
                with self.assertRaises(HandoffError):
                    reopened.handoff(
                        "REL-004", "rel004-handoff", **{
                            **handoff_args,
                            "tool_effects": [{"effect_id": "write-1", "status": "accepted"}],
                        }
                    )

            with EffectJournal(database) as journal:
                prepared = journal.prepare(
                    "rel004-tool-1", "REL-004", operation="inference.record",
                    target="ollama-local", request={"result_sha256": "b" * 64},
                )
                self.assertTrue(prepared["execution_permitted"])
                completed = journal.complete("rel004-tool-1", {"result_sha256": "b" * 64})
                replay = journal.prepare(
                    "rel004-tool-1", "REL-004", operation="inference.record",
                    target="ollama-local", request={"result_sha256": "b" * 64},
                )
                self.assertFalse(replay["execution_permitted"])
                self.assertEqual(replay["result"], completed["result"])

    def test_explicit_provider_handoff_and_windows_job_idempotency(self):
        capabilities = [
            ProviderCapability(
                provider_id="codex", model="gpt-5.6-luna", context_window=32_000,
                tools=frozenset(), privacy_scopes=frozenset({"public_metadata"}),
                locality="remote", quota_remaining=2, available=True,
            ),
            ProviderCapability(
                provider_id="ollama", model="qwen3-8b", context_window=16_384,
                tools=frozenset(), privacy_scopes=frozenset({"public_metadata"}),
                locality="local", quota_remaining=2, available=True,
            ),
        ]
        router = GatewayRouter(ProviderRegistry(capabilities))
        requirements = ProviderRequirements(
            context_tokens=16_000, tools=frozenset(), privacy_scope="public_metadata",
            locality="any", quota_units=1,
        )
        first_requirements = ProviderRequirements(
            context_tokens=16_000, tools=frozenset(), privacy_scope="public_metadata",
            locality="any", quota_units=1, requested_provider="codex",
        )
        first = router.route("REL-004", first_requirements)
        handed = router.route("REL-004", requirements, allow_handoff=True, handoff_provider="ollama")
        self.assertEqual((first.status, first.provider_id), ("routed", "codex"))
        self.assertEqual((handed.status, handed.provider_id), ("routed", "ollama"))

        now = [100.0]
        registry = WindowsAgentRegistry(clock=lambda: now[0], heartbeat_age_seconds=30)
        registry.register_node(NodeManifest(
            node_id="windows-rel004", agent_version="1.0.0", model="qwen3-8b",
            capabilities=frozenset({"summarize"}), data_scopes=frozenset({"public_metadata"}),
        ))
        registry.heartbeat("windows-rel004")
        job = registry.submit(LocalAgentJob(
            job_id="rel004-job", idempotency_key="rel004-idempotency", operation="summarize",
            input_sha256="a" * 64, required_scope="public_metadata", deadline_at=1_000,
            task_id="REL-004", requested_model="qwen3-8b",
        ))
        lease = registry.lease(job.job_id, "windows-rel004")
        result = registry.complete(job.job_id, "windows-rel004", lease.lease_id, result_sha256="b" * 64)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            registry.complete(job.job_id, "windows-rel004", lease.lease_id, result_sha256="b" * 64),
            result,
        )


if __name__ == "__main__":
    unittest.main()
