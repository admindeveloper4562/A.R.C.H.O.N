"""Small, local-only client for an existing Colibri OpenAI-compatible server."""
from __future__ import annotations

import json
import asyncio
import ipaddress
import os
import subprocess
import urllib.error
import urllib.request
import time
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Iterator
from urllib.parse import urlsplit


@dataclass(frozen=True)
class ColibriConfig:
    base_url: str = os.environ.get("JARVIS_COLIBRI_URL", "http://127.0.0.1:8000/v1")
    timeout: float = 4.0
    cli: Path = Path(os.environ.get("JARVIS_COLIBRI_CLI", Path.home() / "colibri/c/coli"))
    preferred_model: str = os.environ.get("JARVIS_COLIBRI_MODEL", "")
    max_message_chars: int = 12000
    retries: int = 1
    retry_backoff: float = 0.05

    def __post_init__(self) -> None:
        """Reject provider URLs that could disclose local prompts off-host.

        Colibri is a local-only dependency.  Do not rely on a prompt or an
        environment variable being benign: a non-loopback override must fail
        before any request is constructed.  Literal loopback addresses avoid
        DNS rebinding through a hostname such as ``localhost``.
        """
        parsed = urlsplit(self.base_url)
        if parsed.scheme != "http" or parsed.username or parsed.password or not parsed.hostname:
            raise ValueError("Colibri URL must be an unauthenticated http loopback URL")
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError as exc:
            raise ValueError("Colibri URL must use a literal loopback address") from exc
        if not address.is_loopback:
            raise ValueError("Colibri URL must target loopback")
        if not isinstance(self.timeout, (int, float)) or isinstance(self.timeout, bool) or not math.isfinite(self.timeout) or not 0 < self.timeout <= 120:
            raise ValueError("Colibri timeout must be between 0 and 120 seconds")
        if type(self.retries) is not int or not 0 <= self.retries <= 3:
            raise ValueError("Colibri retries must be between 0 and 3")
        if not isinstance(self.retry_backoff, (int, float)) or isinstance(self.retry_backoff, bool) or not math.isfinite(self.retry_backoff) or not 0 <= self.retry_backoff <= 5:
            raise ValueError("Colibri retry backoff must be between 0 and 5 seconds")
        if type(self.max_message_chars) is not int or not 1 <= self.max_message_chars <= 50000:
            raise ValueError("Colibri message limit must be between 1 and 50000")
        if not isinstance(self.preferred_model, str) or len(self.preferred_model) > 200:
            raise ValueError("Colibri preferred model must be a bounded string")


class ColibriClient:
    def __init__(self, config: ColibriConfig | None = None) -> None:
        self.config = config or ColibriConfig()

    def _bounded_message(self, message: str) -> str:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must not be empty")
        message = message.strip()
        limit = self.config.max_message_chars
        if limit < 1:
            raise ValueError("max_message_chars must be positive")
        if len(message) > limit:
            # Keep the newest context, which is generally the most actionable part.
            message = message[-limit:]
        return message

    def models(self) -> list[dict]:
        request = urllib.request.Request(self.config.base_url.rstrip("/") + "/models")
        with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
            payload = json.loads(response.read())
        models = payload.get("data", [])
        return [model for model in models if isinstance(model, dict) and isinstance(model.get("id"), str)]

    def status(self) -> dict:
        started = time.monotonic()
        try:
            models = self.models()
            ids = {model["id"] for model in models}
            preferred = self.config.preferred_model if self.config.preferred_model in ids else None
            if not preferred:
                preferred = next((item["id"] for item in models
                                  if re.search(r"qwen(?:3[._-]?5|35)[-_]?4b", item["id"], re.I)), None)
            return {"state": "connected", "models": models,
                    "preferred_model": preferred or (models[0]["id"] if models else None),
                    "checked_at": time.time(), "latency_ms": round((time.monotonic() - started) * 1000, 2),
                    "warmup": "ready" if models else "no_model"}
        except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError) as exc:
            return {"state": "disconnected", "models": [], "preferred_model": None,
                    "checked_at": time.time(), "latency_ms": round((time.monotonic() - started) * 1000, 2),
                    "warmup": "unavailable", "error": type(exc).__name__}

    def warmup(self) -> dict:
        """Perform only the provider's harmless model probe; never starts Colibri."""
        result = self.status()
        result["warmup_requested"] = True
        return result

    def complete(self, message: str, model: str | None = None) -> dict:
        message = self._bounded_message(message)
        chosen = self._available_model(model)
        if not chosen:
            raise ConnectionError("Colibri is disconnected or has no available model")
        payload = json.dumps({"model": chosen, "messages": [{"role": "user", "content": message}]}).encode()
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions", data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        result = None
        for attempt in range(self.config.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                    result = json.loads(response.read())
                break
            except (TimeoutError, urllib.error.URLError, OSError):
                if attempt >= self.config.retries:
                    raise
                # Keep retries bounded and yield to other local work.  The
                # adapter never retries indefinitely or across model changes.
                if self.config.retry_backoff > 0:
                    import time
                    time.sleep(self.config.retry_backoff * (2 ** attempt))
        if result is None:
            raise ConnectionError("Colibri returned no response")
        choices = result.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ValueError("Colibri returned no chat choice")
        message_data = choices[0].get("message")
        if not isinstance(message_data, dict) or not isinstance(message_data.get("content"), str):
            raise ValueError("Colibri returned an invalid chat choice")
        return {"model": result.get("model", chosen), "content": message_data["content"]}

    async def complete_async(self, message: str, model: str | None = None) -> dict:
        """Run completion without leaving a detached provider worker on cancellation."""
        worker = asyncio.create_task(asyncio.to_thread(self.complete, message, model))
        try:
            return await asyncio.wait_for(
                asyncio.shield(worker),
                timeout=self.config.timeout * (self.config.retries + 1),
            )
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Colibri completion timed out") from exc
        finally:
            # urllib has a bounded socket timeout but its thread cannot be
            # interrupted by asyncio cancellation. Join it before returning
            # so a stopped request cannot keep using the provider in secret.
            try:
                await asyncio.shield(worker)
            except Exception:
                pass

    def complete_stream(self, message: str, model: str | None = None) -> Iterator[dict[str, str]]:
        """Yield validated OpenAI-compatible SSE deltas without buffering the answer."""
        message = self._bounded_message(message)
        chosen = self._available_model(model)
        if not chosen:
            raise ConnectionError("Colibri is disconnected or has no available model")
        payload = json.dumps({"model": chosen, "messages": [{"role": "user", "content": message}], "stream": True}).encode()
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions", data=payload,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"}, method="POST")
        with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", "replace").strip()
                if not line or line.startswith(":"):
                    continue
                if not line.startswith("data:"):
                    raise ValueError("Colibri returned invalid streaming data")
                data = line[5:].strip()
                if data == "[DONE]":
                    return
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    raise ValueError("Colibri returned an invalid stream chunk") from exc
                if not isinstance(delta, str):
                    raise ValueError("Colibri returned a non-text stream delta")
                if delta:
                    yield {"model": str(chunk.get("model", chosen)), "content": delta}
        raise ConnectionError("Colibri stream ended before completion")

    def _available_model(self, requested: str | None) -> str:
        if requested is not None and (not isinstance(requested, str) or not requested):
            raise ValueError("requested model must be a non-empty string")
        status = self.status()
        available = {item["id"] for item in status["models"]}
        chosen = requested or status["preferred_model"]
        if not isinstance(chosen, str) or chosen not in available:
            raise ConnectionError("requested local model is unavailable")
        return chosen

    async def complete_stream_async(
        self, message: str, model: str | None = None
    ) -> AsyncIterator[dict[str, str]]:
        """Yield SSE deltas without blocking the asyncio event loop.

        ``complete_stream`` owns a blocking urllib response.  A cancelled or
        timed-out read must finish before its iterator can be closed: otherwise
        the thread can keep reading a response after the owner stopped it.
        """
        iterator = iter(self.complete_stream(message, model))

        def next_delta() -> tuple[bool, dict[str, str] | None]:
            try:
                return True, next(iterator)
            except StopIteration:
                return False, None

        try:
            while True:
                read_task = asyncio.create_task(asyncio.to_thread(next_delta))
                try:
                    try:
                        has_value, delta = await asyncio.wait_for(
                            asyncio.shield(read_task), timeout=self.config.timeout
                        )
                    except asyncio.TimeoutError as exc:
                        raise TimeoutError("Colibri stream timed out") from exc
                except BaseException:
                    # urllib's socket timeout bounds this read.  Do not leave
                    # a detached thread using the generator after cancellation.
                    try:
                        await asyncio.shield(read_task)
                    except Exception:
                        pass
                    raise
                if not has_value:
                    return
                if delta is not None:
                    yield delta
        finally:
            iterator.close()


def cli_status(config: ColibriConfig | None = None) -> dict:
    """Inspect the configured CLI only; never start, stop, or modify Colibri."""
    cfg = config or ColibriConfig()
    if not cfg.cli.is_file():
        return {"available": False, "path": str(cfg.cli), "owned": False, "reason": "not_found"}
    try:
        result = subprocess.run(["python3", str(cfg.cli), "status", "--json"], capture_output=True, text=True, timeout=3, check=False)
        return {"available": True, "path": str(cfg.cli), "owned": False, "status_exit": result.returncode,
                "status": result.stdout[-4000:] if result.stdout else ""}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": True, "path": str(cfg.cli), "owned": False, "reason": type(exc).__name__}
