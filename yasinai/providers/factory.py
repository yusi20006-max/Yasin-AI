"""Provider factory helpers — register built-in and runtime providers."""
from __future__ import annotations

from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.config_store import ProviderConfigError, ProviderStore
from yasinai.providers.generic_openai import GenericOpenAIProvider
from yasinai.providers.local_provider import LocalProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.registry import ProviderRegistry


def register_default_providers(
    registry: ProviderRegistry,
    *,
    include_local: bool = True,
    include_openai: bool = True,
    include_anthropic: bool = True,
    include_configured: bool = True,
    overwrite: bool = False,
) -> ProviderRegistry:
    """Register built-in providers and optional user-configured providers."""
    if include_local:
        registry.register(LocalProvider(), overwrite=overwrite)
    if include_openai:
        registry.register(OpenAIProvider(), overwrite=overwrite)
    if include_anthropic:
        registry.register(AnthropicProvider(), overwrite=overwrite)

    if include_configured:
        try:
            store = ProviderStore()
            for item in store.list():
                config = store.get(item["name"])
                if config is None:
                    continue
                registry.register(
                    GenericOpenAIProvider(
                        name=config["name"],
                        base_url=config["base_url"],
                        api_key=config["api_key"],
                        default_model=config["model"],
                    ),
                    overwrite=overwrite,
                )
        except ProviderConfigError:
            # Configured providers are optional. Existing env-based providers
            # must continue to work when no master key/configuration exists.
            pass

    return registry


def build_default_registry(**kwargs) -> ProviderRegistry:
    """Create a new registry and register default providers."""
    return register_default_providers(ProviderRegistry(), **kwargs)
