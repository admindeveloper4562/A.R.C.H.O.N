import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

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
