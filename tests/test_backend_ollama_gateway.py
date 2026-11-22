from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from jarvis_v2.backend import OllamaInferenceProfile
from jarvis_v2.backend.ollama_gateway import LocalOllamaGateway, OllamaGatewayError
from jarvis_v2.backend.protocol_adapters import ProtocolMessage, ProtocolRequest


def request(model: str = "qwen3:4b", *, tools=()) -> ProtocolRequest:
    return ProtocolRequest(
        "conversation-1",
        1,
        model,
        (ProtocolMessage("user", "hello local model"),),
        tools=tools,
    )


def response(
    *,
    content: str = "local answer",
    model: str = "qwen3:4b",
    tool_calls=None,
    done_reason: str | None = "stop",
) -> bytes:
    return json.dumps({
        "model": model,
        "message": {"role": "assistant", "content": content, "tool_calls": tool_calls or []},
        "done": True,
        "done_reason": done_reason,
    }).encode()


class _Response:
    def __init__(self, body: bytes, *, status: int = 200, length: str | None = None) -> None:
        self.body = body
        self.status = status
        self.length = length
        self.read_size = None

    def getheader(self, name: str):
        return self.length if name.lower() == "content-length" else None

    def read(self, size: int) -> bytes:
        self.read_size = size
        return self.body[:size]


class _Connection:
    def __init__(self, response_obj: _Response) -> None:
        self.response = response_obj
        self.request_args = None
        self.closed = False

    def request(self, *args, **kwargs) -> None:
        self.request_args = (args, kwargs)

    def getresponse(self) -> _Response:
        return self.response

    def close(self) -> None:
        self.closed = True


class LocalOllamaGatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048)
        self.gateway = LocalOllamaGateway(self.profile, timeout_seconds=30)

    def test_posts_to_fixed_loopback_and_decodes_bounded_response(self) -> None:
        response_obj = _Response(response())
        connection = _Connection(response_obj)
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection) as factory:
            result = self.gateway.complete("hello local model", model="qwen3:4b")

        factory.assert_called_once_with("127.0.0.1", 11434, timeout=30.0)
        args, kwargs = connection.request_args
        self.assertEqual(args[:2], ("POST", "/api/chat"))
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
        body = json.loads(kwargs["body"])
        self.assertEqual(body["model"], "qwen3:4b")
        self.assertIs(body["think"], False)
        self.assertEqual(body["options"], self.profile.options())
        self.assertIs(body["stream"], False)
        self.assertEqual(result.content, "local answer")
        self.assertTrue(connection.closed)
        self.assertEqual(response_obj.read_size, 1024 * 1024 + 1)

    def test_rejects_unconfigured_model_before_network(self) -> None:
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection") as factory:
            with self.assertRaisesRegex(OllamaGatewayError, "not_allowlisted"):
                self.gateway.complete("private prompt", model="qwen3:8b")
        factory.assert_not_called()

    def test_rejects_oversized_prompt_before_network(self) -> None:
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection") as factory:
            with self.assertRaises(OllamaGatewayError):
                self.gateway.complete("x" * (64 * 1024 + 1), model="qwen3:4b")
        factory.assert_not_called()

    def test_rejects_oversized_and_non_success_responses_without_echoing_body(self) -> None:
        oversized = _Response(b"x" * 32, length=str(1024 * 1024 + 1))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=_Connection(oversized)):
            with self.assertRaisesRegex(OllamaGatewayError, "too_large"):
                self.gateway.complete("prompt", model="qwen3:4b")

        failing = _Response(b"private server detail", status=500)
        connection = _Connection(failing)
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            with self.assertRaises(OllamaGatewayError) as raised:
                self.gateway.complete("prompt", model="qwen3:4b")
        self.assertEqual(str(raised.exception), "local_model_http_failure")
        self.assertNotIn("private server detail", str(raised.exception))
        self.assertTrue(connection.closed)

    def test_classifies_extremely_long_content_length(self) -> None:
        connection = _Connection(_Response(response(), length="9" * 5_000))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            with self.assertRaisesRegex(OllamaGatewayError, "inference_response_too_large"):
                self.gateway.complete("prompt", model="qwen3:4b")
        self.assertTrue(connection.closed)

    def test_transport_timeout_is_distinct_and_retry_uses_a_fresh_connection(self) -> None:
        timed_out = _Connection(_Response(response()))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=timed_out):
            with patch.object(timed_out, "request", side_effect=TimeoutError("offline")) as request_call:
                with self.assertRaisesRegex(OllamaGatewayError, "local_model_transport_failure"):
                    self.gateway.complete("prompt", model="qwen3:4b")
        request_call.assert_called_once()
        self.assertTrue(timed_out.closed)

        restarted = _Connection(_Response(response(content="after restart")))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=restarted) as factory:
            result = self.gateway.complete("prompt", model="qwen3:4b")
        factory.assert_called_once_with("127.0.0.1", 11434, timeout=30.0)
        self.assertEqual(result.content, "after restart")
        self.assertTrue(restarted.closed)

    def test_malformed_json_is_not_reported_as_transport_failure(self) -> None:
        connection = _Connection(_Response(b"{"))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            with self.assertRaisesRegex(OllamaGatewayError, "inference_response_invalid"):
                self.gateway.complete("prompt", model="qwen3:4b")
        self.assertTrue(connection.closed)

    def test_truncated_output_is_rejected_and_missing_done_reason_is_normalized(self) -> None:
        truncated = _Connection(_Response(response(content="partial", done_reason="length")))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=truncated):
            with self.assertRaisesRegex(OllamaGatewayError, "inference_response_incomplete"):
                self.gateway.complete("prompt", model="qwen3:4b")
        self.assertTrue(truncated.closed)

        complete = _Connection(_Response(response(done_reason=None)))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=complete):
            result = self.gateway.complete("prompt", model="qwen3:4b")
        self.assertEqual(result.finish_reason, "stop")

    def test_rejects_response_from_a_different_model(self) -> None:
        connection = _Connection(_Response(response(model="qwen3:8b")))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            with self.assertRaisesRegex(OllamaGatewayError, "response_model_invalid"):
                self.gateway.complete("prompt", model="qwen3:4b")

    def test_tool_requests_use_bounded_output_cap_and_reject_truncation(self) -> None:
        tool = {"type": "function", "function": {"name": "read_status", "parameters": {"type": "object"}}}
        connection = _Connection(_Response(response(content="", done_reason="length")))
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            with self.assertRaisesRegex(OllamaGatewayError, "inference_response_incomplete"):
                self.gateway.invoke(request(tools=(tool,)))
        _, kwargs = connection.request_args
        body = json.loads(kwargs["body"])
        self.assertEqual(body["options"]["num_predict"], self.profile.tool_num_predict)
        self.assertTrue(connection.closed)

    def test_preserves_tool_calls_as_data_without_executing_them(self) -> None:
        native_calls = [{"function": {"name": "read_status", "arguments": {"scope": "health"}}}]
        connection = _Connection(_Response(response(content="", tool_calls=native_calls)))
        tool = {"type": "function", "function": {"name": "read_status", "parameters": {"type": "object"}}}
        with patch("jarvis_v2.backend.ollama_gateway.http.client.HTTPConnection", return_value=connection):
            result = self.gateway.invoke(request(tools=(tool,)))
        self.assertEqual(len(result.tool_calls), 1)
        self.assertEqual(result.tool_calls[0].name, "read_status")
        self.assertEqual(result.tool_calls[0].arguments, {"scope": "health"})


if __name__ == "__main__":
    unittest.main()
