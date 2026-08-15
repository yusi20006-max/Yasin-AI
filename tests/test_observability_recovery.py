"""#151 — observability primitives and failure-recovery behaviors."""
from __future__ import annotations

import logging

from observability import Counter, MetricsRegistry, Timer
from yasinai.contracts.base import ObservabilityContext
from yasinai.contracts.generation import GenerationRequest
from yasinai.providers.base import (
    GenerationRequest as PReq,
)
from yasinai.providers.base import (
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.services.generation_service import GenerationService


def test_metrics_registry_counter_and_timer():
    reg = MetricsRegistry()
    c = reg.counter("calls")
    t = reg.timer("latency")
    assert isinstance(c, Counter)
    assert isinstance(t, Timer)
    assert c.inc() == 1
    t.observe(0.01)
    assert t.count == 1


def test_observability_context_on_request():
    ctx = ObservabilityContext(trace_id="req-1", caller="test")
    req = GenerationRequest(prompt="hi", context=ctx)
    assert req.context is not None
    assert req.context.trace_id == "req-1"


def test_generation_recovery_from_retryable_failure():
    class Flaky(ProviderBase):
        def __init__(self):
            self.n = 0

        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(
                name="flaky",
                capabilities=frozenset({ProviderCapability.GENERATION}),
                model_ids=["m"],
            )

        def is_available(self) -> bool:
            return True

        def _generate(self, request: PReq) -> GenerationResponse:
            self.n += 1
            if self.n == 1:
                raise ProviderError("flaky", "temp", retryable=True)
            return GenerationResponse(text="recovered", model="m", provider="flaky")

    reg = ProviderRegistry()
    reg.register(Flaky())
    svc = GenerationService(registry=reg, retry_backoff_seconds=0.0, max_retries_per_provider=2)
    result = svc.generate(GenerationRequest(prompt="x"))
    assert result.success is True
    assert result.text == "recovered"


def test_sensitive_data_not_in_generation_error(caplog):
    class Boom(ProviderBase):
        @property
        def info(self) -> ProviderInfo:
            return ProviderInfo(
                name="boom",
                capabilities=frozenset({ProviderCapability.GENERATION}),
                model_ids=["m"],
            )

        def is_available(self) -> bool:
            return True

        def _generate(self, request: PReq) -> GenerationResponse:
            raise RuntimeError("token=SUPERSECRET")

    reg = ProviderRegistry()
    reg.register(Boom())
    svc = GenerationService(registry=reg)
    with caplog.at_level(logging.ERROR):
        result = svc.generate(GenerationRequest(prompt="x"))
    assert result.success is False
    assert "SUPERSECRET" not in (result.error or "")
