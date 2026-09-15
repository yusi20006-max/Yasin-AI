from __future__ import annotations

from yasinai.contracts.generation import GenerationRequest
from yasinai.providers.base import GenerationResponse, ProviderBase, ProviderCapability, ProviderError, ProviderInfo
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter
from yasinai.services.generation_service import GenerationService


class FakeGemini(ProviderBase):
    @property
    def info(self):
        return ProviderInfo("gemini", model_ids=["gemini-3.6-flash"], capabilities=[ProviderCapability.GENERATION])

    def is_available(self):
        return True

    def _generate(self, request):
        raise ProviderError("gemini", "temporary outage", retryable=True)


class FakeLocal(ProviderBase):
    @property
    def info(self):
        return ProviderInfo("local", model_ids=["local-qwen17"], capabilities=[ProviderCapability.GENERATION])

    def is_available(self):
        return True

    def _generate(self, request):
        return GenerationResponse("local answer", request.model or "local-qwen17", "local")


def service_with(gemini, local):
    registry = ProviderRegistry()
    registry.register(gemini)
    registry.register(local)
    return GenerationService(
        registry=registry,
        router=ProviderRouter(registry),
        max_retries_per_provider=0,
        max_provider_fallbacks=1,
    )


def test_retryable_gemini_failure_falls_back_to_local_without_model_pin():
    result = service_with(FakeGemini(), FakeLocal()).generate(GenerationRequest(prompt="hello"))
    assert result.success is True
    assert result.provider == "local"
    assert result.text == "local answer"


def test_pinned_gemini_does_not_fall_back():
    result = service_with(FakeGemini(), FakeLocal()).generate(
        GenerationRequest(prompt="hello", provider="gemini")
    )
    assert result.success is False
    assert result.provider == "gemini"


def test_explicit_gemini_model_is_not_silently_changed():
    result = service_with(FakeGemini(), FakeLocal()).generate(
        GenerationRequest(prompt="hello", model="gemini-3.6-flash")
    )
    assert result.success is False
    assert result.provider == "router" or result.provider == "gemini"
