#!/usr/bin/env python3
"""Independent read-only ATLAS terminal monitor; no SDA worker imported or launched.

Run without installing the project:
    python3 tools/atlas_monitor.py --source atlas --watch

Pass ``--source astra`` only when inspecting the preserved historical Astra
database explicitly.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from jarvis_v2.monitor import main

if __name__ == '__main__':
    raise SystemExit(main())
