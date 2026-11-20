import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.verify_release import _write_checksum_manifest


class ReleaseChecksumManifestTests(unittest.TestCase):
    def test_manifest_paths_validate_from_release_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            distribution = output / "dist"
            distribution.mkdir()
            wheel = distribution / "sample.whl"
            sdist = distribution / "sample.tar.gz"
            image = output / "archon-local-image.tar"
            wheel.write_bytes(b"wheel")
            sdist.write_bytes(b"sdist")
            image.write_bytes(b"image")

            manifest = _write_checksum_manifest(output, [wheel, sdist, image])
            result = subprocess.run(
                ["sha256sum", "-c", manifest.name],
                cwd=output,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                [line.split("  ", 1)[1] for line in manifest.read_text().splitlines()],
                ["dist/sample.whl", "dist/sample.tar.gz", "archon-local-image.tar"],
            )


if __name__ == "__main__":
    unittest.main()
