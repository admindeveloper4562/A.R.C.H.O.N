import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import (
    TaskCapabilityError,
    TaskCapabilityManifest,
    validate_task_request,
)


class TaskCapabilityTests(unittest.TestCase):
    def test_manifest_allows_only_granted_operation_and_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = TaskCapabilityManifest.create(["index"], [root])
            request = validate_task_request(manifest, "index", "A" * 64, path=root / "input.txt")
            self.assertEqual(request.input_sha256, "a" * 64)
            self.assertEqual(request.path, root / "input.txt")
            self.assertEqual(manifest.as_dict()["platform"], "linux")

    def test_disallowed_operation_and_path_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = TaskCapabilityManifest.create(["index"], [root])
            with self.assertRaisesRegex(TaskCapabilityError, "operation"):
                validate_task_request(manifest, "classify", "a" * 64)
            with self.assertRaisesRegex(TaskCapabilityError, "sandbox"):
                validate_task_request(manifest, "index", "a" * 64, path=root.parent / "outside.txt")
            with self.assertRaises(TaskCapabilityError):
                validate_task_request(manifest, "index", "not-a-digest")

    def test_relative_and_symlink_escape_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "allowed"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            link = root / "escape"
            link.symlink_to(outside, target_is_directory=True)
            manifest = TaskCapabilityManifest.create(["index"], [root])
            with self.assertRaisesRegex(TaskCapabilityError, "absolute"):
                validate_task_request(manifest, "index", "a" * 64, path="relative.txt")
            with self.assertRaisesRegex(TaskCapabilityError, "sandbox"):
                validate_task_request(manifest, "index", "a" * 64, path=link / "data.txt")


if __name__ == "__main__":
    unittest.main()
