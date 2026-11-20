# ARCHON Linux release

This release packages the existing Linux implementation as Python version `0.0.3`. The repository has no versioning policy that supports a version bump, so qualification retains the audited version. GitHub Actions is not part of the acceptance evidence.

## Build and qualify

From a clean feature or development branch with Python 3.11 or newer and Docker Compose v2:

```sh
./tools/verify_release.sh
```

The command checks the clean Git state, builds the wheel and source distribution, installs each into clean virtual environments, runs the existing local checks and full `unittest` suite, inventories dependencies, audits the pinned runtime dependency, and builds and exercises the container. It writes full subprocess logs and reports under `artifacts/release-qualification/`. It requires network access to install pinned build/audit dependencies and query vulnerability data. A successful local run does not establish GitHub-hosted policy enforcement.

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

Admission is local to the OS user who can access the private state directory. `jarvis-v2 submit --task-file -` reads one JSON task document from standard input; `jarvis-v2 cancel --task-id ID` cancels a task only while it remains pending. A leased task cannot be cancelled. Expired leases are retried at most three times.

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

### Environment and owner approvals

| Variable | Default | Purpose |
| --- | --- | --- |
| `ARCHON_STATE` | `/var/lib/archon` in Compose | Private persistent runtime state |
| `ARCHON_WORKSPACE` | `/workspace` in Compose | Dedicated private directory for the optional bounded file effect |
| `ARCHON_OWNER_KEYS` | unset | Optional path to a read-only JSON trust store of Ed25519 public keys |

Compose does not configure owner keys, so the file effect is disabled by default. If an operator provisions a trusted public key, mount only the public-key store read-only and set `ARCHON_OWNER_KEYS` to its container path. Keep private signing keys outside the image and container. A `workspace_write` approval binds the task ID, exact single filename, content digest, operation, decision, key ID, and expiry; it can create a new file of at most 64 KiB and cannot overwrite an existing different file. It does not enable arbitrary shell, network, financial, or communication actions.

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

Keep the previous project and volumes stopped until the restored project passes health and task checks. A rollback is to stop the new project and restart the prior project with its original volumes; do not restore over the only copy of a live volume.

## Release limitations

The container qualification uses an isolated disposable workspace and generated test keys only. It does not qualify a real owner key ceremony, trusted AEGIS watchdog, native SDA cutover, external models/providers, finance or communications effects, Windows performance, Apple devices, GPU acceleration, desktop automation, or GitHub-hosted CI. These remain external acceptance gates.
