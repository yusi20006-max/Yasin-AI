"""Generic OpenAI-compatible provider adapter.

This adapter deliberately knows nothing about a specific gateway.  A caller
supplies the provider name, base URL, API key, and model at runtime.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from yasinai.providers.base import GenerationRequest, GenerationResponse, ProviderCapability, ProviderInfo
from yasinai.providers.openai_provider import HttpTransport, OpenAIProvider


def _validation_result_from_exception(exc: Exception, latency_ms: int):
    from yasinai.providers.validation import ValidationResult
    import re
    message = str(exc)
    match = re.search(r"HTTP (\d{3})", message)
    status = int(match.group(1)) if match else None
    if status in (401, 403): return ValidationResult(True, False, status, "UNAUTHORIZED" if status == 401 else "FORBIDDEN", "credential rejected by provider", latency_ms, {})
    if status == 429: return ValidationResult(True, None, status, "RATE_LIMITED", "provider rate limit", latency_ms, {})
    if status and status >= 500: return ValidationResult(True, None, status, "SERVER_ERROR", "provider server error", latency_ms, {})
    if getattr(exc, "retryable", False): return ValidationResult(False, None, status, "NETWORK_ERROR", "provider transport error", latency_ms, {})
    return ValidationResult(None, None, status, "UNKNOWN", "credential validation failed", latency_ms, {})


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
        probe_transport = None,
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
            probe_transport=probe_transport,
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

    def validate_credential(self, credential: str, *, model: str | None = None):
        from time import perf_counter
        from yasinai.providers.validation import ValidationResult
        if not credential:
            return ValidationResult(None, False, error_code="INVALID_CREDENTIAL", error_message="credential is empty")
        started = perf_counter()
        try:
            probe = GenericOpenAIProvider(
                name=self._provider_name,
                api_key=credential,
                base_url=self._base_url,
                default_model=model or self._default_model,
                transport=self._transport,
                probe_transport=self._probe_transport,
            )
            payload = probe._probe_transport(f"{self._base_url}/models", {"Authorization": f"Bearer {credential}"})
            models = [item.get("id") for item in (payload.get("data") or []) if isinstance(item, dict) and item.get("id")]
            latency = round((perf_counter() - started) * 1000)
            capabilities = {"models": models, "generation": "available"}
            if model and model not in models:
                return ValidationResult(True, True, 200, "MODEL_NOT_FOUND", "requested model is not available", latency, capabilities)
            return ValidationResult(True, True, 200, None, None, latency, capabilities)
        except Exception as exc:
            return _validation_result_from_exception(exc, round((perf_counter() - started) * 1000))

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
