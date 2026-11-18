import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from astra_one.test_evidence_cache import EvidenceCache, build_cache_material, cache_key


class EvidenceCacheTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / ".git").mkdir()
        (self.root / "SECURITY.md").write_text("policy-v1\n", encoding="utf-8")
        (self.root / "requirements.txt").write_text("pytest==8\n", encoding="utf-8")
        (self.root / "candidate.py").write_text("VALUE = 1\n", encoding="utf-8")

    def material(self, **context):
        with patch("astra_one.test_evidence_cache.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = "a" * 40
            return build_cache_material(self.root, "sha256:image", ["python3", "-m", "unittest"], context)

    def test_key_contains_material_inputs_and_changes_with_source(self):
        first = self.material(fixture_sha="fixture-a")
        self.assertIsNotNone(first)
        first_key = cache_key(first)
        (self.root / "candidate.py").write_text("VALUE = 2\n", encoding="utf-8")
        second = self.material(fixture_sha="fixture-a")
        self.assertNotEqual(first["source_tree_sha"], second["source_tree_sha"])
        self.assertNotEqual(first_key, cache_key(second))

    def test_cache_only_reuses_a_success_and_rejects_stale_key(self):
        cache = EvidenceCache(self.root / "cache")
        material = self.material()
        key = cache_key(material)
        cache.store(key, {"passed": True, "exit_code": 0, "sandbox": "docker_no_network", "tests_detected": True})
        self.assertTrue(cache.load(key)["passed"])
        self.assertIsNone(cache.load("0" * 64))
        cache.store("1" * 64, {"passed": False, "exit_code": 1, "sandbox": "docker_no_network", "tests_detected": True})
        self.assertIsNone(cache.load("1" * 64))

    def test_context_change_invalidates_key(self):
        first = self.material(changed_files_sha="a")
        second = self.material(changed_files_sha="b")
        self.assertNotEqual(cache_key(first), cache_key(second))


if __name__ == "__main__":
    unittest.main()
