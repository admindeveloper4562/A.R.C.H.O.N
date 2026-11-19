"""Run bounded, network-free CI checks and return only exit status."""

from __future__ import annotations

import os
import re
import base64
import hashlib
import stat
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = ROOT / ".github" / "workflows"
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_WORKFLOW_FILES = 64
MAX_WORKSPACE_FILES = 20_000
ACTION = re.compile(r"\buses:\s*[^@\s]+@([^\s#]+)")
SECRET_PATTERNS = (
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(rb"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
    re.compile(rb"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        rb"(?im)^[ \t]*(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret|client_secret)"
        rb"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{20,}['\"]?(?:\s+#.*)?$"
    ),
)
UNTRUSTED_GITHUB_CONTEXT = re.compile(
    r"\$\{\{\s*github\.(?:event(?:\.|_name\b)|head_ref\b|base_ref\b|ref_name\b)"
)
EXCLUDED_WORKSPACE_DIRS = frozenset({
    ".git", ".serena", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", ".test-output", "build", "dist", "ci-artifacts",
    "codebase", "final-audit",
})


def _quiet_run(
    args: list[str], *, cwd: Path | None = None, timeout: int = 60, env: dict[str, str] | None = None
) -> int:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return 2
    return result.returncode if 0 <= result.returncode <= 255 else 2


def _build_local_wheel(root: Path, project: dict, requirements: list[str], output: Path) -> bool:
    name, version = project["name"], project["version"]
    package_name = name.replace("-", "_").replace(".", "_")
    source_root = root / "src"
    package_root = source_root / package_name
    normalized_name = re.sub(r"[-_.]+", "-", name).lower()
    dist_info = f"{normalized_name.replace('-', '_')}-{version}.dist-info"
    entries: dict[str, bytes] = {}
    total = 0
    try:
        files = sorted(package_root.rglob("*"))
        if not files or len(files) > MAX_WORKSPACE_FILES:
            return False
        for path in files:
            relative = path.relative_to(source_root)
            if any(part in EXCLUDED_WORKSPACE_DIRS for part in relative.parts):
                continue
            if path.is_dir():
                continue
            if path.is_symlink() or not path.is_file() or path.suffix != ".py":
                return False
            data = path.read_bytes()
            total += len(data)
            if len(data) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                return False
            entries[relative.as_posix()] = data
        scripts = project.get("scripts", {})
        if not isinstance(scripts, dict) or any(
            not isinstance(key, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", key)
            or not isinstance(value, str)
            or not value
            or "\n" in value
            or "\r" in value
            for key, value in scripts.items()
        ):
            return False
        metadata = ["Metadata-Version: 2.1", f"Name: {name}", f"Version: {version}"]
        metadata.extend(f"Requires-Dist: {item}" for item in requirements)
        entries[f"{dist_info}/METADATA"] = ("\n".join(metadata) + "\n").encode("utf-8")
        entries[f"{dist_info}/WHEEL"] = (
            "Wheel-Version: 1.0\nGenerator: archon-ci\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        ).encode("utf-8")
        if scripts:
            entry_points = "[console_scripts]\n" + "\n".join(
                f"{key} = {value}" for key, value in sorted(scripts.items())
            ) + "\n"
            entries[f"{dist_info}/entry_points.txt"] = entry_points.encode("utf-8")
        records = []
        for arcname, data in sorted(entries.items()):
            digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
            records.append(f"{arcname},sha256={digest},{len(data)}")
        entries[f"{dist_info}/RECORD"] = ("\n".join(records) + f"\n{dist_info}/RECORD,,\n").encode("utf-8")
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for arcname, data in sorted(entries.items()):
                archive.writestr(arcname, data)
        return output.is_file() and output.stat().st_size <= MAX_FILE_BYTES
    except (OSError, UnicodeError, ValueError, zipfile.BadZipFile):
        return False


def dependency_scan() -> int:
    """Check declared project dependencies in a fresh no-network environment."""
    try:
        pyproject = ROOT / "pyproject.toml"
        if pyproject.stat().st_size > MAX_FILE_BYTES:
            return 2
        metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = metadata.get("project")
        build_system = metadata.get("build-system")
        setuptools = metadata.get("tool", {}).get("setuptools", {}) if isinstance(metadata.get("tool", {}), dict) else {}
        package_find = setuptools.get("packages", {}).get("find", {}) if isinstance(setuptools, dict) else {}
        if not isinstance(project, dict):
            return 2
        if (
            not isinstance(build_system, dict)
            or build_system.get("build-backend") != "setuptools.build_meta"
            or build_system.get("requires") != ["setuptools>=68"]
            or package_find.get("where") != ["src"]
        ):
            return 2
        name, version = project.get("name"), project.get("version")
        dependencies = project.get("dependencies", [])
        optional = project.get("optional-dependencies", {})
        if not isinstance(name, str) or not name or not isinstance(version, str) or not version:
            return 2
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            return 2
        if not isinstance(optional, dict):
            return 2
        requirements = list(dependencies)
        for extra, values in optional.items():
            if not isinstance(extra, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", extra):
                return 2
            if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                return 2
            requirements.extend(f'{item}; extra == "{extra}"' for item in values)
        if any(
            not item or len(item) > 500 or "\n" in item or "\r" in item
            for item in requirements
        ):
            return 2
        package_name = name.replace("-", "_").replace(".", "_")
        if not (ROOT / "src" / package_name).is_dir():
            return 2
    except (OSError, UnicodeError, tomllib.TOMLDecodeError, AttributeError):
        return 2

    with tempfile.TemporaryDirectory(prefix="archon-dependency-scan-") as temporary:
        workspace = Path(temporary)
        virtualenv = workspace / "venv"
        clean_env = {
            "HOME": str(workspace / "home"),
            "LANG": "C",
            "LC_ALL": "C",
            "PATH": os.environ.get("PATH", ""),
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
            "PIP_NO_INDEX": "1",
            "PYTHONNOUSERSITE": "1",
        }
        (workspace / "home").mkdir()
        venv_rc = _quiet_run([sys.executable, "-m", "venv", str(virtualenv)], timeout=60, env=clean_env)
        if venv_rc:
            return venv_rc
        python = virtualenv / "bin" / "python"
        site_packages = virtualenv / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        normalized_name = re.sub(r"[-_.]+", "-", name).lower()
        if (
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.!+_-]{0,63}", version)
            or not site_packages.is_dir()
        ):
            return 2
        wheel = workspace / f"{normalized_name.replace('-', '_')}-{version}-py3-none-any.whl"
        if not _build_local_wheel(ROOT, project, requirements, wheel):
            return 2
        if not site_packages.resolve().is_relative_to(virtualenv.resolve()):
            return 2
        install_rc = _quiet_run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-index", "--no-deps", "--no-cache-dir", str(wheel)],
            timeout=60,
            env=clean_env,
        )
        if install_rc:
            return install_rc
        return _quiet_run([str(python), "-m", "pip", "check"], timeout=60, env=clean_env)


def _contains_secret(data: bytes) -> bool:
    return any(pattern.search(data) for pattern in SECRET_PATTERNS)


def _workspace_files() -> Iterable[str]:
    count = 0
    for directory, names, files, directory_fd in os.fwalk(ROOT, topdown=True, follow_symlinks=False):
        names[:] = sorted(names)
        files[:] = sorted(files)
        for name in tuple(names):
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if name in EXCLUDED_WORKSPACE_DIRS:
                names.remove(name)
                continue
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise RuntimeError("workspace symlink")
        for name in files:
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise RuntimeError("workspace file boundary")
            count += 1
            if count > MAX_WORKSPACE_FILES:
                raise RuntimeError("workspace file limit")
            yield (Path(directory).relative_to(ROOT) / name).as_posix()


def _read_workspace_file(relative: str) -> bytes:
    parts = PurePosixPath(relative).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise RuntimeError("invalid workspace path")
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(ROOT, directory_flags | nofollow)
    try:
        for part in parts[:-1]:
            child_fd = os.open(part, directory_flags | nofollow, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | nofollow, dir_fd=directory_fd)
        try:
            before = os.fstat(file_fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
                raise RuntimeError("workspace file boundary")
            remaining = before.st_size
            chunks = []
            while remaining:
                chunk = os.read(file_fd, min(64 * 1024, remaining))
                if not chunk:
                    raise RuntimeError("workspace file changed")
                chunks.append(chunk)
                remaining -= len(chunk)
            after = os.fstat(file_fd)
            if after.st_size != before.st_size:
                raise RuntimeError("workspace file changed")
            return b"".join(chunks)
        finally:
            os.close(file_fd)
    finally:
        os.close(directory_fd)


def secret_scan() -> int:
    total = 0
    try:
        for relative in _workspace_files():
            data = _read_workspace_file(relative)
            size = len(data)
            if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
                return 2
            total += size
            if _contains_secret(data):
                return 1
    except (OSError, RuntimeError, UnicodeError, subprocess.SubprocessError):
        return 2
    return 0


def _workflow_is_safe(text: str) -> bool:
    required_ids = (
        "unit_tests",
        "policy",
        "foundation",
        "bootstrap",
        "dependency_scan",
        "secret_scan",
        "security_scan",
        "ios_tests",
    )
    job_blocks = {}
    in_jobs = False
    current_job = None
    for line in text.splitlines():
        if line == "jobs:":
            in_jobs = True
            continue
        if in_jobs and line and not line.startswith(" "):
            in_jobs = False
            current_job = None
        if in_jobs:
            match = re.fullmatch(r"  ([A-Za-z0-9_-]+):", line)
            if match:
                current_job = match.group(1)
                job_blocks[current_job] = []
            elif current_job:
                job_blocks[current_job].append(line)
    all_job_text = "\n".join("\n".join(lines) for lines in job_blocks.values())
    if (
        not job_blocks
        or any("runs-on:" not in "\n".join(lines) or "steps:" not in "\n".join(lines) for lines in job_blocks.values())
        or any(f"id: {name}" not in all_job_text for name in required_ids)
        or "steps.unit_tests.outcome != 'success'" not in text
        or "steps.ios_tests.outcome != 'success'" not in text
    ):
        return False
    references = ACTION.findall(text)
    if not references or any(not re.fullmatch(r"[0-9a-fA-F]{40}", reference) for reference in references):
        return False
    if re.search(r"(?m)^permissions:\s*$", text) is None or re.search(
        r"(?m)^\s+contents:\s+read\s*$", text
    ) is None:
        return False
    if re.search(r"(?im)^\s*(?:permissions:.*(?:write-all|read-all)|[A-Za-z_-]+:\s*write)\s*$", text):
        return False
    if re.search(r"(?m)^\s*(?:pull_request_target|workflow_run):", text):
        return False
    if UNTRUSTED_GITHUB_CONTEXT.search(text):
        return False
    if (
        'ci_report.py --profile python --root "$artifact_dir" --output "$artifact_dir/report.json"' not in text
        or 'ci_report.py --profile ios --root "$artifact_dir" --output "$artifact_dir/report.json"' not in text
    ):
        return False
    for lines in job_blocks.values():
        job_text = "\n".join(lines)
        steps = re.findall(r"(?ms)^      - .*?(?=^      - |\Z)", job_text)
        for step in steps:
            if "actions/checkout@" in step and not re.search(r"(?m)^\s+persist-credentials:\s+false\s*$", step):
                return False
    return True


def _workflow_files() -> Iterable[Path]:
    return sorted({*WORKFLOW_ROOT.rglob("*.yml"), *WORKFLOW_ROOT.rglob("*.yaml")})


def security_scan() -> int:
    try:
        files = list(_workflow_files())
        if not files or len(files) > MAX_WORKFLOW_FILES:
            return 2
        total = 0
        for path in files:
            if path.is_symlink() or not path.is_file():
                return 2
            size = path.stat().st_size
            if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
                return 2
            total += size
            if not _workflow_is_safe(path.read_text(encoding="utf-8")):
                return 1
    except (OSError, UnicodeError):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    values = list(argv if argv is not None else sys.argv[1:])
    checks = {
        "dependency_scan": dependency_scan,
        "secret_scan": secret_scan,
        "security_scan": security_scan,
    }
    if len(values) != 1 or values[0] not in checks:
        return 2
    return checks[values[0]]()


if __name__ == "__main__":
    raise SystemExit(main())
