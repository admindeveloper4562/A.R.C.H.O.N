import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.storage import (
    Migration,
    MigrationError,
    OwnershipError,
    StorageManager,
)


def migration(module: str, version: int, table: str, *, bad_sql: bool = False) -> Migration:
    return Migration(
        module=module,
        version=version,
        name=f"{module}-{version}",
        tables=(table,),
        up_sql=(
            f"CREATE TABLE {table} (record_id TEXT PRIMARY KEY, value TEXT NOT NULL)",
            "CREATE TABLE broken (" if bad_sql else "SELECT 1",
        ),
        down_sql=(f"DROP TABLE {table}", "DROP TABLE IF EXISTS broken"),
    )


class BackendStorageTests(unittest.TestCase):
    def test_default_migration_is_idempotent_and_backend_owns_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            with StorageManager(Path(directory) / "backend.sqlite") as storage:
                first = storage.migrate()
                second = storage.migrate()
                self.assertEqual([(item["module"], item["version"]) for item in first], [("backend", 1)])
                self.assertEqual(second, first)
                storage.module("backend").insert(
                    "backend_records",
                    {
                        "record_id": "record-1",
                        "kind": "schema",
                        "payload_json": "{}",
                        "created_at": "now",
                        "updated_at": "now",
                    },
                )
                self.assertEqual(storage.module("backend").rows("backend_records")[0]["record_id"], "record-1")

    def test_module_ownership_fences_cross_module_writes(self):
        migrations = (
            migration("core", 1, "core_records"),
            migration("backend", 1, "backend_records"),
        )
        with tempfile.TemporaryDirectory() as directory:
            with StorageManager(Path(directory) / "owned.sqlite", migrations=migrations) as storage:
                storage.migrate()
                storage.module("core").insert("core_records", {"record_id": "c1", "value": "ok"})
                with self.assertRaises(OwnershipError):
                    storage.module("backend").insert("core_records", {"record_id": "x", "value": "deny"})
                self.assertEqual(storage.table_owner("core_records"), "core")
                self.assertEqual(storage.module("core").rows("core_records")[0]["value"], "ok")

    def test_failed_migration_rolls_back_table_and_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = StorageManager(
                Path(directory) / "failed.sqlite",
                migrations=(migration("core", 1, "core_records", bad_sql=True),),
            )
            with self.assertRaises(MigrationError):
                storage.migrate()
            self.assertEqual(storage.applied_migrations(), [])
            self.assertIsNone(storage.table_owner("core_records"))
            storage.close()

    def test_rollback_removes_owned_table_and_preserves_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            with StorageManager(
                Path(directory) / "rollback.sqlite",
                migrations=(migration("core", 1, "core_records"),),
            ) as storage:
                storage.migrate()
                self.assertEqual(storage.rollback("core"), [])
                self.assertIsNone(storage.table_owner("core_records"))
                with self.assertRaises(OwnershipError):
                    storage.module("core").rows("core_records")

    def test_changed_definition_and_invalid_plan_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "definitions.sqlite"
            original = migration("core", 1, "core_records")
            with StorageManager(path, migrations=(original,)) as storage:
                storage.migrate()
            changed = Migration(
                module="core",
                version=1,
                name="changed",
                tables=original.tables,
                up_sql=original.up_sql,
                down_sql=original.down_sql,
            )
            with StorageManager(path, migrations=(changed,)) as storage:
                with self.assertRaises(MigrationError):
                    storage.migrate()
            with self.assertRaises(MigrationError):
                StorageManager(
                    Path(directory) / "invalid.sqlite",
                    migrations=(migration("core", 2, "core_records"),),
                )


if __name__ == "__main__":
    unittest.main()
