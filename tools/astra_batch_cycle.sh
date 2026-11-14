#!/usr/bin/env bash
# ATLAS managed Astra One batch; a separate service, not an interactive Codex session.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ASTRA_ROOT="$ROOT/bootstrap/astra-one"
STATE="${ARCHON_ASTRA_HOME:-$HOME/.local/state/archon-astra}"
TEST_IMAGE="${ARCHON_ASTRA_TEST_IMAGE:-python:3.12-slim}"
CLI=(python3 -m astra_one.linux_cli --home "$STATE")
for marker in STOP PAUSE PAUSED_QUOTA; do
  if [[ -e "$STATE/$marker" ]]; then
    printf '[ARCHON/ATLAS] %s present: no worker or develop push will start\n' "$marker"
    exit 0
  fi
done
[[ -f "$STATE/sda.sqlite3" ]] || { echo 'Astra state is not initialized' >&2; exit 1; }
cd "$ASTRA_ROOT"
# Repeated calls are safe: the Python Master acquires an exclusive file lock.
RUN_RC=0
# Full imported parent plan with bounded repair claims; the Master still caps
# concurrent workers at five and the service has a wall-clock limit.
RUN_OUTPUT=$("${CLI[@]}" run \
  --workers 5 --model gpt-5.6-luna --effort medium \
  --max-tasks 1000 --max-minutes 120 --max-seconds-per-task 1800 \
  --max-repairs 3 --auto-integrate --test-image "$TEST_IMAGE" 2>&1) || RUN_RC=$?
printf '%s\n' "$RUN_OUTPUT"
# A refusal to start is an operational error. A completed batch with terminal
# worker failures may still publish unrelated, already-QC-approved commits;
# retain its nonzero status for systemd after the publication check.
if (( RUN_RC == 2 )); then
  exit "$RUN_RC"
fi
# STOP, PAUSE or exhausted quota blocks Git publication.
for marker in STOP PAUSE PAUSED_QUOTA; do
  if [[ -e "$STATE/$marker" ]]; then
    echo "[ARCHON/ATLAS] $marker blocks publication" >&2
    exit 0
  fi
done
INTEGRATION="$STATE/integration"
if [[ ! -d "$INTEGRATION/.git" && ! -f "$INTEGRATION/.git" ]]; then
  echo '[ARCHON/ATLAS] No local integration worktree yet; nothing to publish'
  exit "$RUN_RC"
fi
# Only a complete, independently reviewed local integration SHA is eligible.
python3 - "$STATE/sda.sqlite3" "$INTEGRATION" <<'PY'
import sqlite3, subprocess, sys
from pathlib import Path
p, worktree = Path(sys.argv[1]), Path(sys.argv[2])
with sqlite3.connect(f'file:{p.as_posix()}?mode=ro', uri=True) as con:
    expected = con.execute("SELECT value FROM settings WHERE key='integration_sha'").fetchone()[0]
    source = con.execute("SELECT value FROM settings WHERE key='source'").fetchone()[0]
head = subprocess.check_output(['git','-C',str(worktree),'rev-parse','HEAD'],text=True).strip()
if expected != head or not str(source):
    raise SystemExit('Stored Astra integration SHA does not match inspected Git HEAD')
PY
[[ -z "$(git -C "$INTEGRATION" status --porcelain --untracked-files=all)" ]] || {
  echo '[ARCHON/ATLAS] Integration worktree dirty, refusing develop publication' >&2; exit 1;
}
# Full tests before a single, non-force fast-forward-only develop update.
cd "$INTEGRATION"
PYTHONPATH=src:. python3 -m unittest discover -s tests -p 'test_*.py' -q
python3 tools/verify_foundation.py
git diff --check HEAD^ HEAD
REMOTE="https://github.com/admindeveloper4562/A.R.C.H.O.N.git"
[[ "$(git config --get remote.origin.url)" == "$REMOTE" ]] || { echo 'Unexpected Git origin; refusing push' >&2; exit 1; }
git fetch --no-tags origin develop
REMOTE_SHA="$(git rev-parse refs/remotes/origin/develop)"
LOCAL_SHA="$(git rev-parse HEAD)"
if [[ "$REMOTE_SHA" == "$LOCAL_SHA" ]]; then
  echo '[ARCHON/ATLAS] No new accepted commits to publish'
  exit "$RUN_RC"
fi
if ! git merge-base --is-ancestor "$REMOTE_SHA" "$LOCAL_SHA"; then
  echo '[ARCHON/ATLAS] Remote develop diverged: manual review required, no force push' >&2
  touch "$STATE/PAUSE"
  exit 1
fi
# Authorized by owner's request: develop only, never main.
git push origin HEAD:refs/heads/develop || {
  touch "$STATE/PAUSE"
  echo '[ARCHON/ATLAS] Develop publication rejected; PAUSE set for operator review' >&2
  exit 1
}
printf '[ARCHON/ATLAS] Published verified integration commit %s to develop\n' "$LOCAL_SHA"
exit "$RUN_RC"
