"""Local checks for the iOS application scaffold.

The native iOS target is not present yet, so this executable harness verifies
that the tracked app boundary exists on the hosted macOS runner. Native
Xcode tests belong here once the target is introduced.
"""

import unittest
from pathlib import Path


class IOSScaffoldTests(unittest.TestCase):
    def test_ios_app_boundary_is_tracked(self):
        app_root = Path(__file__).parents[1]
        self.assertTrue(app_root.is_dir())
        self.assertTrue((app_root / ".gitkeep").is_file())


if __name__ == "__main__":
    unittest.main()
