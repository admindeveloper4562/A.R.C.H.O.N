import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis_v2.backend import backup as backup_module
from jarvis_v2.backend.backup import BackupError, BackupManager


class TestCipher:
    """Test-only cipher boundary; production callers supply approved crypto."""

    def seal(self, payload: bytes) -> bytes:
        return b"ARCHON-TEST-CIPHER\0" + payload

    def unseal(self, payload: bytes) -> bytes:
        prefix = b"ARCHON-TEST-CIPHER\0"
        if not payload.startswith(prefix):
            raise ValueError("invalid test envelope")
        return payload[len(prefix) :]


class BackendBackupTests(unittest.TestCase):
    def make_database(self, path: Path) -> None:
        with sqlite3.connect(path) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA wal_autocheckpoint=0")
            db.execute("PRAGMA user_version=7")
            db.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("INSERT INTO records(value) VALUES ('preserved')")
            db.commit()

    def test_backup_and_restore_preserve_schema_data_and_wal_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            backup = root / "backups" / "source.sqlite"
            restored = root / "restored.sqlite"
            self.make_database(source)
            with sqlite3.connect(source) as held:
                held.execute("PRAGMA wal_autocheckpoint=0")
                held.execute("INSERT INTO records(value) VALUES ('wal-data')")
                held.commit()
                manager = BackupManager()
                inspection = manager.inspect(source)
                self.assertEqual(inspection["journal_mode"], "wal")
                self.assertTrue(inspection["wal_present"])
                receipt = manager.create(source, backup)
                restored_receipt = manager.restore(
                    backup, restored, expected_schema_version=7
                )
                self.assertEqual(receipt.integrity, "ok")
                self.assertEqual(restored_receipt.integrity, "ok")
                self.assertEqual(os.stat(backup).st_mode & 0o777, 0o600)
            with sqlite3.connect(restored) as db:
                self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 7)
                self.assertEqual(
                    db.execute("SELECT value FROM records ORDER BY id").fetchall(),
                    [("preserved",), ("wal-data",)],
                )

    def test_destination_is_never_overwritten_and_source_is_not_mutated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            backup = root / "backup.sqlite"
            self.make_database(source)
            manager = BackupManager()
            first = manager.create(source, backup)
            source_sha = manager.inspect(source)["state_sha256"]
            with self.assertRaises(BackupError):
                manager.create(source, backup)
            self.assertEqual(first.source_state_sha256, source_sha)
            self.assertEqual(manager.inspect(source)["state_sha256"], source_sha)

    def test_explicit_cipher_round_trip_and_digest_fence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            backup = root / "backup.bin"
            restored = root / "restored.sqlite"
            self.make_database(source)
            manager = BackupManager()
            receipt = manager.create(source, backup, cipher=TestCipher())
            self.assertTrue(receipt.encrypted)
            self.assertNotEqual(backup.read_bytes()[:16], b"SQLite format 3\x00")
            with self.assertRaises(BackupError):
                manager.restore(backup, root / "bad.sqlite", expected_sha256="0" * 64, cipher=TestCipher())
            restored_receipt = manager.restore(backup, restored, cipher=TestCipher(), expected_sha256=receipt.backup_sha256)
            self.assertTrue(restored_receipt.encrypted)
            with sqlite3.connect(restored) as db:
                self.assertEqual(db.execute("SELECT value FROM records").fetchone()[0], "preserved")

    def test_plaintext_restore_uses_captured_bytes_after_backup_path_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            backup = root / "backup.sqlite"
            destination = root / "restored.sqlite"
            self.make_database(source)
            manager = BackupManager()
            backup_receipt = manager.create(source, backup)
            bounded_bytes = backup_module._bounded_bytes

            def replace_after_capture(path, limit):
                captured = bounded_bytes(path, limit)
                path.write_bytes(b"changed after capture")
                return captured

            with patch.object(backup_module, "_bounded_bytes", side_effect=replace_after_capture):
                receipt = manager.restore(backup, destination)

            self.assertEqual(receipt.backup_sha256, backup_receipt.backup_sha256)
            with sqlite3.connect(destination) as db:
                self.assertEqual(db.execute("SELECT value FROM records").fetchone()[0], "preserved")

    def test_encrypted_restore_uses_captured_bytes_after_backup_path_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            backup = root / "backup.bin"
            destination = root / "restored.sqlite"
            self.make_database(source)
            manager = BackupManager()
            cipher = TestCipher()
            backup_receipt = manager.create(source, backup, cipher=cipher)
            bounded_bytes = backup_module._bounded_bytes

            def replace_after_capture(path, limit):
                captured = bounded_bytes(path, limit)
                path.write_bytes(b"changed after capture")
                return captured

            with patch.object(backup_module, "_bounded_bytes", side_effect=replace_after_capture):
                receipt = manager.restore(backup, destination, cipher=cipher)

            self.assertEqual(receipt.backup_sha256, backup_receipt.backup_sha256)
            self.assertTrue(receipt.encrypted)
            with sqlite3.connect(destination) as db:
                self.assertEqual(db.execute("SELECT value FROM records").fetchone()[0], "preserved")

    def test_oversized_backup_is_rejected_before_digest_or_destination_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "oversized.sqlite"
            destination = root / "restored.sqlite"
            backup.write_bytes(b"x" * 17)
            manager = BackupManager(max_backup_bytes=16)

            with patch.object(backup_module, "_sha256") as digest:
                with self.assertRaisesRegex(BackupError, "backup exceeds bounded size"):
                    manager.restore(backup, destination)
                digest.assert_not_called()

            self.assertFalse(destination.exists())

    def test_restore_staging_cannot_be_replaced_from_writable_destination_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared = root / "shared"
            shared.mkdir()
            shared.chmod(0o777)
            source = root / "source.sqlite"
            backup = root / "backup.sqlite"
            destination = shared / "restored.sqlite"
            victim = root / "victim"
            victim.mkdir()
            sentinel = victim / "sentinel.txt"
            sentinel.write_bytes(b"keep this file unchanged")
            self.make_database(source)
            manager = BackupManager()
            manager.create(source, backup)
            original_inspect = manager.inspect
            swapped_staging = {}

            def replace_staging_name(database):
                if not swapped_staging:
                    stage_fd = int(database.parts[4])
                    stage_path = Path(os.readlink(f"/proc/self/fd/{stage_fd}"))
                    moved = stage_path.with_name(stage_path.name + ".moved")
                    stage_path.rename(moved)
                    stage_path.symlink_to(victim, target_is_directory=True)
                    swapped_staging.update(stage_path=stage_path, moved=moved)
                return original_inspect(database)

            with patch.object(manager, "inspect", side_effect=replace_staging_name):
                manager.restore(backup, destination)

            self.assertTrue(swapped_staging)
            self.assertTrue(swapped_staging["stage_path"].is_symlink())
            self.assertEqual(sentinel.read_bytes(), b"keep this file unchanged")
            self.assertEqual({path.name for path in victim.iterdir()}, {"sentinel.txt"})
            with sqlite3.connect(destination) as db:
                self.assertEqual(db.execute("SELECT value FROM records").fetchone()[0], "preserved")
            self.assertEqual(list(swapped_staging["moved"].iterdir()), [])
            swapped_staging["stage_path"].unlink()
            swapped_staging["moved"].rmdir()

    def test_wal_sidecar_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite"
            self.make_database(source)
            (Path(f"{source}-wal")).write_bytes(b"orphan")
            with self.assertRaises(BackupError):
                BackupManager().inspect(source)


if __name__ == "__main__":
    unittest.main()
