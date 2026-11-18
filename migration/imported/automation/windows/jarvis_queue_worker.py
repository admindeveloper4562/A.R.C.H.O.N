#!/usr/bin/env python3
"""Cross-platform JARVIS worker for a Cloudflare-backed Ollama queue.

The worker is intentionally stdlib-only. It registers on every startup, leases
at most one job at a time, calls a local Ollama server, renews the worker/job
heartbeat while inference is running, and reports completion or failure.

Required environment:
  JARVIS_COORDINATOR_URL    Cloudflare Worker base URL.
  JARVIS_COORDINATOR_TOKEN  Bearer token accepted by the coordinator.

Optional environment:
  JARVIS_WORKER_ID          Stable worker id; defaults to hostname plus a suffix.
  OLLAMA_URL                Defaults to http://127.0.0.1:11434.
  OLLAMA_MODEL              Defaults to qwen3:8b.
  JARVIS_WORKER_POLL_SECONDS
  JARVIS_WORKER_LEASE_SECONDS
  JARVIS_WORKER_HEARTBEAT_SECONDS
  JARVIS_WORKER_NUM_PREDICT
  JARVIS_WORKER_NUM_CTX
  JARVIS_HTTP_TIMEOUT_SECONDS

Examples:
  python scripts/jarvis_queue_worker.py
  python scripts/jarvis_queue_worker.py --once
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import socket
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


LOG = logging.getLogger("jarvis-queue-worker")
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_POLL_SECONDS = 15.0
DEFAULT_LEASE_SECONDS = 120
DEFAULT_HEARTBEAT_SECONDS = 30.0
DEFAULT_NUM_PREDICT = 512
DEFAULT_NUM_CTX = 4096
DEFAULT_HTTP_TIMEOUT_SECONDS = 60.0
MAX_ERROR_LENGTH = 4000


def bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Parse an integer and clamp it to a safe inclusive range."""
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def bounded_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    """Parse a float and clamp it to a safe inclusive range."""
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def normalize_url(value: str) -> str:
    return value.rstrip("/")


def make_worker_id() -> str:
    hostname = socket.gethostname().strip() or "unknown-host"
    suffix = uuid.uuid4().hex[:10]
    return f"{hostname}-{suffix}"


def require_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def error_text(exc: BaseException) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message[:MAX_ERROR_LENGTH]


def extract_job(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return a normalized job object from a lease response.

    The coordinator returns {"job": null} when the queue is empty. A direct job
    object is accepted as a small compatibility convenience for local stubs.
    """
    job = response.get("job", response)
    if job is None:
        return None
    if not isinstance(job, dict):
        raise ValueError("coordinator lease response did not contain a job object")
    if not job.get("id"):
        raise ValueError("leased job is missing id")
    if not job.get("lease_token"):
        raise ValueError("leased job is missing lease_token")
    return job


def job_payload(job: Dict[str, Any]) -> Dict[str, Any]:
    payload = job.get("payload", job.get("payload_json", {}))
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise ValueError("job payload must be a JSON object")
    return payload


def build_ollama_request(
    job: Dict[str, Any],
    default_model: str = DEFAULT_MODEL,
    num_predict: int = DEFAULT_NUM_PREDICT,
    num_ctx: int = DEFAULT_NUM_CTX,
) -> Tuple[str, Dict[str, Any]]:
    """Build a non-streaming Ollama chat or generate request from a job."""
    payload = job_payload(job)
    model = str(payload.get("model") or default_model)
    options = payload.get("options", {})
    if not isinstance(options, dict):
        raise ValueError("job options must be a JSON object")
    options = dict(options)
    options.setdefault("num_predict", num_predict)
    options.setdefault("num_ctx", num_ctx)

    common: Dict[str, Any] = {
        "model": model,
        "stream": False,
        "options": options,
        "keep_alive": payload.get("keep_alive", "10m"),
    }
    if "think" in payload:
        common["think"] = bool(payload["think"])

    messages = payload.get("messages")
    if messages is not None:
        if not isinstance(messages, list) or not messages:
            raise ValueError("messages must be a non-empty JSON array")
        common["messages"] = messages
        return "/api/chat", common

    prompt = payload.get("prompt")
    if prompt is None or not str(prompt).strip():
        raise ValueError("job payload must include messages or a non-empty prompt")
    common["prompt"] = str(prompt)
    for key in ("system", "template", "context", "raw", "suffix"):
        if key in payload:
            common[key] = payload[key]
    return "/api/generate", common


def extract_ollama_result(response: Dict[str, Any]) -> Dict[str, Any]:
    """Keep queue results compact while preserving useful Ollama metadata."""
    result: Dict[str, Any] = {
        "model": response.get("model"),
        "done": response.get("done"),
    }
    if "response" in response:
        result["response"] = response["response"]
    if "message" in response:
        result["message"] = response["message"]
    metrics = {}
    for key in (
        "created_at",
        "total_duration",
        "load_duration",
        "prompt_eval_count",
        "prompt_eval_duration",
        "eval_count",
        "eval_duration",
    ):
        if key in response:
            metrics[key] = response[key]
    if metrics:
        result["metrics"] = metrics
    return result


@dataclass(frozen=True)
class Settings:
    coordinator_url: str
    coordinator_token: str
    worker_id: str
    ollama_url: str
    model: str
    poll_seconds: float
    lease_seconds: int
    heartbeat_seconds: float
    num_predict: int
    num_ctx: int
    http_timeout_seconds: float

    @classmethod
    def from_environment(cls) -> "Settings":
        lease_seconds = bounded_int(
            os.environ.get("JARVIS_WORKER_LEASE_SECONDS"),
            DEFAULT_LEASE_SECONDS,
            30,
            3600,
        )
        heartbeat_default = min(DEFAULT_HEARTBEAT_SECONDS, max(5.0, lease_seconds / 3.0))
        return cls(
            coordinator_url=normalize_url(require_environment("JARVIS_COORDINATOR_URL")),
            coordinator_token=require_environment("JARVIS_COORDINATOR_TOKEN"),
            worker_id=os.environ.get("JARVIS_WORKER_ID", "").strip() or make_worker_id(),
            ollama_url=normalize_url(os.environ.get("OLLAMA_URL", DEFAULT_OLLAMA_URL)),
            model=os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
            poll_seconds=bounded_float(
                os.environ.get("JARVIS_WORKER_POLL_SECONDS"),
                DEFAULT_POLL_SECONDS,
                1.0,
                300.0,
            ),
            lease_seconds=lease_seconds,
            heartbeat_seconds=bounded_float(
                os.environ.get("JARVIS_WORKER_HEARTBEAT_SECONDS"),
                heartbeat_default,
                5.0,
                max(5.0, float(lease_seconds - 1)),
            ),
            num_predict=bounded_int(
                os.environ.get("JARVIS_WORKER_NUM_PREDICT"),
                DEFAULT_NUM_PREDICT,
                1,
                32768,
            ),
            num_ctx=bounded_int(
                os.environ.get("JARVIS_WORKER_NUM_CTX"),
                DEFAULT_NUM_CTX,
                256,
                131072,
            ),
            http_timeout_seconds=bounded_float(
                os.environ.get("JARVIS_HTTP_TIMEOUT_SECONDS"),
                DEFAULT_HTTP_TIMEOUT_SECONDS,
                5.0,
                900.0,
            ),
        )


class HttpError(RuntimeError):
    pass


class CoordinatorClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        url = self.settings.coordinator_url + "/" + path.lstrip("/")
        headers = {
            "Authorization": "Bearer " + self.settings.coordinator_token,
            "Accept": "application/json",
            "User-Agent": "JARVIS-Queue-Worker/1.0",
        }
        data = None
        if body is not None:
            data = json_bytes(body)
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout or self.settings.http_timeout_seconds,
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise HttpError(f"{method} {path} returned HTTP {exc.code}: {detail[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise HttpError(f"{method} {path} failed: {exc.reason}") from exc
        if not raw:
            return {}
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HttpError(f"{method} {path} returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise HttpError(f"{method} {path} returned a non-object JSON value")
        return decoded

    def register(self) -> Dict[str, Any]:
        return self.request(
            "POST",
            "/v1/workers/register",
            {
                "worker_id": self.settings.worker_id,
                "platform": platform.platform(),
                "model": self.settings.model,
                "ollama_url": self.settings.ollama_url,
                "capabilities": {
                    "queue_worker": True,
                    "max_concurrency": 1,
                    "supports_chat": True,
                    "supports_generate": True,
                },
            },
        )

    def heartbeat(self, current_job_id: Optional[str]) -> Dict[str, Any]:
        return self.request(
            "POST",
            "/v1/workers/heartbeat",
            {
                "worker_id": self.settings.worker_id,
                "current_job_id": current_job_id,
                "model": self.settings.model,
            },
            timeout=min(self.settings.http_timeout_seconds, 30.0),
        )

    def lease(self) -> Optional[Dict[str, Any]]:
        response = self.request(
            "POST",
            "/v1/jobs/lease",
            {
                "worker_id": self.settings.worker_id,
                "lease_seconds": self.settings.lease_seconds,
                "model": self.settings.model,
            },
        )
        return extract_job(response)

    def job_heartbeat(self, job: Dict[str, Any]) -> Dict[str, Any]:
        return self.request(
            "POST",
            "/v1/jobs/" + str(job["id"]) + "/heartbeat",
            {
                "worker_id": self.settings.worker_id,
                "lease_token": job["lease_token"],
                "lease_seconds": self.settings.lease_seconds,
            },
            timeout=min(self.settings.http_timeout_seconds, 30.0),
        )

    def complete(self, job: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        return self.request(
            "POST",
            "/v1/jobs/" + str(job["id"]) + "/complete",
            {
                "worker_id": self.settings.worker_id,
                "lease_token": job["lease_token"],
                "result": result,
            },
        )

    def fail(self, job: Dict[str, Any], message: str, retryable: bool = True) -> Dict[str, Any]:
        return self.request(
            "POST",
            "/v1/jobs/" + str(job["id"]) + "/fail",
            {
                "worker_id": self.settings.worker_id,
                "lease_token": job["lease_token"],
                "error": message[:MAX_ERROR_LENGTH],
                "retryable": retryable,
            },
        )


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, job: Dict[str, Any]) -> Dict[str, Any]:
        path, body = build_ollama_request(
            job,
            default_model=self.settings.model,
            num_predict=self.settings.num_predict,
            num_ctx=self.settings.num_ctx,
        )
        url = self.settings.ollama_url + path
        request = urllib.request.Request(
            url,
            data=json_bytes(body),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.http_timeout_seconds,
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise HttpError(f"Ollama returned HTTP {exc.code}: {detail[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise HttpError(f"Ollama request failed: {exc.reason}") from exc
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HttpError("Ollama returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise HttpError("Ollama returned a non-object JSON value")
        if decoded.get("error"):
            raise HttpError("Ollama error: " + str(decoded["error"]))
        return extract_ollama_result(decoded)


class QueueWorker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.coordinator = CoordinatorClient(settings)
        self.ollama = OllamaClient(settings)
        self.stop_event = threading.Event()
        self.current_job_lock = threading.Lock()
        self.current_job_id: Optional[str] = None

    def set_current_job(self, job_id: Optional[str]) -> None:
        with self.current_job_lock:
            self.current_job_id = job_id

    def get_current_job(self) -> Optional[str]:
        with self.current_job_lock:
            return self.current_job_id

    def heartbeat_loop(self) -> None:
        while not self.stop_event.wait(self.settings.heartbeat_seconds):
            try:
                current_job_id = self.get_current_job()
                self.coordinator.heartbeat(current_job_id)
                if current_job_id:
                    # The full job is looked up by the main loop and stored for
                    # the next renewal to avoid racing with a new lease.
                    job = getattr(self, "_current_job", None)
                    if job and str(job.get("id")) == current_job_id:
                        self.coordinator.job_heartbeat(job)
            except Exception as exc:
                # A transient heartbeat failure should not kill inference.
                # The coordinator lease decides whether a vanished worker is
                # reclaimed.
                LOG.warning("heartbeat failed: %s", error_text(exc))

    def start_heartbeat(self) -> threading.Thread:
        thread = threading.Thread(
            target=self.heartbeat_loop,
            name="jarvis-heartbeat",
            daemon=True,
        )
        thread.start()
        return thread

    def process_job(self, job: Dict[str, Any]) -> None:
        job_id = str(job["id"])
        self._current_job = job
        self.set_current_job(job_id)
        LOG.info("processing job %s", job_id)
        try:
            result = self.ollama.generate(job)
        except Exception as exc:
            message = error_text(exc)
            LOG.exception("job %s failed: %s", job_id, message)
            try:
                self.coordinator.fail(job, message, retryable=True)
            except Exception as report_exc:
                LOG.error("could not report failure for %s: %s", job_id, error_text(report_exc))
        else:
            try:
                self.coordinator.complete(job, result)
            except Exception as exc:
                # Do not report a second failure after inference succeeded: if
                # completion delivery failed, the expired lease can safely be
                # retried by the coordinator with its idempotency key.
                LOG.error("could not report completion for %s: %s", job_id, error_text(exc))
            else:
                LOG.info("completed job %s", job_id)
        finally:
            self.set_current_job(None)
            self._current_job = None

    def run_once(self) -> bool:
        job = self.coordinator.lease()
        if job is None:
            LOG.info("queue is empty")
            return False
        self.process_job(job)
        return True

    def run_forever(self) -> None:
        self.coordinator.register()
        self.start_heartbeat()
        LOG.info(
            "worker %s online; polling every %.1fs; one active Ollama generation",
            self.settings.worker_id,
            self.settings.poll_seconds,
        )
        while not self.stop_event.is_set():
            try:
                processed = self.run_once()
                if not processed:
                    self.stop_event.wait(self.settings.poll_seconds)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                LOG.warning("worker loop error: %s", error_text(exc))
                self.stop_event.wait(min(self.settings.poll_seconds * 2.0, 60.0))

    def stop(self) -> None:
        self.stop_event.set()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once",
        action="store_true",
        help="register, process at most one queued job, then exit",
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("JARVIS_LOG_LEVEL", "INFO"),
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = Settings.from_environment()
    worker = QueueWorker(settings)
    if args.once:
        worker.coordinator.register()
        return 0 if worker.run_once() else 2
    try:
        worker.run_forever()
    except KeyboardInterrupt:
        LOG.info("shutdown requested")
        worker.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

