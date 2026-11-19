"""Validate the repository-level ARCHON installation contract without side effects."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "infra" / "installation_manifest.json"
PLATFORM_IDS = ("linux", "windows", "cloudflare", "ios", "tws")
STATUSES = {
    "supported_local",
    "supported_wsl_harness",
    "optional_owner_operated",
    "deferred_unclaimed",
    "out_of_scope",
}
SECRET_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
RELATIVE = re.compile(r"^[^\\/][^\\]*$")


class InstallationManifestError(ValueError):
    """Raised when the installation contract is malformed or incomplete."""


def _relative_file(value: object, *, root: Path, label: str) -> Path:
    if not isinstance(value, str) or not value or not RELATIVE.fullmatch(value):
        raise InstallationManifestError(f"{label} must be a POSIX relative path")
    path = Path(*value.split("/"))
    if path.is_absolute() or ".." in path.parts:
        raise InstallationManifestError(f"{label} escapes repository root")
    candidate = root / path
    resolved_root = root.resolve()
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (FileNotFoundError, ValueError) as exc:
        raise InstallationManifestError(f"{label} does not resolve inside repository") from exc
    if candidate.is_symlink() or not candidate.is_file():
        raise InstallationManifestError(f"{label} must be a regular file")
    return resolved


def _bounded_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise InstallationManifestError(f"{label} must be a bounded string")
    return value


def validate_manifest(root: Path = ROOT) -> dict[str, Any]:
    """Validate all declared platform artifacts and return the parsed manifest."""
    root = root.resolve(strict=True)
    manifest_path = root / "infra" / "installation_manifest.json"
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallationManifestError("installation manifest is not valid JSON") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise InstallationManifestError("unsupported installation manifest")
    if document.get("product") != "ARCHON Astra One":
        raise InstallationManifestError("unexpected product identity")
    if document.get("source_branch") != "develop":
        raise InstallationManifestError("installation must bind to develop")
    if document.get("integration_policy") != "local_serialized_merger_only":
        raise InstallationManifestError("unsafe integration policy")
    if document.get("remote_execution") != "disabled":
        raise InstallationManifestError("remote execution must remain disabled")

    platforms = document.get("platforms")
    if not isinstance(platforms, list) or len(platforms) != len(PLATFORM_IDS):
        raise InstallationManifestError("manifest must declare exactly five platforms")
    by_id: dict[str, dict[str, Any]] = {}
    for item in platforms:
        if not isinstance(item, dict):
            raise InstallationManifestError("platform entry must be an object")
        platform_id = item.get("id")
        if platform_id not in PLATFORM_IDS or platform_id in by_id:
            raise InstallationManifestError("platform IDs must be unique and complete")
        status = item.get("status")
        if status not in STATUSES:
            raise InstallationManifestError(f"invalid status for {platform_id}")
        tools = item.get("required_tools")
        if not isinstance(tools, list) or any(not isinstance(tool, str) or not tool for tool in tools):
            raise InstallationManifestError(f"invalid required tools for {platform_id}")
        artifacts = item.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) > 20:
            raise InstallationManifestError(f"invalid artifacts for {platform_id}")
        for index, artifact in enumerate(artifacts):
            _relative_file(artifact, root=root, label=f"{platform_id}.artifacts[{index}]")
        runbook = item.get("runbook")
        _relative_file(runbook, root=root, label=f"{platform_id}.runbook")
        _bounded_string(item.get("network_mode"), f"{platform_id}.network_mode")
        _bounded_string(item.get("startup_action"), f"{platform_id}.startup_action")
        secret_names = item.get("secret_names", [])
        if not isinstance(secret_names, list) or any(
            not isinstance(name, str) or not SECRET_NAME.fullmatch(name) for name in secret_names
        ):
            raise InstallationManifestError(f"invalid secret names for {platform_id}")
        if platform_id in {"ios", "tws"} and artifacts:
            raise InstallationManifestError(f"deferred platform {platform_id} cannot claim artifacts")
        by_id[platform_id] = item
    if tuple(by_id) != PLATFORM_IDS:
        raise InstallationManifestError("platform ordering or coverage is invalid")
    if by_id["ios"]["status"] != "deferred_unclaimed":
        raise InstallationManifestError("iOS must remain deferred_unclaimed")
    if by_id["tws"]["status"] != "out_of_scope":
        raise InstallationManifestError("TWS must remain out_of_scope")
    return document


def _tool_presence(platform: dict[str, Any]) -> dict[str, bool]:
    """Check executable names only; never logs credentials or invokes them."""
    result: dict[str, bool] = {}
    for requirement in platform["required_tools"]:
        executable = requirement.split(">=", 1)[0].split(" ", 1)[0].lower()
        if executable in {"powershell", "powershell.exe", "wsl2", "macos", "xcode", "ios", "simulator", "or", "device"}:
            result[requirement] = False
        else:
            result[requirement] = shutil.which(executable) is not None
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=PLATFORM_IDS, default=None)
    parser.add_argument("--check-tools", action="store_true", help="check local executable presence without running tools")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        document = validate_manifest()
        selected = [item for item in document["platforms"] if args.platform is None or item["id"] == args.platform]
        tool_results = {item["id"]: _tool_presence(item) for item in selected} if args.check_tools else {}
        if args.check_tools and any(not present for result in tool_results.values() for present in result.values()):
            exit_code = 2
        else:
            exit_code = 0
        payload = {"status": "ok" if exit_code == 0 else "missing_tools", "platforms": [item["id"] for item in selected]}
        if args.check_tools:
            payload["tools"] = tool_results
        if args.as_json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print("ARCHON installation contract OK:", ", ".join(payload["platforms"]))
            if args.check_tools:
                print(json.dumps(tool_results, sort_keys=True))
        return exit_code
    except InstallationManifestError as exc:
        print(f"ARCHON installation contract failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
