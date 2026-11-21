#!/usr/bin/env bash
set -euo pipefail
[[ -n "${GITHUB_HEAD_REF:-}" && -n "${GITHUB_BASE_REF:-}" ]] || { echo 'Not a PR context; no branch check needed'; exit 0; }
python3 tools/check_git_policy.py --branch "$GITHUB_HEAD_REF"
git fetch --no-tags origin "$GITHUB_BASE_REF" >/dev/null
base=$(git merge-base HEAD "origin/$GITHUB_BASE_REF")
while IFS= read -r msg; do
  [[ -z "$msg" ]] && continue
  python3 tools/check_git_policy.py --branch "$GITHUB_HEAD_REF" --commit "$msg"
done < <(git log --no-merges --format=%s "$base..HEAD")
