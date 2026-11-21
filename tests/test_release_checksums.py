import io
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.verify_release import ENTRY_POINTS, Verification, _normalize_sdist, _write_checksum_manifest


class ReleaseChecksumManifestTests(unittest.TestCase):
    def test_source_distribution_normalization_removes_archive_times(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            archives = [Path(temporary_directory) / f"source-{index}.tar.gz" for index in (1, 2)]
            for path, timestamp in zip(archives, (100, 200)):
                with tarfile.open(path, "w:gz") as archive:
                    data = b"source payload"
                    member = tarfile.TarInfo("sample-0.0.3/source.txt")
                    member.size = len(data)
                    member.mtime = timestamp
                    member.uid = member.gid = timestamp
                    archive.addfile(member, io.BytesIO(data))
                _normalize_sdist(path, 1234567890)

            self.assertEqual(archives[0].read_bytes(), archives[1].read_bytes())
            self.assertEqual(int.from_bytes(archives[0].read_bytes()[4:8], "little"), 1234567890)
            with tarfile.open(archives[0], "r:gz") as archive:
                member = archive.getmember("sample-0.0.3/source.txt")
                self.assertEqual((member.mtime, member.uid, member.gid), (1234567890, 0, 0))
                self.assertEqual(archive.extractfile(member).read(), b"source payload")

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


    def test_artifact_report_paths_are_relative_to_release_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            verifier = Verification(output)
            distribution = output / "dist"
            wheel = distribution / "sample.whl"
            sdist = distribution / "sample.tar.gz"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("sample-0.0.3.dist-info/entry_points.txt", "\n".join(sorted(ENTRY_POINTS)))
                archive.writestr("sample-0.0.3.dist-info/METADATA", "Requires-Python: >=3.11\n")
                archive.writestr("sample/share/jarvis-v2/modules.json", "{}")
                archive.writestr("sample/share/jarvis-v2/identities.json", "{}")
            with tarfile.open(sdist, "w:gz") as archive:
                for name in (
                    "sample/config/modules.json", "sample/config/identities.json",
                    "sample/requirements/build.lock", "sample/requirements/runtime.lock",
                ):
                    data = b"{}"
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))

            report = verifier.validate_artifacts(wheel, sdist, {"project": {"dependencies": []}})

            self.assertEqual(report["wheel"]["path"], "dist/sample.whl")
            self.assertEqual(report["sdist"]["path"], "dist/sample.tar.gz")


if __name__ == "__main__":
    unittest.main()
