"""Run local zero-network source/package verification using stdlib + installed tsc/node."""
import json
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
checks=[([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-q'],root),
        (['tsc','--noEmit'],root/'cloudflare'/'astra-one-monitor'),
        (['tsc','--noEmit','false','--outDir','.test-output'],root/'cloudflare'/'astra-one-monitor'),
        (['node','--test','tests/worker.test.mjs'],root/'cloudflare'/'astra-one-monitor')]
for cmd,cwd in checks:
    print('RUN', ' '.join(cmd),'in',cwd)
    p=subprocess.run(cmd,cwd=cwd,check=False)
    if p.returncode:
        print('Verification FAILED:',cmd,file=sys.stderr)
        raise SystemExit(p.returncode)
print('Astra One offline verification complete: Python + TypeScript + API smoke.')
