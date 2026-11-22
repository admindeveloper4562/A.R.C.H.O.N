"""Bounded Ollama chat transport restricted to the local Linux service."""
from __future__ import annotations

import http.client
import json
from collections.abc import Mapping
from math import isfinite
from typing import Any
from uuid import uuid4

from .ollama_profile import OllamaInferenceProfile
from .protocol_adapters import (
    MAX_PROTOCOL_BYTES,
    MAX_TOOL_CALLS,
    AdapterError,
    ChatAdapter,
    ProtocolMessage,
    ProtocolRequest,
    ProtocolResponse,
)

_HOST = "127.0.0.1"
_PORT = 11434
_PATH = "/api/chat"
_MAX_RESPONSE_BYTES = 1024 * 1024
_MAX_TIMEOUT_SECONDS = 120


class OllamaGatewayError(ConnectionError):
    """A local inference request failed without exposing request data."""


class LocalOllamaGateway:
    """Invoke one explicitly selected Qwen3 model through Ollama loopback."""

    def __init__(
        self,
        profile: OllamaInferenceProfile,
        *,
        timeout_seconds: float = 45,
    ) -> None:
        if not isinstance(profile, OllamaInferenceProfile):
            raise OllamaGatewayError("inference_profile_required")
        if (
            type(timeout_seconds) not in (int, float)
            or timeout_seconds < 1
            or timeout_seconds > _MAX_TIMEOUT_SECONDS
            or (isinstance(timeout_seconds, float) and not isfinite(timeout_seconds))
        ):
            raise OllamaGatewayError("inference_timeout_invalid")
        self.profile = profile
        self.timeout_seconds = float(timeout_seconds)
        self._adapter = ChatAdapter("ollama-local")

    def complete(self, message: str, *, model: str) -> ProtocolResponse:
        if not isinstance(message, str) or "\x00" in message:
            raise OllamaGatewayError("inference_message_invalid")
        if model != self.profile.model:
            raise OllamaGatewayError("inference_model_not_allowlisted")
        try:
            request = ProtocolRequest(
                "ollama-local",
                1,
                model,
                (ProtocolMessage("user", message),),
            )
        except AdapterError as exc:
            raise OllamaGatewayError("inference_request_invalid") from exc
        return self.invoke(request)

    def invoke(self, request: ProtocolRequest) -> ProtocolResponse:
        if not isinstance(request, ProtocolRequest):
            raise OllamaGatewayError("inference_request_invalid")
        if request.model != self.profile.model:
            raise OllamaGatewayError("inference_model_not_allowlisted")
        try:
            return self._adapter.invoke(request, self._post)
        except AdapterError as exc:
            raise OllamaGatewayError("inference_response_invalid") from exc

    def _post(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping) or payload.get("model") != self.profile.model:
            raise OllamaGatewayError("inference_model_not_allowlisted")
        body = dict(payload)
        body["stream"] = False
        body["options"] = self.profile.options()
        try:
            encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
            if len(encoded) > MAX_PROTOCOL_BYTES:
                raise OllamaGatewayError("inference_request_too_large")
        except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
            raise OllamaGatewayError("inference_request_invalid") from exc

        connection = http.client.HTTPConnection(
            _HOST,
            _PORT,
            timeout=self.timeout_seconds,
        )
        try:
            connection.request(
                "POST",
                _PATH,
                body=encoded,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            response = connection.getresponse()
            if response.status != 200:
                raise OllamaGatewayError("local_model_http_failure")
            length = response.getheader("Content-Length")
            if length is not None:
                if not isinstance(length, str) or not length.isascii() or not length.isdigit():
                    raise OllamaGatewayError("inference_response_invalid")
                normalized_length = length.lstrip("0") or "0"
                max_length = str(_MAX_RESPONSE_BYTES)
                if len(normalized_length) > len(max_length) or (
                    len(normalized_length) == len(max_length) and normalized_length > max_length
                ):
                    raise OllamaGatewayError("inference_response_too_large")
            raw = response.read(_MAX_RESPONSE_BYTES + 1)
            if len(raw) > _MAX_RESPONSE_BYTES:
                raise OllamaGatewayError("inference_response_too_large")
        except OllamaGatewayError:
            raise
        except (OSError, TimeoutError, http.client.HTTPException) as exc:
            raise OllamaGatewayError("local_model_transport_failure") from exc
        finally:
            connection.close()

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError, RecursionError) as exc:
            raise OllamaGatewayError("inference_response_invalid") from exc
        return self._as_chat_completion(decoded)

    def _as_chat_completion(self, payload: Any) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping) or payload.get("model") != self.profile.model:
            raise OllamaGatewayError("inference_response_model_invalid")
        done_reason = payload.get("done_reason")
        if payload.get("done") is not True or done_reason == "length":
            raise OllamaGatewayError("inference_response_incomplete")
        if done_reason not in (None, "", "stop"):
            raise OllamaGatewayError("inference_response_invalid")
        message = payload.get("message")
        if not isinstance(message, Mapping) or message.get("role") != "assistant":
            raise OllamaGatewayError("inference_response_invalid")
        content = message.get("content", "")
        if content is None:
            content = ""
        if not isinstance(content, str):
            raise OllamaGatewayError("inference_response_invalid")
        native_calls = message.get("tool_calls", [])
        if not isinstance(native_calls, list) or len(native_calls) > MAX_TOOL_CALLS:
            raise OllamaGatewayError("inference_tool_calls_invalid")
        calls = []
        for index, call in enumerate(native_calls):
            if not isinstance(call, Mapping):
                raise OllamaGatewayError("inference_tool_calls_invalid")
            function = call.get("function")
            if not isinstance(function, Mapping):
                raise OllamaGatewayError("inference_tool_calls_invalid")
            arguments = function.get("arguments", {})
            if isinstance(arguments, Mapping):
                try:
                    arguments = json.dumps(
                        arguments,
                        allow_nan=False,
                        separators=(",", ":"),
                    )
                except (TypeError, ValueError, RecursionError) as exc:
                    raise OllamaGatewayError("inference_tool_calls_invalid") from exc
            if not isinstance(arguments, str):
                raise OllamaGatewayError("inference_tool_calls_invalid")
            calls.append({
                "id": f"ollama-call-{uuid4().hex[:16]}-{index}",
                "type": "function",
                "function": {"name": function.get("name"), "arguments": arguments},
            })
        return {
            "id": f"ollama-{uuid4().hex}",
            "model": self.profile.model,
            "choices": [{
                "message": {"role": "assistant", "content": content, "tool_calls": calls},
                "finish_reason": done_reason or "stop",
            }],
        }


__all__ = ["LocalOllamaGateway", "OllamaGatewayError"]
