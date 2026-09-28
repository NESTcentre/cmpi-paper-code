"""Thin wrappers around the Ollama Python client.

Defines two Protocols (sync and async) so retry orchestration can be tested with stubs.
"""

from typing import Protocol


class LLMClient(Protocol):
    def generate(self, *, prompt: str, options: dict) -> str: ...


class AsyncLLMClient(Protocol):
    async def generate(self, *, prompt: str, options: dict) -> str: ...


class OllamaClient:
    """Real Ollama client (sync). Lazily imported so tests can avoid the dependency."""

    def __init__(self):
        import ollama  # local import; tests may not need it

        self._ollama = ollama

    def generate(self, *, prompt: str, options: dict) -> str:
        """Call ollama.generate and return the response text."""
        # `model` is part of options in our config; extract it for the API call.
        opts = dict(options)
        model = opts.pop("model")
        result = self._ollama.generate(model=model, prompt=prompt, options=opts, stream=False)
        return result["response"]


class OllamaAsyncClient:
    """Real Ollama client (async). Wraps ollama.AsyncClient for concurrent dispatch.

    Throughput depends on Ollama's OLLAMA_NUM_PARALLEL env var: with N>=1 the daemon
    processes that many requests concurrently. Set it before launching ollama serve.
    """

    def __init__(self):
        import ollama

        self._client = ollama.AsyncClient()

    async def generate(self, *, prompt: str, options: dict) -> str:
        opts = dict(options)
        model = opts.pop("model")
        result = await self._client.generate(model=model, prompt=prompt, options=opts, stream=False)
        return result["response"]
