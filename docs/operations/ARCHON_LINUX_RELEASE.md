# ARCHON Linux release

This release packages the existing Linux implementation as Python version `0.0.3`. The repository has no versioning policy that supports a version bump, so qualification retains the audited version. GitHub Actions is not part of the acceptance evidence.

## Build and qualify

From a clean feature or development branch with Python 3.11 or newer and Docker Compose v2:

```sh
PIP_NO_INDEX= PIP_INDEX_URL=https://pypi.org/simple PIP_DEFAULT_TIMEOUT=120 ./tools/verify_release.sh
```

The command checks the clean Git state, builds the wheel and source distribution, installs each into clean virtual environments, runs the existing local checks and full `unittest` suite, inventories dependencies, audits the pinned runtime dependency, and builds and exercises the container. It writes full subprocess logs and reports under `artifacts/release-qualification/`. It requires network access to install pinned build/audit dependencies and query vulnerability data. Clear `PIP_NO_INDEX` when it is set by an offline shell; a successful local run does not establish GitHub-hosted policy enforcement.

The wheel, source distribution and locally built container image remain local. `SHA256SUMS.txt`, dependency inventory, regression report, security report, container report, and release manifest are written alongside them. The verifier refuses dirty worktrees and `main`.

## Install the Python package

Create an isolated environment and install the wheel produced by the verifier:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-cache-dir artifacts/release-qualification/dist/jarvis_v2-0.0.3-py3-none-any.whl
jarvis-v2 modules
jarvis-v2 init --state "$HOME/.local/state/archon"
jarvis-v2 health --state "$HOME/.local/state/archon" --repo "$PWD"
```

The three installed commands are `jarvis-v2`, `atlas-monitor`, and `archon-native-controller`. The wheel carries the static module and identity manifests. The state directory and SQLite files are created with private permissions. To process local queue tasks, keep the native controller in the foreground:

```sh
archon-native-controller --watch --state "$HOME/.local/state/archon" --repository "$PWD"
```

Admission remains local; no task network API is exposed. In addition to OS access to the private state directory, `jarvis-v2 submit` requires an owner-signed approval for the exact canonical task document. The Ed25519 approval binds `task_submit`, the task ID, SHA-256 of the full task document, decision, key ID, and expiry; both the CLI and queue API verify it before writing, and the native controller verifies the persisted approval again before leasing. Use `--approval-file signed-approval.json`. The trusted public-key store is fixed at `/etc/archon/owner-keys.json`; no CLI flag or process environment variable can select a different store.

Create the approval on the owner's workstation. Keep the private key there; only its public key belongs in the read-only trust store mounted into the container. The trust store format is `{"schema":1,"keys":{"owner-1":"BASE64_RAW_ED25519_PUBLIC_KEY"}}`. Save this as `sign_task.py` and run `python sign_task.py task.json owner-private.pem task-approval.json owner-1` to sign one task file:

```python
import base64, hashlib, json, sys, time, uuid
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

task_path, private_key_path, approval_path, key_id = sys.argv[1:5]
task = json.loads(Path(task_path).read_text(encoding="utf-8"))
task_bytes = json.dumps(task, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
claims = {
    "schema": 1, "approval_id": f"admit-{uuid.uuid4().hex}", "key_id": key_id,
    "task_id": task["task_id"], "operation": "task_submit", "target": task["task_id"],
    "content_sha256": hashlib.sha256(task_bytes).hexdigest(),
    "expires_at": int(time.time()) + 600, "decision": "APPROVE",
}
key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
if not isinstance(key, Ed25519PrivateKey):
    raise TypeError("expected an Ed25519 private key")
message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
approval = dict(claims, signature=base64.b64encode(key.sign(message)).decode())
Path(approval_path).write_text(json.dumps(approval), encoding="utf-8")
```

Submit with `jarvis-v2 submit --task-file task.json --approval-file task-approval.json`. Cancellation also requires an Ed25519 approval bound to `task_cancel` and the exact task ID; its signed approval and receipt are persisted. Only pending tasks can be cancelled; a leased task cannot. A task receives at most three lease attempts total, including expired leases and explicit releases after failed handoffs; it is failed and quarantined before another attempt.

## Run the container

```sh
docker compose build
docker compose up -d
docker compose exec -T archon jarvis-v2 health --state /var/lib/archon --repo /app
docker compose logs -f archon
docker compose stop -t 10
```

Compose starts a foreground native controller, initializes the runtime volume, and uses a read-only root filesystem, UID/GID `10001`, dropped Linux capabilities, `no-new-privileges`, no network, and no published ports. The state and bounded workspace are named persistent volumes. Core operation does not need Ollama, a desktop session, host systemd, GPU access, Astra One, or network access. Local model, browser/desktop, hardware, finance, communications, and native service integrations remain optional or disabled.

The container health check runs `jarvis-v2 health`. The controller handles `SIGTERM`; stop it with `docker compose stop -t 10` so it can finish its current bounded operation and close SQLite cleanly.

## Upgrade and rollback
Back up the state and workspace using the procedure below before upgrading. Keep the current image under a separate tag, then build from the new verified checkout and recreate the service:
```sh
rollback_image="archon-local:rollback-$(date -u +%Y%m%dT%H%M%SZ)"
docker image tag archon-local:0.0.3 "$rollback_image"
docker compose stop -t 10
ARCHON_SOURCE_SHA="$(git rev-parse HEAD)" docker compose build
docker compose up -d --force-recreate
docker compose exec -T archon jarvis-v2 health --state /var/lib/archon --repo /app
docker compose exec -T archon jarvis-v2 modules
```
Keep the backup and tagged image until health and task checks pass. If an upgrade fails after changing the database, stop that project and restore the backup into a new Compose project using the procedure below. Create an override for the saved image:
```sh
rollback_override="$(mktemp --suffix=.yaml)"
cat > "$rollback_override" <<EOF
services:
  archon:
    image: $rollback_image
EOF
```
In the restore procedure below set `project=archon-rollback` and replace its final `up -d` command with `docker compose -p "$project" -f compose.yaml -f "$rollback_override" up -d`. Keep the failed project's volumes until the restored instance passes its checks; never restore over the only copy of a live volume or run the older image against a database the newer release may have migrated.

For a wheel installation, stop the foreground controller, keep the prior virtual environment, and back up `runtime.sqlite3`, `atlas.sqlite3`, and `effects.sqlite3` with SQLite's backup API; check each backup with `PRAGMA integrity_check`. Install the new wheel with `python -m pip install --upgrade artifacts/release-qualification/dist/jarvis_v2-0.0.3-py3-none-any.whl`, then run `jarvis-v2 health` before restarting the controller. If the migration or health check fails, switch back to the previous environment and restore the verified database backup into a separate state directory before starting it.

### Environment and owner approvals

| Variable | Default | Purpose |
| --- | --- | --- |
| `ARCHON_STATE` | `/var/lib/archon` in Compose | Private persistent runtime state |
| `ARCHON_WORKSPACE` | `/workspace` in Compose | Dedicated private directory for the optional bounded file effect |

Compose does not mount owner keys, so task submission, processing, cancellation, and the file effect are unavailable by default. The core container still starts and reports health without this trust store. To enable them, install the public-key store at `/etc/archon/owner-keys.json` on Linux with administrator-controlled ownership and no group/world write access; in Compose, mount only that file read-only at the same container path. The file must be readable by UID `10001` (for example mode `0644`). If the store is unavailable, pending tasks remain queued; tasks with missing, invalid, expired, or mismatched admission proof are failed before an executor receives them. Keep private signing keys outside the image and container. A `workspace_write` approval binds the task ID, exact single filename, content digest, operation, decision, key ID, and expiry; it can create a new file of at most 64 KiB and cannot overwrite an existing different file. Admission and `task_cancel` approvals bind the exact task or cancellation request; signed approval documents and receipts are retained in queue events. These controls do not enable arbitrary shell, network, financial, or communication actions.

Do not mount the Docker socket, host home directory, Astra One state, credentials, or general-purpose host paths into the service.

## Backup and restore

Create a host-side archive while the service is running. SQLite uses its backup API for each database; the workspace is included. Keep the archive private because it contains queued task data and workspace files.

```sh
umask 077
backup="archon-state-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
docker compose exec -T archon python - > "$backup" <<'PY'
from pathlib import Path
import os
import sqlite3
import sys
import tarfile
import tempfile

state = Path("/var/lib/archon")
workspace = Path("/workspace")
if any(path.is_symlink() for path in workspace.rglob("*")):
    raise SystemExit("workspace contains a symlink; archive it separately")
with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    backups = []
    for name in ("runtime.sqlite3", "atlas.sqlite3", "effects.sqlite3"):
        source_path = state / name
        if not source_path.exists():
            continue
        source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
        target_path = temp / name
        target = sqlite3.connect(target_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        os.chmod(target_path, 0o600)
        backups.append(target_path)
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w:gz") as archive:
        for path in backups:
            archive.add(path, arcname=f"state/{path.name}")
        archive.add("/workspace", arcname="workspace", recursive=True)
PY
```

Restore into a **new Compose project** so the existing volumes remain available for rollback. Stop the old service, then restore the archive into newly created volumes. The archive should come from the backup procedure above.

```sh
docker compose stop -t 10
project=archon-restore
docker compose -p "$project" run --rm --no-deps -T \
  -v "$PWD/$backup:/restore/backup.tar.gz:ro" \
  --entrypoint python archon -c '
import shutil, tarfile, tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    with tarfile.open("/restore/backup.tar.gz", "r:gz") as archive:
        for member in archive.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isdir() or member.isfile()):
                raise SystemExit("unsafe archive member")
        archive.extractall(root, filter="data")
    shutil.copytree(root / "state", "/var/lib/archon", dirs_exist_ok=True)
    shutil.copytree(root / "workspace", "/workspace", dirs_exist_ok=True)
    Path("/var/lib/archon").chmod(0o700)
    Path("/workspace").chmod(0o700)
    for name in ("runtime.sqlite3", "atlas.sqlite3", "effects.sqlite3"):
        restored = Path("/var/lib/archon") / name
        if restored.exists():
            restored.chmod(0o600)
'
docker compose -p "$project" up -d
docker compose -p "$project" exec -T archon jarvis-v2 health --state /var/lib/archon --repo /app
```

Keep the previous project and volumes stopped until the restored project passes health and task checks. For an in-place upgrade rollback, start the restored project with the previous image using the Compose override described above. Do not restore over the only copy of a live volume.

## Release limitations

The container qualification uses an isolated disposable workspace and generated test keys only. It does not qualify a real owner key ceremony, trusted AEGIS watchdog, native SDA cutover, external models/providers, finance or communications effects, Windows performance, Apple devices, GPU acceleration, desktop automation, or GitHub-hosted CI. These remain external acceptance gates.
