import tempfile
import unittest
from pathlib import Path

from jarvis_v2.runtime import FileActionError, FileActionService


class FileActionServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "files"
        self.root.mkdir()
        self.db = Path(self.temp.name) / "actions.sqlite"
        self.trash = Path(self.temp.name) / "trash"
        self.log = Path(self.temp.name) / "DELETE-LOGS.md"
        self.service = FileActionService(
            self.db,
            allowed_roots=[self.root],
            trash_root=self.trash,
            audit_log=self.log,
        )

    def tearDown(self):
        self.service.close()
        self.temp.cleanup()

    def test_preview_requires_one_file_and_directory_approval_is_forbidden(self):
        target = self.root / "draft.txt"
        target.write_text("draft", encoding="utf-8")
        preview = self.service.preview(target)
        self.assertEqual(preview["action"], "trash_file")
        with self.assertRaisesRegex(FileActionError, "directory-wide"):
            self.service.propose_directory(self.root, "cleanup")
        with self.assertRaisesRegex(FileActionError, "approval"):
            self.service.trash_file("A" * 32)

    def test_each_file_requires_approval_and_trash_is_recoverable(self):
        first = self.root / "first.txt"
        second = self.root / "second.txt"
        first.write_text("one", encoding="utf-8")
        second.write_text("two", encoding="utf-8")
        request = self.service.propose_trash(first, "remove one obsolete draft")
        self.assertEqual(request.model_context()["state"], "pending")
        with self.assertRaisesRegex(FileActionError, "approval"):
            self.service.trash_file(request.request_id)
        self.service.decide(request.request_id, True)
        trash_path = self.service.trash_file(request.request_id)
        self.assertFalse(first.exists())
        self.assertTrue(trash_path.is_file())
        self.assertTrue(second.exists())
        manifest = self.service.trash_manifest(request.request_id)
        self.assertIsNotNone(manifest)
        self.assertIn("moved_to_trash", self.log.read_text(encoding="utf-8"))
        restore_request = self.service.propose_restore(request.request_id, "restore the draft")
        self.service.decide(restore_request.request_id, True)
        restored = self.service.restore_file(restore_request.request_id)
        self.assertEqual(restored, first)
        self.assertEqual(first.read_text(encoding="utf-8"), "one")
        self.assertIn("restored_from_trash", self.log.read_text(encoding="utf-8"))

    def test_identity_change_and_protected_or_outside_paths_fail_closed(self):
        target = self.root / "draft.txt"
        target.write_text("draft", encoding="utf-8")
        request = self.service.propose_trash(target, "remove draft")
        target.write_text("changed", encoding="utf-8")
        self.service.decide(request.request_id, True)
        with self.assertRaisesRegex(FileActionError, "identity"):
            self.service.trash_file(request.request_id)
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        with self.assertRaisesRegex(FileActionError, "outside"):
            self.service.propose_trash(outside, "no")
        protected = self.root / ".env"
        protected.write_text("x", encoding="utf-8")
        with self.assertRaisesRegex(FileActionError, "outside|protected"):
            self.service.propose_trash(protected, "no")

    def test_audit_is_redacted_and_no_direct_delete_operation_exists(self):
        target = self.root / "draft.txt"
        target.write_text("draft", encoding="utf-8")
        request = self.service.propose_trash(target, "owner reason")
        events = self.service.audit()
        self.assertTrue(events)
        self.assertNotIn(str(target), str(events))
        self.assertNotIn("owner reason", str(events))
        self.assertFalse(hasattr(self.service, "delete_file"))
        self.assertFalse(hasattr(self.service, "execute_many"))


if __name__ == "__main__":
    unittest.main()
