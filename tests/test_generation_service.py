"""Tests for Generation contract + GenerationService (Phase 3.2)."""
from __future__ import annotations

import pytest

from yasinai.contracts import GenerationRequest, GenerationResult, ContractViolationError
from yasinai.providers import LocalProvider, OpenAIProvider, ProviderRegistry
from yasinai.providers.base import (
    GenerationRequest as ProviderGenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.services import GenerationService


class _FlakyProvider(ProviderBase):
    """Test double: fails N times (retryable or not), then succeeds."""

    def __init__(self, name: str, *, fail_times: int, retryable: bool = True) -> None:
        self._name = name
        self._fail_times = fail_times
        self._retryable = retryable
        self.call_count = 0

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self._name,
            capabilities=[ProviderCapability.GENERATION],
            model_ids=[],
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: ProviderGenerationRequest) -> GenerationResponse:
        self.call_count += 1
        if self.call_count <= self._fail_times:
            raise ProviderError(self._name, "simulated failure", retryable=self._retryable)
        return GenerationResponse(text="ok", model="fake-model", provider=self._name)


class _AlwaysFailsProvider(ProviderBase):
    def __init__(self, name: str, *, retryable: bool = True) -> None:
        self._name = name
        self._retryable = retryable
        self.call_count = 0

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self._name,
            capabilities=[ProviderCapability.GENERATION],
            model_ids=[],
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: ProviderGenerationRequest) -> GenerationResponse:
        self.call_count += 1
        raise ProviderError(self._name, "always fails", retryable=self._retryable)


def test_generation_request_validation():
    with pytest.raises(ContractViolationError, match="prompt"):
        GenerationRequest(prompt="")
    with pytest.raises(ContractViolationError, match="temperature"):
        GenerationRequest(prompt="hi", temperature=3.0)
    with pytest.raises(ContractViolationError, match="max_tokens"):
        GenerationRequest(prompt="hi", max_tokens=0)


def test_generate_via_local_provider():
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    svc = GenerationService(registry=reg)
    result = svc.generate(GenerationRequest(prompt="hello phase 3.2"))
    assert isinstance(result, GenerationResult)
    assert result.success is True
    assert "hello phase 3.2" in result.text
    assert result.provider == "local"
    assert result.meta.capability == "generation"
    assert result.meta.provider == "local"


def test_generate_preferred_provider():
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    svc = GenerationService(registry=reg)
    result = svc.generate(
        GenerationRequest(prompt="ping", provider="local", system_prompt="sys")
    )
    assert result.success is True
    assert result.provider == "local"
    assert "[system: sys]" in result.text


def test_generate_unavailable_provider():
    reg = ProviderRegistry()
    reg.register(OpenAIProvider(api_key=""))  # not available
    svc = GenerationService(registry=reg)
    result = svc.generate(GenerationRequest(prompt="x"))
    assert result.success is False
    assert result.error
    assert "provider" in result.error.lower() or "No available" in result.error


def test_generate_unknown_named_provider():
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    svc = GenerationService(registry=reg)
    result = svc.generate(GenerationRequest(prompt="x", provider="does-not-exist"))
    assert result.success is False


def test_default_registry_includes_local(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    svc = GenerationService()
    result = svc.generate(GenerationRequest(prompt="offline ok"))
    assert result.success is True
    assert result.provider == "local"


def test_service_import_surface():
    from yasinai import services
    from yasinai import contracts

    assert hasattr(services, "GenerationService")
    assert hasattr(contracts, "GenerationRequest")
    assert hasattr(contracts, "GenerationResult")


def test_generate_retries_retryable_error_then_succeeds():
    provider = _FlakyProvider("flaky", fail_times=1, retryable=True)
    reg = ProviderRegistry()
    reg.register(provider)
    svc = GenerationService(registry=reg, retry_backoff_seconds=0.0)

    result = svc.generate(GenerationRequest(prompt="hello"))
    assert result.success is True
    assert result.provider == "flaky"
    assert provider.call_count == 2  # 1 failure + 1 retry that succeeded


def test_generate_does_not_retry_non_retryable_error():
    provider = _FlakyProvider("flaky", fail_times=1, retryable=False)
    reg = ProviderRegistry()
    reg.register(provider)
    svc = GenerationService(registry=reg, retry_backoff_seconds=0.0)

    result = svc.generate(GenerationRequest(prompt="hello"))
    assert result.success is False
    assert provider.call_count == 1  # no retry attempted


def test_generate_retry_budget_is_bounded():
    provider = _AlwaysFailsProvider("stubborn", retryable=True)
    reg = ProviderRegistry()
    reg.register(provider)
    svc = GenerationService(
        registry=reg, retry_backoff_seconds=0.0, max_retries_per_provider=2, max_provider_fallbacks=0
    )

    result = svc.generate(GenerationRequest(prompt="hello"))
    assert result.success is False
    assert provider.call_count == 3  # 1 initial attempt + 2 retries, then gives up


def test_generate_falls_back_to_next_provider_when_first_exhausted():
    failing = _AlwaysFailsProvider("bad", retryable=True)
    healthy = LocalProvider()
    reg = ProviderRegistry()
    reg.register(failing)
    reg.register(healthy)
    svc = GenerationService(
        registry=reg, retry_backoff_seconds=0.0, max_retries_per_provider=1, max_provider_fallbacks=1
    )

    result = svc.generate(GenerationRequest(prompt="hello"))
    assert result.success is True
    assert result.provider == "local"
    assert failing.call_count == 2  # 1 initial + 1 retry before falling back


def test_generate_pinned_provider_is_only_retried_never_substituted():
    failing = _AlwaysFailsProvider("bad", retryable=True)
    healthy = LocalProvider()
    reg = ProviderRegistry()
    reg.register(failing)
    reg.register(healthy)
    svc = GenerationService(
        registry=reg, retry_backoff_seconds=0.0, max_retries_per_provider=1, max_provider_fallbacks=5
    )

    result = svc.generate(GenerationRequest(prompt="hello", provider="bad"))
    assert result.success is False
    assert result.provider == "bad"
    assert failing.call_count == 2  # initial + 1 retry, never touches 'healthy'


def test_generate_fallback_budget_is_bounded():
    bad1 = _AlwaysFailsProvider("bad1", retryable=False)
    bad2 = _AlwaysFailsProvider("bad2", retryable=False)
    bad3 = _AlwaysFailsProvider("bad3", retryable=False)
    reg = ProviderRegistry()
    reg.register(bad1)
    reg.register(bad2)
    reg.register(bad3)
    svc = GenerationService(registry=reg, retry_backoff_seconds=0.0, max_provider_fallbacks=1)

    result = svc.generate(GenerationRequest(prompt="hello"))
    assert result.success is False
    # Only 2 providers tried total: primary + 1 fallback (budget=1), third never touched.
    tried = bad1.call_count + bad2.call_count + bad3.call_count
    assert tried == 2
