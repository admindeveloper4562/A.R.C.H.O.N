import unittest

from jarvis_v2.guardian import (
    GuardianModelError,
    LocalGuardianModel,
)


class GuardianModelTests(unittest.TestCase):
    def test_local_model_and_inference_are_probed_without_retaining_output(self):
        calls = []

        def runner(command, timeout):
            calls.append((command, timeout))
            return 0

        health = LocalGuardianModel(runner=runner, timeout_seconds=7).probe()
        self.assertTrue(health.available)
        self.assertTrue(health.inference_verified)
        self.assertTrue(health.deterministic_stop_available)
        self.assertEqual(health.provider, "ollama")
        self.assertEqual(calls, [
            (["ollama", "show", "qwen3:4b"], 7),
            (["ollama", "run", "qwen3:4b", "Reply READY only"], 7),
        ])

    def test_missing_model_does_not_fallback_and_stop_remains_available(self):
        health = LocalGuardianModel(
            model="qwen3:4b",
            runner=lambda command, timeout: 1,
        ).probe()
        self.assertFalse(health.available)
        self.assertFalse(health.inference_verified)
        self.assertEqual(health.reason, "model_unavailable")
        self.assertTrue(health.deterministic_stop_available)

    def test_inference_failure_is_distinct_from_model_presence(self):
        def runner(command, timeout):
            return 0 if command[1] == "show" else 1

        health = LocalGuardianModel(runner=runner).probe()
        self.assertFalse(health.available)
        self.assertEqual(health.reason, "inference_unavailable")

    def test_model_and_timeout_are_bounded(self):
        with self.assertRaises(GuardianModelError):
            LocalGuardianModel(model="gpt hosted")
        with self.assertRaises(GuardianModelError):
            LocalGuardianModel(timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
