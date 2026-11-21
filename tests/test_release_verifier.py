from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

from tools.verify_release import Verification


class VerificationSubprocessTests(unittest.TestCase):
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
