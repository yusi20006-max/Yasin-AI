"""
Provider factory helpers — register default adapters into a registry.

Does not import any third-party SDK at module level.
"""
from __future__ import annotations

from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.local_provider import LocalProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.registry import ProviderRegistry


def register_default_providers(
    registry: ProviderRegistry,
    *,
    include_local: bool = True,
    include_openai: bool = True,
    include_anthropic: bool = True,
    overwrite: bool = False,
) -> ProviderRegistry:
    """
    Register built-in providers. Availability is determined at call time
    via each provider's ``is_available()`` (env keys).
    """
    if include_local:
        registry.register(LocalProvider(), overwrite=overwrite)
    if include_openai:
        registry.register(OpenAIProvider(), overwrite=overwrite)
    if include_anthropic:
        registry.register(AnthropicProvider(), overwrite=overwrite)
    return registry


def build_default_registry(**kwargs) -> ProviderRegistry:
    """Create a new registry and register default providers."""
    return register_default_providers(ProviderRegistry(), **kwargs)
