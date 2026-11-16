import unittest

from jarvis_v2.backend import (
    ProviderCapability,
    ProviderRegistry,
    ProviderRegistryError,
    ProviderRequirements,
)


def capability(**overrides):
    values = {
        "provider_id": "codex",
        "model": "gpt-5.6-luna",
        "context_window": 32_000,
        "tools": frozenset({"filesystem.read", "git.inspect"}),
        "privacy_scopes": frozenset({"public_metadata", "internal_metadata"}),
        "locality": "remote",
        "quota_remaining": 10,
    }
    values.update(overrides)
    return ProviderCapability(**values)


class BackendProviderRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = ProviderRegistry([capability()])

    def test_compatible_request_is_selected(self):
        result = self.registry.negotiate(ProviderRequirements(
            context_tokens=16_000,
            tools=frozenset({"filesystem.read"}),
            privacy_scope="internal_metadata",
            locality="remote",
            requested_model="gpt-5.6-luna",
        ))
        self.assertEqual(result.status, "available")
        self.assertEqual(result.selected_provider, "codex")
        self.assertEqual(result.reason, "capabilities_satisfied")

    def test_each_dispatch_requirement_blocks_incompatible_provider(self):
        cases = (
            ({"context_tokens": 64_000}, "context_window_insufficient"),
            ({"tools": frozenset({"filesystem.write"})}, "tool_support_missing"),
            ({"privacy_scope": "scoped_private"}, "privacy_scope_unavailable"),
            ({"locality": "local"}, "locality_mismatch"),
            ({"quota_units": 11}, "quota_unavailable"),
        )
        for changes, reason in cases:
            values = {
                "context_tokens": 1_000,
                "tools": frozenset(),
                "privacy_scope": "public_metadata",
                "locality": "any",
                "quota_units": 1,
            }
            values.update(changes)
            with self.subTest(reason=reason):
                result = self.registry.negotiate(ProviderRequirements(**values))
                self.assertEqual((result.status, result.reason), ("blocked", reason))

    def test_requested_identity_does_not_silently_fallback(self):
        result = self.registry.negotiate(ProviderRequirements(
            context_tokens=1,
            tools=frozenset(),
            privacy_scope="public_metadata",
            requested_provider="missing",
            requested_model="gpt-6-sol",
        ))
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.reason, "requested_provider_unavailable")

    def test_invalid_capabilities_and_requirements_are_rejected(self):
        with self.assertRaises(ProviderRegistryError):
            capability(privacy_scopes=frozenset({"backend:write"}))
        with self.assertRaises(ProviderRegistryError):
            ProviderRequirements(context_tokens=1, tools=frozenset(), privacy_scope="public_metadata", locality="any", quota_units=0)
        with self.assertRaises(ProviderRegistryError):
            ProviderRequirements(context_tokens=1, tools=frozenset({"bad tool"}), privacy_scope="public_metadata")


if __name__ == "__main__":
    unittest.main()
