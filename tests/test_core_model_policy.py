import unittest

from jarvis_v2.core import ModelPolicy, ModelPolicyError


class CoreModelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = ModelPolicy({"gpt-5.6-luna"})

    def test_available_requested_alias_is_selected(self):
        result = self.policy.resolve("gpt-5.6-luna")

        self.assertEqual(result.status, "available")
        self.assertEqual(result.selected, "gpt-5.6-luna")
        self.assertEqual(result.reason, "requested_model")

    def test_unsupported_alias_blocks_without_silent_fallback(self):
        result = self.policy.resolve("gpt-6-sol-medium")

        self.assertEqual(result.status, "blocked")
        self.assertIsNone(result.selected)
        self.assertEqual(result.reason, "unsupported_model_alias")

    def test_fallback_requires_explicit_opt_in_and_target(self):
        requested = "gpt-6-sol-medium"

        self.assertEqual(
            self.policy.resolve(requested, fallback="gpt-5.6-luna").reason,
            "unsupported_model_alias",
        )
        self.assertEqual(
            self.policy.resolve(requested, allow_fallback=True).reason,
            "fallback_not_configured",
        )
        result = self.policy.resolve(
            requested, fallback="gpt-5.6-luna", allow_fallback=True
        )
        self.assertEqual(result.status, "fallback")
        self.assertEqual(result.selected, "gpt-5.6-luna")
        self.assertEqual(result.reason, "explicit_fallback_policy")

    def test_unavailable_fallback_is_blocked(self):
        result = self.policy.resolve(
            "gpt-6-sol-medium", fallback="gpt-5.6-luna-high", allow_fallback=True
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.reason, "fallback_unavailable")
        self.assertIsNone(result.selected)

    def test_alias_validation_is_bounded(self):
        with self.assertRaises(ModelPolicyError):
            ModelPolicy(["gpt 6"])
        with self.assertRaises(ModelPolicyError):
            self.policy.resolve(" ")


if __name__ == "__main__":
    unittest.main()
