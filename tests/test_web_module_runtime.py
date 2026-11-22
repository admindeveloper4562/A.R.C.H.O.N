import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from apps.web.module_runtime import ModuleRuntime, ModuleRuntimeError


class ModuleRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repository = self.root / "repo"
        self.repository.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repository)], check=True)
        (self.repository / "src").mkdir()
        (self.repository / "src" / "module.py").write_text('answer = "alpha-local"\n', encoding="utf-8")
        (self.repository / "docs" / "architecture").mkdir(parents=True)
        (self.repository / "docs" / "architecture" / "module.md").write_text("alpha architecture", encoding="utf-8")
        (self.repository / "docs" / "final-audit").mkdir(parents=True)
        (self.repository / "docs" / "final-audit" / "private.md").write_text("alpha private host data", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repository), "add", "."], check=True)
        self.state = self.root / "state"
        self.state.mkdir(mode=0o700)
        self.runtime = ModuleRuntime(self.state, self.repository)

    def tearDown(self):
        self.temp.cleanup()

    def test_research_uses_current_tracked_sources_and_skips_audit_data(self):
        first = self.runtime.snapshot("research", query="alpha")
        items = first["sections"][0]["items"]
        self.assertEqual({item["title"] for item in items}, {"src/module.py", "docs/architecture/module.md"})
        first_sha = first["snapshot_sha"]

        (self.repository / "src" / "module.py").write_text('answer = "beta-local"\n', encoding="utf-8")
        second = self.runtime.snapshot("research", query="beta")
        self.assertNotEqual(first_sha, second["snapshot_sha"])
        self.assertEqual([item["title"] for item in second["sections"][0]["items"]], ["src/module.py"])
        alpha_items = self.runtime.snapshot("research", query="alpha")["sections"][0]["items"]
        self.assertEqual({item["title"] for item in alpha_items}, {"docs/architecture/module.md"})

    def test_local_module_stores_open_and_remain_private(self):
        for module in ("tws", "wic", "finance", "automation"):
            self.assertTrue(self.runtime.snapshot(module)["sections"])
        module_dir = self.state / "modules"
        self.assertEqual(os.stat(module_dir).st_mode & 0o777, 0o700)
        for path in module_dir.iterdir():
            if path.suffix == ".sqlite3":
                self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)

    def test_unknown_module_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "module_data_unavailable"):
            self.runtime.snapshot("unknown")

    def test_allowlisted_local_actions_persist_and_reject_unknown_effects(self):
        self.runtime.action("tws", "add_wing", {"wing_id": "local-wing", "name": "Local wing"})
        self.runtime.action("tws", "create_quest", {
            "quest_id": "local-quest", "wing_id": "local-wing", "title": "Local quest",
        })
        tws = self.runtime.snapshot("tws")
        self.assertEqual(tws["metrics"][0]["value"], "1")
        self.assertEqual(tws["metrics"][1]["value"], "1")

        self.runtime.action("finance", "open_paper_account", {
            "account_id": "test-account", "scope_id": "local-paper", "currency": "THB", "cash_satang": 1000,
        })
        self.runtime.action("finance", "place_paper_order", {
            "order_id": "test-order", "account_id": "test-account", "symbol": "TEST",
            "side": "buy", "quantity": 2, "price_satang": 100,
        })
        result = self.runtime.action("finance", "fill_paper_order", {"order_id": "test-order"})
        self.assertEqual(result["mode"], "paper_only")
        self.assertEqual(result["record"]["status"], "filled")
        self.assertEqual(self.runtime.snapshot("finance")["metrics"][1]["value"], "1")

        due_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.runtime.action("automation", "schedule_once", {
            "schedule_id": "test-reminder", "message": "Local reminder", "due_at": due_at,
        })
        self.runtime.action("automation", "schedule_once", {
            "schedule_id": "due-reminder", "message": "Due reminder",
            "due_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        })
        automation = self.runtime.snapshot("automation")
        self.assertEqual(automation["metrics"][0]["value"], "2")
        self.assertEqual(automation["metrics"][1]["value"], "1")
        self.assertEqual(automation["sections"][1]["items"][0]["schedule_id"], "due-reminder")
        self.runtime.action("automation", "cancel_schedule", {"schedule_id": "due-reminder"})
        self.assertEqual(self.runtime.snapshot("automation")["metrics"][0]["value"], "1")

        with self.assertRaisesRegex(ModuleRuntimeError, "module_action_not_allowed"):
            self.runtime.action("core", "execute", {"command": "anything"})
        with self.assertRaisesRegex(ModuleRuntimeError, "module_action_invalid"):
            self.runtime.action("tws", "add_wing", {"wing_id": "bad", "name": "Bad", "path": "/tmp"})


if __name__ == "__main__":
    unittest.main()
