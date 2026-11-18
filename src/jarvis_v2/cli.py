"""Read-only and local deterministic foundation commands. No background agents."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from .guardian.release import inspect
from .health import HealthError, collect_health

def main(argv=None):
    p=argparse.ArgumentParser(prog="jarvis-v2")
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("modules");s.add_parser("identities")
    h=s.add_parser("health")
    h.add_argument("--state",type=Path,default=Path(os.environ.get("ARCHON_STATE", Path.home()/".local/state/archon-astra")))
    h.add_argument("--repo",type=Path,default=Path.cwd())
    x=s.add_parser("guardian-gate");x.add_argument("manifest",type=Path)
    args=p.parse_args(argv)
    if args.command in ("modules","identities"):
        file=Path(__file__).resolve().parents[2]/"config"/("identities.json" if args.command=="identities" else "modules.json")
        if file.exists(): print(file.read_text(encoding="utf-8"))
        else: print(json.dumps({"status":"no manifest; installed wheel has no repository config"}))
    elif args.command=="health":
        try:
            print(json.dumps(collect_health(state_dir=args.state, repository=args.repo), indent=2, sort_keys=True))
        except HealthError as exc:
            print(f"archon health: {exc}", file=__import__("sys").stderr)
            return 2
    else:print(json.dumps(inspect(args.manifest),indent=2))
    return 0
if __name__ == "__main__": raise SystemExit(main())
