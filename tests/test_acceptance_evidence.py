"""BASE-014 local evidence checks; no host qualification or live ledger access."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from jarvis_v2.backend.module_manifest import (
    EXPECTED_DEPENDENCIES, MODULE_IDS, ManifestValidationError, ModuleManifest,
    validate_module_manifest, validate_module_manifests,
)
from jarvis_v2.core.queue import MAX_HISTORY_ENTRIES, TaskQueue
from tools.ci_report import CHECK_ORDER, normalize_report


FIXTURE = Path(__file__).parent / "fixtures" / "base014.json"
ROOT = FIXTURE.parents[2]


class AcceptanceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        temporary = tempfile.TemporaryDirectory(prefix="base014-")
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / "fixture.sqlite"
        self.queue = TaskQueue(self.database)
        self.addCleanup(self.queue.close)

    def seed_history(self):
        f = self.fixture
        for task_id in (f["task_id"], f["other_task_id"]):
            self.queue.add(task_id=task_id, priority="P3", module="sda", payload=f["payload"])
        # Replace only synthetic events in this fresh temporary database.
        with self.queue.db:
            self.queue.db.execute("DELETE FROM events")
            self.queue.db.executemany(
                "INSERT INTO events(seq,task_id,kind,detail) VALUES (?,?,?,?)",
                [(e["seq"], e["task_id"], e["kind"], f["model_text"]) for e in f["events"]],
            )

    def test_history_sorts_before_limiting_and_filters_task(self):
        self.seed_history()
        task = self.fixture["task_id"]
        for limit in (1, 2, 3, 4):
            with self.subTest(limit=limit):
                result = self.queue.history(task, limit=limit)
                self.assertEqual([e["seq"] for e in result], self.fixture["expected_sequences"][:limit])
                self.assertTrue(all(e["task_id"] == task for e in result))
                self.assertTrue(all(set(e) == {"seq", "task_id", "kind"} for e in result))
        self.assertEqual(self.queue.history("FIXTURE-UNKNOWN"), [])
        self.assertEqual(self.queue.history("' OR 1=1 --"), [])
        self.assertEqual(self.queue.history(task), self.queue.history(task, limit=100))

    def test_history_limit_boundary_and_invalid_types(self):
        self.seed_history()
        task = self.fixture["task_id"]
        with self.queue.db:
            self.queue.db.executemany(
                "INSERT INTO events(task_id,kind,detail) VALUES (?,?,?)",
                [(task, "pending", self.fixture["model_text"])] * MAX_HISTORY_ENTRIES,
            )
        for limit in (MAX_HISTORY_ENTRIES, MAX_HISTORY_ENTRIES + 1, 10**30):
            result = self.queue.history(task, limit=limit)
            self.assertEqual(len(result), MAX_HISTORY_ENTRIES)
            self.assertEqual([e["seq"] for e in result[:3]], [1, 3, 8])
        for limit in self.fixture["invalid_limits"]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.queue.history(task, limit=limit)

    def test_invalid_history_requests_are_rejected_before_sql(self):
        # A disconnected instance makes any database access observable without I/O.
        queue = object.__new__(TaskQueue)
        queue.db = Mock()
        for task in (None, True, 1, [], {}, ""):
            with self.subTest(task_type=type(task).__name__), self.assertRaises(ValueError):
                queue.history(task)
        for limit in (*self.fixture["invalid_limits"], [], {}, float("inf"), float("nan")):
            with self.subTest(limit_type=type(limit).__name__), self.assertRaises(ValueError):
                queue.history(self.fixture["task_id"], limit=limit)
        queue.db.execute.assert_not_called()

    def test_restart_stale_and_duplicate_completion_expose_only_metadata(self):
        f = self.fixture
        self.queue.add(task_id=f["task_id"], priority="P3", module="sda", payload=f["payload"])
        lease = self.queue.lease_next()["lease"]
        before = self.queue.history(f["task_id"])
        with self.assertRaises(ValueError):
            self.queue.finish(f["task_id"], "stale", ok=True, receipt=f["receipt"])
        self.assertEqual(self.queue.history(f["task_id"]), before)
        self.queue.close()
        reopened = TaskQueue(self.database)
        try:
            self.assertIsNone(reopened.lease_next())
            reopened.finish(f["task_id"], lease, ok=True, receipt=f["receipt"])
            before = reopened.history(f["task_id"])
            with self.assertRaises(ValueError):
                reopened.finish(f["task_id"], lease, ok=True, receipt=f["receipt"])
            self.assertEqual(reopened.history(f["task_id"]), before)
            self.assertEqual([e["kind"] for e in before], ["pending", "leased", "completed"])
            self.assertTrue(all(set(e) == {"seq", "task_id", "kind"} for e in before))
            encoded = json.dumps(before)
            self.assertTrue(all(value not in encoded for value in (
                f["payload"]["text"], f["receipt"], f["model_text"], lease,
            )))
        finally:
            reopened.close()

    def test_evidence_rejects_duplicate_missing_and_private_fields(self):
        valid = [{"name": name, "status": "passed", "exit_code": 0} for name in CHECK_ORDER]
        report = normalize_report(valid, commit="f482e846855285aa7eeefe595530156eb06f2e3f")
        self.assertEqual(report["remote_ci"], "DEFERRED_QUOTA")
        self.assertTrue(all(set(e) == {"name", "status", "exit_code"} for e in report["checks"]))
        for field in ("payload", "receipt", "model_text"):
            invalid = [{**valid[0], field: self.fixture[field]}, *valid[1:]]
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize_report(invalid)
        for invalid in (valid[:-1], [valid[0]] * len(valid),
                        [{**valid[0], "exit_code": True}, *valid[1:]],
                        [{**valid[0], "exit_code": 1}, *valid[1:]]):
            with self.assertRaises(ValueError):
                normalize_report(invalid)
        # CI receipt order follows the caller; it is not chronological event history.
        self.assertEqual(normalize_report(list(reversed(valid)))["checks"], list(reversed(valid)))

    def test_ci_shape_bounds_and_unavailable_are_not_success_claims(self):
        valid = [{"name": name, "status": "passed", "exit_code": 0} for name in CHECK_ORDER]
        for invalid in (None, {}, tuple(valid), [], [None] * len(valid), valid + [valid[0]]):
            with self.subTest(shape=type(invalid).__name__), self.assertRaises(ValueError):
                normalize_report(invalid)
        for field, values in {
            "name": (None, [], "unknown"),
            "status": (None, {}, "unknown"),
            "exit_code": (None, "0", 0.0, -1, 256, False),
        }.items():
            for value in values:
                with self.subTest(field=field, value_type=type(value).__name__), self.assertRaises(ValueError):
                    normalize_report([{**valid[0], field: value}, *valid[1:]])
        for status, code in (("failed", 255), ("cancelled", 0)):
            report = normalize_report([{**valid[0], "status": status, "exit_code": code}, *valid[1:]])
            self.assertEqual(report["checks"][0]["status"], status)
            self.assertEqual(report["remote_ci"], "DEFERRED_QUOTA")
            self.assertEqual(set(report), {
                "schema_version", "profile", "commit", "run_id", "remote_ci",
                "provenance", "checks", "remediation",
            })
        unavailable = [dict(item) for item in valid]
        unavailable[1]["status"] = "unavailable"  # Only the policy check permits this.
        self.assertEqual(normalize_report(unavailable)["checks"][1]["status"], "unavailable")
        with self.assertRaises(ValueError):
            normalize_report([{**valid[0], "status": "unavailable"}, *valid[1:]])

    @staticmethod
    def manifest(module_id):
        key = MODULE_IDS[module_id]
        return {
            "module_id": module_id, "key": key,
            "dependencies": list(EXPECTED_DEPENDENCIES[key]),
            "health_endpoint_label": key,
            "permission_scopes": [f"{key}:read", f"{key}:health"],
        }

    def test_explicit_module_local_permissions_and_typed_compatibility(self):
        manifests = [self.manifest(i) for i in MODULE_IDS]
        validated = validate_module_manifests(list(reversed(manifests)))
        self.assertEqual([item.module_id for item in validated], list(MODULE_IDS))
        for item in validated:
            self.assertIs(validate_module_manifest(item), item)
            self.assertEqual(item.permission_scopes, frozenset({f"{item.key}:read", f"{item.key}:health"}))
        for module_id, key in MODULE_IDS.items():
            candidate = self.manifest(module_id)
            other = "sda" if key == "core" else "core"
            scopes = [f"{key}:{action}" for action in (
                "write", "process", "execute", "network", "privilege", "admin", "*", "",
            )]
            scopes += [f"{other}:read", f"{other}:health", "*", "read", "business:read"]
            for scope in scopes:
                for typed in (False, True):
                    invalid = {**candidate, "permission_scopes": [f"{key}:read", scope]}
                    if typed:
                        invalid = ModuleManifest(module_id, key, tuple(candidate["dependencies"]), key,
                                                 frozenset(invalid["permission_scopes"]))
                    with self.subTest(module=key, typed=typed, scope=scope), self.assertRaises(ManifestValidationError):
                        validate_module_manifest(invalid)

    def test_manifest_malformed_shapes_and_inferred_permissions_rejected(self):
        candidate = self.manifest(3)
        for field, values in {
            "module_id": (True, None, "3", 0, 11, []),
            "key": (None, [], "core", "business"),
            "dependencies": (None, "core", ["core", "core"], [None], {}, []),
            "health_endpoint_label": (None, [], "/health/backend", "core"),
            "permission_scopes": (None, "backend:read", [], {}, [True], [[]],
                                  ["backend:read", "backend:read"]),
        }.items():
            for value in values:
                with self.subTest(field=field, value_type=type(value).__name__), self.assertRaises(ManifestValidationError):
                    validate_module_manifest({**candidate, field: value})
        invalid = [None, [], {}]
        invalid += [{k: v for k, v in candidate.items() if k != field} for field in candidate]
        invalid += [{**candidate, field: self.fixture[field]} for field in ("payload", "receipt", "model_text")]
        for value in invalid:
            with self.assertRaises(ManifestValidationError):
                validate_module_manifest(value)

    def test_gate_and_milestone_evidence_fields_are_complete(self):
        text = (ROOT / "docs/engineering/PROJECT_ACCEPTANCE.md").read_text(encoding="utf-8")
        aliases = {}
        for line in text.splitlines():
            if line.startswith("| ") and "python3 -m unittest" in line:
                key, command = [part.strip().strip("`") for part in line.split("|")[1:-1]]
                aliases[key] = command
                self.assertTrue(command.startswith("PYTHONPATH=src:. python3 -m unittest discover -s tests"))
                if " -p " in command:
                    self.assertTrue((ROOT / "tests" / command.split(" -p ")[1].split()[0]).is_file())
        self.assertTrue(aliases)
        seen = []
        artifacts = set()
        for line in text.splitlines():
            if not (line.startswith("| [ ] M") or any(line.startswith(f"| {gate} / S |") for gate in "ABCDEFGHIJKLMNO")):
                continue
            fields = [part.strip() for part in line.split("|")[1:-1]]
            self.assertEqual(len(fields), 6)
            self.assertTrue(all(fields))
            self.assertEqual(fields[0].split(" / ")[1], "S")
            for alias in fields[2].split(", "):
                self.assertIn(alias, aliases)
            artifact = fields[4].strip("`")
            self.assertRegex(artifact, r"^[A-O0-9M]+/[a-z-]+$")
            self.assertNotIn(artifact, artifacts)
            artifacts.add(artifact)
            seen.append(fields[0].removeprefix("[ ] ").split(" / ")[0])
        self.assertEqual(seen, list("ABCDEFGHIJKLMNO") + [f"M{i}" for i in range(10)])
        self.assertIn("f482e846855285aa7eeefe595530156eb06f2e3f", text)


if __name__ == "__main__":
    unittest.main()
