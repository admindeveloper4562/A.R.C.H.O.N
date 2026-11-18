"""Read-only discovery of optional local speech adapters.

Discovery never starts a process and never records or transmits audio.  The
dashboard can therefore distinguish an unavailable adapter from a configured
one without making a claim based on a prompt or a hard-coded fixture.
"""
from __future__ import annotations

import os
import shutil

_STT_COMMANDS = ("whisper", "whisper.cpp")
_TTS_COMMANDS = ("piper", "kokoro")


def _found(commands: tuple[str, ...]) -> list[dict[str, str]]:
    return [{"id": command, "label": command} for command in commands if shutil.which(command)]


def local_adapters() -> dict:
    """Return installed command names only; do not probe by executing them."""
    stt = _found(_STT_COMMANDS)
    tts = _found(_TTS_COMMANDS)
    # A voice is not considered configured merely because a binary exists:
    # loading models and selecting a voice require an explicit later setup.
    return {
        "stt": {"state": "available" if stt else "unavailable", "adapters": stt},
        "tts": {"state": "available" if tts else "unavailable", "adapters": tts},
        "configured": bool(os.environ.get("JARVIS_VOICE_MODEL")) and bool(tts),
        "probe": "binary_presence_only",
    }
