import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.import_legacy import prepare_manifest


class MigrationGuardrailTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo, self.dest = root / "old", root / "new"
        self.repo.mkdir()
        self.dest.mkdir()

        def git(*args):
            return subprocess.run(
                ["git", "-C", str(self.repo), *args],
                capture_output=True, text=True, check=True,
            ).stdout.strip()

        self.git = git
        git("init", "-b", "develop")
        git("config", "user.name", "Test")
        git("config", "user.email", "t@example.test")
        (self.repo / "source.py").write_text("answer = 42\n", encoding="utf-8")
        git("add", "source.py")
        git("commit", "-m", "initial")
        self.commit = git("rev-parse", "HEAD")
        git("remote", "add", "origin", "https://github.com/admindeveloper4562/personal-jarvis.git")
        git("update-ref", "refs/remotes/origin/develop", self.commit)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, **entry):
        value = {"area": "core", "ref": "develop", "source": "source.py",
                 "target": "migration/imported/core/source.py"}
        value.update(entry)
        return {"schema": "jarvis-v2.legacy-import/1", "entries": [value]}

    def test_dry_run_and_apply_preserve_commit_provenance(self):
        before = self.git("status", "--porcelain")
        manifest = self.manifest(expected_source_commit=self.commit)
        report = prepare_manifest(self.repo, self.dest, manifest)
        self.assertTrue(report["dry_run"])
        self.assertFalse((self.dest / "migration").exists())
        self.assertEqual(before, self.git("status", "--porcelain"))

        applied = prepare_manifest(self.repo, self.dest, manifest, apply=True)
        self.assertEqual(applied["entries"][0]["source_commit"], self.commit)
        log = json.loads((self.dest / "migration/provenance/import-log.json").read_text())
        self.assertEqual(log["entries"][0]["source_commit"], self.commit)
        self.assertEqual(log["entries"][0]["sha256"], report["entries"][0]["sha256"])

    def test_mismatched_commit_fails_before_writing(self):
        manifest = self.manifest(expected_source_commit="0" * 40)
        with self.assertRaises(ValueError):
            prepare_manifest(self.repo, self.dest, manifest, apply=True)
        self.assertFalse((self.dest / "migration").exists())

    def test_case_only_collisions_fail_before_writing(self):
        (self.dest / "migration/imported/core").mkdir(parents=True)
        (self.dest / "migration/imported/core/Source.py").write_text("existing\n")
        with self.assertRaises(FileExistsError):
            prepare_manifest(self.repo, self.dest, self.manifest(), apply=True)
        self.assertEqual("existing\n", (self.dest / "migration/imported/core/Source.py").read_text())

    def test_case_only_collisions_between_entries_fail_closed(self):
        manifest = {"schema": "jarvis-v2.legacy-import/1", "entries": [
            {"area": "core", "ref": "develop", "source": "source.py",
             "target": "migration/imported/core/one.py"},
            {"area": "core", "ref": "develop", "source": "source.py",
             "target": "migration/imported/core/ONE.py"},
        ]}
        with self.assertRaises(FileExistsError):
            prepare_manifest(self.repo, self.dest, manifest, apply=True)
        self.assertFalse((self.dest / "migration").exists())


if __name__ == "__main__":
    unittest.main()
