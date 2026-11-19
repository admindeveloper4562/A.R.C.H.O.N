import tempfile
import unittest
from pathlib import Path

from jarvis_v2.cli import main
from jarvis_v2.system_inventory import collect_inventory, compare_inventories, inventory_digest, scan_filesystem


class SystemInventoryTests(unittest.TestCase):
    def test_scan_is_metadata_only_bounded_and_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "nested").mkdir()
            (root / "nested" / "file.txt").write_text("private content", encoding="utf-8")
            (root / "link").symlink_to(root / "nested", target_is_directory=True)
            inventory = scan_filesystem(root, max_entries=20)
            paths = {item["path"] for item in inventory["entries"]}
            self.assertIn(str(root / "nested" / "file.txt"), paths)
            self.assertIn(str(root / "link"), paths)
            self.assertNotIn(str(root / "link" / "file.txt"), paths)
            self.assertFalse(inventory["coverage"]["symlink_recursion"])

    def test_digest_and_comparison_ignore_collection_time(self):
        old = {
            "collected_at": "old",
            "hardware": {"cpu": "old"},
            "filesystem": {"entries": [{"path": "/a", "size": 1}], "capacity": {"free": 10}},
        }
        new = {
            "collected_at": "new",
            "hardware": {"cpu": "new"},
            "filesystem": {
                "entries": [{"path": "/a", "size": 2}, {"path": "/b"}],
                "capacity": {"free": 9},
            },
        }
        self.assertEqual(inventory_digest(old), inventory_digest({**old, "collected_at": "new"}))
        result = compare_inventories(old, new)
        self.assertEqual(result["added"], ["/b"])
        self.assertEqual(result["changed"], ["/a"])
        self.assertEqual(result["changed_sections"], ["hardware"])
        self.assertTrue(result["capacity_changed"])

    def test_inventory_reports_model_and_acceleration_capability_slots(self):
        with tempfile.TemporaryDirectory() as temp:
            inventory = collect_inventory(
                root=Path(temp),
                max_entries=10,
                runner=lambda _args: (0, "safe capability metadata", ""),
            )
            self.assertIn("runtime_capabilities", inventory)
            self.assertIn("ollama_models", inventory["runtime_capabilities"]["model_runtimes"])
            self.assertIn("nvidia_smi", inventory["runtime_capabilities"]["acceleration"])

    def test_inventory_cli_writes_private_output_and_returns_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "inventory.json"
            self.assertEqual(
                main(["inventory", "--root", str(root), "--max-entries", "20", "--output", str(output)]),
                0,
            )
            self.assertTrue(output.is_file())
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
