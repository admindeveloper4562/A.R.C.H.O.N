"""MIG-016 identity overlay and legacy compatibility coverage."""

import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.import_legacy import OPERATOR_IDENTITY, prepare_manifest


ROOT = Path(__file__).resolve().parents[1]


class Mig016IdentityTests(unittest.TestCase):
    def test_contract_keeps_module_ids_and_documents_legacy_names(self):
        modules = json.loads((ROOT / "config/modules.json").read_text())
        self.assertEqual([item["id"] for item in modules["modules"]], list(range(1, 11)))
        contract = (ROOT / "docs/migration/MIG-016_OPERATOR_IDENTITIES.md").read_text()
        for identity in ("ARCHON", "AEGIS", "ATLAS"):
            self.assertIn(identity, contract)
        for legacy in ("jarvis-v2.legacy-import/1", "jarvis-v2.legacy-provenance/1", "jarvis_v2"):
            self.assertIn(legacy, contract)

    def test_receipts_add_atlas_identity_without_rewriting_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, dest = root / "old", root / "new"
            repo.mkdir()
            dest.mkdir()

            def git(*args):
                return subprocess.run(
                    ["git", "-C", str(repo), *args],
                    capture_output=True, text=True, check=True,
                ).stdout.strip()

            git("init", "-b", "develop")
            git("config", "user.name", "Test")
            git("config", "user.email", "t@example.test")
            (repo / "source.py").write_text("module = 'core'\n")
            git("add", "source.py")
            git("commit", "-m", "initial")
            commit = git("rev-parse", "HEAD")
            git("remote", "add", "origin", "https://github.com/admindeveloper4562/personal-jarvis.git")
            git("update-ref", "refs/remotes/origin/develop", commit)

            db = dest / "records.sqlite3"
            with sqlite3.connect(db) as connection:
                connection.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, module TEXT NOT NULL)")
                connection.execute("INSERT INTO tasks VALUES ('CORE-001', 'core')")
            before = hashlib.sha256(db.read_bytes()).digest()

            report = prepare_manifest(repo, dest, {
                "schema": "jarvis-v2.legacy-import/1",
                "entries": [{
                    "area": "core", "ref": "develop", "source": "source.py",
                    "target": "migration/imported/core/source.py",
                }],
            }, apply=True)

            after = hashlib.sha256(db.read_bytes()).digest()
            self.assertEqual(OPERATOR_IDENTITY, "ATLAS")
            self.assertEqual(report["entries"][0]["operator_identity"], "ATLAS")
            provenance = json.loads((dest / "migration/provenance/import-log.json").read_text())
            self.assertEqual(provenance["operator_identity"], "ATLAS")
            self.assertEqual(before, after)
            self.assertEqual(
                provenance["schema"], "jarvis-v2.legacy-provenance/1"
            )


if __name__ == "__main__":
    unittest.main()
