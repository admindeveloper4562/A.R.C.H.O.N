"""Enforce clean Git naming on PRs (requires full checkout to inspect commits)."""
from __future__ import annotations
import argparse, re, sys, subprocess
BRANCH = re.compile(r"^(feat|fix|refactor|test|docs|chore|recovery|experiment|hotfix)/(core|sda|backend|runtime|research|tws|wic|finance|guardian|automation|platform|migration|release)/([A-Z]{2,8}-[0-9]{3,4})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
COMMIT = re.compile(r"^(feat|fix|refactor|test|docs|chore|perf|build|ci|revert)\(([a-z][a-z0-9-]*)\)!?: ([a-z][^\n]{0,71}?) \[([A-Z]{2,8}-[0-9]{3,4})\]$")
ALIASES={"tws":"TWS","wic":"WIC","automation":"AUTO","migration":"MIG","runtime":"RUN","guardian":"GUARD","backend":"BACK","finance":"FIN","research":"RES","platform":"BASE","release":"REL"}
def check_branch(name: str):
 if name in ("main","develop") or re.fullmatch(r"release/[1-9][0-9]*\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", name): return True
 m=BRANCH.fullmatch(name)
 if not m:return False
 module,tid=m.group(2),m.group(3)
 return tid.split("-")[0] == ALIASES.get(module,module.upper())
def check_commit(s: str):
 m=COMMIT.fullmatch(s)
 if not m or m.group(3).endswith(".") or len(s)>105:return False
 return True

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--branch",required=True);p.add_argument("--commit",action="append",default=[])
 a=p.parse_args(argv)
 errors=[]
 if not check_branch(a.branch):errors.append("invalid branch: "+a.branch)
 for m in a.commit:
  if not check_commit(m):errors.append("invalid commit: "+m)
 if errors:
  print("\n".join(errors),file=sys.stderr);return 1
 print("Branch and commit conventions OK");return 0
if __name__=="__main__":raise SystemExit(main())
