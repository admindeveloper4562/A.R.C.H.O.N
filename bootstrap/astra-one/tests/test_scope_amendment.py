import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from astra_one.linux_sda import (
    PROJECT_ID,
    State,
    _amendment_payload_sha,
    file_sha256,
)
from astra_one.full_plan import payload_sha


def git_repo(root: Path) -> Path:
    root.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "develop", str(root)], check=True)
    (root / "docs" / "tasks").mkdir(parents=True)
    (root / "docs" / "tasks" / "JARVIS_V2_TASK_PLAN.json").write_text(
        '{"format":"scope-amendment-test"}\n', encoding="utf-8"
    )
    (root / "README.md").write_text("scope amendment test\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=test", "-c",
        "user.email=test@local.invalid", "commit", "-qm", "initial",
    ], check=True)
    return root


class TwsScopeAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = git_repo(self.root / "source")
        self.state = State(self.root / "state")
        self.state.init(self.source)
        self.project_payload = "d" * 64
        dependency_map = {
            "REL-009": ["TWS-020", "REL-001"],
            "REL-015": ["BACK-018", "REL-009", "REL-011", "REL-013"],
            "REL-016": ["BASE-003", "REL-012", "REL-015"],
            "REL-017": ["REL-014", "REL-016", "MIG-015"],
            "REL-018": ["REL-007", "REL-008", "REL-009", "REL-010", "REL-011", "REL-017"],
            "REL-019": ["REL-012", "REL-018"],
            "REL-020": ["REL-019", "MIG-014"],
        }
        original = {
            "REL-009": (
                "Verify TWS mobile pairing, 3D fallback and cross-module quest gates",
                ["Real iPhone/device evidence, XP non-duplication and graceful failure"],
            ),
            "REL-015": (
                "Validate backup/restore and data retention per domain",
                ["Clean-room restore preserves state without inappropriate private-data retention"],
            ),
            "REL-016": (
                "Run full CI on declared Python versions and native iOS runners",
                ["All required jobs execute and pass; artifacts stored per SHA"],
            ),
            "REL-017": (
                "Produce deployment IaC/manifests, installation and operator runbooks",
                ["Reproducible documented Linux, Windows, Cloudflare and optional iOS install"],
            ),
            "REL-018": (
                "Run staging end-to-end user-acceptance scenarios and accessibility audit",
                ["Owner-approved scripted journeys pass with objective evidence"],
            ),
            "REL-019": (
                "Review licensing, provenance, threat model and release-blocking defects",
                ["No unreviewed third-party artifacts or unresolved critical findings"],
            ),
            "REL-020": (
                "Review exact accepted backlog IDs and frozen candidate Git SHA",
                ["No required tasks incomplete, or documented owner-approved deferrals that do not violate gates"],
            ),
        }
        tws_ids = {"TWS-013", "TWS-014", "TWS-015", "TWS-016", "TWS-019", "TWS-020"}
        changed_ids = set(original) | tws_ids
        all_ids = changed_ids | {dep for deps in dependency_map.values() for dep in deps}
        now = "2026-11-19T00:00:00+00:00"
        with self.state.db() as db:
            db.execute(
                "INSERT INTO projects(id,name,source_repository,integration_branch,parent_task_count,"
                "subtask_count,workers,model,reasoning,source_ref,source_commit,parent_plan_blob_sha,"
                "subtask_index_sha,payload_sha,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    PROJECT_ID, "ARCHON test", "test/repo", "develop", 247, 0, 1,
                    "test", "medium", "test-ref", self.state.get("source_sha"),
                    "b" * 40, "c" * 64, self.project_payload, "pending", now, now,
                ),
            )
            db.execute(
                "INSERT INTO project_queue(project_id,status,enqueue_seq,created_at,updated_at) VALUES(?,?,?,?,?)",
                (PROJECT_ID, "pending", 0, now, now),
            )
            for sequence, task_id in enumerate(sorted(all_ids), start=1):
                title, acceptance = original.get(
                    task_id, (f"Build {task_id}", ["The bounded task is tested and reviewable"])
                )
                spec = {
                    "task_id": task_id,
                    "objective": f"Implement the bounded {task_id} task for the scope amendment test.",
                    "acceptance": acceptance,
                    "depends_on": dependency_map.get(task_id, []),
                    "area": task_id.split("-", 1)[0].lower(),
                    "title": title,
                }
                db.execute(
                    "INSERT INTO tasks(id,spec,status,architecture_sha,available_at,created_at,updated_at,"
                    "project_id,module,milestone,priority,owner_gate,payload_sha,enqueue_seq) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        task_id, json.dumps(spec, sort_keys=True),
                        "blocked" if task_id in changed_ids else "completed",
                        "a" * 64, 0, now, now, PROJECT_ID,
                        task_id.split("-", 1)[0], "test", "P1", 0,
                        payload_sha(spec), sequence,
                    ),
                )

    def tearDown(self):
        self.temp.cleanup()

    def amendment(self) -> dict:
        amended = {
            "REL-009": (
                "Record TWS mobile pairing, 3D fallback and cross-module quest gates as deferred",
                ["TWS/iOS/device verification is explicitly deferred and out of scope for this release; no real-device evidence or completion claim is recorded."],
            ),
            "REL-015": (
                "Validate in-scope backup/restore and data retention per domain",
                ["Clean-room restore preserves in-scope state without inappropriate private-data retention; TWS artifacts are explicitly excluded and remain deferred."],
            ),
            "REL-016": (
                "Run full CI on declared Python versions and supported platform runners",
                ["All in-scope Linux/Windows CI jobs execute and pass; native iOS runner coverage is explicitly deferred and not claimed; artifacts are stored per SHA."],
            ),
            "REL-017": (
                "Produce deployment IaC/manifests, installation and operator runbooks",
                ["Reproducible documented Linux, Windows and Cloudflare installation is verified; iOS/TWS installation is explicitly deferred and not claimed."],
            ),
            "REL-018": (
                "Run staging non-TWS end-to-end user-acceptance scenarios and accessibility audit",
                ["Owner-approved scripted non-TWS journeys pass with objective evidence; TWS/iOS journeys remain explicitly deferred and unclaimed."],
            ),
            "REL-019": (
                "Review in-scope licensing, provenance, threat model and release-blocking defects",
                ["No unreviewed third-party artifacts or unresolved critical findings remain in the in-scope release; the deferred TWS scope is recorded as a residual risk."],
            ),
            "REL-020": (
                "Review accepted in-scope backlog IDs and frozen candidate Git SHA",
                ["No required in-scope tasks are incomplete, and the TWS/iOS work is explicitly deferred under a documented owner-approved scope decision that does not violate in-scope release gates."],
            ),
        }
        dependency_updates = [
            {"task_id": "REL-009", "original_dependencies": ["TWS-020", "REL-001"], "amended_dependencies": ["REL-001"]},
            {"task_id": "REL-015", "original_dependencies": ["BACK-018", "REL-009", "REL-011", "REL-013"], "amended_dependencies": ["BACK-018", "REL-011", "REL-013"]},
            {"task_id": "REL-018", "original_dependencies": ["REL-007", "REL-008", "REL-009", "REL-010", "REL-011", "REL-017"], "amended_dependencies": ["REL-007", "REL-008", "REL-010", "REL-011", "REL-017"]},
        ]
        acceptance_updates = []
        for task_id in ("REL-009", "REL-015", "REL-016", "REL-017", "REL-018", "REL-019", "REL-020"):
            with self.state.db() as db:
                spec = json.loads(db.execute("SELECT spec FROM tasks WHERE id=?", (task_id,)).fetchone()[0])
            amended_title, amended_acceptance = amended[task_id]
            acceptance_updates.append({
                "task_id": task_id,
                "original_title": spec["title"],
                "amended_title": amended_title,
                "original_acceptance": spec["acceptance"],
                "amended_acceptance": amended_acceptance,
            })
        artifact = {
            "format": "archon-scope-amendment-v1",
            "amendment_id": "ARCHON-TWS-OUT-OF-SCOPE-TEST",
            "project_id": PROJECT_ID,
            "version": 1,
            "original_plan_sha256": file_sha256(self.source / "docs" / "tasks" / "JARVIS_V2_TASK_PLAN.json"),
            "amended_plan_sha256": "",
            "original_project_payload_sha256": self.project_payload,
            "deferred_task_ids": sorted({"REL-009", "TWS-013", "TWS-014", "TWS-015", "TWS-016", "TWS-019", "TWS-020"}),
            "dependency_updates": dependency_updates,
            "acceptance_updates": acceptance_updates,
            "owner_authorization": {
                "authorized": True,
                "reference": "test owner authorization",
                "scope": "de-scope unfinished TWS work",
            },
            "residual_risks": ["iOS/device evidence remains unavailable and unclaimed"],
            "verification": {
                "no_tws_implementation_claim": True,
                "no_ios_device_evidence_claim": True,
                "main_unchanged": True,
            },
        }
        artifact["amended_plan_sha256"] = _amendment_payload_sha(artifact)
        return artifact

    def test_scope_amendment_is_validated_applied_and_idempotent(self):
        artifact_path = self.root / "amendment.json"
        artifact_path.write_text(json.dumps(self.amendment(), indent=2) + "\n", encoding="utf-8")

        preview = self.state.validate_tws_scope_amendment(artifact_path)
        self.assertEqual(preview["status"], "validated")
        applied = self.state.record_tws_scope_amendment(artifact_path)
        self.assertEqual(applied["status"], "active")
        self.assertFalse(applied["idempotent"])

        with self.state.db() as db:
            archived = db.execute(
                "SELECT id,status,last_error FROM tasks WHERE id IN (?,?,?,?,?,?,?) ORDER BY id",
                ("REL-009", "TWS-013", "TWS-014", "TWS-015", "TWS-016", "TWS-019", "TWS-020"),
            ).fetchall()
            self.assertTrue(all(row[1] == "archived" and row[2] == "scope_deferred_tws" for row in archived))
            rel015 = json.loads(db.execute("SELECT spec FROM tasks WHERE id='REL-015'").fetchone()[0])
            self.assertEqual(rel015["depends_on"], ["BACK-018", "REL-011", "REL-013"])
            self.assertEqual(db.execute("SELECT count(*) FROM scope_amendments").fetchone()[0], 1)

        status = self.state.full_plan_status()
        self.assertEqual(status["deferred_scope"]["count"], 7)
        self.assertEqual(status["deferred_scope"]["parent_ids"], [
            "REL-009", "TWS-013", "TWS-014", "TWS-015", "TWS-016", "TWS-019", "TWS-020",
        ])
        second = self.state.record_tws_scope_amendment(artifact_path)
        self.assertTrue(second["idempotent"])


if __name__ == "__main__":
    unittest.main()
