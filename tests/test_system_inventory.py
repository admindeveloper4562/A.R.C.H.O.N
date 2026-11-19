import tempfile
import unittest
from pathlib import Path

from jarvis_v2.cli import main
from jarvis_v2.system_inventory import InventoryError, collect_inventory, compare_inventories, inventory_digest, scan_filesystem


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

    def test_scan_cursor_resumes_without_duplicates_or_root_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("a", "b", "c"):
                (root / name).mkdir()
                (root / name / "item").write_text("metadata only", encoding="utf-8")
            first = scan_filesystem(root, max_entries=3)
            self.assertTrue(first["coverage"]["truncated"])
            cursor = first["coverage"]["resume_cursor"]
            second = scan_filesystem(root, max_entries=20, resume_cursor=cursor)
            paths = [entry["path"] for entry in first["entries"] + second["entries"]]
            self.assertEqual(len(paths), len(set(paths)))
            self.assertEqual(set(paths), {str(path) for path in root.rglob("*")} | {str(root)})
            self.assertFalse(second["coverage"]["truncated"])
            self.assertIsNone(second["coverage"]["resume_cursor"])

    def test_scan_cursor_cannot_change_root_or_cross_mount(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = scan_filesystem(root, max_entries=1)
            cursor = dict(first["coverage"]["resume_cursor"])
            cursor["root"] = str(root / "other")
            with self.assertRaisesRegex(InventoryError, "resume cursor"):
                scan_filesystem(root, max_entries=2, resume_cursor=cursor)

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
