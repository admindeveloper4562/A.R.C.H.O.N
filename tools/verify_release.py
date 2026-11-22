#!/usr/bin/env python3
"""Build and verify local ARCHON Linux release artifacts without hosted CI."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import time
import tomllib
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOLS = tuple(
    line.strip()
    for line in (ROOT / "requirements/build.lock").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
)
AUDIT_TOOL = "pip-audit==2.10.1"
ENTRY_POINTS = {
    "jarvis-v2 = jarvis_v2.cli:main",
    "atlas-monitor = jarvis_v2.monitor:main",
    "archon-native-controller = jarvis_v2.native_controller:main",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verified_container_archive(output: Path, source_sha: str) -> Path:
    report = json.loads((output / "container-smoke-report.json").read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("result") != "passed" or report.get("source_sha") != source_sha:
        raise RuntimeError("container smoke report does not match the verified source")
    name = report.get("image_archive")
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise RuntimeError("container smoke report has an invalid image archive path")
    archive = output / name
    if archive.is_symlink() or not archive.is_file() or report.get("image_archive_sha256") != _sha256(archive):
        raise RuntimeError("container image archive is missing or its checksum does not match")
    return archive


def _normalize_sdist(path: Path, epoch: int) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        with tarfile.open(path, "r:gz") as source, temporary.open("wb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=epoch, compresslevel=9) as compressed:
                with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as normalized:
                    for member in sorted(source.getmembers(), key=lambda item: item.name):
                        member.mtime = epoch
                        member.uid = member.gid = 0
                        member.uname = member.gname = ""
                        member.pax_headers = {}
                        payload = source.extractfile(member) if member.isfile() else None
                        if member.isfile() and payload is None:
                            raise RuntimeError(f"source distribution member is unreadable: {member.name}")
                        try:
                            normalized.addfile(member, payload)
                        finally:
                            if payload is not None:
                                payload.close()
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_checksum_manifest(output: Path, artifacts: list[Path]) -> Path:
    checksum_file = output / "SHA256SUMS.txt"
    checksum_file.write_text(
        "".join(
            f"{_sha256(path)}  {path.relative_to(output).as_posix()}\n"
            for path in artifacts
        ),
        encoding="utf-8",
    )
    return checksum_file


class Verification:
    def __init__(self, output: Path) -> None:
        self.output = output.resolve()
        self.logs = self.output / "logs"
        self.dist = self.output / "dist"
        self.work = self.output / "work" / uuid.uuid4().hex
        for directory in (self.logs, self.dist, self.work):
            directory.mkdir(parents=True, exist_ok=True)
        self.environment = os.environ.copy()
        for name in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "FORCE_COLOR", "CLICOLOR_FORCE"):
            self.environment.pop(name, None)
        self.environment.update({
            "NO_COLOR": "1",
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
            "PIP_NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        })
        self.records: list[dict[str, object]] = []

    def run(
        self,
        name: str,
        command: list[str],
        *,
        cwd: Path = ROOT,
        env: dict[str, str] | None = None,
        timeout: int = 600,
        input_text: str | None = None,
        expected_returncodes: tuple[int, ...] = (0,),
    ) -> subprocess.CompletedProcess[str]:
        if (
            not isinstance(expected_returncodes, tuple)
            or not expected_returncodes
            or any(type(code) is not int for code in expected_returncodes)
        ):
            raise ValueError("expected_returncodes must be a non-empty tuple of integers")
        started = time.monotonic()
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env or self.environment,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration = time.monotonic() - started
        output = result.stdout + result.stderr
        log = self.logs / f"{name}.log"
        log.write_text(output, encoding="utf-8")
        self.records.append({
            "name": name,
            "command": command,
            "returncode": result.returncode,
            "expected_returncodes": list(expected_returncodes),
            "exit_classification": "expected" if result.returncode in expected_returncodes else "unexpected",
            "duration_seconds": round(duration, 3),
            "log": str(log.relative_to(self.output)),
        })
        if result.returncode not in expected_returncodes:
            tail = "\n".join(output.splitlines()[-30:])
            raise RuntimeError(
                f"{name} exited {result.returncode}; expected {expected_returncodes}; see {log}\n{tail}"
            )
        return result

    def write_json(self, name: str, content: object) -> Path:
        path = self.output / name
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def validate_git(self) -> dict[str, str]:
        branch = self.run("git-branch", ["git", "branch", "--show-current"]).stdout.strip()
        sha = self.run("git-source-sha", ["git", "rev-parse", "HEAD"]).stdout.strip()
        status = self.run("git-status", ["git", "status", "--porcelain", "--untracked-files=all"]).stdout
        if branch == "main":
            raise RuntimeError("release verification refuses to run on main")
        if status.strip():
            raise RuntimeError("release verification requires a clean tracked/untracked worktree")
        return {"branch": branch, "source_sha": sha, "status": "clean"}

    def source_date_epoch(self, source_sha: str) -> str:
        epoch = self.run(
            "source-date-epoch",
            ["git", "show", "-s", "--format=%ct", source_sha],
        ).stdout.strip()
        if not epoch.isdecimal():
            raise RuntimeError("Git commit timestamp is not a numeric SOURCE_DATE_EPOCH")
        return epoch

    def create_venv(self, name: str) -> Path:
        directory = self.work / name
        self.run(f"venv-{name}", [sys.executable, "-m", "venv", str(directory)])
        return directory / "bin" / "python"

    def validate_artifacts(self, wheel: Path, sdist: Path, metadata: dict) -> dict[str, object]:
        with zipfile.ZipFile(wheel) as archive:
            bad = archive.testzip()
            names = archive.namelist()
            wheel_file_count = len(names)
            if bad:
                raise RuntimeError(f"wheel CRC validation failed: {bad}")
            entry_file = next((name for name in names if name.endswith(".dist-info/entry_points.txt")), None)
            if entry_file is None:
                raise RuntimeError("wheel is missing console entry points")
            entries = set(archive.read(entry_file).decode("utf-8").splitlines())
            if not ENTRY_POINTS <= entries:
                raise RuntimeError("wheel console entry points do not match pyproject.toml")
            if not any(name.endswith("/share/jarvis-v2/modules.json") for name in names):
                raise RuntimeError("wheel is missing modules.json package data")
            if not any(name.endswith("/share/jarvis-v2/identities.json") for name in names):
                raise RuntimeError("wheel is missing identities.json package data")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise RuntimeError("wheel contains an unsafe path")
            if any(Path(name).suffix.lower() in {
                ".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite3",
                ".sqlite3-wal", ".sqlite3-shm", ".log", ".pem",
            } for name in names):
                raise RuntimeError("wheel contains runtime or private files")
            metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
            pkg_metadata = archive.read(metadata_name).decode("utf-8")
            if "Requires-Python: >=3.11" not in pkg_metadata:
                raise RuntimeError("wheel Python version metadata is missing")
            for dependency in metadata["project"]["dependencies"]:
                if f"Requires-Dist: {dependency}" not in pkg_metadata:
                    raise RuntimeError(f"wheel is missing runtime dependency {dependency}")

        with tarfile.open(sdist, "r:gz") as archive:
            names = archive.getnames()
            if not any(name.endswith("/config/modules.json") for name in names):
                raise RuntimeError("source distribution is missing modules.json")
            if not any(name.endswith("/config/identities.json") for name in names):
                raise RuntimeError("source distribution is missing identities.json")
            if not all(
                any(name.endswith(f"/{lock}") for name in names)
                for lock in ("requirements/build.lock", "requirements/runtime.lock")
            ):
                raise RuntimeError("source distribution is missing release dependency locks")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise RuntimeError("source distribution contains an unsafe path")
            if any(Path(name).suffix.lower() in {
                ".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite3",
                ".sqlite3-wal", ".sqlite3-shm", ".log", ".pem",
            } for name in names):
                raise RuntimeError("source distribution contains runtime or private files")
        return {
            "wheel": {
                "path": wheel.relative_to(self.output).as_posix(),
                "sha256": _sha256(wheel), "bytes": wheel.stat().st_size,
            },
            "sdist": {
                "path": sdist.relative_to(self.output).as_posix(),
                "sha256": _sha256(sdist), "bytes": sdist.stat().st_size,
            },
            "wheel_file_count": wheel_file_count,
        }

    def verify(self) -> int:
        started = _utc_now()
        git = self.validate_git()
        source_date_epoch = self.source_date_epoch(git["source_sha"])
        self.environment.update({"SOURCE_DATE_EPOCH": source_date_epoch, "PYTHONHASHSEED": "0"})
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = metadata["project"]
        version = project["version"]
        runtime_pins = [line.strip() for line in (ROOT / "requirements/runtime.lock").read_text().splitlines()
                        if line.strip() and not line.lstrip().startswith("#")]
        project_dependencies = project.get("dependencies", [])
        if not isinstance(project_dependencies, list) or not set(project_dependencies) <= set(runtime_pins):
            raise RuntimeError("requirements/runtime.lock is missing a declared dependency")
        if len(runtime_pins) != len(set(runtime_pins)):
            raise RuntimeError("requirements/runtime.lock contains duplicate pins")
        if not all(re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s;]+", item) for item in runtime_pins):
            raise RuntimeError("runtime dependencies must be exactly pinned")

        builder = self.create_venv("builder")
        self.run("install-build-tools", [str(builder), "-m", "pip", "install", *BUILD_TOOLS], timeout=600)
        build_command = [str(builder), "-m", "build", "--no-isolation", "--wheel", "--sdist"]
        self.run("build-wheel-and-sdist", [*build_command, "--outdir", str(self.dist)], timeout=900)
        wheels = list(self.dist.glob("*.whl"))
        sdists = list(self.dist.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise RuntimeError("build must produce exactly one wheel and one source distribution")
        wheel, sdist = wheels[0], sdists[0]
        _normalize_sdist(sdist, int(source_date_epoch))
        artifact_report = self.validate_artifacts(wheel, sdist, metadata)
        repeat_dist = self.work / "repeat-dist"
        repeat_dist.mkdir()
        self.run("rebuild-wheel-and-sdist", [*build_command, "--outdir", str(repeat_dist)], timeout=900)
        repeat_wheels = list(repeat_dist.glob("*.whl"))
        repeat_sdists = list(repeat_dist.glob("*.tar.gz"))
        if len(repeat_wheels) != 1 or len(repeat_sdists) != 1:
            raise RuntimeError("reproducibility build must produce exactly one wheel and one source distribution")
        _normalize_sdist(repeat_sdists[0], int(source_date_epoch))
        repeat_wheel_sha = _sha256(repeat_wheels[0])
        repeat_sdist_sha = _sha256(repeat_sdists[0])
        if repeat_wheel_sha != _sha256(wheel) or repeat_sdist_sha != _sha256(sdist):
            raise RuntimeError("Python release artifacts are not reproducible for the same source timestamp")
        artifact_report["reproducibility"] = {
            "source_date_epoch": source_date_epoch,
            "result": "passed",
            "wheel_sha256": repeat_wheel_sha,
            "sdist_sha256": repeat_sdist_sha,
        }

        runtime = self.create_venv("wheel-install")
        self.run("install-wheel-runtime", [str(runtime), "-m", "pip", "install", *runtime_pins], timeout=600)
        self.run("install-wheel", [str(runtime), "-m", "pip", "install", "--no-deps", str(wheel)], timeout=600)
        self.run("wheel-pip-check", [str(runtime), "-m", "pip", "check"])
        inspect = self.run("wheel-dependency-inventory", [str(runtime), "-m", "pip", "inspect", "--local"])
        inventory = json.loads(inspect.stdout)
        self.write_json("dependency-inventory.json", inventory)

        outside = self.work / "outside-checkout"
        outside.mkdir(exist_ok=True)
        cli_env = {**self.environment, "HOME": str(self.work / "wheel-home")}
        Path(cli_env["HOME"]).mkdir(exist_ok=True)
        commands = (
            ("wheel-cli-help", "jarvis-v2", "--help"),
            ("wheel-cli-modules", "jarvis-v2", "modules"),
            ("wheel-cli-identities", "jarvis-v2", "identities"),
            ("wheel-cli-controller-help", "archon-native-controller", "--help"),
            ("wheel-cli-monitor-help", "atlas-monitor", "--help"),
        )
        for name, *command in commands:
            self.run(name, [str(runtime.parent / command[0]), *command[1:]], cwd=outside, env=cli_env)
        module_document = json.loads((self.logs / "wheel-cli-modules.log").read_text(encoding="utf-8"))
        expected_modules = {"core", "sda", "backend", "runtime", "research", "tws", "wic", "finance", "guardian", "automation"}
        module_names = {item["key"] for item in module_document.get("modules", []) if isinstance(item, dict)}
        if module_names != expected_modules:
            raise RuntimeError("installed wheel did not resolve all ten module configuration entries")
        identity_document = json.loads((self.logs / "wheel-cli-identities.log").read_text(encoding="utf-8"))
        if identity_document.get("active_module_count") != 10:
            raise RuntimeError("installed wheel identity manifest is incomplete")
        state = self.work / "wheel-state"
        self.run("wheel-cli-init", [str(runtime.parent / "jarvis-v2"), "init", "--state", str(state)],
                 cwd=outside, env=cli_env)
        health = self.run("wheel-cli-health", [str(runtime.parent / "jarvis-v2"), "health", "--state",
                                                str(state), "--repo", str(outside)], cwd=outside, env=cli_env)
        if json.loads(health.stdout).get("status") != "healthy":
            raise RuntimeError("installed wheel health check did not pass")
        task_file = self.work / "wheel-task.json"
        task_file.write_text(json.dumps({
            "task_id": "wheel-readonly",
            "priority": "P3",
            "module": "core",
            "payload": {"operation": "native_capabilities"},
        }), encoding="utf-8")
        owner_keys = self.work / "wheel-owner-keys.json"
        approval_file = self.work / "wheel-admission-approval.json"
        cli_env["ARCHON_OWNER_KEYS"] = str(owner_keys)
        approval_script = r"""import base64,hashlib,json,sys,time
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
task=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
private=Ed25519PrivateKey.generate()
claims={'schema':1,'approval_id':'wheel-submit','key_id':'wheel-owner','task_id':task['task_id'],'operation':'task_submit','target':task['task_id'],'content_sha256':hashlib.sha256(json.dumps(task,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest(),'expires_at':int(time.time())+600,'decision':'APPROVE'}
message=json.dumps(claims,sort_keys=True,separators=(',',':')).encode()
public=private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
Path(sys.argv[2]).write_text(json.dumps({'schema':1,'keys':{'wheel-owner':base64.b64encode(public).decode()}}),encoding='utf-8')
Path(sys.argv[2]).chmod(0o644)
Path(sys.argv[3]).write_text(json.dumps(dict(claims,signature=base64.b64encode(private.sign(message)).decode())),encoding='utf-8')
Path(sys.argv[3]).chmod(0o644)
"""
        self.run("wheel-cli-admission-fixture", [str(runtime), "-c", approval_script,
                                                  str(task_file), str(owner_keys), str(approval_file)],
                 cwd=outside, env=cli_env)
        submitted = self.run("wheel-cli-rejects-caller-trust-store", [str(runtime.parent / "jarvis-v2"), "submit",
                                                                        "--state", str(state), "--task-file", str(task_file),
                                                                        "--approval-file", str(approval_file)],
                             cwd=outside, env=cli_env, expected_returncodes=(2,))
        if submitted.returncode != 2 or "task admission approval is not authorized" not in submitted.stderr:
            raise RuntimeError("installed CLI did not reject the caller-selected owner trust store")
        if submitted.stdout.strip():
            raise RuntimeError("installed CLI accepted a caller-selected owner trust store")
        once = self.run("wheel-controller-once", [str(runtime.parent / "archon-native-controller"), "--once",
                                                  "--state", str(state), "--repository", str(outside)],
                        cwd=outside, env=cli_env)
        if json.loads(once.stdout).get("state") != "idle":
            raise RuntimeError("installed controller did not start cleanly without optional owner keys")
        uninstall_env = self.create_venv("uninstall-check")
        self.run("install-for-uninstall-check", [str(uninstall_env), "-m", "pip", "install", "--no-deps", str(wheel)])
        self.run("wheel-pip-uninstall", [str(uninstall_env), "-m", "pip", "uninstall", "-y", project["name"]])
        uninstalled = self.run("wheel-pip-uninstalled", [str(uninstall_env), "-m", "pip", "show", project["name"]],
                               expected_returncodes=(1,))
        if project["name"].casefold() not in (uninstalled.stdout + uninstalled.stderr).casefold() or "not found" not in (
            uninstalled.stdout + uninstalled.stderr
        ).casefold():
            raise RuntimeError("pip uninstall did not report the package as absent")

        source_env = self.create_venv("sdist-install")
        self.run("install-sdist-build-tools", [str(source_env), "-m", "pip", "install",
                                                "setuptools==84.2.1", "wheel==0.48.0", *runtime_pins], timeout=600)
        self.run("install-sdist", [str(source_env), "-m", "pip", "install", "--no-deps", "--no-build-isolation",
                                    str(sdist)], timeout=600)
        self.run("sdist-pip-check", [str(source_env), "-m", "pip", "check"])
        self.run("sdist-installed-cli", [str(source_env.parent / "jarvis-v2"), "modules"],
                 cwd=outside, env=cli_env)

        self.run("compileall", [str(runtime), "-m", "compileall", "-q", "src", "tests", "tools"])
        for check in ("dependency_scan", "secret_scan", "security_scan"):
            self.run(f"local-{check}", [str(builder), "tools/ci_checks.py", check])
        test_started = time.monotonic()
        tests = self.run("full-regression", [str(runtime), "-m", "unittest", "discover", "-s", "tests", "-v"],
                         timeout=1800)
        test_duration = time.monotonic() - test_started
        match = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", tests.stdout + tests.stderr)
        if not match:
            raise RuntimeError("unittest regression count was not present in the test log")
        regression = {
            "source_sha": git["source_sha"],
            "test_count": int(match.group(1)),
            "unittest_seconds": float(match.group(2)),
            "wall_seconds": round(test_duration, 3),
            "result": "passed",
        }
        self.write_json("full-regression-report.json", regression)

        audit_env = self.create_venv("dependency-audit")
        self.run("install-pip-audit", [str(audit_env), "-m", "pip", "install", AUDIT_TOOL], timeout=600)
        audit_lock = self.work / "release-audit.lock"
        audit_lock.write_text("\n".join((*runtime_pins, *BUILD_TOOLS)) + "\n", encoding="utf-8")
        audit = self.run("pip-audit", [str(audit_env.parent / "pip-audit"),
                                        "--requirement", str(audit_lock),
                                        "--format", "json"], timeout=600, expected_returncodes=(0, 1))
        try:
            audit_json = json.loads(audit.stdout)
            vulnerabilities = sum(len(item.get("vulns", [])) for item in audit_json.get("dependencies", []))
            audit_status = "passed" if audit.returncode == 0 and vulnerabilities == 0 else "vulnerabilities_found"
        except (json.JSONDecodeError, AttributeError, TypeError):
            audit_json = {"error": "audit output was not valid JSON", "returncode": audit.returncode}
            vulnerabilities = None
            audit_status = "unavailable"
        security = {
            "source_sha": git["source_sha"],
            "local_scans": {name: "passed" for name in ("dependency_scan", "secret_scan", "security_scan")},
            "pip_audit_version": AUDIT_TOOL,
            "pip_audit_result": audit_status,
            "vulnerabilities": vulnerabilities,
            "pip_audit": audit_json,
        }
        self.write_json("security-report.json", security)

        container_started = time.monotonic()
        container = self.run("clean-container-acceptance", [str(runtime), "tools/container_smoke.py",
                                                              "--output-dir", str(self.output)], timeout=1800)
        container_report = json.loads(container.stdout)
        container_report["wall_seconds"] = round(time.monotonic() - container_started, 3)
        self.write_json("container-smoke-summary.json", container_report)
        image_archive = _verified_container_archive(self.output, git["source_sha"])
        artifact_report["container_image_archive"] = {
            "name": image_archive.name,
            "sha256": _sha256(image_archive),
        }

        checksums = [
            (wheel, _sha256(wheel)),
            (sdist, _sha256(sdist)),
            (image_archive, _sha256(image_archive)),
        ]
        checksum_file = _write_checksum_manifest(self.output, [path for path, _ in checksums])
        self.run("verify-release-checksums", ["sha256sum", "-c", checksum_file.name], cwd=self.output)

        local_ci = {
            "source_sha": git["source_sha"],
            "source_date_epoch": source_date_epoch,
            "branch": git["branch"],
            "worktree": git["status"],
            "package_version": version,
            "runtime_dependencies": runtime_pins,
            "build_tools": list(BUILD_TOOLS),
            "checks": self.records,
            "result": "passed" if audit_status == "passed" else "conditional",
            "hosted_ci": "not_run_github_actions_billing_unavailable",
        }
        self.write_json("local-ci-report.json", local_ci)
        manifest = {
            "schema": 1,
            "project": project["name"],
            "package_version": version,
            "source_sha": git["source_sha"],
            "source_date_epoch": source_date_epoch,
            "branch": git["branch"],
            "started_at": started,
            "finished_at": _utc_now(),
            "python": sys.version,
            "platform": sys.platform,
            "dependency_inventory": "dependency-inventory.json",
            "regression_report": "full-regression-report.json",
            "security_report": "security-report.json",
            "container_report": "container-smoke-report.json",
            "local_ci_report": "local-ci-report.json",
            "artifacts": artifact_report,
            "checksums": checksum_file.name,
            "result": "passed" if audit_status == "passed" else "conditional",
            "known_external_gates": [
                "GitHub Actions billing unavailable",
                "Windows and Apple device acceptance not run",
                "native SDA cutover and trusted AEGIS watchdog remain disabled",
                "finance and communications effects remain disabled",
            ],
        }
        self.write_json("release-manifest.json", manifest)
        return 0 if audit_status == "passed" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "release-qualification")
    args = parser.parse_args()
    verification = Verification(args.output_dir)
    try:
        return verification.verify()
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError, KeyError, StopIteration) as exc:
        verification.write_json("verification-failure.json", {
            "result": "failed",
            "source_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                          capture_output=True, text=True, check=False).stdout.strip(),
            "error": str(exc),
            "finished_at": _utc_now(),
            "commands": verification.records,
        })
        print(f"release verification failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
