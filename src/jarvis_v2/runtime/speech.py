"""Bounded local speech streaming with explicit interruption semantics."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Iterable
import inspect
import re
from typing import Any

from jarvis_v2.backend.conversation import MAX_TURN_CONTENT_BYTES


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
MAX_AUDIO_CHUNK_BYTES = 256 * 1024
MAX_AUDIO_CHUNKS = 4096


class SpeechServiceError(ValueError):
    """Raised when a local speech request or adapter result is invalid."""


SpeechAdapter = Callable[[str, str], Any]


class SpeechService:
    """Stream local speech without making audio part of conversation history."""

    def __init__(self, adapter: SpeechAdapter, *, default_voice: str = "en_GB") -> None:
        if not callable(adapter):
            raise SpeechServiceError("speech adapter is required")
        self.adapter = adapter
        self.default_voice = self._voice(default_voice)

    async def stream(
        self,
        text: str,
        *,
        voice: str | None = None,
        cancel_event: Any = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Yield audio chunks and never persist partial or interrupted speech."""
        try:
            self._text(text)
            selected_voice = self._voice(self.default_voice if voice is None else voice)
        except SpeechServiceError:
            yield self._error("invalid_request", "Speech request is invalid; nothing was played.")
            return
        if self._cancelled(cancel_event):
            yield self._cancelled_event()
            return

        chunks = 0
        try:
            produced = self.adapter(text, selected_voice)
            if inspect.isawaitable(produced):
                produced = await produced
            async for raw in self._chunks(produced):
                if self._cancelled(cancel_event):
                    await self._stop_adapter()
                    yield self._cancelled_event()
                    return
                chunk = self._audio_chunk(raw)
                chunks += 1
                if chunks > MAX_AUDIO_CHUNKS:
                    raise SpeechServiceError("too many audio chunks")
                yield {"type": "audio", "content": chunk, "voice": selected_voice}
        except asyncio.CancelledError:
            await self._stop_adapter()
            return
        except TimeoutError:
            yield self._error("provider_timeout", "Speech timed out; conversation history was unchanged.")
            return
        except (ConnectionError, OSError):
            yield self._error("provider_unavailable", "Speech is unavailable; conversation history was unchanged.")
            return
        except SpeechServiceError:
            yield self._error("provider_invalid", "Speech returned invalid audio; conversation history was unchanged.")
            return
        except Exception:
            yield self._error("provider_failed", "Speech failed; conversation history was unchanged.")
            return

        if chunks == 0:
            yield self._error("empty_response", "Speech returned no audio; conversation history was unchanged.")
            return
        if self._cancelled(cancel_event):
            await self._stop_adapter()
            yield self._cancelled_event()
            return
        yield {"type": "done", "status": "completed", "voice": selected_voice, "chunks": chunks}

    @staticmethod
    async def _chunks(produced: Any) -> AsyncIterator[Any]:
        if isinstance(produced, (bytes, bytearray, memoryview)):
            yield produced
            return
        if hasattr(produced, "__aiter__"):
            async for item in produced:
                yield item
            return
        if isinstance(produced, Iterable):
            for item in produced:
                yield item
            return
        raise SpeechServiceError("speech adapter stream is invalid")

    @staticmethod
    def _text(value: str) -> str:
        if not isinstance(value, str) or not value or len(value.encode("utf-8")) > MAX_TURN_CONTENT_BYTES:
            raise SpeechServiceError("invalid text")
        return value

    @staticmethod
    def _voice(value: str) -> str:
        if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
            raise SpeechServiceError("invalid voice")
        return value

    @staticmethod
    def _audio_chunk(value: Any) -> bytes:
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise SpeechServiceError("audio chunk is invalid")
        chunk = bytes(value)
        if not chunk or len(chunk) > MAX_AUDIO_CHUNK_BYTES:
            raise SpeechServiceError("audio chunk is invalid")
        return chunk

    async def _stop_adapter(self) -> None:
        stop = getattr(self.adapter, "stop", None)
        if not callable(stop):
            return
        try:
            result = stop()
            if inspect.isawaitable(result):
                await result
        except Exception:
            return

    @staticmethod
    def _cancelled(value: Any) -> bool:
        return value is not None and bool(value.is_set())

    @staticmethod
    def _cancelled_event() -> dict[str, Any]:
        return SpeechService._error("cancelled", "Speech was interrupted; conversation history was unchanged.")

    @staticmethod
    def _error(code: str, message: str) -> dict[str, Any]:
        return {"type": "error", "error": {"code": code, "message": message}}


__all__ = [
    "MAX_AUDIO_CHUNK_BYTES",
    "MAX_AUDIO_CHUNKS",
    "SpeechAdapter",
    "SpeechService",
    "SpeechServiceError",
]
