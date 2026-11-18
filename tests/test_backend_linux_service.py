import unittest

from jarvis_v2.backend import LinuxServiceError, LinuxServiceProfile, startup_decision


class LinuxServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = LinuxServiceProfile(
            "archon-astra.service", "/usr/local/bin/archon-astra",
            ("/usr/local/bin/archon-astra", "health", "--json"),
        )

    def test_unit_is_shell_free_and_hardened(self):
        unit = self.profile.render()
        self.assertIn("ExecStart=/usr/local/bin/archon-astra", unit)
        self.assertIn("ExecStartPost=/usr/local/bin/archon-astra health --json", unit)
        self.assertIn("NoNewPrivileges=yes", unit)
        self.assertIn("ProtectSystem=strict", unit)
        self.assertNotIn("$(", unit)

    def test_startup_does_not_duplicate_a_healthy_service(self):
        self.assertEqual(startup_decision(self.profile, {self.profile.unit_name: 0}, True), "start")
        self.assertEqual(startup_decision(self.profile, {self.profile.unit_name: 1}, True), "already_running")
        self.assertEqual(startup_decision(self.profile, {self.profile.unit_name: 1}, False), "health_failed")
        with self.assertRaisesRegex(LinuxServiceError, "duplicate"):
            startup_decision(self.profile, {self.profile.unit_name: 2}, True)

    def test_invalid_profile_inputs_fail_closed(self):
        with self.assertRaises(LinuxServiceError):
            LinuxServiceProfile("bad", "/usr/bin/archon", ("/usr/bin/archon", "health"))
        with self.assertRaises(LinuxServiceError):
            LinuxServiceProfile("archon-astra.service", "archon", ("archon", "health"))
        with self.assertRaises(LinuxServiceError):
            LinuxServiceProfile("archon-astra.service", "/usr/bin/archon", ("/bin/sh", "-c", "health"))


if __name__ == "__main__":
    unittest.main()
