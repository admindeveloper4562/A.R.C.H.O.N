"""Typed, transport-neutral adapters for common provider chat protocols."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
import re
from typing import Any


MAX_PROTOCOL_BYTES = 64 * 1024
MAX_MESSAGES = 128
MAX_TOOLS = 64
MAX_TOOL_CALLS = 64
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_ROLES = frozenset({"system", "developer", "user", "assistant", "tool"})


class AdapterError(ValueError):
    """Raised when a protocol request or response is invalid."""


def _bounded(value: str, pattern: re.Pattern[str], label: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not pattern.fullmatch(value)):
        raise AdapterError(f"invalid {label}")
    if empty and len(value.encode("utf-8")) > 128:
        raise AdapterError(f"invalid {label}")
    return value


def _json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AdapterError(f"{label} must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_PROTOCOL_BYTES:
        raise AdapterError(f"{label} exceeds bounded size")
    return encoded


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AdapterError(f"{label} must be an object")
    result = dict(value)
    _json(result, label)
    return result


def _text(value: object, label: str, *, required: bool = True) -> str:
    if not isinstance(value, str) or (required and not value):
        raise AdapterError(f"invalid {label}")
    if len(value.encode("utf-8")) > 32 * 1024:
        raise AdapterError(f"{label} exceeds bounded size")
    return value


@dataclass(frozen=True)
class ProtocolMessage:
    """Provider-neutral message content."""

    role: str
    content: str

    def __post_init__(self) -> None:
        if self.role not in _ROLES:
            raise AdapterError("invalid message role")
        _text(self.content, "message content", required=False)

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ProtocolToolCall:
    """Normalized function/tool call returned by either wire protocol."""

    call_id: str
    name: str
    arguments: Mapping[str, Any]

    def __post_init__(self) -> None:
        _bounded(self.call_id, _IDENTIFIER, "tool call id")
        _bounded(self.name, _IDENTIFIER, "tool name")
        if not isinstance(self.arguments, Mapping):
            raise AdapterError("tool arguments must be an object")
        _json(dict(self.arguments), "tool arguments")


@dataclass(frozen=True)
class ProtocolRequest:
    """A bounded request accepted by every protocol adapter."""

    conversation_id: str
    sequence: int
    model: str
    messages: Sequence[ProtocolMessage]
    tools: Sequence[Mapping[str, Any]] = ()

    def __post_init__(self) -> None:
        _bounded(self.conversation_id, _IDENTIFIER, "conversation id")
        _bounded(self.model, _MODEL, "model")
        if type(self.sequence) is not int or self.sequence < 1:
            raise AdapterError("sequence must be positive")
        messages = tuple(self.messages)
        if not 1 <= len(messages) <= MAX_MESSAGES or any(not isinstance(item, ProtocolMessage) for item in messages):
            raise AdapterError("messages are invalid")
        tools = tuple(self.tools)
        if len(tools) > MAX_TOOLS or any(not isinstance(item, Mapping) for item in tools):
            raise AdapterError("tools are invalid")
        _json([dict(item) for item in tools], "tools")
        object.__setattr__(self, "messages", messages)
        object.__setattr__(self, "tools", tools)


@dataclass(frozen=True)
class ProtocolResponse:
    """Normalized response independent of provider wire shape."""

    provider: str
    response_id: str
    model: str
    content: str
    finish_reason: str
    tool_calls: Sequence[ProtocolToolCall] = ()

    def __post_init__(self) -> None:
        _bounded(self.provider, _IDENTIFIER, "provider")
        _bounded(self.response_id, _IDENTIFIER, "response id")
        _bounded(self.model, _MODEL, "model")
        _text(self.content, "response content", required=False)
        _bounded(self.finish_reason, _IDENTIFIER, "finish reason", empty=True)
        calls = tuple(self.tool_calls)
        if len(calls) > MAX_TOOL_CALLS or any(not isinstance(item, ProtocolToolCall) for item in calls):
            raise AdapterError("tool calls are invalid")
        object.__setattr__(self, "tool_calls", calls)


class ProtocolAdapter:
    """Base adapter that separates wire conversion from transport execution."""

    protocol = ""

    def __init__(self, provider_id: str):
        self.provider_id = _bounded(provider_id, _IDENTIFIER, "provider")

    def encode(self, request: ProtocolRequest) -> dict[str, Any]:
        if not isinstance(request, ProtocolRequest):
            raise AdapterError("protocol request is required")
        return self._encode(request)

    def decode(self, payload: Mapping[str, Any]) -> ProtocolResponse:
        data = _object(payload, "provider response")
        return self._decode(data)

    def invoke(
        self,
        request: ProtocolRequest,
        transport: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    ) -> ProtocolResponse:
        if not callable(transport):
            raise AdapterError("transport must be callable")
        payload = transport(self.encode(request))
        return self.decode(payload)

    def _encode(self, request: ProtocolRequest) -> dict[str, Any]:
        raise NotImplementedError

    def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse:
        raise NotImplementedError


class ResponsesAdapter(ProtocolAdapter):
    """Adapter for providers exposing an OpenAI Responses-shaped endpoint."""

    protocol = "responses"

    def _encode(self, request: ProtocolRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "input": [message.as_dict() for message in request.messages],
        }
        if request.tools:
            payload["tools"] = [dict(tool) for tool in request.tools]
        _json(payload, "responses request")
        return payload

    def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse:
        response_id = _bounded(payload.get("id"), _IDENTIFIER, "response id")
        model = _bounded(payload.get("model"), _MODEL, "model")
        content: list[str] = []
        calls: list[ProtocolToolCall] = []
        output = payload.get("output")
        if not isinstance(output, list):
            raise AdapterError("responses output must be a list")
        for item in output:
            entry = _object(item, "responses output item")
            kind = entry.get("type")
            if kind == "message":
                parts = entry.get("content", [])
                if not isinstance(parts, list):
                    raise AdapterError("responses message content must be a list")
                for part in parts:
                    part_data = _object(part, "responses content item")
                    text = part_data.get("text")
                    if isinstance(text, str):
                        content.append(text)
            elif kind == "function_call":
                calls.append(self._function_call(entry))
        output_text = payload.get("output_text")
        if isinstance(output_text, str):
            content = [output_text]
        finish_reason = payload.get("status", "")
        return ProtocolResponse(self.provider_id, response_id, model, "".join(content), finish_reason, tuple(calls))

    @staticmethod
    def _function_call(entry: Mapping[str, Any]) -> ProtocolToolCall:
        arguments = entry.get("arguments", {})
        return ProtocolToolCall(
            _bounded(entry.get("call_id", entry.get("id")), _IDENTIFIER, "tool call id"),
            _bounded(entry.get("name"), _IDENTIFIER, "tool name"),
            _arguments(arguments),
        )


class ChatCompletionsAdapter(ProtocolAdapter):
    """Adapter for providers exposing a Chat Completions-shaped endpoint."""

    protocol = "chat"

    def _encode(self, request: ProtocolRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [message.as_dict() for message in request.messages],
        }
        if request.tools:
            payload["tools"] = [dict(tool) for tool in request.tools]
        _json(payload, "chat request")
        return payload

    def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse:
        response_id = _bounded(payload.get("id"), _IDENTIFIER, "response id")
        model = _bounded(payload.get("model"), _MODEL, "model")
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AdapterError("chat choices must be non-empty")
        choice = _object(choices[0], "chat choice")
        message = _object(choice.get("message"), "chat message")
        content = message.get("content", "")
        if content is None:
            content = ""
        content = _text(content, "chat content", required=False)
        calls = tuple(self._tool_call(_object(item, "chat tool call")) for item in message.get("tool_calls", []))
        if len(calls) > MAX_TOOL_CALLS:
            raise AdapterError("too many tool calls")
        finish_reason = choice.get("finish_reason", "")
        return ProtocolResponse(self.provider_id, response_id, model, content, _text(finish_reason, "finish reason", required=False), calls)

    @staticmethod
    def _tool_call(entry: Mapping[str, Any]) -> ProtocolToolCall:
        function = _object(entry.get("function"), "chat function")
        return ProtocolToolCall(
            _bounded(entry.get("id"), _IDENTIFIER, "tool call id"),
            _bounded(function.get("name"), _IDENTIFIER, "tool name"),
            _arguments(function.get("arguments", {})),
        )


def _arguments(value: object) -> Mapping[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise AdapterError("tool arguments are not valid JSON") from exc
    return _object(value, "tool arguments")


ChatAdapter = ChatCompletionsAdapter


__all__ = [
    "AdapterError",
    "ChatAdapter",
    "ChatCompletionsAdapter",
    "MAX_MESSAGES",
    "MAX_PROTOCOL_BYTES",
    "MAX_TOOL_CALLS",
    "MAX_TOOLS",
    "ProtocolAdapter",
    "ProtocolMessage",
    "ProtocolRequest",
    "ProtocolResponse",
    "ProtocolToolCall",
    "ResponsesAdapter",
]
