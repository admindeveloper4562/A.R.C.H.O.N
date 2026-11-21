#!/usr/bin/env python3
"""Exercise the built Linux image using fresh, retained Docker volumes."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]


class Smoke:
    def __init__(self, output: Path) -> None:
        self.output = output.resolve()
        self.logs = self.output / "container-logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.records: list[dict[str, object]] = []
        self.project = f"archon-release-{uuid.uuid4().hex[:10]}"
        self.started = datetime.now(timezone.utc).isoformat()
        self.container_started = False
        self.environment = os.environ.copy()
        self.override = self.output / "compose.release-test.yaml"
        self.key_store = self.output / "release-test-owner-keys.json"
        self.cancel_approval_path = self.output / "release-test-cancel-approval.json"
        self.admission_approval_path = self.output / "release-test-admission-approval.json"
        self.compose = [
            "docker", "compose", "-p", self.project,
            "-f", str(ROOT / "compose.yaml"), "-f", str(self.override),
        ]

    def command(
        self,
        name: str,
        args: list[str],
        *,
        input_text: str | None = None,
        timeout: int = 120,
        expected: int = 0,
    ) -> str:
        started = time.monotonic()
        result = subprocess.run(
            args,
            cwd=ROOT,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env={**self.environment, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        duration = time.monotonic() - started
        output = result.stdout + result.stderr
        (self.logs / f"{name}.log").write_text(output, encoding="utf-8")
        self.records.append({
            "name": name,
            "command": args,
            "returncode": result.returncode,
            "duration_seconds": round(duration, 3),
            "log": f"container-logs/{name}.log",
        })
        if result.returncode != expected:
            raise RuntimeError(f"{name} exited {result.returncode}; see {self.logs / (name + '.log')}")
        return result.stdout.rstrip("\r\n")

    def task_document(self, private_key: Ed25519PrivateKey, task_id: str, target: str, content: str) -> dict:
        claims = {
            "schema": 1,
            "approval_id": f"approval-{task_id}",
            "key_id": "release-test-owner",
            "task_id": task_id,
            "operation": "workspace_write",
            "target": target,
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        return {
            "task_id": task_id,
            "priority": "P3",
            "module": "core",
            "payload": {
                "operation": "workspace_write",
                "target": target,
                "content": content,
                "approval": {
                    **claims,
                    "signature": base64.b64encode(private_key.sign(message)).decode(),
                },
            },
        }

    def cancel_document(self, private_key: Ed25519PrivateKey, task_id: str) -> dict:
        claims = {
            "schema": 1,
            "approval_id": f"cancel-{task_id}",
            "key_id": "release-test-owner",
            "task_id": task_id,
            "operation": "task_cancel",
            "target": task_id,
            "content_sha256": hashlib.sha256(task_id.encode()).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        return dict(claims, signature=base64.b64encode(private_key.sign(message)).decode())

    def admission_document(self, private_key: Ed25519PrivateKey, task: dict) -> dict:
        task_id = task["task_id"]
        task_bytes = json.dumps(
            task, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()
        claims = {
            "schema": 1,
            "approval_id": f"admit-{hashlib.sha256(task_id.encode()).hexdigest()[:24]}",
            "key_id": "release-test-owner",
            "task_id": task_id,
            "operation": "task_submit",
            "target": task_id,
            "content_sha256": hashlib.sha256(task_bytes).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        return dict(claims, signature=base64.b64encode(private_key.sign(message)).decode())

    def submit(
        self,
        name: str,
        task: dict,
        *,
        approval_key: Ed25519PrivateKey | None = None,
        running: bool = True,
        expected: int = 0,
    ) -> dict | str:
        approval = self.admission_document(approval_key, task) if approval_key else {}
        self.admission_approval_path.write_text(json.dumps(approval), encoding="utf-8")
        self.admission_approval_path.chmod(0o644)
        if running:
            command = [*self.compose, "exec", "-T", "archon", "jarvis-v2", "submit"]
        else:
            command = [*self.compose, "run", "--rm", "--no-deps", "-T",
                       "--entrypoint", "jarvis-v2", "archon", "submit"]
        output = self.command(
            name,
            [*command, "--state", "/var/lib/archon", "--task-file", "-",
             "--approval-file", "/run/secrets/admission-approval.json"],
            input_text=json.dumps(task),
            expected=expected,
        )
        return json.loads(output) if expected == 0 else output

    def queue_state(self, task_id: str, *, running: bool = True) -> dict | None:
        invocation = ["exec", "-T", "archon"] if running else [
            "run", "--rm", "--no-deps", "-T", "--entrypoint", "python", "archon",
        ]
        code = (
            "import json,sqlite3; "
            "db=sqlite3.connect('file:/var/lib/archon/atlas.sqlite3?mode=ro',uri=True); "
            f"row=db.execute('select state,receipt from tasks where id=?',[{json.dumps(task_id)}]).fetchone(); "
            "print(json.dumps({'state':row[0],'receipt':row[1]} if row else None))"
        )
        command = [*self.compose, *invocation]
        if running:
            command += ["python", "-c", code]
        else:
            command += ["-c", code]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False)
        if result.returncode:
            raise RuntimeError(f"queue state query failed: {result.stderr.strip()}")
        return json.loads(result.stdout.strip())

    def wait_task(self, task_id: str, expected_state: str, timeout: int = 45) -> dict:
        deadline = time.monotonic() + timeout
        state = None
        while time.monotonic() < deadline:
            state = self.queue_state(task_id)
            if state and state["state"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(1)
        if not state or state["state"] != expected_state:
            raise RuntimeError(f"task {task_id} ended as {state}; expected {expected_state}")
        return state

    def wait_healthy(self, timeout: int = 90) -> str:
        deadline = time.monotonic() + timeout
        container_id = ""
        status = "missing"
        while time.monotonic() < deadline:
            container_id = self.command(
                f"container-id-{int(deadline-time.monotonic())}",
                [*self.compose, "ps", "-q", "archon"],
            )
            if container_id:
                check = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}} {{.State.Status}}", container_id],
                    cwd=ROOT, capture_output=True, text=True, timeout=20, check=False,
                )
                status = check.stdout.strip()
                if check.returncode == 0 and status.startswith("healthy "):
                    return container_id
                if check.returncode == 0 and status.endswith(" exited"):
                    break
            time.sleep(1)
        logs = self.command("compose-logs-failed-health", [*self.compose, "logs", "--no-color", "archon"], expected=0)
        raise RuntimeError(f"container did not become healthy ({status}): {logs[-2000:]}")

    def run(self) -> dict:
        source_sha = self.command("source-sha", ["git", "rev-parse", "HEAD"])
        source_date_epoch = self.environment.get("SOURCE_DATE_EPOCH", "0")
        if not source_date_epoch.isdecimal():
            raise RuntimeError("SOURCE_DATE_EPOCH must be a numeric Unix timestamp")
        self.environment.update({
            "ARCHON_SOURCE_SHA": source_sha,
            "SOURCE_DATE_EPOCH": source_date_epoch,
            "PYTHONHASHSEED": "0",
        })
        trusted = Ed25519PrivateKey.generate()
        untrusted = Ed25519PrivateKey.generate()
        public = trusted.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.key_store.write_text(json.dumps({
            "schema": 1,
            "keys": {"release-test-owner": base64.b64encode(public).decode()},
        }), encoding="utf-8")
        self.key_store.chmod(0o644)
        self.cancel_approval_path.write_text("{}", encoding="utf-8")
        self.cancel_approval_path.chmod(0o644)
        self.admission_approval_path.write_text("{}", encoding="utf-8")
        self.admission_approval_path.chmod(0o644)
        self.override.write_text(
            "services:\n"
            "  archon:\n"
            "    volumes:\n"
            "      - type: bind\n"
            f"        source: {json.dumps(str(self.key_store))}\n"
            "        target: /etc/archon/owner-keys.json\n"
            "        read_only: true\n"
            "      - type: bind\n"
            f"        source: {json.dumps(str(self.cancel_approval_path))}\n"
            "        target: /run/secrets/cancel-approval.json\n"
            "        read_only: true\n"
            "      - type: bind\n"
            f"        source: {json.dumps(str(self.admission_approval_path))}\n"
            "        target: /run/secrets/admission-approval.json\n"
            "        read_only: true\n",
            encoding="utf-8",
        )
        build_project = f"archon-release-build-{source_sha[:12]}"
        build_compose = [
            "docker", "compose", "-p", build_project,
            "-f", str(ROOT / "compose.yaml"), "-f", str(self.override),
        ]
        self.command("compose-build", [*build_compose, "build"], timeout=900)
        rendered = self.command("compose-config", [*self.compose, "config", "--quiet"])
        del rendered
        self.command("compose-up", [*self.compose, "up", "-d", "--no-build"], timeout=120)
        self.container_started = True
        container_id = self.wait_healthy()

        modules = json.loads(self.command(
            "modules", [*self.compose, "exec", "-T", "archon", "jarvis-v2", "modules"],
        ))
        module_names = {item["key"] for item in modules.get("modules", []) if isinstance(item, dict)}
        expected_modules = {"core", "sda", "backend", "runtime", "research", "tws", "wic", "finance", "guardian", "automation"}
        if module_names != expected_modules:
            raise RuntimeError(f"installed module manifest is incomplete: {sorted(module_names)}")
        identities = json.loads(self.command(
            "identities", [*self.compose, "exec", "-T", "archon", "jarvis-v2", "identities"],
        ))
        if identities.get("active_module_count") != 10:
            raise RuntimeError("installed identity manifest does not declare ten active modules")
        health = json.loads(self.command(
            "fresh-health", [*self.compose, "exec", "-T", "archon", "jarvis-v2", "health",
                              "--state", "/var/lib/archon", "--repo", "/app"],
        ))
        if health.get("status") != "healthy":
            raise RuntimeError("fresh container health did not report healthy")

        untrusted_task = {
            "task_id": "container-unauthorized-admission",
            "priority": "P3",
            "module": "core",
            "payload": {"operation": "native_capabilities"},
        }
        self.submit(
            "submit-unauthorized-admission", untrusted_task,
            approval_key=untrusted, expected=2,
        )
        if self.queue_state(untrusted_task["task_id"]) is not None:
            raise RuntimeError("untrusted task admission changed the persistent queue")

        read_only = {
            "task_id": "container-read-only",
            "priority": "P3",
            "module": "core",
            "payload": {"operation": "native_capabilities"},
        }
        self.submit("submit-read-only", read_only, approval_key=trusted)
        read_only_state = self.wait_task(read_only["task_id"], "completed")

        allowed = self.task_document(trusted, "container-write", "release-result.txt", "approved in disposable workspace\n")
        allowed_content = base64.b64encode(allowed["payload"]["content"].encode()).decode()
        self.submit("submit-approved-effect", allowed, approval_key=trusted)
        effect_state = self.wait_task(allowed["task_id"], "completed")
        content = self.command(
            "approved-effect-content", [*self.compose, "exec", "-T", "archon", "python", "-c",
                                         "import base64; from pathlib import Path; print(base64.b64encode(Path('/workspace/release-result.txt').read_bytes()).decode())"],
        )
        if content != allowed_content:
            raise RuntimeError("approved workspace effect did not persist exact content")

        denied = self.task_document(untrusted, "container-denied", "denied-result.txt", "must not be written\n")
        self.submit("submit-unauthorized-effect", denied, approval_key=trusted)
        denied_state = self.wait_task(denied["task_id"], "failed")
        exists = self.command(
            "unauthorized-effect-check", [*self.compose, "exec", "-T", "archon", "python", "-c",
                                           "from pathlib import Path; print(Path('/workspace/denied-result.txt').exists())"],
        )
        if exists != "False":
            raise RuntimeError("unauthorized workspace effect created a file")

        self.command("stop-for-cancel-test", [*self.compose, "stop", "-t", "10"])
        cancelled_task = {
            "task_id": "container-cancelled",
            "priority": "P3",
            "module": "core",
            "payload": {"operation": "native_capabilities"},
        }
        cancellation_approval = self.cancel_document(trusted, cancelled_task["task_id"])
        self.cancel_approval_path.write_text(json.dumps(cancellation_approval), encoding="utf-8")
        self.submit("submit-queued-cancel", cancelled_task, approval_key=trusted, running=False)
        cancelled = json.loads(self.command(
            "cancel-pending-task", [*self.compose, "run", "--rm", "--no-deps", "-T",
                                     "--entrypoint", "jarvis-v2", "archon", "cancel", "--state",
                                     "/var/lib/archon", "--task-id", cancelled_task["task_id"],
                                     "--approval-file", "/run/secrets/cancel-approval.json"],
        ))
        if cancelled["state"] != "cancelled":
            raise RuntimeError("queued cancellation was not durable")
        self.command("restart-after-cancel", [*self.compose, "up", "-d"])
        container_id = self.wait_healthy()
        if self.queue_state(cancelled_task["task_id"])["state"] != "cancelled":
            raise RuntimeError("cancelled task was dispatched after restart")
        persisted_content = self.command(
            "persisted-effect-after-restart", [*self.compose, "exec", "-T", "archon", "python", "-c",
                                                 "import base64; from pathlib import Path; print(base64.b64encode(Path('/workspace/release-result.txt').read_bytes()).decode())"],
        )
        if persisted_content != allowed_content:
            raise RuntimeError("workspace volume did not persist across container restart")

        self.command("stop-for-recovery-fixture", [*self.compose, "stop", "-t", "10"])
        recovery = self.task_document(trusted, "container-recovery", "recovered-result.txt", "reconciled after restart\n")
        self.submit("submit-recovery-task", recovery, approval_key=trusted, running=False)
        approval = recovery["payload"]["approval"]
        request = {
            "approval_id": approval["approval_id"],
            "content_sha256": approval["content_sha256"],
            "size_bytes": len(recovery["payload"]["content"].encode()),
        }
        fixture = (
            "import json,os; from pathlib import Path; from hashlib import sha256; "
            "from jarvis_v2.backend.effects import EffectJournal; "
            "p=Path('/var/lib/archon/effects.sqlite3'); "
            f"with_journal={json.dumps(request,sort_keys=True,separators=(',',':'))!r}; "
            f"task_id={recovery['task_id']!r}; target='recovered-result.txt'; "
            "j=EffectJournal(p); j.__enter__(); "
            "j.prepare(sha256(task_id.encode()).hexdigest(),task_id,operation='workspace_write',target=target,request=json.loads(with_journal)); "
            "j.__exit__(None,None,None); "
            f"out=Path('/workspace/{recovery['payload']['target']}'); "
            f"out.write_text({recovery['payload']['content']!r}); os.chmod(out,0o600)"
        )
        self.command(
            "seed-interrupted-effect", [*self.compose, "run", "--rm", "--no-deps", "-T",
                                         "--entrypoint", "python", "archon", "-c", fixture],
        )
        self.command("restart-for-recovery", [*self.compose, "up", "-d"])
        container_id = self.wait_healthy()
        recovered_state = self.wait_task(recovery["task_id"], "completed")
        recovery_content = base64.b64encode(recovery["payload"]["content"].encode()).decode()
        recovered_content = self.command(
            "recovered-effect-content", [*self.compose, "exec", "-T", "archon", "python", "-c",
                                          "import base64; from pathlib import Path; print(base64.b64encode(Path('/workspace/recovered-result.txt').read_bytes()).decode())"],
        )
        if recovered_content != recovery_content:
            raise RuntimeError("effect recovery did not preserve the target file")
        health = json.loads(self.command(
            "post-restart-health", [*self.compose, "exec", "-T", "archon", "jarvis-v2", "health",
                                     "--state", "/var/lib/archon", "--repo", "/app"],
        ))
        integrity_code = (
            "import json,sqlite3\n"
            "from pathlib import Path\n"
            "result={}\n"
            "for name in ('runtime.sqlite3','atlas.sqlite3','effects.sqlite3'):\n"
            " path=Path('/var/lib/archon')/name\n"
            " db=sqlite3.connect(f'file:{path}?mode=ro',uri=True)\n"
            " result[name]=db.execute('PRAGMA integrity_check').fetchone()[0]\n"
            " db.close()\n"
            "print(json.dumps(result,sort_keys=True))\n"
        )
        database_integrity = json.loads(self.command(
            "sqlite-integrity", [*self.compose, "exec", "-T", "archon", "python", "-c", integrity_code],
        ))
        if set(database_integrity) != {"runtime.sqlite3", "atlas.sqlite3", "effects.sqlite3"} or any(
            value != "ok" for value in database_integrity.values()
        ):
            raise RuntimeError("container SQLite integrity check failed")

        security = self.command(
            "container-security-config", ["docker", "inspect", "--format",
                                          "{{.Config.User}}|{{.HostConfig.ReadonlyRootfs}}|{{json .HostConfig.CapDrop}}|{{.HostConfig.NetworkMode}}|{{json .HostConfig.SecurityOpt}}",
                                          container_id],
        )
        if security != "10001:10001|true|[\"ALL\"]|none|[\"no-new-privileges:true\"]":
            raise RuntimeError(f"container security settings differ from policy: {security}")
        self.command("save-container-image", ["docker", "save", "--output",
                                               str(self.output / "archon-local-image.tar"),
                                               "archon-local:0.0.3"], timeout=300)
        self.command("graceful-stop", [*self.compose, "stop", "-t", "10"], timeout=60)
        exit_code = self.command(
            "container-exit-code", ["docker", "inspect", "--format", "{{.State.ExitCode}}", container_id],
        )
        if exit_code != "0":
            raise RuntimeError(f"container did not stop cleanly: exit {exit_code}")
        report = {
            "schema": 1,
            "source_sha": source_sha,
            "source_date_epoch": source_date_epoch,
            "result": "passed",
            "project": self.project,
            "container_id": container_id,
            "container_image": "archon-local:0.0.3",
            "fresh_state": True,
            "network_mode": "none",
            "persistent_volumes_retained": [f"{self.project}_archon-state", f"{self.project}_archon-workspace"],
            "task_receipts": {
                "unauthorized_admission": "rejected_without_queue_entry",
                "read_only": read_only_state,
                "approved_workspace_write": effect_state,
                "unauthorized_write": denied_state,
                "cancelled_pending_task": cancelled["state"],
                "interrupted_effect_recovery": recovered_state,
            },
            "health": health,
            "database_integrity": database_integrity,
            "security_config": security,
            "container_exit_code": int(exit_code),
            "test_key": "ephemeral test-only key; private component remained in host memory",
            "commands": self.records,
            "started_at": self.started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        (self.output / "container-smoke-report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    smoke = Smoke(args.output_dir)
    try:
        report = smoke.run()
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
        if smoke.container_started:
            result = subprocess.run(
                [*smoke.compose, "stop", "-t", "10"], cwd=ROOT,
                capture_output=True, text=True, timeout=30, check=False,
            )
            (smoke.logs / "stop-after-failure.log").write_text(
                result.stdout + result.stderr, encoding="utf-8"
            )
        print(f"container smoke failed: {exc}", file=__import__("sys").stderr)
        return 1
    print(json.dumps({"result": report["result"], "project": report["project"],
                      "container_id": report["container_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
