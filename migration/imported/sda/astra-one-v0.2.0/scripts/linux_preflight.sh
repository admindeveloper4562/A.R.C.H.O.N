#!/usr/bin/env bash
set -euo pipefail
if [[ $(id -u) -eq 0 ]]; then echo "Refusing to run SDA as root" >&2; exit 2; fi
command -v python3 >/dev/null || { echo 'Python 3.11+ required'; exit 2; }
python3 - <<'PY'
import sys
if sys.version_info<(3,11):
    raise SystemExit('Python 3.11+ required')
PY
for tool in git codex docker; do
  if command -v "$tool" >/dev/null 2>&1; then echo "$tool: present"; else echo "$tool: missing"; fi
done
codex login status || true
python3 -m astra_one.linux_cli doctor
python3 -m unittest discover -s tests -p 'test_linux_sda.py' -q
