#!/usr/bin/env bash
# ATLAS managed Astra One batch; a separate service, not an interactive Codex session.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ASTRA_ROOT="$ROOT/bootstrap/astra-one"
STATE="${ARCHON_ASTRA_HOME:-$HOME/.local/state/archon-astra}"
TEST_IMAGE="${ARCHON_ASTRA_TEST_IMAGE:-archon-python:3.12-git-20261114}"
RECOVERY_MODEL="${ARCHON_ASTRA_RECOVERY_MODEL:-gpt-6.1-sol}"
RECOVERY_EFFORT="${ARCHON_ASTRA_RECOVERY_EFFORT:-high}"
CLI=(python3 -m astra_one.linux_cli --home "$STATE")
for marker in STOP PAUSE PAUSED_QUOTA; do
  if [[ -e "$STATE/$marker" ]]; then
    printf '[ARCHON/ATLAS] %s present: no worker or develop push will start\n' "$marker"
    exit 0
  fi
done
[[ -f "$STATE/sda.sqlite3" ]] || { echo 'Astra state is not initialized' >&2; exit 1; }
cd "$ASTRA_ROOT"
# The durable Supervisor pass only classifies recorded failures and opens
# bounded recovery cases; it never claims, approves, merges or starts a model.
SUPERVISOR_OUTPUT=$("${CLI[@]}" supervisor-tick --limit 50)
printf '%s\n' "$SUPERVISOR_OUTPUT"
# Repeated calls are safe: the Python Master acquires an exclusive file lock.
RUN_RC=0
# Full imported parent plan with bounded repair claims; the Master still caps
# concurrent workers at five and the service has a wall-clock limit.
RUN_OUTPUT=$("${CLI[@]}" run \
  --workers 5 --model gpt-5.6-luna --effort medium \
  --max-tasks 1000 --max-minutes 120 --max-seconds-per-task 1800 \
  --max-repairs 3 --auto-integrate --test-image "$TEST_IMAGE" 2>&1) || RUN_RC=$?
printf '%s\n' "$RUN_OUTPUT"
# Failed generations are repaired only after the normal Master releases its
# lock. The recovery lanes are bounded and fenced by the same canonical state.
RECOVERY_RC=0
RECOVERY_OUTPUT=$("${CLI[@]}" supervisor-recover --limit 2 --model "$RECOVERY_MODEL" --effort "$RECOVERY_EFFORT" \
  --test-image "$TEST_IMAGE" --max-seconds-per-task 1800 2>&1) || RECOVERY_RC=$?
printf '%s\n' "$RECOVERY_OUTPUT"
# A refusal to start is an operational error. A completed batch with terminal
# worker failures may still publish unrelated, already-QC-approved commits;
# retain its nonzero status for systemd after the publication check.
if (( RUN_RC == 2 || RECOVERY_RC == 2 )); then
  exit 2
fi
# STOP, PAUSE or exhausted quota blocks Git publication.
for marker in STOP PAUSE PAUSED_QUOTA; do
  if [[ -e "$STATE/$marker" ]]; then
    echo "[ARCHON/ATLAS] $marker blocks publication" >&2
    exit "$RUN_RC"
  fi
done
INTEGRATION="$(python3 - "$STATE/sda.sqlite3" <<'PY'
import sqlite3
import sys
from pathlib import Path

database = Path(sys.argv[1]).resolve(strict=True)
with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as con:
    row = con.execute(
        "SELECT value FROM settings WHERE key='integration_path'"
    ).fetchone()
if not row or not row[0]:
    raise SystemExit("Missing canonical integration_path setting")
path = Path(row[0]).expanduser().resolve()
state = database.parent.resolve()
try:
    path.relative_to(state)
except ValueError as exc:
    raise SystemExit("Canonical integration path is outside Astra state") from exc
print(path)
PY
)"
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
LOCAL_SHA="$(git rev-parse HEAD)"
# GitHub Actions quota is exhausted for this project. Keep the durable local
# integration checkpoint and require a separate owner-approved publication
# operation after remote CI policy is reviewed; this unattended service never
# fetches or pushes and therefore cannot consume remote CI quota.
printf '[ARCHON/ATLAS] Remote develop publication deferred; local checkpoint=%s\n' "$LOCAL_SHA"
exit "$RUN_RC"
