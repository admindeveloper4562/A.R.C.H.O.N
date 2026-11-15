#!/usr/bin/env bash
# Single clean root commit containing Foundation + Astra One; then safe Codex background startup.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="admindeveloper4562/A.R.C.H.O.N"
REMOTE="https://github.com/${REPO}.git"
ASTRA="$ROOT/bootstrap/astra-one"
SRC="$HOME/Projects/ARCHON-astra-source"
STATE="$HOME/.local/state/archon-astra"
TEST_IMAGE="${ARCHON_ASTRA_TEST_IMAGE:-archon-python:3.12-git-20261114}"
for bin in git gh python3 codex docker systemctl; do
  command -v "$bin" >/dev/null || { echo "Missing dependency: $bin" >&2; exit 2; }
done
[[ -z "${SUDO_USER:-}" && "${EUID}" -ne 0 ]] || { echo 'Run as your normal Linux user, never sudo/root' >&2; exit 2; }
[[ -d "$ROOT/src/jarvis_v2" && -f "$ASTRA/MANIFEST.json" ]] || { echo 'Missing foundation or Astra source' >&2; exit 2; }
[[ ! -e "$ROOT/.git" ]] || { echo 'This foundation is already a Git checkout; inspect it before retrying.' >&2; exit 2; }
[[ ! -e "$SRC" && ! -e "$STATE/sda.sqlite3" ]] || { echo 'Existing Astra source or state; refusing to overwrite' >&2; exit 2; }
# Refuse a second old Workhorse controller; inspect/stop it separately before bootstrapping.
if pgrep -u "$(id -u)" -f 'scripts/codex_workhorse_v2[.]py|scripts/codex_workhorse[.]py|scripts/codex_autopilot[.]py' >/dev/null 2>&1; then
  echo 'A legacy Workhorse/Autopilot process is already running; refuse duplicate orchestration' >&2
  exit 2
fi
gh auth status >/dev/null
gh auth setup-git >/dev/null
VISIBILITY="$(gh repo view "$REPO" --json visibility --jq '.visibility')"
[[ "$VISIBILITY" == PRIVATE ]] || { echo 'Target GitHub repository must be private' >&2; exit 2; }
HEADS="$(git ls-remote --heads "$REMOTE")"
[[ -z "$HEADS" ]] || { echo 'Remote already has commits; refusing to overwrite one-commit main' >&2; exit 2; }
cd "$ROOT"
# Bring the reviewed, dependency-validated 247-task planning snapshot into the new repo.
# The plan remains documentary; only explicit kickoff jobs are enqueued.
PLAN="$ROOT/docs/tasks/JARVIS_V2_TASK_PLAN.json"
gh api "repos/admindeveloper4562/personal-jarvis/contents/planning/JARVIS_V2_TASK_PLAN.json?ref=planning/jarvis-v2-complete-backlog-20261113" \
  --jq '.content' | base64 --decode > "$PLAN"
python3 - "$PLAN" <<'PY_PLAN'
import json, sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
assert p.get('task_count',0)>=247 and len(p['tasks'])==p['task_count']
assert p.get('business_module_active') is False
print('Pinned planned tasks:',p['task_count'])
PY_PLAN
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_*.py' -q
python3 tools/verify_foundation.py
(cd "$ASTRA" && python3 scripts/verify_manifest.py && python3 -m unittest discover -s tests -p 'test_*.py' -q)
# The focus packet must match the full architecture stored in this same foundation.
python3 - "$ROOT" <<'PY'
from pathlib import Path
import hashlib, re, sys
root=Path(sys.argv[1]);focus=(root/'docs/tasks/ASTRA_PHASE1_CONTEXT.md').read_text()
match=re.search(r'Full architecture SHA-256:\*\* `([0-9a-f]{64})`',focus)
actual=hashlib.sha256((root/'docs/architecture/JARVIS_V2_CONSOLIDATED.md').read_bytes()).hexdigest()
if not match or match.group(1)!=actual: raise SystemExit('Focus vs full architecture digest mismatch; review needed')
print('Pinned complete architecture SHA256:',actual)
PY
# First and only root commit on main (remote was checked empty immediately above).
GITHUB_LOGIN="$(gh api user --jq .login)"
GITHUB_ID="$(gh api user --jq .id)"
git init -b main
git remote add origin "$REMOTE"
git config user.name "$GITHUB_LOGIN"
git config user.email "${GITHUB_ID}+${GITHUB_LOGIN}@users.noreply.github.com"
git add -A
python3 tools/check_git_policy.py --branch main --commit 'chore(repo): establish ARCHON foundation and Astra One [MIG-001]'
git commit -m 'chore(repo): establish ARCHON foundation and Astra One [MIG-001]'
git push -u origin main
MAIN_SHA="$(git rev-parse HEAD)"
# The repository description is metadata, not a second Git commit.
gh repo edit "$REPO" --description 'ARCHON — local-first autonomous AI with AEGIS Guardian, ATLAS infrastructure and five-worker SDA' || \
  echo '[ARCHON] Warning: repository description could not be updated' >&2
git switch -c develop
git push -u origin develop
printf '\nMAIN/DEVELOP INITIAL SHA %s\n' "$MAIN_SHA"
# No additional commit is made to main; develop remains the only future integration destination.
mkdir -p "$(dirname "$SRC")"
git clone --single-branch --branch develop "$REMOTE" "$SRC"
(cd "$ASTRA" && python3 -m astra_one.linux_cli doctor --source "$SRC")
cd "$ASTRA"
python3 -m astra_one.linux_cli --home "$STATE" init --source "$SRC"
python3 -m astra_one.linux_cli --home "$STATE" architecture import --file "$SRC/docs/tasks/ASTRA_PHASE1_CONTEXT.md"
FOCUS_SHA="$(sha256sum "$SRC/docs/tasks/ASTRA_PHASE1_CONTEXT.md" | cut -d' ' -f1)"
# Executing this bootstrap script is the owner's approval of this exact reviewed scope.
python3 -m astra_one.linux_cli --home "$STATE" architecture approve --sha "$FOCUS_SHA"
python3 -m astra_one.linux_cli --home "$STATE" enqueue --file "$ROOT/config/astra_kickoff_tasks.json"
# One real Codex smoke test. If this fails, source is still committed but the runner is not started.
codex login status
codex exec --ephemeral --sandbox read-only -C "$SRC" \
  -m gpt-5.6-luna -c model_reasoning_effort=medium \
  'Reply with exactly ARCHON_READY'
docker info >/dev/null
docker image inspect "$TEST_IMAGE" >/dev/null || { echo "Missing Docker test image: $TEST_IMAGE" >&2; exit 2; }
# No system-wide service. Timer runs under the current authenticated user.
UNIT="$HOME/.config/systemd/user"
mkdir -p "$UNIT"
cat > "$UNIT/archon-astra.service" <<SERVICE
[Unit]
Description=ATLAS Astra One verified five-worker development batch
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$ASTRA
Environment=PATH=$PATH
Environment=ARCHON_ASTRA_HOME=$STATE
Environment=ARCHON_ASTRA_TEST_IMAGE=$TEST_IMAGE
ExecStart=/usr/bin/env bash $ROOT/tools/astra_batch_cycle.sh
TimeoutStartSec=0
KillMode=control-group
NoNewPrivileges=true
SERVICE
cat > "$UNIT/archon-astra.timer" <<'TIMER'
[Unit]
Description=Periodically resume approved ARCHON SDA development batches

[Timer]
OnBootSec=3min
OnUnitInactiveSec=3min
AccuracySec=20s
Unit=archon-astra.service

[Install]
WantedBy=timers.target
TIMER
systemctl --user daemon-reload
systemctl --user enable --now archon-astra.timer
systemctl --user start --no-block archon-astra.service
printf '\nARCHON INIT COMPLETE\nRepo: %s\nmain SHA: %s\ndevelop: created from main\nSDA state: %s\n' "$REPO" "$MAIN_SHA" "$STATE"
echo 'Monitor: python3 ~/Projects/ARCHON/tools/atlas_monitor.py --source astra --db ~/.local/state/archon-astra/sda.sqlite3 --watch'
echo 'Live logs: journalctl --user -fu archon-astra.service'
echo 'Pause: cd ~/Projects/ARCHON/bootstrap/astra-one && python3 -m astra_one.linux_cli --home ~/.local/state/archon-astra pause'
