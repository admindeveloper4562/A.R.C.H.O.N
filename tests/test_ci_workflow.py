"""Regression checks for executable hosted CI jobs."""

import unittest
from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"


class CIWorkflowTests(unittest.TestCase):
    def test_python_and_ios_jobs_have_runners_and_test_commands(self):
        workflow = WORKFLOW.read_text()

        python_job = workflow.split("\n  ios:\n", 1)[0]
        ios_job = "\n  ios:\n" + workflow.split("\n  ios:\n", 1)[1]

        self.assertIn("  test:\n", python_job)
        self.assertIn("runs-on: ubuntu-latest", python_job)
        self.assertIn("python -m unittest discover -s tests", python_job)

        self.assertIn("  ios:\n", ios_job)
        self.assertIn("runs-on: macos-latest", ios_job)
        self.assertIn("actions/checkout@v4", ios_job)
        self.assertIn(
            "python3 -m unittest discover -s apps/ios/tests -p 'test_*.py' -v",
            ios_job,
        )


if __name__ == "__main__":
    unittest.main()
