"""Regression checks for executable hosted CI jobs."""

import unittest
import tempfile
import json
import subprocess
import sys
import os
import textwrap
from pathlib import Path

from tools.ci_checks import _contains_secret, _workflow_is_safe
from tools.ci_report import CHECK_ORDER, _write_report, main, normalize_report, write_report


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
ROOT = WORKFLOW.parents[2]


class CIWorkflowTests(unittest.TestCase):
    def test_python_and_ios_jobs_have_runners_and_test_commands(self):
        workflow = WORKFLOW.read_text()

        python_job = workflow.split("\n  ios:\n", 1)[0]
        ios_job = "\n  ios:\n" + workflow.split("\n  ios:\n", 1)[1]

        self.assertIn("  test:\n", python_job)
        self.assertIn("runs-on: ubuntu-latest", python_job)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v", python_job)

        self.assertIn("  ios:\n", ios_job)
        self.assertIn("runs-on: macos-latest", ios_job)
        self.assertRegex(ios_job, r"actions/checkout@[0-9a-f]{40}")
        self.assertEqual(ios_job.count("persist-credentials: false"), 1)
        self.assertIn(
            "python3 -m unittest discover -s apps/ios/tests -p 'test_*.py' -v",
            ios_job,
        )

    def test_python_job_installs_locked_runtime_dependencies_before_tests(self):
        workflow = WORKFLOW.read_text()
        python_job = workflow.split("\n  ios:\n", 1)[0]
        install = python_job.index(
            "python -m pip install --disable-pip-version-check --no-input -r requirements/runtime.lock"
        )
        tests = python_job.index(
            "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v"
        )
        self.assertLess(install, tests)

    def test_fallback_receipt_runs_without_prerequisite_checkout(self):
        workflow = WORKFLOW.read_text()
        fallback = workflow.split("  fallback_receipt:", 1)[1]
        self.assertIn("if: always()", fallback)
        self.assertIn("needs: [preflight, test, ios]", fallback)
        self.assertIn("PREFLIGHT_RESULT", fallback)
        self.assertIn("ci-report-fallback", fallback)
        self.assertGreaterEqual(workflow.count("len(run_id) > 32"), 2)
        self.assertNotIn("actions/checkout@", fallback)
        self.assertNotIn("actions/setup-python@", fallback)

    def test_preflight_and_fallback_receipt_scripts_write_to_runner_temp(self):
        workflow = WORKFLOW.read_text()
        cases = (
            ("Write startup receipt", "startup.json"),
            ("Write prerequisite-failure receipt", "fallback.json"),
        )
        for step_name, filename in cases:
            with self.subTest(step=step_name), tempfile.TemporaryDirectory() as temp:
                block = workflow.split(f"      - name: {step_name}\n", 1)[1].split("\n      - name:", 1)[0]
                script = block.split("python3 - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
                script = textwrap.dedent(script)
                artifact_dir = Path(temp) / "ci-artifacts"
                artifact_dir.mkdir()
                env = os.environ.copy()
                env.update({
                    "RUNNER_TEMP": temp,
                    "GITHUB_SHA": "a" * 40,
                    "GITHUB_RUN_ID": "12345",
                    "GITHUB_REPOSITORY": "owner/repository",
                    "PREFLIGHT_RESULT": "success",
                    "PYTHON_RESULT": "failure",
                    "IOS_RESULT": "success",
                })
                result = subprocess.run(
                    [sys.executable, "-c", script],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                receipt = json.loads((artifact_dir / filename).read_text())
                self.assertEqual(receipt["commit"], "a" * 40)
                self.assertEqual(receipt["run_id"], "12345")
                self.assertEqual((artifact_dir / filename).stat().st_mode & 0o777, 0o600)

    def test_workflow_pins_actions_and_uploads_bounded_receipt(self):
        workflow = WORKFLOW.read_text()
        self.assertNotRegex(workflow, r"uses:\s+[^@\s]+@v\d")
        self.assertIn("python3 tools/ci_checks.py dependency_scan", workflow)
        self.assertIn("python3 tools/ci_checks.py secret_scan", workflow)
        self.assertIn("python3 tools/ci_checks.py security_scan", workflow)
        self.assertIn("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("ci-report-preflight", workflow)
        self.assertEqual(workflow.count("persist-credentials: false"), 2)
        self.assertNotIn("github.event.pull_request.head.repo.full_name", workflow)
        self.assertNotIn("ref: ${{ github.event", workflow)
        self.assertIn("steps.unit_tests.outcome != 'success'", workflow)
        self.assertIn("steps.policy.outcome != 'skipped'", workflow)
        self.assertIn("ios_tests", workflow)
        self.assertTrue(_workflow_is_safe(workflow))

    def test_report_rejects_raw_payloads_and_extra_fields(self):
        valid = [{"name": name, "status": "passed", "exit_code": 0} for name in CHECK_ORDER]
        self.assertEqual(normalize_report(valid)["checks"], valid)
        with self.assertRaises(ValueError):
            normalize_report([{**valid[0], "detail": "raw secret"}])
        with self.assertRaises(ValueError):
            normalize_report([{**valid[0], "exit_code": True}])
        with self.assertRaises(ValueError):
            normalize_report(valid[:-1])
        with self.assertRaises(ValueError):
            normalize_report([{**item, "status": "passed", "exit_code": 1} if item["name"] == "unit_tests" else item for item in valid])
        unavailable = [{"name": name, "status": "passed", "exit_code": 0} for name in CHECK_ORDER]
        unavailable[1] = {"name": "policy", "status": "unavailable", "exit_code": 0}
        self.assertEqual(normalize_report(unavailable)["checks"], unavailable)

    def test_report_rejects_escape_and_symlink_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            checks = [{"name": "unit_tests", "status": "passed", "exit_code": 0}]
            with self.assertRaises(ValueError):
                _write_report(root / ".." / "escape.json", checks, root)
            link = root / "link.json"
            link.symlink_to(root / "target.json")
            with self.assertRaises(ValueError):
                _write_report(link, checks, root)
            with tempfile.TemporaryDirectory() as outside:
                with self.assertRaises(ValueError):
                    write_report(Path(outside) / "outside.json", [{"name": name, "status": "passed", "exit_code": 0} for name in CHECK_ORDER], root=root)
            self.assertFalse((root / "escape.json").exists())

    def test_cli_writes_complete_bounded_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.json"
            values = [f"{name}=0" for name in CHECK_ORDER]
            values[1] = "policy=SKIPPED"
            prefix = [
                "--profile", "python", "--root", temp, "--output", str(output), "--commit", "a" * 40,
                "--run-id", "42", "--remote-status", "DEFERRED_QUOTA", "--repository", "local/test",
                "--workflow", "test", "--job", "test", "--matrix", "none", "--artifact", "test-report",
            ]
            self.assertEqual(main([*prefix, *values]), 0)
            report = json.loads(output.read_text())
            self.assertEqual([item["status"] for item in report["checks"]][1], "unavailable")
            self.assertEqual(report["remote_ci"], "DEFERRED_QUOTA")
            failed_output = Path(temp) / "failed.json"
            failed_values = [f"{name}=0" for name in CHECK_ORDER]
            failed_values[0] = "unit_tests=1"
            failed_values[1] = "policy=SKIPPED"
            self.assertEqual(main([
                "--profile", "python", "--root", temp, "--output", str(failed_output), "--commit", "c" * 40,
                "--run-id", "44", "--remote-status", "DEFERRED_QUOTA", "--repository", "local/test",
                "--workflow", "test", "--job", "test", "--matrix", "none", "--artifact", "failed-report", *failed_values,
            ]), 0)
            failed_report = json.loads(failed_output.read_text())
            self.assertEqual(failed_report["checks"][0]["status"], "failed")
            self.assertEqual(failed_report["remediation"]["unit_tests"], "inspect_unit_test_failure")
            invalid_prefix = [
                "--profile", "python", "--root", temp, "--output", str(output.with_name("invalid.json")), "--commit", "a" * 40,
                "--run-id", "42", "--remote-status", "DEFERRED_QUOTA", "--repository", "local/test",
                "--workflow", "test", "--job", "test", "--matrix", "none", "--artifact", "invalid-report",
            ]
            self.assertEqual(main([*invalid_prefix, *values[:1], "policy=-1", *values[2:]]), 2)
            ios_output = Path(temp) / "ios-report.json"
            self.assertEqual(main([
                "--profile", "ios", "--root", temp, "--output", str(ios_output), "--commit", "b" * 40,
                "--run-id", "43", "--remote-status", "EXECUTED_HOSTED", "--repository", "local/test",
                "--workflow", "test", "--job", "ios", "--matrix", "none", "--artifact", "ios-report", "ios_tests=0",
            ]), 0)
            with self.assertRaises(ValueError):
                normalize_report([{"name": "ios_tests", "status": "unavailable", "exit_code": 0}], profile="ios")

    def test_public_check_and_report_clis(self):
        scan = subprocess.run(
            [sys.executable, "tools/ci_checks.py", "security_scan"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=30,
        )
        self.assertEqual(scan.returncode, 0)
        for check in ("dependency_scan", "secret_scan"):
            result = subprocess.run(
                [sys.executable, "tools/ci_checks.py", check],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.json"
            args = [
                sys.executable,
                "tools/ci_report.py",
                "--profile", "ios",
                "--root", temp,
                "--output", str(output),
                "--commit", "d" * 40,
                "--run-id", "45",
                "--remote-status", "EXECUTED_HOSTED",
                "--repository", "local/test",
                "--workflow", "test",
                "--job", "ios",
                "--matrix", "none",
                "--artifact", "ios-report",
                "ios_tests=0",
            ]
            result = subprocess.run(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=30)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(output.read_text())["profile"], "ios")

    def test_secret_and_workflow_boundaries_reject_common_unsafe_inputs(self):
        self.assertTrue(_contains_secret(b"password: super-secret-value-1234567890"))
        self.assertTrue(_contains_secret(b"AIza" + b"A" * 35))
        self.assertFalse(_contains_secret(b"password: ${PASSWORD_FROM_ENV}"))
        workflow = WORKFLOW.read_text()
        self.assertFalse(_workflow_is_safe(workflow.replace("contents: read", "contents: write", 1)))
        self.assertFalse(_workflow_is_safe(workflow.replace("persist-credentials: false", "persist-credentials: true", 1)))
        self.assertFalse(_workflow_is_safe(workflow.replace("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683", "actions/checkout@v4", 1)))
        self.assertFalse(_workflow_is_safe(workflow + "\n  unsafe:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"))


if __name__ == "__main__":
    unittest.main()
