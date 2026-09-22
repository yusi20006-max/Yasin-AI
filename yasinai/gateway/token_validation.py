"""Secure localhost bridge for API Token Manager -> Yasin-AI validation."""
from __future__ import annotations
import os
from typing import Any
from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.gemini_provider import GeminiProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.validation import ValidationResult
from yasinai.services.token_health import TokenHealthEngine

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
    def _provider(name: str, credential: str):
        if name == "openai": return OpenAIProvider(api_key=credential)
        if name == "anthropic": return AnthropicProvider(api_key=credential)
        if name == "gemini": return GeminiProvider(api_key=credential)
        raise ValueError("unsupported provider")

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        provider = str(payload.get("provider") or "").strip().lower()
        credential = payload.get("credential")
        if not provider or not isinstance(credential, str) or not credential:
            return {"error": {"message": "provider and credential are required", "type": "invalid_request_error"}}
        result = self._provider(provider, credential).validate_credential(credential, model=payload.get("model"))
        return {"provider": provider, "health": result.public_dict()}

    def health_engine(self, provider: str, credential: str):
        adapter = self._provider(provider, credential)
        return TokenHealthEngine(adapter.validate_credential).check(credential)
