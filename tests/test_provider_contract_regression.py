"""#146 — deterministic provider contract & fallback regression (no network)."""
from __future__ import annotations

import pytest

from yasinai.contracts.generation import GenerationRequest
from yasinai.providers.base import (
    GenerationRequest as ProviderGenerationRequest,
)
from yasinai.providers.base import (
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter, ProviderUnavailableError
from yasinai.services.generation_service import GenerationService


class _Stub(ProviderBase):
    def __init__(self, name: str, models: list[str], *, fail: str | None = None, retryable: bool = True):
        self._name = name
        self._models = models
        self._fail = fail
        self._retryable = retryable
        self.calls = 0

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self._name,
            capabilities=frozenset({ProviderCapability.GENERATION}),
            model_ids=list(self._models),
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: ProviderGenerationRequest) -> GenerationResponse:
        self.calls += 1
        if self._fail == "always":
            raise ProviderError(self._name, "fail", retryable=self._retryable)
        return GenerationResponse(
            text=f"ok:{self._name}:{request.prompt}",
            model=request.model or self._models[0],
            provider=self._name,
        )


def test_router_exact_model_pinning():
    reg = ProviderRegistry()
    reg.register(_Stub("a", ["model-a"]))
    reg.register(_Stub("b", ["model-b"]))
    router = ProviderRouter(reg)
    assert router.select(ProviderCapability.GENERATION, model="model-b").info.name == "b"


def test_router_unknown_model_raises_by_default():
    reg = ProviderRegistry()
    reg.register(_Stub("a", ["model-a"]))
    router = ProviderRouter(reg)
    with pytest.raises(ProviderUnavailableError):
        router.select(ProviderCapability.GENERATION, model="missing")


def test_router_allow_fallback_opt_in():
    reg = ProviderRegistry()
    reg.register(_Stub("a", ["model-a"]))
    router = ProviderRouter(reg)
    p = router.select(ProviderCapability.GENERATION, model="missing", allow_fallback=True)
    assert p.info.name == "a"


def test_service_explicit_provider_pin_no_cross_provider_fallback():
    bad = _Stub("bad", ["m1"], fail="always", retryable=False)
    good = _Stub("good", ["m1"])
    reg = ProviderRegistry()
    reg.register(bad)
    reg.register(good)
    svc = GenerationService(registry=reg, max_retries_per_provider=0, max_provider_fallbacks=3)
    result = svc.generate(GenerationRequest(prompt="hi", provider="bad", model="m1"))
    assert result.success is False
    assert good.calls == 0


def test_service_bounded_fallback_to_second_provider():
    bad = _Stub("bad", ["m1"], fail="always", retryable=False)
    good = _Stub("good", ["m1"])
    reg = ProviderRegistry()
    reg.register(bad)
    reg.register(good)
    svc = GenerationService(registry=reg, max_retries_per_provider=0, max_provider_fallbacks=1)
    result = svc.generate(GenerationRequest(prompt="hi", model="m1"))
    assert result.success is True
    assert result.provider == "good"


def test_non_retryable_error_does_not_retry_same_provider():
    p = _Stub("x", ["m"], fail="always", retryable=False)
    reg = ProviderRegistry()
    reg.register(p)
    svc = GenerationService(registry=reg, max_retries_per_provider=3, max_provider_fallbacks=0)
    result = svc.generate(GenerationRequest(prompt="hi"))
    assert result.success is False
    assert p.calls == 1


def test_provider_error_message_not_raw_http():
    err = ProviderError("openai", "OpenAI request failed with HTTP 400", retryable=False)
    assert "request failed" in str(err).lower()
    assert "{" not in str(err)
