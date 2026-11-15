#!/usr/bin/env bash
# Resume an interrupted (already-committed) one-root ARCHON bootstrap without touching Git history.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REPO='admindeveloper4562/A.R.C.H.O.N'
REMOTE="https://github.com/${REPO}.git"
ASTRA="$ROOT/bootstrap/astra-one"
SRC="$HOME/Projects/ARCHON-astra-source"
STATE="$HOME/.local/state/archon-astra"
TEST_IMAGE="${ARCHON_ASTRA_TEST_IMAGE:-archon-python:3.12-git-20261114}"
if [[ "$EUID" -eq 0 || -n "${SUDO_USER:-}" ]]; then
  echo 'Run as your normal Linux user; never sudo/root' >&2; exit 2
fi
for binary in git gh python3 codex docker systemctl; do
  command -v "$binary" >/dev/null || { echo "Missing: $binary" >&2; exit 2; }
done
[[ -d "$ROOT/.git" ]] || { echo 'Repository has no .git; use archon_bootstrap.sh first.' >&2; exit 2; }
[[ -f "$ASTRA/MANIFEST.json" ]] || { echo 'Astra One source missing' >&2; exit 2; }
[[ "$(git -C "$ROOT" config --get remote.origin.url)" == "$REMOTE" ]] || { echo 'Unexpected origin URL' >&2; exit 2; }
git -C "$ROOT" show-ref --quiet refs/heads/main || { echo 'Local main branch missing' >&2; exit 2; }
git -C "$ROOT" show-ref --quiet refs/heads/develop || { echo 'Local develop branch missing' >&2; exit 2; }
# Preserve all operator work. Do not copy, reset, checkout or pull over a dirty tree.
[[ -z "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]] || { echo 'ARCHON checkout dirty; manually preserve changes.' >&2; exit 2; }
gh auth status >/dev/null
[[ "$(gh repo view "$REPO" --json visibility --jq .visibility)" == PRIVATE ]] || { echo 'Target repo must remain private' >&2; exit 2; }
for name in main develop; do
  git ls-remote --exit-code --heads "$REMOTE" "$name" >/dev/null || { echo "Missing remote $name branch" >&2; exit 2; }
done
if [[ ! -e "$SRC" ]]; then
  git clone --single-branch --branch develop "$REMOTE" "$SRC"
fi
[[ -d "$SRC/.git" ]] || { echo 'Source clone is not a standalone Git checkout' >&2; exit 2; }
[[ -z "$(git -C "$SRC" status --porcelain --untracked-files=all)" ]] || { echo 'Source clone dirty; preserve before retrying' >&2; exit 2; }
cd "$ASTRA"
python3 scripts/verify_manifest.py
python3 -m astra_one.linux_cli doctor --source "$SRC"
SANDBOX_READY="$(PYTHONPATH=. python3 - <<'PY'
from astra_one.linux_runtime import sandbox_status
print('yes' if sandbox_status()['available'] else 'no')
PY
)"
if [[ "$SANDBOX_READY" != yes ]]; then
  echo 'Codex Linux sandbox is unavailable; load the Ubuntu AppArmor bubblewrap profile before resuming Astra.' >&2
  exit 2
fi
if [[ ! -f "$STATE/sda.sqlite3" ]]; then
  python3 -m astra_one.linux_cli --home "$STATE" init --source "$SRC"
fi
# A fresh interrupted setup may safely import the exact checked-in focus packet.
FOCUS="$SRC/docs/tasks/ASTRA_PHASE1_CONTEXT.md"
FOCUS_SHA="$(sha256sum "$FOCUS" | awk '{print $1}')"
ARCH_STATUS="$(python3 -m astra_one.linux_cli --home "$STATE" architecture status)"
python3 - "$ARCH_STATUS" "$FOCUS_SHA" <<'PY'
import json,sys
status=json.loads(sys.argv[1]);digest=sys.argv[2]
if status.get('sha256') and status['sha256']!=digest:
    raise SystemExit('Existing approved or imported architecture differs; do not overwrite it')
PY
if ! python3 - "$ARCH_STATUS" <<'PY'
import json,sys
raise SystemExit(0 if json.loads(sys.argv[1]).get('sha256') else 1)
PY
then
  python3 -m astra_one.linux_cli --home "$STATE" architecture import --file "$FOCUS"
fi
ARCH_STATUS="$(python3 -m astra_one.linux_cli --home "$STATE" architecture status)"
if ! python3 - "$ARCH_STATUS" <<'PY'
import json,sys
raise SystemExit(0 if json.loads(sys.argv[1]).get('approved') else 1)
PY
then
  python3 -m astra_one.linux_cli --home "$STATE" architecture approve --sha "$FOCUS_SHA"
fi
# Never auto-enqueue when any task history exists, including failed or completed tasks.
TASK_COUNT="$(python3 - "$STATE/sda.sqlite3" <<'PY'
import sqlite3,sys
with sqlite3.connect(f'file:{sys.argv[1]}?mode=ro',uri=True) as db:
    print(db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])
PY
)"
if [[ "$TASK_COUNT" == 0 ]]; then
  python3 -m astra_one.linux_cli --home "$STATE" enqueue --file "$ROOT/config/astra_kickoff_tasks.json"
fi
codex login status
codex exec --ephemeral --sandbox read-only -C "$SRC" -m gpt-5.6-luna \
  -c model_reasoning_effort=medium 'Reply with exactly ARCHON_READY'
docker info >/dev/null
docker image inspect "$TEST_IMAGE" >/dev/null || { echo "Missing Docker test image: $TEST_IMAGE" >&2; exit 2; }
UNIT="$HOME/.config/systemd/user"
mkdir -p "$UNIT"
cat > "$UNIT/archon-astra.service" <<SERVICE
[Unit]
Description=ATLAS Astra One Main Codex candidate QC and serial Merger
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
Description=ATLAS periodically resumes approved SDA development batches

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
printf 'ARCHON READY: main preserved, develop-only SDA background started; source=%s state=%s\n' "$SRC" "$STATE"
