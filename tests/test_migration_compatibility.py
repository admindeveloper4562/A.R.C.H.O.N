import json
import shutil
import tempfile
import unittest
from pathlib import Path

from migration.adapters.legacy_contracts import (
    LegacyContractAdapter,
    MigrationCompatibilityError,
)


ROOT = Path(__file__).resolve().parents[1]


class MigrationCompatibilityTests(unittest.TestCase):
    def test_snapshot_maps_all_three_contract_areas(self):
        snapshot = LegacyContractAdapter(ROOT).snapshot()
        self.assertEqual(snapshot["execution"], "metadata_and_ast_only")
        self.assertEqual(len(snapshot["contracts"]["core"]), 2)
        self.assertEqual(len(snapshot["contracts"]["backend"]), 4)
        self.assertEqual(len(snapshot["contracts"]["runtime"]), 5)
        for paths in snapshot["v2_targets"].values():
            self.assertTrue(paths)

    def test_snapshot_contains_no_legacy_source_content(self):
        snapshot = LegacyContractAdapter(ROOT).snapshot()
        encoded = json.dumps(snapshot)
        self.assertNotIn("def ", encoded)
        self.assertNotIn("password", encoded.lower())

    def test_tampered_staged_blob_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            target = root / "migration/imported/core/tasks.py"
            target.write_bytes(target.read_bytes() + b"\n# tampered\n")
            with self.assertRaisesRegex(MigrationCompatibilityError, "digest"):
                LegacyContractAdapter(root).snapshot()

    def test_incomplete_contract_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            log = root / "migration/provenance/import-log.json"
            document = json.loads(log.read_text())
            document["entries"] = document["entries"][1:]
            log.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(MigrationCompatibilityError, "incomplete"):
                LegacyContractAdapter(root).snapshot()


if __name__ == "__main__":
    unittest.main()
