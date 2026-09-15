"""LocalProvider — OpenAI-compatible local inference adapter.

The provider owns request/response translation only. Optional process lifecycle
is delegated to LocalLLMRuntime; it never launches llama-server directly.
"""
from __future__ import annotations

import os
import urllib.error
import urllib.request

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.providers.openai_provider import HttpTransport, OpenAIProvider
from yasinai.runtime.local_llm import LocalLLMRuntime


DEFAULT_MODEL = "local-qwen17"
DEFAULT_BASE_URL = "http://127.0.0.1:18765"


class LocalProvider(OpenAIProvider):
    """Local OpenAI-compatible provider backed by llama-server."""

    DEFAULT_MODEL = DEFAULT_MODEL

    def __init__(
        self,
        *,
        model_id: str | None = None,
        base_url: str | None = None,
        runtime: LocalLLMRuntime | None = None,
        transport: HttpTransport | None = None,
    ) -> None:
        self._model_id = model_id or os.environ.get("YASINAI_LOCAL_MODEL", DEFAULT_MODEL)
        self._runtime = runtime
        resolved_base_url = base_url or (
            runtime.config.base_url if runtime is not None else None
        ) or os.environ.get("YASINAI_LOCAL_BASE_URL", DEFAULT_BASE_URL)
        super().__init__(
            api_key="local",
            base_url=resolved_base_url,
            default_model=self._model_id,
            transport=transport,
        )

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="local",
            version="2.0.0",
            capabilities=[ProviderCapability.GENERATION, ProviderCapability.CHAT],
            model_ids=[self._model_id],
            metadata={
                "network": "localhost",
                "protocol": "openai-chat-completions",
                "managed_runtime": self._runtime is not None,
            },
        )

    def is_available(self) -> bool:
        """Return whether the configured local endpoint is reachable and healthy."""
        if self._runtime is not None:
            return self._runtime.health()
        try:
            with urllib.request.urlopen(f"{self._base_url}/health", timeout=2) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        if self._runtime is not None and not self._runtime.health():
            try:
                self._runtime.start()
            except Exception as exc:
                raise ProviderError(
                    "local",
                    "local inference runtime is unavailable",
                    retryable=True,
                ) from exc

        try:
            response = super()._generate(request)
        except ProviderError as exc:
            if exc.provider == "openai":
                raise ProviderError("local", str(exc).split("] ", 1)[-1], exc.retryable) from exc
            raise
        return GenerationResponse(
            text=response.text,
            model=response.model,
            provider="local",
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            finish_reason=response.finish_reason,
            metadata=response.metadata,
        )
