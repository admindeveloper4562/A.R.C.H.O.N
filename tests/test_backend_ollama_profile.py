import unittest

from jarvis_v2.backend import (
    OllamaInferenceProfile,
    OllamaProfileError,
    parse_ollama_probe,
)


class OllamaProfileTests(unittest.TestCase):
    def test_default_profile_is_reproducible_and_linux_only(self):
        profile = OllamaInferenceProfile()
        self.assertEqual(profile.as_dict(), {
            "model": "qwen3:8b",
            "platform": "linux",
            "num_ctx": 16_384,
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


if __name__ == "__main__":
    unittest.main()
