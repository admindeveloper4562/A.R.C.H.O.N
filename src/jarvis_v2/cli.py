"""Read-only and local deterministic foundation commands. No background agents."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .guardian.release import inspect

def main(argv=None):
    p=argparse.ArgumentParser(prog="jarvis-v2")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("modules");s.add_parser("identities");s.add_parser("health")
    x=s.add_parser("guardian-gate");x.add_argument("manifest",type=Path)
    args=p.parse_args(argv)
    if args.command in ("modules","identities"):
        file=Path(__file__).resolve().parents[2]/"config"/("identities.json" if args.command=="identities" else "modules.json")
        if file.exists(): print(file.read_text(encoding="utf-8"))
        else: print(json.dumps({"status":"no manifest; installed wheel has no repository config"}))
    elif args.command=="health":print(json.dumps({"status":"seed_only","deployed":False,"sda_running":False,"guardian_running":False,"archon_running":False,"aegis_running":False,"atlas_sda_running":False,"terminal_monitor_available":True,"modules_implemented":False},indent=2))
    else:print(json.dumps(inspect(args.manifest),indent=2))
    return 0
if __name__ == "__main__": raise SystemExit(main())
