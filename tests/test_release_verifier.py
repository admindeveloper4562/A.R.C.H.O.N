from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from tools.verify_release import Verification


class VerificationSubprocessTests(unittest.TestCase):
    def test_source_date_epoch_comes_from_git_commit_time(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = CompletedProcess(["git"], 0, stdout="1795190000" + chr(10), stderr="")
            with patch.object(verifier, "run", return_value=result) as run:
                self.assertEqual(verifier.source_date_epoch("a" * 40), "1795190000")
        run.assert_called_once_with(
            "source-date-epoch", ["git", "show", "-s", "--format=%ct", "a" * 40]
        )

    def test_source_date_epoch_rejects_non_numeric_git_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = CompletedProcess(["git"], 0, stdout="unknown" + chr(10), stderr="")
            with patch.object(verifier, "run", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "numeric SOURCE_DATE_EPOCH"):
                    verifier.source_date_epoch("b" * 40)

    def test_records_an_expected_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = verifier.run(
                "expected-rejection",
                [sys.executable, "-c", "raise SystemExit(2)"],
                expected_returncodes=(2,),
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(verifier.records[0]["exit_classification"], "expected")
        self.assertEqual(verifier.records[0]["expected_returncodes"], [2])

    def test_unexpected_exit_is_reported_and_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            with self.assertRaisesRegex(RuntimeError, r"expected \(1,\)"):
                verifier.run(
                    "unexpected-success",
                    [sys.executable, "-c", "raise SystemExit(0)"],
                    expected_returncodes=(1,),
                )
        self.assertEqual(verifier.records[0]["exit_classification"], "unexpected")


if __name__ == "__main__":
    unittest.main()
