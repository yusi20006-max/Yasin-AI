"""Secure localhost bridge for API Token Manager -> Yasin-AI validation."""
from __future__ import annotations

import os
from typing import Any

from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.generic_openai import GenericOpenAIProvider
from yasinai.providers.gemini_provider import GeminiProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.services.token_health import TokenHealthEngine

ORCAROUTER_BASE_URL = "https://api.orcarouter.ai/v1"


class TokenValidationBridge:
    def __init__(self, *, bridge_token: str | None = None, allowed_origin: str | None = None):
        self.bridge_token = bridge_token or os.environ.get("YASINAI_BRIDGE_TOKEN")
        self.allowed_origin = allowed_origin or os.environ.get("YASINAI_ALLOWED_ORIGIN", "http://localhost")
        if not self.bridge_token:
            raise ValueError("YASINAI_BRIDGE_TOKEN is required for token validation bridge")

    def authorize(self, headers: dict[str, str], origin: str | None) -> bool:
        if origin != self.allowed_origin:
            return False
        return headers.get("X-YasinAI-Bridge-Token") == self.bridge_token

    @staticmethod
    def _provider(
        name: str,
        credential: str,
        *,
        base_url: str | None = None,
        model: str | None = None,
    ):
        if name == "openai":
            return OpenAIProvider(api_key=credential, base_url=base_url, default_model=model or "gpt-4o-mini")
        if name == "anthropic":
            return AnthropicProvider(api_key=credential)
        if name == "gemini":
            return GeminiProvider(api_key=credential)
        if name == "orcarouter":
            if base_url != ORCAROUTER_BASE_URL:
                raise ValueError("unsupported OrcaRouter base URL")
            if not model:
                raise ValueError("OrcaRouter model is required")
            return GenericOpenAIProvider(
                name="orcarouter",
                api_key=credential,
                base_url=ORCAROUTER_BASE_URL,
                default_model=model,
            )
        raise ValueError("unsupported provider")

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        provider = str(payload.get("provider") or "").strip().lower()
        credential = payload.get("credential")
        base_url = payload.get("baseUrl") or payload.get("base_url")
        model = payload.get("model")
        if not provider or not isinstance(credential, str) or not credential:
            return {"error": {"message": "provider and credential are required", "type": "invalid_request_error"}}
        try:
            adapter = self._provider(
                provider,
                credential,
                base_url=str(base_url).strip() if base_url else None,
                model=str(model).strip() if model else None,
            )
        except ValueError:
            return {"error": {"message": "unsupported provider configuration", "type": "invalid_request_error"}}
        result = adapter.validate_credential(credential, model=model)
        return {"provider": provider, "health": result.public_dict()}

    def health_engine(self, provider: str, credential: str):
        adapter = self._provider(provider, credential)
        return TokenHealthEngine(adapter.validate_credential).check(credential)
