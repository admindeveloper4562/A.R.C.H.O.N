import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sda003_probe", ROOT / "tools" / "verify_codex_profiles.py")
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class SDA003ProfileTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="sda003-test-"))
        self.models = {role: f"requested-{role}" for role in probe.ROLES}
        self.efforts = dict.fromkeys(probe.ROLES, "medium")

    @staticmethod
    def events(marker):
        return "\n".join([
            json.dumps({"type": "thread.started"}),
            json.dumps({"type": "turn.started"}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": marker}}),
            json.dumps({"type": "turn.completed"}),
        ])

    def fake_run(self, calls, *, denied_model="", failure_reason=""):
        def run(command, **kwargs):
            calls.append(command)
            if command[-1] == "--version":
                return {"exit_code": 0, "reason": ""}, "codex-cli 0.169.0\n", ""
            if command[-2:] == ["login", "status"]:
                return {"exit_code": 0, "reason": ""}, "Logged in using ChatGPT\n", ""
            model = command[command.index("-m") + 1]
            if model == denied_model:
                return {"exit_code": 1, "reason": ""}, "", "model does not exist"
            if failure_reason:
                return {"exit_code": 1, "reason": failure_reason}, "", ""
            marker = re.search(r"Reply exactly (\S+)", kwargs["prompt"]).group(1).rstrip(".")
            return {"exit_code": 0, "reason": ""}, self.events(marker), ""
        return run

    def test_default_is_pending_and_validation_does_not_launch(self):
        with patch.object(probe, "_bounded_run") as process:
            result = probe.verify_profiles(models=self.models, efforts=self.efforts)
        self.assertEqual(result["status"], "PENDING")
        process.assert_not_called()
        for kwargs in (
            {"models": {}, "efforts": self.efforts},
            {"models": self.models, "efforts": {}, "timeout": 60},
            {"models": {**self.models, "qc": "bad alias"}, "efforts": self.efforts},
            {"models": self.models, "efforts": self.efforts, "timeout": True},
            {"models": self.models, "efforts": self.efforts, "timeout": 301},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, "invalid_profile"):
                probe.verify_profiles(execute=True, home=self.home, **kwargs)

    def test_event_protocol_rejects_incomplete_duplicate_corrupt_and_tool_events(self):
        good = self.events("marker")
        cases = [
            ("", "smoke_incomplete"),
            ("not-json", "invalid_events"),
            (good + "\n" + good, "invalid_events"),
            (json.dumps({"type": "error"}), "model_error"),
            (good.replace('"marker"', '"wrong"'), "smoke_incomplete"),
            (json.dumps({"type": "item.completed", "item": {"type": "command_execution"}}), "unexpected_tool"),
        ]
        for stream, expected in cases:
            with self.subTest(expected=expected):
                reason, _ = probe._event_reason(stream, "", 0, "marker")
                self.assertEqual(reason, expected)
        self.assertEqual(probe._event_reason(good, "", 1, "marker")[0], "cli_nonzero")

    def test_profile_commands_are_read_only_and_preserve_each_requested_alias(self):
        calls = []
        with patch.object(probe, "_bounded_run", side_effect=self.fake_run(calls)):
            result = probe.verify_profiles(models=self.models, efforts=self.efforts,
                                           execute=True, home=self.home, timeout=5)
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(len(calls), 6)
        for role, args in zip(probe.ROLES, calls[2:]):
            self.assertEqual(args[args.index("-m") + 1], self.models[role])
            self.assertEqual(args[args.index("--sandbox") + 1], "read-only")
            self.assertIn("--ephemeral", args)
            self.assertIn("--skip-git-repo-check", args)
            self.assertIn("--ignore-user-config", args)
            self.assertIn("model_provider=openai", args)
            self.assertIn("agents.enabled=false", args)
            self.assertIn("approval_policy=never", args)
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)

    def test_unavailable_alias_stops_without_fallback_or_later_roles(self):
        calls = []
        with patch.object(probe, "_bounded_run", side_effect=self.fake_run(calls, denied_model=self.models["qc"])):
            result = probe.verify_profiles(models=self.models, efforts=self.efforts,
                                           execute=True, home=self.home, timeout=5)
        self.assertEqual(result["reason"], "model_unavailable")
        self.assertEqual([item["status"] for item in result["profiles"]], ["VERIFIED", "VERIFIED", "STOP", "PENDING"])
        self.assertEqual(len(calls), 5)
        self.assertEqual(calls[-1][calls[-1].index("-m") + 1], self.models["qc"])

    def test_controls_and_authentication_stop_before_model_calls(self):
        marker = self.home / "PAUSED_QUOTA"
        marker.write_text("preserve")
        with patch.object(probe, "_bounded_run") as process:
            result = probe.verify_profiles(models=self.models, efforts=self.efforts,
                                           execute=True, home=self.home)
        self.assertEqual(result["reason"], "PAUSED_QUOTA")
        process.assert_not_called()
        self.assertEqual(marker.read_text(), "preserve")

        marker.unlink()
        calls = []
        def denied_login(command, **kwargs):
            calls.append(command)
            if command[-1] == "--version":
                return {"exit_code": 0, "reason": ""}, "codex-cli 0.169.0\n", ""
            return {"exit_code": 1, "reason": ""}, "", "Not logged in"
        with patch.object(probe, "_bounded_run", side_effect=denied_login):
            result = probe.verify_profiles(models=self.models, efforts=self.efforts,
                                           execute=True, home=self.home, timeout=5)
        self.assertEqual(result["reason"], "cli_nonzero")
        self.assertFalse(result["authenticated"])
        self.assertEqual([item["status"] for item in result["profiles"]], ["PENDING"] * 4)
        self.assertEqual(len(calls), 2)

    def test_model_failure_reasons_propagate_without_fallback(self):
        for failure_reason in ("quota_or_rate_limit", "timeout", "output_limit"):
            with self.subTest(reason=failure_reason):
                calls = []
                with patch.object(probe, "_bounded_run", side_effect=self.fake_run(calls, failure_reason=failure_reason)):
                    result = probe.verify_profiles(models=self.models, efforts=self.efforts,
                                                   execute=True, home=self.home, timeout=1)
                self.assertEqual(result["reason"], failure_reason)
                self.assertEqual(result["status"], "STOP")

    def test_process_timeout_and_output_limit_are_bounded(self):
        timeout_receipt, _, _ = probe._bounded_run(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            cwd=self.home, home=self.home, timeout=1,
        )
        self.assertEqual(timeout_receipt["reason"], "timeout")
        flood_receipt, stdout, _ = probe._bounded_run(
            [sys.executable, "-c", "import sys; sys.stdout.write('x' * 1048576)"],
            cwd=self.home, home=self.home, timeout=5,
        )
        self.assertEqual(flood_receipt["reason"], "output_limit")
        self.assertTrue(flood_receipt["output_truncated"])
        self.assertLessEqual(len(stdout), probe.OUTPUT_LIMIT)


if __name__ == "__main__":
    unittest.main()
