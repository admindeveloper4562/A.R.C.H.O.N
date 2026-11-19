"""REL-017 installation contract and platform-boundary tests."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

from infra.verify_installation import ROOT, validate_manifest

ASTRA_ROOT = ROOT / "bootstrap" / "astra-one"
sys.path.insert(0, str(ASTRA_ROOT))
from astra_one.linux_runtime import ALLOWED_SUFFIXES


class Rel017InstallationTests(unittest.TestCase):
    def test_manifest_declares_complete_platform_boundary(self):
        document = validate_manifest(ROOT)
        self.assertEqual(
            [item["id"] for item in document["platforms"]],
            ["linux", "windows", "cloudflare", "ios", "tws"],
        )
        platforms = {item["id"]: item for item in document["platforms"]}
        self.assertEqual(platforms["ios"]["status"], "deferred_unclaimed")
        self.assertEqual(platforms["tws"]["status"], "out_of_scope")
        self.assertEqual(document["remote_execution"], "disabled")

    def test_manifest_artifacts_are_real_regular_files(self):
        document = json.loads((ROOT / "infra" / "installation_manifest.json").read_text())
        for platform in document["platforms"]:
            for artifact in platform["artifacts"]:
                path = ROOT / Path(*artifact.split("/"))
                self.assertTrue(path.is_file(), artifact)
                self.assertFalse(path.is_symlink(), artifact)

    def test_linux_units_are_hardened_and_qc_only(self):
        service = (ROOT / "infra/systemd/archon-astra.service").read_text()
        timer = (ROOT / "infra/systemd/archon-astra.timer").read_text()
        self.assertIn("Type=oneshot", service)
        self.assertIn("NoNewPrivileges=yes", service)
        self.assertIn("ProtectSystem=strict", service)
        self.assertIn("ProtectHome=read-only", service)
        self.assertIn("qc", (ROOT / "tools/astra_batch_cycle.sh").read_text())
        self.assertIn("OnBootSec=3min", timer)
        self.assertIn("Persistent=no", timer)

    def test_windows_script_has_no_embedded_credentials_or_remote_queue(self):
        script = (ROOT / "infra/windows/install.ps1").read_text()
        self.assertIn("SupportsShouldProcess", script)
        self.assertIn("Register-ScheduledTask", script)
        self.assertIn("remote_queue = 'disabled'", script)
        self.assertNotRegex(script, r"(?i)(password|secret|token)\s*=\s*['\"]")

    def test_cloudflare_contract_names_only_secure_secrets(self):
        document = json.loads((ROOT / "infra" / "installation_manifest.json").read_text())
        cloudflare = next(item for item in document["platforms"] if item["id"] == "cloudflare")
        self.assertEqual(cloudflare["secret_names"], ["ASTRA_INGEST_TOKEN", "ASTRA_VIEW_TOKEN"])
        self.assertEqual(cloudflare["network_mode"], "metadata_monitor_only")
        self.assertNotIn("value", cloudflare)

    def test_verifier_cli_is_read_only_and_green(self):
        result = subprocess.run(
            [sys.executable, "infra/verify_installation.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ok")

    def test_controller_allows_installation_manifest_suffixes(self):
        self.assertTrue({".service", ".timer", ".ps1"}.issubset(ALLOWED_SUFFIXES))


if __name__ == "__main__":
    unittest.main()
