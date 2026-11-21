# Local Ollama chat

ARCHON can use one explicitly configured local Qwen3 model through Ollama. Install the model separately and keep Ollama bound to `127.0.0.1:11434`; ARCHON does not download models or accept a remote Ollama URL.

```python
from jarvis_v2.backend import LocalOllamaGateway, OllamaInferenceProfile
from jarvis_v2.runtime import OllamaOfflineAdapter, OfflineChatService

profile = OllamaInferenceProfile(model="qwen3:4b", num_ctx=2048)
adapter = OllamaOfflineAdapter(LocalOllamaGateway(profile))
offline = OfflineChatService(
    chat_service,
    {adapter.model_alias},
    adapter=adapter,
    provider_id="ollama-local",
)
```

The runtime alias `qwen3-4b` maps only to the configured Ollama model `qwen3:4b`. The transport uses the [Ollama chat API](https://docs.ollama.com/api/chat) at fixed loopback address `127.0.0.1:11434`, with a bounded request and response and a finite timeout. It does not send prompts to an external provider. Model tool calls are returned as data and are never executed by this adapter. Offline fallback remains opt-in through `OfflineChatService.allow_fallback`.

Responses are buffered before they are emitted. Cancelling chat prevents persistence, but an in-flight local generation continues until Ollama responds or the timeout expires.

Run the host-backed persistence check when Ollama and `qwen3:4b` are available:

```sh
ARCHON_RUN_OLLAMA_INTEGRATION=1 python -m unittest discover -s tests -p 'test_runtime_ollama.py' -v
```

The normal unit suite does not require Ollama; the host-backed test is skipped unless explicitly enabled.
