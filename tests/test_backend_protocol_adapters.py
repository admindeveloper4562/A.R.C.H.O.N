import unittest

from jarvis_v2.backend import (
    AdapterError,
    ChatAdapter,
    ProtocolMessage,
    ProtocolRequest,
    ResponsesAdapter,
)


def request():
    return ProtocolRequest(
        conversation_id="conversation-1",
        sequence=2,
        model="gpt-5.6-luna",
        messages=(
            ProtocolMessage("system", "be concise"),
            ProtocolMessage("user", "status"),
        ),
        tools=({"type": "function", "function": {"name": "health"}},),
    )


class BackendProtocolAdapterTests(unittest.TestCase):
    def test_responses_adapter_encodes_and_decodes_compatible_wire_shape(self):
        adapter = ResponsesAdapter("codex")
        request_payload = adapter.encode(request())
        self.assertEqual(request_payload["input"][1]["content"], "status")
        response = adapter.invoke(
            request(),
            lambda payload: {
                "id": "resp-1",
                "model": payload["model"],
                "status": "completed",
                "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
            },
        )
        self.assertEqual((response.provider, response.content, response.finish_reason), ("codex", "ok", "completed"))

    def test_chat_adapter_encodes_and_decodes_tool_arguments(self):
        adapter = ChatAdapter("ollama")
        payload = adapter.encode(request())
        self.assertEqual(payload["messages"][0]["role"], "system")
        response = adapter.decode({
            "id": "chat-1",
            "model": "qwen3:8b",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "health", "arguments": '{"scope":"local"}'},
                    }],
                },
                "finish_reason": "tool_calls",
            }],
        })
        self.assertEqual(response.tool_calls[0].arguments, {"scope": "local"})
        self.assertEqual(response.finish_reason, "tool_calls")

    def test_function_tool_schemas_are_validated_before_transport(self):
        valid = {
            "type": "function",
            "function": {
                "name": "lookup_status",
                "parameters": {
                    "type": "object",
                    "properties": {"scope": {"type": "string", "enum": ["health"]}},
                    "required": ["scope"],
                },
            },
        }
        nested = {
            "type": "function",
            "function": {
                "name": "search",
                "parameters": {
                    "type": "object",
                    "properties": {"filter": {"oneOf": [{"type": "string"}]}},
                },
            },
        }
        self.assertEqual(request().tools[0]["type"], "function")
        self.assertEqual(
            ProtocolRequest("conversation-1", 1, "gpt-5.6-luna", (ProtocolMessage("user", "x"),),
                            tools=(valid, nested)).tools,
            (valid, nested),
        )
        invalid = (
            {"type": "other", "function": {"name": "lookup_status"}},
            {"type": "function", "function": {"name": "invalid name"}},
            {"type": "function", "function": {"name": "lookup_status",
             "parameters": {"type": "string"}}},
            {"type": "function", "function": {"name": "lookup_status",
             "parameters": {"type": "object", "properties": {"scope": "string"}}}},
            {"type": "function", "function": {"name": "lookup_status",
             "parameters": {"type": "object", "properties": {}, "required": ["missing"]}}},
            {"type": "function", "function": {"name": "lookup_status",
             "parameters": {"type": "object", "properties": {"scope": {}},
                            "required": ["scope", "scope"]}}},
        )
        for tool in invalid:
            with self.subTest(tool=tool), self.assertRaises(AdapterError):
                ProtocolRequest(
                    "conversation-1", 1, "gpt-5.6-luna",
                    (ProtocolMessage("user", "x"),), tools=(tool,),
                )

    def test_invalid_wire_responses_are_rejected(self):
        with self.assertRaises(AdapterError):
            ResponsesAdapter("codex").decode({"id": "resp-1", "model": "gpt-5.6-luna", "output": "bad"})
        with self.assertRaises(AdapterError):
            ChatAdapter("ollama").decode({"id": "chat-1", "model": "qwen3:8b", "choices": []})
        with self.assertRaises(AdapterError):
            ChatAdapter("ollama").decode({
                "id": "chat-1", "model": "qwen3:8b",
                "choices": [{"message": {"content": "", "tool_calls": [{"id": "call-1", "function": {"name": "x", "arguments": "not-json"}}]}}],
            })

    def test_request_boundaries_are_checked_before_transport(self):
        with self.assertRaises(AdapterError):
            ProtocolRequest("conversation-1", 1, "gpt-5.6-luna", (ProtocolMessage("user", "ok"),), tools=("bad",))
        with self.assertRaises(AdapterError):
            ProtocolMessage("unknown", "ok")
        with self.assertRaises(AdapterError):
            ChatAdapter("ollama").invoke(request(), object())


if __name__ == "__main__":
    unittest.main()
