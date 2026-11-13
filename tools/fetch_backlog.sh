#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
command -v gh >/dev/null || { echo 'GitHub CLI required' >&2; exit 2; }
gh auth status >/dev/null || exit 3
out='docs/tasks/JARVIS_V2_TASK_PLAN.json'
[[ ! -e "$out" ]] || { echo "Refusing to overwrite $out" >&2; exit 3; }
# Only download historical planning data; no SDA task is enqueued.
gh api 'repos/admindeveloper4562/personal-jarvis/contents/planning/JARVIS_V2_TASK_PLAN.json?ref=planning/jarvis-v2-complete-backlog-20261113' --jq '.content' | base64 -d > "$out"
python3 -c 'import json;d=json.load(open("docs/tasks/JARVIS_V2_TASK_PLAN.json"));print("Reviewed backlog entries:",len(d["tasks"]))'
echo 'Downloaded. Review and commit separately; do not import directly into a live queue.'
