import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[1] / "bootstrap" / "astra-one"
SCRIPTS = PACKAGE / "scripts"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


manifest_checker = load_script("verify_manifest")
package_runner = load_script("verify_package")


class PackagingPolicyTests(unittest.TestCase):
    def make_package(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "VERSION").write_text("1\n", encoding="utf-8")
        return root

    def write_manifest(self, root: Path, names: list[str]) -> None:
        files = {}
        for name in names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name, encoding="utf-8")
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (root / "MANIFEST.json").write_text(
            json.dumps({"version": "1", "files": files}), encoding="utf-8"
        )

    def test_actual_case_collision_is_rejected(self):
        root = self.make_package()
        self.write_manifest(root, ["docs/Guide.md"])
        (root / "docs" / "guide.md").write_text("collision", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "case-colliding"):
            manifest_checker._verify_manifest(root)

    def test_actual_generated_directory_is_rejected(self):
        root = self.make_package()
        self.write_manifest(root, ["README.md"])
        (root / "build").mkdir()
        (root / "build" / "generated.js").write_text("generated", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "generated artifact"):
            manifest_checker._verify_manifest(root)

    def test_actual_case_colliding_directories_are_rejected(self):
        root = self.make_package()
        self.write_manifest(root, ["Docs/one.txt"])
        (root / "docs").mkdir()
        (root / "docs" / "two.txt").write_text("collision", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "case-colliding"):
            manifest_checker._verify_manifest(root)

    def test_unlisted_file_is_rejected(self):
        root = self.make_package()
        self.write_manifest(root, ["README.md"])
        (root / "extra.txt").write_text("unlisted", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "file set mismatch"):
            manifest_checker._verify_manifest(root)

    def test_symlink_is_rejected_without_following_it(self):
        root = self.make_package()
        target = root / "target.txt"
        target.write_text("preserve", encoding="utf-8")
        (root / "link.txt").symlink_to(target)
        (root / "MANIFEST.json").write_text(
            json.dumps({"version": "1", "files": {"link.txt": "0" * 64}}),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "symlink"):
            manifest_checker._verify_manifest(root)
        self.assertEqual(target.read_text(encoding="utf-8"), "preserve")

    def test_preexisting_build_output_is_preserved(self):
        root = self.make_package()
        build = root / "cloudflare" / "astra-one-monitor" / ".test-output"
        build.mkdir(parents=True)
        marker = build / "marker"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "pre-existing"):
            package_runner._verify_package(root)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_generated_manifest_entries_and_wrangle_directories_are_rejected(self):
        root = self.make_package()
        self.write_manifest(root, ["README.md", "cache.pyc"])
        with self.assertRaisesRegex(ValueError, "generated"):
            manifest_checker._verify_manifest(root)
        root = self.make_package()
        self.write_manifest(root, ["README.md"])
        (root / ".wrangler").mkdir()
        (root / ".wrangler" / "state").write_text("generated", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "generated"):
            manifest_checker._verify_manifest(root)

    def test_windows_unsafe_manifest_and_import_components_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Windows"):
            manifest_checker._safe_relative("docs/CON.txt")
        with self.assertRaisesRegex(ValueError, "Windows"):
            manifest_checker._safe_relative("docs/name. ")
        foundation_spec = importlib.util.spec_from_file_location(
            "verify_foundation_policy", PACKAGE.parents[1] / "tools" / "verify_foundation.py"
        )
        assert foundation_spec.loader is not None
        foundation = importlib.util.module_from_spec(foundation_spec)
        foundation_spec.loader.exec_module(foundation)
        with self.assertRaisesRegex(ValueError, "Windows"):
            foundation.safe_import_target("migration/imported/CON.txt")
        with self.assertRaisesRegex(ValueError, "Windows"):
            foundation.safe_import_target("migration/imported/name.")

    def test_package_tools_do_not_forward_inherited_environment(self):
        root = self.make_package()
        (root / "cloudflare" / "astra-one-monitor").mkdir(parents=True)
        captured = []

        def fake_run(command, cwd, env):
            captured.append(dict(env))

        with patch.dict("os.environ", {"ARCHON_TEST_SECRET": "must-not-forward"}, clear=False), \
                patch.object(package_runner, "_run", side_effect=fake_run), \
                patch.object(package_runner, "_verify_manifest"):
            package_runner._verify_package(root)
        self.assertEqual(len(captured), 4)
        for env in captured:
            self.assertNotIn("ARCHON_TEST_SECRET", env)
            self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")
            self.assertEqual(env["HOME"], env["TMPDIR"])


if __name__ == "__main__":
    unittest.main()
