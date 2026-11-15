"""MIG-015 regression coverage for the monitor boundary and identity overlay."""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.monitor import snapshot


ROOT = Path(__file__).resolve().parents[1]


class Mig015AcceptanceTests(unittest.TestCase):
    def test_identity_manifest_and_operator_docs_use_approved_roles(self):
        identities = json.loads((ROOT / "config/identities.json").read_text())
        self.assertEqual(
            {identities[key]["name"] for key in ("main_ai", "guardian", "infrastructure")},
            {"ARCHON", "AEGIS", "ATLAS"},
        )
        docs = "\n".join(
            (ROOT / path).read_text()
            for path in ("README.md", "docs/architecture/IDENTITIES.md", "docs/operations/ATLAS_TERMINAL_MONITOR.md")
        )
        for role in ("ARCHON", "AEGIS", "ATLAS"):
            self.assertIn(role, docs)

    def test_native_snapshot_is_read_only_and_does_not_invoke_runner(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "atlas.sqlite3"
            with sqlite3.connect(path) as db:
                db.executescript("""
                    CREATE TABLE tasks(
                      id TEXT PRIMARY KEY, priority INTEGER NOT NULL, module TEXT NOT NULL,
                      payload TEXT NOT NULL, state TEXT NOT NULL, created_id INTEGER NOT NULL,
                      lease TEXT, receipt TEXT, title TEXT NOT NULL DEFAULT '');
                    CREATE TABLE events(
                      seq INTEGER PRIMARY KEY, task_id TEXT NOT NULL,
                      kind TEXT NOT NULL, detail TEXT NOT NULL);
                    INSERT INTO tasks VALUES
                      ('CORE-015', 1, 'core', '{\"private\":\"hidden\"}', 'leased', 1, 'lease', NULL, 'Monitor');
                    INSERT INTO events VALUES (1, 'CORE-015', 'leased', 'private');
                """)
            before = hashlib.sha256(path.read_bytes()).digest()
            data = snapshot(path, source="atlas", show_objectives=True)
            after = hashlib.sha256(path.read_bytes()).digest()
            self.assertEqual(before, after)
            self.assertEqual(data["engine"], "atlas")
            self.assertEqual(data["active"][0]["id"], "CORE-015")
            self.assertNotIn("hidden", json.dumps(data))


if __name__ == "__main__":
    unittest.main()
