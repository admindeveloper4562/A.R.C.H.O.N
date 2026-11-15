"""Verify archive contents against the release's pinned SHA-256 manifest."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
if manifest['version'] != (root/'VERSION').read_text().strip():
    raise SystemExit('MANIFEST version mismatch')
for name, digest in manifest['files'].items():
    path = root/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit('MANIFEST verification failed for: '+name)
print('Astra One Linux release integrity OK:', len(manifest['files']), 'files')
