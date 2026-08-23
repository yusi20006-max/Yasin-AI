"""Generic OpenAI-compatible provider adapter.

This adapter deliberately knows nothing about a specific gateway.  A caller
supplies the provider name, base URL, API key, and model at runtime.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from yasinai.providers.base import GenerationRequest, GenerationResponse, ProviderCapability, ProviderInfo
from yasinai.providers.openai_provider import HttpTransport, OpenAIProvider


class GenericOpenAIProvider(OpenAIProvider):
    """Runtime-configured provider for OpenAI-compatible chat APIs."""

    def __init__(
        self,
        *,
        name: str,
        api_key: str,
        base_url: str,
        default_model: str,
        transport: HttpTransport | None = None,
    ) -> None:
        if not name.strip():
            raise ValueError("Provider name must not be empty")
        if not api_key:
            raise ValueError("API key must not be empty")
        if not default_model.strip():
            raise ValueError("Model must not be empty")
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            default_model=default_model,
            transport=transport,
        )
        self._provider_name = name.strip()

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self._provider_name,
            version="1.0.0",
            capabilities=[ProviderCapability.GENERATION, ProviderCapability.CHAT],
            model_ids=[self._default_model],
            metadata={"base_url": self._base_url, "protocol": "openai-chat-completions"},
        )

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        response = super()._generate(request)
        return replace(response, provider=self._provider_name)

    def public_config(self) -> dict[str, Any]:
        """Return non-secret provider metadata suitable for display."""
        return {
            "name": self._provider_name,
            "base_url": self._base_url,
            "model": self._default_model,
            "protocol": "openai-chat-completions",
        }
