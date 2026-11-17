from pathlib import Path
import unittest


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"


class TWSCILocalTests(unittest.TestCase):
    def test_python_and_ios_jobs_have_executable_local_equivalents(self):
        workflow = WORKFLOW.read_text()
        python_job = workflow.split("\n  ios:\n", 1)[0]
        ios_job = "\n  ios:\n" + workflow.split("\n  ios:\n", 1)[1]

        self.assertIn("  test:\n", python_job)
        self.assertIn("runs-on: ubuntu-latest", python_job)
        self.assertIn("PYTHONPATH=src python -m unittest discover -s tests", python_job)
        self.assertIn("  ios:\n", ios_job)
        self.assertIn("runs-on: macos-latest", ios_job)
        self.assertIn(
            "python3 -m unittest discover -s apps/ios/tests -p 'test_*.py' -v",
            ios_job,
        )

    def test_fallback_receipt_preserves_failure_visibility_without_checkout(self):
        workflow = WORKFLOW.read_text()
        fallback = workflow.split("  fallback_receipt:", 1)[1]

        self.assertIn("needs: [preflight, test, ios]", fallback)
        self.assertIn("if: always()", fallback)
        self.assertIn('"remote_ci": "EXECUTED_HOSTED"', fallback)
        self.assertNotIn("actions/checkout@", fallback)


if __name__ == "__main__":
    unittest.main()
