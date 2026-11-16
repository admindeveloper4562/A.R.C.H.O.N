import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import (
    AuthorizationError,
    AuthorizationServer,
    ConnectorBroker,
    ContextPackError,
    ContextPacker,
    LocalAgentJob,
    NodeManifest,
    OwnerApproval,
    WindowsAgentRegistry,
)
from jarvis_v2.backend.backup import BackupManager
from jarvis_v2.backend.storage import StorageManager
from jarvis_v2.core import ModuleRegistry
from tools.import_legacy import prepare_manifest


ROOT = Path(__file__).resolve().parents[1]
INPUT_SHA = "a" * 64
RESULT_SHA = "b" * 64


class BackendAcceptanceTests(unittest.TestCase):
    def test_scoped_authorization_and_context_reject_cross_scope_data(self):
        modules = ModuleRegistry.from_config(ROOT / "config/modules.json")
        authorization = AuthorizationServer(modules)
        authorization.register_identity("core-service", "core")
        with self.assertRaises(AuthorizationError):
            authorization.grant("core-service", "backend", ["backend:read"])
        approval = OwnerApproval.for_grant(
            "backend-acceptance-approval", "core-service", "backend", ["backend:read"]
        )
        grant = authorization.grant(
            "core-service", "backend", ["backend:read"], approval=approval
        )
        self.assertTrue(
            authorization.authorize(
                "core-service", "backend", "backend:read", grant_id=grant.grant_id
            )
        )
        self.assertFalse(
            authorization.authorize(
                "core-service", "backend", "backend:health", grant_id=grant.grant_id
            )
        )

        broker = ConnectorBroker()
        broker.grant("owner-service", "mira", ["mira:read"], credential_ref="mira-ref")
        broker.grant("audit-service", "mira", ["mira:read"], credential_ref="audit-ref")
        broker.revoke_connector("owner-service", "mira")
        self.assertFalse(broker.authorize("owner-service", "mira", "mira:read"))
        self.assertTrue(broker.authorize("audit-service", "mira", "mira:read"))
        self.assertTrue(all(not item.get("credential_value") for item in broker.grants()))

        with self.assertRaises(ContextPackError):
            ContextPacker().pack({"raw_prompt": "not retained"}, {}, [])

    def test_offline_node_requeues_and_second_node_completes_job(self):
        now = [100.0]
        registry = WindowsAgentRegistry(clock=lambda: now[0], heartbeat_age_seconds=30)
        for node_id in ("windows-a", "windows-b"):
            registry.register_node(
                NodeManifest(
                    node_id=node_id,
                    agent_version="1.0.0",
                    model="qwen3-8b",
                    capabilities=frozenset({"summarize"}),
                    data_scopes=frozenset({"public_metadata"}),
                )
            )
            registry.heartbeat(node_id)
        job = LocalAgentJob(
            job_id="BACK-022-job",
            idempotency_key="BACK-022-idempotency",
            operation="summarize",
            input_sha256=INPUT_SHA,
            required_scope="public_metadata",
            deadline_at=1_000.0,
            task_id="BACK-022",
        )
        registry.submit(job)
        first_lease = registry.lease(job.job_id, "windows-a")
        registry.heartbeat("windows-a", status="offline")
        self.assertEqual(registry.reconcile(), 1)
        self.assertEqual(registry.route("summarize", "public_metadata").node_id, "windows-b")
        second_lease = registry.lease(job.job_id, "windows-b")
        with self.assertRaises(ValueError):
            registry.complete(
                job.job_id, "windows-a", first_lease.lease_id, result_sha256=RESULT_SHA
            )
        result = registry.complete(
            job.job_id, "windows-b", second_lease.lease_id, result_sha256=RESULT_SHA
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result_sha256"], RESULT_SHA)

    def test_backup_restore_preserves_owned_backend_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "backend.sqlite"
            backup = root / "backup.sqlite"
            restored = root / "restored.sqlite"
            with StorageManager(source) as storage:
                storage.migrate()
                storage.module("backend").insert(
                    "backend_records",
                    {
                        "record_id": "BACK-022-record",
                        "kind": "acceptance",
                        "payload_json": json.dumps({"scope": "backend"}),
                        "created_at": "now",
                        "updated_at": "now",
                    },
                )
            manager = BackupManager()
            receipt = manager.create(source, backup)
            restored_receipt = manager.restore(
                backup, restored, expected_schema_version=0
            )
            self.assertEqual(receipt.integrity, "ok")
            self.assertEqual(restored_receipt.integrity, "ok")
            self.assertEqual(os.stat(backup).st_mode & 0o777, 0o600)
            with StorageManager(restored) as recovered:
                self.assertEqual(
                    recovered.module("backend").rows("backend_records")[0]["record_id"],
                    "BACK-022-record",
                )
                self.assertEqual(recovered.table_owner("backend_records"), "backend")

    def test_create_only_migration_records_provenance_without_touching_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "legacy"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()

            def git(*args: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(source), *args],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()

            git("init", "-b", "develop")
            git("config", "user.name", "Acceptance Test")
            git("config", "user.email", "acceptance@example.test")
            (source / "backend.py").write_text("BACKEND_VALUE = 1\n", encoding="utf-8")
            git("add", "backend.py")
            git("commit", "-m", "legacy backend fixture")
            source_sha = git("rev-parse", "HEAD")
            git("remote", "add", "origin", "https://github.com/admindeveloper4562/personal-jarvis.git")
            git("update-ref", "refs/remotes/origin/develop", source_sha)
            before = git("status", "--porcelain")
            manifest = {
                "schema": "jarvis-v2.legacy-import/1",
                "expected_source_commit": source_sha,
                "entries": [
                    {
                        "area": "backend",
                        "ref": "develop",
                        "source": "backend.py",
                        "target": "migration/imported/backend/backend.py",
                    }
                ],
            }
            dry_run = prepare_manifest(source, destination, manifest)
            self.assertTrue(dry_run["dry_run"])
            self.assertFalse((destination / "migration").exists())
            self.assertEqual(before, git("status", "--porcelain"))
            applied = prepare_manifest(source, destination, manifest, apply=True)
            self.assertEqual(applied["entries"][0]["source_commit"], source_sha)
            self.assertEqual(
                json.loads(
                    (destination / "migration/provenance/import-log.json").read_text()
                )["entries"][0]["sha256"],
                applied["entries"][0]["sha256"],
            )
            self.assertEqual(before, git("status", "--porcelain"))


if __name__ == "__main__":
    unittest.main()
