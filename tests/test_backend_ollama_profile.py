import unittest

from jarvis_v2.backend import (
    OllamaErrorEvidence,
    OllamaInferenceProfile,
    OllamaProfileError,
    classify_ollama_error,
    parse_ollama_probe,
    parse_ollama_telemetry,
)


class OllamaProfileTests(unittest.TestCase):
    def test_default_profile_is_reproducible_and_linux_only(self):
        profile = OllamaInferenceProfile()
        self.assertEqual(profile.as_dict(), {
            "model": "qwen3:8b",
            "platform": "linux",
            "num_ctx": 16_384,
            "num_predict": 128,
            "kv_cache_type": "q8_0",
            "flash_attn": True,
        })

    def test_measured_linux_probe_is_redacted_and_bound_to_profile(self):
        profile = OllamaInferenceProfile(model="qwen3:4b", num_ctx=4_096)
        evidence = parse_ollama_probe({
            "model": "qwen3:4b",
            "done": True,
            "response": "READY",
            "total_duration": 21_580_538_176,
            "prompt_eval_count": 14,
            "eval_count": 23,
            "secret": "must-not-be-retained",
        }, profile, artifact_sha256="a" * 64)
        self.assertEqual(evidence.as_dict()["profile"], profile.as_dict())
        self.assertNotIn("secret", evidence.as_dict())
        self.assertEqual(evidence.eval_count, 23)

    def test_invalid_profile_and_probe_states_are_rejected(self):
        for changes in (
            {"model": "qwen2.5:7b"},
            {"num_ctx": 512},
            {"num_predict": 0},
            {"num_predict": 4_097},
            {"kv_cache_type": "q8_1"},
            {"flash_attn": 1},
            {"platform": "windows"},
        ):
            with self.subTest(changes=changes), self.assertRaises(OllamaProfileError):
                OllamaInferenceProfile(**changes)
        profile = OllamaInferenceProfile(model="qwen3:4b", num_ctx=4_096)
        for payload in (
            {"model": "qwen3:8b", "done": True, "response": "READY", "total_duration": 1,
             "prompt_eval_count": 1, "eval_count": 1},
            {"model": "qwen3:4b", "done": False, "response": "READY", "total_duration": 1,
             "prompt_eval_count": 1, "eval_count": 1},
            {"model": "qwen3:4b", "done": True, "response": "NO", "total_duration": 1,
             "prompt_eval_count": 1, "eval_count": 1},
            {"model": "qwen3:4b", "done": True, "response": "READY", "total_duration": 0,
             "prompt_eval_count": 1, "eval_count": 1},
        ):
            with self.subTest(payload=payload), self.assertRaises(OllamaProfileError):
                parse_ollama_probe(payload, profile)

    def test_linux_telemetry_reports_rates_limits_and_unavailable_accelerator(self):
        profile = OllamaInferenceProfile(model="qwen3:4b", num_ctx=4_096)
        telemetry = parse_ollama_telemetry({
            "model": "qwen3:4b",
            "done": True,
            "context": [1, 2, 3, 4],
            "total_duration": 4_000_000_000,
            "prompt_eval_count": 20,
            "prompt_eval_duration": 2_000_000_000,
            "eval_count": 40,
            "eval_duration": 2_000_000_000,
            "resource_limits": {"num_gpu": 0},
        }, profile)
        self.assertEqual(telemetry.context_tokens, 4)
        self.assertEqual(telemetry.generated_tokens_per_second, 20.0)
        self.assertEqual(telemetry.as_dict()["accelerator"], "unavailable")
        self.assertEqual(telemetry.as_dict()["resource_limits"]["num_ctx"], 4_096)
        self.assertNotIn("context", telemetry.as_dict())

    def test_error_attribution_requires_a_bounded_category(self):
        error = classify_ollama_error({"error": "redacted", "error_category": "resource", "retryable": True})
        self.assertIsInstance(error, OllamaErrorEvidence)
        self.assertEqual(error.as_dict(), {"category": "resource", "retryable": True})
        for payload in (
            {"error": "redacted"},
            {"error": "redacted", "error_category": "other"},
        ):
            with self.subTest(payload=payload), self.assertRaises(OllamaProfileError):
                classify_ollama_error(payload)


if __name__ == "__main__":
    unittest.main()
