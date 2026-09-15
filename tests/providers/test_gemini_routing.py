from __future__ import annotations

from yasinai.providers.factory import build_default_registry
from yasinai.providers.router import ProviderRouter
from yasinai.providers.base import ProviderCapability


def test_configured_gemini_is_first_available_provider(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    registry = build_default_registry(
        include_openai=False,
        include_anthropic=False,
        include_configured=False,
    )
    selected = ProviderRouter(registry).select(ProviderCapability.GENERATION)
    assert selected.info.name == "gemini"
