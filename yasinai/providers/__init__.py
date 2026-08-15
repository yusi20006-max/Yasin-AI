"""
Yasin-AI Provider Abstraction Layer

This package defines the provider boundary for Yasin-AI.
It contains:
  - The public ProviderBase interface (all providers implement this)
  - The ProviderRegistry (single registry, per-Runtime instance)
  - The ProviderRouter (select provider by capability/model hint)
  - Concrete adapters: OpenAI, Anthropic, Local (Phase 3.1)

STATUS: Phase 3.1 — concrete providers implemented.

Usage:
    from yasinai.providers import ProviderRegistry, ProviderRouter, build_default_registry
    from yasinai.providers.base import GenerationRequest, GenerationResponse
"""

from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)
from yasinai.providers.factory import build_default_registry, register_default_providers
from yasinai.providers.local_provider import LocalProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter

__all__ = [
    "AnthropicProvider",
    "GenerationRequest",
    "GenerationResponse",
    "LocalProvider",
    "OpenAIProvider",
    "ProviderBase",
    "ProviderCapability",
    "ProviderError",
    "ProviderInfo",
    "ProviderRegistry",
    "ProviderRouter",
    "build_default_registry",
    "register_default_providers",
]
