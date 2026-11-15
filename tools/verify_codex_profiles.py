#!/usr/bin/env python3
"""Run a bounded, read-only Codex profile smoke without touching Astra state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap" / "astra-one"))

from astra_one.linux_runtime import codex_command
from astra_one.linux_sda import DEFAULT_HOME, EFFORT, MODEL


ROLES = ("supervisor", "worker", "qc", "merger")
CONTROLS = ("STOP", "PAUSE", "PAUSED_QUOTA", "PAUSE_NORMAL", "PAUSE_RECOVERY")
OUTPUT_LIMIT = 256 * 1024
MODEL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")


def _control(home: Path) -> str:
    return next((name for name in CONTROLS if (home / name).is_file()), "")


def _bounded_run(command: list[str], *, cwd: Path, home: Path, timeout: int,
                 prompt: str = "") -> tuple[dict, str, str]:
    """Run one bounded process and return output only to the caller in memory."""
    if marker := _control(home):
        return {"exit_code": None, "reason": marker}, "", ""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError:
        return {"exit_code": None, "reason": "cli_unavailable"}, "", ""

    streams = [bytearray(), bytearray()]
    reason = ""
    deadline = time.monotonic() + timeout
    try:
        try:
            process.stdin.write(prompt.encode())
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, 0)
            selector.register(process.stderr, selectors.EVENT_READ, 1)
            while selector.get_map() or process.poll() is None:
                reason = _control(home)
                if not reason and time.monotonic() >= deadline:
                    reason = "timeout"
                if reason:
                    break
                for key, _ in selector.select(min(0.1, max(0.01, deadline - time.monotonic()))):
                    chunk = os.read(key.fileobj.fileno(), 8192)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    output = streams[key.data]
                    remaining = OUTPUT_LIMIT - len(output)
                    output.extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        reason = "output_limit"
                        break
                if reason:
                    break
    finally:
        if reason or process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                stream.close()
            except OSError:
                pass

    receipt = {
        "exit_code": process.returncode,
        "reason": reason or _control(home),
        "stdout_sha256": hashlib.sha256(streams[0]).hexdigest(),
        "stderr_sha256": hashlib.sha256(streams[1]).hexdigest(),
        "output_truncated": reason == "output_limit",
    }
    return receipt, *(bytes(stream).decode("utf-8", errors="replace") for stream in streams)


def _event_reason(stdout: str, stderr: str, exit_code: int | None, marker: str) -> tuple[str, list[str]]:
    combined = stdout + "\n" + stderr
    if re.search(r"quota|rate[ -]?limit|usage[ -]?limit|\b429\b", combined, re.I):
        return "quota_or_rate_limit", []
    if re.search(
        r"model[^\n]*(?:not[ -]?found|not[ -]?supported|unsupported|does not exist|unavailable|access)"
        r"|(?:invalid|unsupported)_model",
        combined,
        re.I,
    ):
        return "model_unavailable", []
    if exit_code:
        return "cli_nonzero", []

    events = []
    try:
        for line in stdout.splitlines():
            if line.strip():
                event = json.loads(line)
                if not isinstance(event, dict):
                    return "invalid_events", []
                events.append(event)
    except (json.JSONDecodeError, RecursionError):
        return "invalid_events", []

    messages: list[str] = []
    completed = False
    types: list[str] = []
    for event in events:
        kind = event.get("type")
        if not isinstance(kind, str):
            return "invalid_events", types
        types.append(kind)
        if completed:
            return "invalid_events", types
        if kind in {"error", "turn.failed"}:
            return "model_error", types
        if kind == "turn.completed":
            completed = True
        elif kind in {"item.started", "item.updated", "item.completed"}:
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") not in {"agent_message", "reasoning"}:
                return "unexpected_tool", types
            if kind == "item.completed" and item.get("type") == "agent_message":
                messages.append(item.get("text"))
        elif kind not in {"thread.started", "turn.started"}:
            return "invalid_events", types

    if not completed or messages != [marker]:
        return "smoke_incomplete", types
    return "", types


def _profile_command(worktree: Path, model: str, effort: str) -> list[str]:
    command = codex_command(worktree, model, effort, None, "read-only")
    insert_at = command.index("-")
    command[insert_at:insert_at] = [
        "--skip-git-repo-check",
        "--ignore-user-config",
        "-c", "model_provider=openai",
        "-c", "project_doc_max_bytes=0",
    ]
    return command


def _valid_profiles(models: dict[str, str], efforts: dict[str, str], timeout: int) -> bool:
    return (
        isinstance(models, dict)
        and set(models) == set(ROLES)
        and isinstance(efforts, dict)
        and set(efforts) == set(ROLES)
        and all(isinstance(model, str) and MODEL_NAME.fullmatch(model) for model in models.values())
        and all(effort in {"low", "medium", "high", "xhigh"} for effort in efforts.values())
        and type(timeout) is int
        and 1 <= timeout <= 300
    )


def verify_profiles(*, models: dict[str, str], efforts: dict[str, str] | None = None,
                    execute: bool = False, home: Path = DEFAULT_HOME,
                    timeout: int = 60) -> dict:
    if efforts is None:
        efforts = dict.fromkeys(ROLES, EFFORT)
    if not _valid_profiles(models, efforts, timeout):
        raise ValueError("invalid_profile")
    result = {
        "task_id": "SDA-003",
        "status": "PENDING",
        "reason": "live_smoke_not_executed",
        "authenticated": False,
        "profiles": [
            {"role": role, "model": models[role], "effort": efforts[role],
             "sandbox": "read-only", "status": "PENDING"}
            for role in ROLES
        ],
    }
    if not execute:
        return result
    result.update(status="STOP", reason="")
    if marker := _control(home):
        result["reason"] = marker
        return result

    with tempfile.TemporaryDirectory(prefix="sda-003-smoke-") as temporary:
        worktree = Path(temporary)
        executable = os.environ.get("ASTRA_CODEX_BIN") or "codex"
        preflight = []
        for arguments in (("--version",), ("login", "status")):
            receipt, stdout, stderr = _bounded_run(
                [executable, *arguments], cwd=worktree, home=home, timeout=timeout,
            )
            preflight.append(dict(receipt, command=list(arguments)))
            reason = receipt["reason"] or ("cli_nonzero" if receipt["exit_code"] else "")
            if arguments == ("--version",) and not reason:
                if not re.fullmatch(r"codex-cli [0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.+-]*", stdout.strip()):
                    reason = "cli_version_unverified"
                else:
                    result["cli_version"] = stdout.strip()
            if arguments == ("login", "status") and not reason:
                if re.search(r"^Logged in using (?:ChatGPT|an API key|API key)\b", stdout + "\n" + stderr, re.I | re.M):
                    result["authenticated"] = True
                else:
                    reason = "authentication_unverified"
            if reason:
                result["preflight"] = preflight
                result["reason"] = reason
                return result

        result["preflight"] = preflight
        for profile in result["profiles"]:
            marker = "SDA003_" + uuid.uuid4().hex
            receipt, stdout, stderr = _bounded_run(
                _profile_command(worktree, profile["model"], profile["effort"]),
                cwd=worktree,
                home=home,
                timeout=timeout,
                prompt=f"Reply exactly {marker}. Do not use tools, read files, or launch agents.\n",
            )
            reason, event_types = (
                (receipt["reason"], []) if receipt["reason"]
                else _event_reason(stdout, stderr, receipt["exit_code"], marker)
            )
            profile.update(
                receipt=receipt,
                event_types=event_types,
                message_verified=not reason,
                status="VERIFIED" if not reason else "STOP",
            )
            if reason:
                profile["reason"] = result["reason"] = reason
                return result

    result.update(status="VERIFIED", reason="")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh"], default=EFFORT)
    parser.add_argument("--timeout", type=int, default=60)
    for role in ROLES:
        parser.add_argument(f"--{role}-model")
        parser.add_argument(f"--{role}-effort", choices=["low", "medium", "high", "xhigh"])
    args = parser.parse_args(argv)
    models = {role: getattr(args, f"{role}_model") or args.model for role in ROLES}
    efforts = {role: getattr(args, f"{role}_effort") or args.effort for role in ROLES}
    try:
        result = verify_profiles(models=models, efforts=efforts, execute=args.execute,
                                 home=args.home, timeout=args.timeout)
    except ValueError:
        result = {"task_id": "SDA-003", "status": "STOP", "reason": "invalid_profile"}
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"VERIFIED": 0, "STOP": 2, "PENDING": 3}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
