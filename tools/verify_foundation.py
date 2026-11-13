#!/usr/bin/env python3
"""Fail-closed metadata conventions; never invokes external processes."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
mod=json.loads((root/"config/modules.json").read_text())
imp=json.loads((root/"config/legacy_import_manifest.json").read_text())
identities=json.loads((root/"config/identities.json").read_text())
assert identities["main_ai"]["name"]=="ARCHON"
assert identities["guardian"]["name"]=="AEGIS"
assert identities["infrastructure"]["name"]=="ATLAS"
assert (root/"tools/atlas_monitor.py").is_file()
assert mod["business_module_enabled"] is False
assert len(mod["modules"])==10
assert set(x["id"] for x in mod["modules"])==set(range(1,11))
assert len(set(x["key"] for x in mod["modules"]))==10
for module in mod["modules"]:
    assert (root/"src/jarvis_v2"/module["key"]/"__init__.py").is_file()
for item in imp["entries"]:
    assert item["target"].startswith("migration/imported/")
    assert not Path(item["target"]).is_absolute()
    assert ".." not in Path(item["target"]).parts
assert not (root/"src/jarvis_v2/business").exists()
print("Validated: 10 modules, ARCHON/AEGIS/ATLAS names, independent monitor, no Business, imports and source layout")
