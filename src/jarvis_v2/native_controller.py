"""Native ARCHON queue controller with durable local single-writer fencing.

The controller owns queue admission and lease completion. Domain work is an
explicit injected executor; without one, it never claims queued work.
"""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import signal
import stat
import time
from typing import Any

from .automation.queue_api import CoordinatorQueue, QueueApiError, QueueEnvelope
from .backend.ollama_gateway import LocalOllamaGateway
from .backend.ollama_profile import OllamaInferenceProfile
from .native_executor import NativeControlPlaneExecutor, NativeExecutorError, _load_configured_owner_keys


CONTROL_MARKERS = ("STOP", "PAUSE", "PAUSED_QUOTA")
DEFAULT_POLL_SECONDS = 2
MAX_POLL_SECONDS = 300
DEFAULT_LEASE_SECONDS = 60
MODEL_LEASE_COMPLETION_MARGIN_SECONDS = 15
MAX_OWNER_ID = 128


class NativeControllerError(RuntimeError):
    """Raised when native controller ownership or queue handling fails."""


Executor = Callable[[QueueEnvelope], Mapping[str, Any]]


def _absolute(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise NativeControllerError(f"{label} must be absolute")
    return path


def _child(root: Path, value: str | Path, label: str) -> Path:
    path = _absolute(value, label)
    resolved_root = root.resolve(strict=False)
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(resolved_root):
        raise NativeControllerError(f"{label} must remain inside the state root")
    return resolved


def _directory(path: Path, label: str) -> Path:
    if path.exists() and (path.is_symlink() or not path.is_dir()):
        raise NativeControllerError(f"{label} is not a directory")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise NativeControllerError(f"{label} is accessible by another identity")
    return path


def _receipt(task_id: str, value: Mapping[str, Any]) -> str:
    try:
        encoded = json.dumps(
            {"task_id": task_id, "result": dict(value)},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise NativeControllerError("executor result must be JSON-compatible") from exc
    return sha256(encoded).hexdigest()


class NativeController:
    """Run bounded local queue cycles without importing Astra or spawning code workers."""

    def __init__(
        self,
        state_dir: str | Path,
        *,
        queue_path: str | Path | None = None,
        control_dir: str | Path | None = None,
        owner_id: str = "archon-native",
        executor: Executor | None = None,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
        poll_seconds: int = DEFAULT_POLL_SECONDS,
    ) -> None:
        self.state_dir = _directory(_absolute(state_dir, "state directory"), "state directory")
        self.run_dir = _directory(self.state_dir / "run", "run directory")
        self.queue_path = _child(
            self.state_dir,
            queue_path or self.state_dir / "atlas.sqlite3",
            "queue database",
        )
        self.control_dir = _directory(
            _child(self.state_dir, control_dir or self.state_dir / "controls", "control directory"),
            "control directory",
        )
        if not isinstance(owner_id, str) or not owner_id or len(owner_id) > MAX_OWNER_ID:
            raise NativeControllerError("invalid owner id")
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= 3_600:
            raise NativeControllerError("lease duration is outside the bounded policy")
        if isinstance(executor, NativeControlPlaneExecutor) and "model_inference" in executor.capabilities():
            gateway = executor.model_gateway
            if gateway is None:
                raise NativeControllerError("model capability has no configured local gateway")
            minimum_lease = math.ceil(gateway.timeout_seconds + MODEL_LEASE_COMPLETION_MARGIN_SECONDS)
            if lease_seconds < minimum_lease:
                raise NativeControllerError(
                    f"local model inference requires a lease of at least {minimum_lease} seconds"
                )
        if type(poll_seconds) is not int or not 1 <= poll_seconds <= MAX_POLL_SECONDS:
            raise NativeControllerError("poll interval is outside the bounded policy")
        if executor is not None and not callable(executor):
            raise NativeControllerError("executor must be callable")
        self.owner_id = owner_id
        self.executor = executor
        self.lease_seconds = lease_seconds
        self.poll_seconds = poll_seconds
        self._lock_file = self._acquire_lock()
        try:
            self.queue = CoordinatorQueue.open(self.queue_path)
        except Exception:
            self._release_lock()
            raise

    def _acquire_lock(self):
        try:
            import fcntl

            flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(self.run_dir / "controller.lock", flags, 0o600)
            os.chmod(fd, 0o600)
            stream = os.fdopen(fd, "a+b")
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                stream.close()
                raise NativeControllerError("native controller lock is held") from exc
            return stream
        except NativeControllerError:
            raise
        except (OSError, ImportError) as exc:
            raise NativeControllerError("native controller lock is unavailable") from exc

    def _release_lock(self) -> None:
        stream = getattr(self, "_lock_file", None)
        if stream is None:
            return
        try:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        except (OSError, ImportError):
            pass
        stream.close()
        self._lock_file = None

    def active_controls(self) -> tuple[str, ...]:
        return tuple(marker for marker in CONTROL_MARKERS if (self.control_dir / marker).exists())

    def snapshot(self) -> dict[str, Any]:
        rows = self.queue.status()
        counts = Counter(row["state"] for row in rows)
        return {
            "controller": self.owner_id,
            "pid": os.getpid(),
            "controls": self.queue.control_status(),
            "control_markers": list(self.active_controls()),
            "counts": dict(sorted(counts.items())),
            "executor_configured": self.executor is not None,
        }

    def run_once(self) -> dict[str, Any]:
        """Run one admission/lease/complete cycle and return digest-only evidence."""
        markers = self.active_controls()
        controls = self.queue.control_status()
        if markers:
            return {"state": "safe_mode", "reason": "control_marker_active", "controls": list(markers)}
        if controls["state"] != "running":
            return {"state": controls["state"], "reason": "dispatch_control", "controls": controls}
        if self.executor is None:
            return {"state": "idle", "reason": "executor_unconfigured", "eligible": len(self.queue.eligible())}
        try:
            item = self.queue.lease_next(lease_seconds=self.lease_seconds)
        except QueueApiError as exc:
            raise NativeControllerError("native lease admission failed") from exc
        if item is None:
            return {"state": "idle", "reason": "no_ready_work"}
        try:
            result = self.executor(item)
            if not isinstance(result, Mapping):
                raise NativeControllerError("executor result must be an object")
            receipt = _receipt(item.task_id, result)
            completed = self.queue.complete(item, ok=True, receipt=receipt)
            summary = {"state": "completed", "task_id": item.task_id, "receipt": completed["receipt"]}
            task_key = sha256(item.task_id.encode("utf-8")).hexdigest()
            expected_ref = f"native-{task_key}"
            if result.get("operation") == "model_inference" and result.get("conversation_id") == expected_ref:
                summary["result_ref"] = expected_ref
            return summary
        except NativeControllerError as exc:
            reason = type(exc).__name__
        except Exception as exc:  # executor failures are recorded, not leaked
            reason = type(exc).__name__
        failure_receipt = sha256(f"{item.task_id}:{reason}".encode("utf-8")).hexdigest()
        try:
            self.queue.complete(item, ok=False, receipt=failure_receipt)
        except QueueApiError as exc:
            raise NativeControllerError("native failure completion was rejected") from exc
        return {"state": "failed", "task_id": item.task_id, "reason": "executor_failed", "receipt": failure_receipt}

    def run_forever(self, stop: Any) -> None:
        while not stop.is_set():
            self.run_once()
            stop.wait(self.poll_seconds)

    def close(self) -> None:
        queue = getattr(self, "queue", None)
        if queue is not None:
            queue.close()
            self.queue = None
        self._release_lock()

    def __enter__(self) -> "NativeController":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _default_state() -> Path:
    return Path(os.environ.get("ARCHON_STATE", Path.home() / ".local/state/archon"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="archon-native-controller")
    parser.add_argument("--state", type=Path, default=_default_state())
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--control-dir", type=Path)
    parser.add_argument("--owner-id", default="archon-native")
    parser.add_argument("--lease-seconds", type=int, default=DEFAULT_LEASE_SECONDS)
    parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--workspace", type=Path, default=os.environ.get("ARCHON_WORKSPACE"))
    parser.add_argument(
        "--ollama-model",
        default=os.environ.get("ARCHON_OLLAMA_MODEL") or None,
        help="enable signed local model_inference tasks through loopback Ollama",
    )
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args(argv)
    if args.once and args.watch:
        parser.error("--once and --watch are mutually exclusive")
    try:
        owner_keys = _load_configured_owner_keys()
        if args.ollama_model is not None and not owner_keys:
            parser.error("--ollama-model requires the configured trusted owner key store")
        model_gateway = None
        if args.ollama_model is not None:
            model_gateway = LocalOllamaGateway(
                OllamaInferenceProfile(model=args.ollama_model, num_ctx=2_048),
                timeout_seconds=45,
            )
        executor = NativeControlPlaneExecutor(
            repository=args.repository,
            state_dir=args.state,
            workspace_root=args.workspace,
            owner_keys=owner_keys,
            model_gateway=model_gateway,
        )
        with NativeController(
            args.state,
            queue_path=args.queue,
            control_dir=args.control_dir,
            owner_id=args.owner_id,
            executor=executor,
            lease_seconds=args.lease_seconds,
            poll_seconds=args.poll_seconds,
        ) as controller:
            if args.watch:
                import threading

                stop = threading.Event()
                def request_stop(_signum: int, _frame: Any) -> None:
                    stop.set()

                previous = {
                    signum: signal.signal(signum, request_stop)
                    for signum in (signal.SIGINT, signal.SIGTERM)
                }
                try:
                    controller.run_forever(stop)
                finally:
                    for signum, handler in previous.items():
                        signal.signal(signum, handler)
            else:
                print(json.dumps(controller.run_once(), sort_keys=True))
    except (NativeControllerError, NativeExecutorError, OSError, ValueError) as exc:
        parser.exit(2, f"archon-native-controller: {exc}\n")
    return 0


__all__ = ["CONTROL_MARKERS", "NativeController", "NativeControllerError", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
