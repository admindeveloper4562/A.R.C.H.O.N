#!/usr/bin/env python3
"""Fail-closed metadata conventions and legacy-import path validation."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath


WINDOWS_RESERVED = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
})


def _validate_windows_component(part: str) -> None:
    if (not part or part.endswith((".", " ")) or any(char in part for char in ':*?"<>|')):
        raise ValueError("Windows-unsafe import target component")
    if part.split(".", 1)[0].casefold() in WINDOWS_RESERVED:
        raise ValueError("Windows-reserved import target component")


def safe_import_target(value: object) -> PurePosixPath:
    if (not isinstance(value, str) or not value or "\\" in value or "\x00" in value
            or value.startswith("/") or value.endswith("/") or "//" in value):
        raise ValueError("unsafe import target")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("unsafe import target")
    for part in path.parts:
        _validate_windows_component(part)
    if path.parts[:2] != ("migration", "imported"):
        raise ValueError("import target outside migration/imported")
    return path


def verify_foundation() -> str:
    repository = Path(__file__).resolve().parents[1]
    if repository.is_symlink() or not repository.is_dir():
        raise ValueError("repository root must be a real directory")
    repository = repository.resolve()
    mod = json.loads((repository / "config/modules.json").read_text(encoding="utf-8"))
    imp = json.loads((repository / "config/legacy_import_manifest.json").read_text(encoding="utf-8"))
    identities = json.loads((repository / "config/identities.json").read_text(encoding="utf-8"))
    assert identities["main_ai"]["name"] == "ARCHON"
    assert identities["guardian"]["name"] == "AEGIS"
    assert identities["infrastructure"]["name"] == "ATLAS"
    assert (repository / "tools/atlas_monitor.py").is_file()
    assert mod["business_module_enabled"] is False
    assert len(mod["modules"]) == 10
    assert {item["id"] for item in mod["modules"]} == set(range(1, 11))
    assert len({item["key"] for item in mod["modules"]}) == 10
    for module in mod["modules"]:
        assert (repository / "src/jarvis_v2" / module["key"] / "__init__.py").is_file()
    for item in imp["entries"]:
        safe_import_target(item.get("target"))
    assert not (repository / "src/jarvis_v2/business").exists()
    return "Validated: 10 modules, ARCHON/AEGIS/ATLAS names, independent monitor, no Business, imports and source layout"


if __name__ == "__main__":
    print(verify_foundation())
