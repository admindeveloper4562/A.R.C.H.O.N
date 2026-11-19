"""Read-only and local deterministic foundation commands. No background agents."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from .guardian.release import inspect
from .health import HealthError, collect_health
from .system_inventory import InventoryError, collect_inventory, write_inventory

DEFAULT_STATE = Path.home() / ".local" / "state" / "archon"

def main(argv=None):
    p=argparse.ArgumentParser(prog="jarvis-v2")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("modules");s.add_parser("identities")
    i=s.add_parser("inventory")
    i.add_argument("--root",type=Path,default=Path("/"))
    i.add_argument("--max-entries",type=int,default=10000)
    i.add_argument("--output",type=Path)
    h=s.add_parser("health")
    h.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", DEFAULT_STATE)))
    h.add_argument("--repo",type=Path,default=Path.cwd())
    x=s.add_parser("guardian-gate");x.add_argument("manifest",type=Path)
    args=p.parse_args(argv)
    if args.command in ("modules","identities"):
        file=Path(__file__).resolve().parents[2]/"config"/("identities.json" if args.command=="identities" else "modules.json")
        if file.exists(): print(file.read_text(encoding="utf-8"))
        else: print(json.dumps({"status":"no manifest; installed wheel has no repository config"}))
    elif args.command=="inventory":
        try:
            inventory=collect_inventory(root=args.root,max_entries=args.max_entries)
            if args.output:
                write_inventory(args.output, inventory)
            print(json.dumps({
                "inventory_sha256": inventory["inventory_sha256"],
                "entries": inventory["filesystem"]["coverage"]["scanned_entries"],
                "truncated": inventory["filesystem"]["coverage"]["truncated"],
                "permission_denied": len(inventory["filesystem"]["coverage"]["permission_denied"]),
                "skipped_mounts": len(inventory["filesystem"]["coverage"]["skipped_mounts"]),
                "output": str(args.output) if args.output else None,
            }, sort_keys=True))
        except InventoryError as exc:
            print(f"archon inventory: {exc}", file=__import__("sys").stderr)
            return 2
    elif args.command=="health":
        try:
            print(json.dumps(collect_health(state_dir=args.state, repository=args.repo), indent=2, sort_keys=True))
        except HealthError as exc:
            print(f"archon health: {exc}", file=__import__("sys").stderr)
            return 2
    else:print(json.dumps(inspect(args.manifest),indent=2))
    return 0
if __name__ == "__main__": raise SystemExit(main())
