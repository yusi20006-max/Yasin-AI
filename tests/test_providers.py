"""
Tests for Yasin-AI Provider Abstraction Layer
Phase 2.6
"""
import pytest

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.providers.registry import ProviderRegistry, ProviderRegistryError
from yasinai.providers.router import ProviderRouter, ProviderUnavailableError


# ---------------------------------------------------------------------------
# Fixtures — stub provider implementations
# ---------------------------------------------------------------------------

class StubGenerationProvider(ProviderBase):
    """Minimal stub that supports GENERATION and is always available."""

    def __init__(self, name: str = "stub-gen", models: list = None, available: bool = True):
        self._name = name
        self._models = models or ["stub-model-v1"]
        self._available = available

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self._name,
            version="0.1.0",
            capabilities=[ProviderCapability.GENERATION],
            model_ids=self._models,
        )

    def is_available(self) -> bool:
        return self._available

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            text=f"echo: {request.prompt}",
            model=request.model or self._models[0],
            provider=self._name,
        )


class StubEmbeddingProvider(ProviderBase):
    """Stub that supports only EMBEDDING."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="stub-embed",
            capabilities=[ProviderCapability.EMBEDDING],
            model_ids=["embed-v1"],
        )

    def is_available(self) -> bool:
        return True


class UnavailableProvider(ProviderBase):
    """Stub that is always unavailable."""

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="unavailable",
            capabilities=[ProviderCapability.GENERATION],
            model_ids=[],
        )

    def is_available(self) -> bool:
        return False


# ---------------------------------------------------------------------------
# GenerationRequest validation
# ---------------------------------------------------------------------------

def test_generation_request_valid():
    req = GenerationRequest(prompt="hello", model="stub-model-v1")
    assert req.prompt == "hello"
    assert req.max_tokens == 1024


def test_generation_request_empty_prompt():
    with pytest.raises(ValueError, match="prompt"):
        GenerationRequest(prompt="")


def test_generation_request_invalid_temperature():
    with pytest.raises(ValueError, match="temperature"):
        GenerationRequest(prompt="x", temperature=3.0)


def test_generation_request_invalid_max_tokens():
    with pytest.raises(ValueError, match="max_tokens"):
        GenerationRequest(prompt="x", max_tokens=0)


# ---------------------------------------------------------------------------
# ProviderBase interface
# ---------------------------------------------------------------------------

def test_provider_info():
    p = StubGenerationProvider()
    assert p.info.name == "stub-gen"
    assert ProviderCapability.GENERATION in p.info.capabilities


def test_provider_generate_works():
    p = StubGenerationProvider()
    req = GenerationRequest(prompt="test prompt")
    resp = p.generate(req)
    assert resp.text == "echo: test prompt"
    assert resp.provider == "stub-gen"


def test_provider_generate_wrong_capability():
    p = StubEmbeddingProvider()
    req = GenerationRequest(prompt="test")
    with pytest.raises(NotImplementedError):
        p.generate(req)


def test_provider_error():
    err = ProviderError("my-provider", "connection refused", retryable=True)
    assert err.provider == "my-provider"
    assert err.retryable is True
    assert "my-provider" in str(err)


# ---------------------------------------------------------------------------
# ProviderRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_get():
    reg = ProviderRegistry()
    p = StubGenerationProvider()
    reg.register(p)
    assert reg.get("stub-gen") is p


def test_registry_duplicate_raises():
    reg = ProviderRegistry()
    p = StubGenerationProvider()
    reg.register(p)
    with pytest.raises(ProviderRegistryError):
        reg.register(StubGenerationProvider())


def test_registry_overwrite():
    reg = ProviderRegistry()
    p1 = StubGenerationProvider(name="gen")
    p2 = StubGenerationProvider(name="gen")
    reg.register(p1)
    reg.register(p2, overwrite=True)
    assert reg.get("gen") is p2


def test_registry_unregister():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider())
    assert reg.unregister("stub-gen") is True
    assert reg.get("stub-gen") is None
    assert reg.unregister("stub-gen") is False


def test_registry_list():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider())
    reg.register(StubEmbeddingProvider())
    names = [i.name for i in reg.list()]
    assert "stub-gen" in names
    assert "stub-embed" in names


def test_registry_for_capability():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider())
    reg.register(StubEmbeddingProvider())
    gen_providers = reg.for_capability(ProviderCapability.GENERATION)
    assert len(gen_providers) == 1
    assert gen_providers[0].info.name == "stub-gen"


def test_registry_available_for_capability_excludes_unavailable():
    reg = ProviderRegistry()
    reg.register(UnavailableProvider())
    result = reg.available_for_capability(ProviderCapability.GENERATION)
    assert result == []


def test_registry_len():
    reg = ProviderRegistry()
    assert len(reg) == 0
    reg.register(StubGenerationProvider())
    assert len(reg) == 1


# ---------------------------------------------------------------------------
# ProviderRouter
# ---------------------------------------------------------------------------

def test_router_selects_available_provider():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider())
    router = ProviderRouter(reg)
    provider = router.select(ProviderCapability.GENERATION)
    assert provider.info.name == "stub-gen"


def test_router_selects_by_model_hint():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider(name="provider-a", models=["model-a"]))
    reg.register(StubGenerationProvider(name="provider-b", models=["model-b"]))
    router = ProviderRouter(reg)
    provider = router.select(ProviderCapability.GENERATION, model="model-b")
    assert provider.info.name == "provider-b"


def test_router_falls_back_when_no_model_match():
    reg = ProviderRegistry()
    reg.register(StubGenerationProvider(name="only-provider", models=["model-x"]))
    router = ProviderRouter(reg)
    # unknown-model has no exact match — falls back to first available
    provider = router.select(ProviderCapability.GENERATION, model="unknown-model")
    assert provider.info.name == "only-provider"


def test_router_raises_when_no_provider():
    reg = ProviderRegistry()
    router = ProviderRouter(reg)
    with pytest.raises(ProviderUnavailableError) as exc_info:
        router.select(ProviderCapability.GENERATION)
    assert exc_info.value.capability == ProviderCapability.GENERATION


def test_router_raises_when_all_unavailable():
    reg = ProviderRegistry()
    reg.register(UnavailableProvider())
    router = ProviderRouter(reg)
    with pytest.raises(ProviderUnavailableError):
        router.select(ProviderCapability.GENERATION)


def test_router_respects_capability_boundary():
    reg = ProviderRegistry()
    reg.register(StubEmbeddingProvider())
    router = ProviderRouter(reg)
    with pytest.raises(ProviderUnavailableError) as exc_info:
        router.select(ProviderCapability.GENERATION)
    assert exc_info.value.capability == ProviderCapability.GENERATION


def test_provider_unavailable_error_message():
    err = ProviderUnavailableError(ProviderCapability.GENERATION, model="gpt-4o")
    assert "generation" in str(err)
    assert "gpt-4o" in str(err)
