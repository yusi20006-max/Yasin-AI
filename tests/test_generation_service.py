"""Tests for Generation contract + GenerationService (Phase 3.2)."""
from __future__ import annotations

import pytest

from yasinai.contracts import GenerationRequest, GenerationResult, ContractViolationError
from yasinai.providers import LocalProvider, OpenAIProvider, ProviderRegistry
from yasinai.services import GenerationService


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
