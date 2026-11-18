#!/usr/bin/env bash
# ATLAS managed Astra One batch; a separate service, not an interactive Codex session.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ASTRA_ROOT="$ROOT/bootstrap/astra-one"
STATE="${ARCHON_ASTRA_HOME:-$HOME/.local/state/archon-astra}"
TEST_IMAGE="${ARCHON_ASTRA_TEST_IMAGE:-archon-python:3.12-git-20261114}"
CLI=(python3 -m astra_one.linux_cli --home "$STATE")
for marker in STOP PAUSE; do
  if [[ -e "$STATE/$marker" ]]; then
    printf '[ARCHON/ATLAS] %s present: no worker or develop push will start\n' "$marker"
    exit 0
  fi
done
if [[ -e "$STATE/PAUSED_QUOTA" ]]; then
  printf '[ARCHON/ATLAS] PAUSED_QUOTA present: deterministic QC/Merger only; no model or develop push\n'
fi
[[ -f "$STATE/sda.sqlite3" ]] || { echo 'Astra state is not initialized' >&2; exit 1; }
cd "$ASTRA_ROOT"
# The durable Supervisor pass only classifies recorded failures and opens
# bounded recovery cases; it never claims, approves, merges or starts a model.
SUPERVISOR_OUTPUT=$("${CLI[@]}" supervisor-tick --limit 50)
printf '%s\n' "$SUPERVISOR_OUTPUT"
# Keep the qualification cohort authoritative until its target is genuinely
# met. External members remain in history, while batch-replenish admits
# dependency-ready replacements. After the target is met, normal dispatch
# resumes over the full queue.
BATCH_ID="${ARCHON_ASTRA_BATCH_ID:-ARCHON-V3-TRIAL-020}"
BATCH_STATUS=$("${CLI[@]}" batch-status "$BATCH_ID") || {
  rc=$?
  printf '[ARCHON/ATLAS] batch-status failed for %s (exit %s)\n' "$BATCH_ID" "$rc" >&2
  exit "$rc"
}
BATCH_DECISION=0
if python3 - "$BATCH_STATUS" <<'PY'
import json, sys
try:
    item=json.loads(sys.argv[1])
    completed=item["completed_count"]
    target=item["target_count"]
    if not isinstance(completed, int) or not isinstance(target, int) or target < 1:
        raise ValueError("invalid batch counts")
    raise SystemExit(0 if completed < target else 1)
except (TypeError, ValueError, KeyError, json.JSONDecodeError):
    raise SystemExit(2)
PY
then
  printf '[ARCHON/ATLAS] Replenishing qualification cohort %s\n' "$BATCH_ID"
  "${CLI[@]}" batch-replenish "$BATCH_ID" --target 20
else
  BATCH_DECISION=$?
  if (( BATCH_DECISION == 2 )); then
    printf '[ARCHON/ATLAS] batch-status returned invalid JSON or counts\n' >&2
    exit 1
  fi
fi
# Astra One is now a control-plane runner.  Main Codex claims and writes the
# candidate; this service only performs independent QC and serial merging.
RUN_RC=0
RUN_OUTPUT=$("${CLI[@]}" qc-merge \
  --limit 1 --test-image "$TEST_IMAGE" --max-seconds 1800 2>&1) || RUN_RC=$?
printf '%s\n' "$RUN_OUTPUT"
# Any nonzero QC/Merger result is an operational error. Do not continue to
# publication checks after an incomplete or failed control-plane pass.
if (( RUN_RC != 0 )); then
  printf '[ARCHON/ATLAS] qc-merge failed (exit %s); publication skipped\n' "$RUN_RC" >&2
  exit "$RUN_RC"
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
