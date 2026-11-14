"""Run local zero-network package verification without deleting user output."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
from verify_manifest import _verify_manifest


def _run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    print("RUN", " ".join(command), "in", cwd)
    result = subprocess.run(command, cwd=cwd, check=False, env=env)
    if result.returncode:
        raise SystemExit(result.returncode)


def _verify_package(package_root: Path) -> None:
    if package_root.is_symlink() or not package_root.is_dir():
        raise RuntimeError("package root must be a real directory")
    package_root = package_root.resolve()
    monitor = package_root / "cloudflare" / "astra-one-monitor"
    build_dir = monitor / ".test-output"
    if build_dir.exists() or build_dir.is_symlink():
        raise RuntimeError("pre-existing generated build directory; refusing cleanup")
    with tempfile.TemporaryDirectory(prefix="astra-package-tools-") as sandbox:
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": sandbox,
            "TMPDIR": sandbox,
            "TMP": sandbox,
            "TEMP": sandbox,
            "LANG": "C",
            "LC_ALL": "C",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        for name in ("SYSTEMROOT", "WINDIR"):
            if os.environ.get(name):
                env[name] = os.environ[name]
        _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"], package_root, env)
        _run(["tsc", "--noEmit"], monitor, env)
        build_dir.mkdir()
        try:
            _run(["tsc", "--noEmit", "false", "--outDir", ".test-output"], monitor, env)
            _run(["node", "--test", "tests/worker.test.mjs"], monitor, env)
        finally:
            # The directory was absent before this run and was created by this run.
            shutil.rmtree(build_dir)
        _verify_manifest(package_root)


def verify_package() -> None:
    """Verify only the package containing this script."""
    _verify_package(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    verify_package()
    print("Astra One offline verification complete: Python + TypeScript + API smoke.")
