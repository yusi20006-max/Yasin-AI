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

from yasinai.providers.base import (
    ProviderBase,
    ProviderCapability,
    ProviderInfo,
    GenerationRequest,
    GenerationResponse,
    ProviderError,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter
from yasinai.providers.factory import build_default_registry, register_default_providers
from yasinai.providers.local_provider import LocalProvider
from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.anthropic_provider import AnthropicProvider

__all__ = [
    "ProviderBase",
    "ProviderCapability",
    "ProviderInfo",
    "GenerationRequest",
    "GenerationResponse",
    "ProviderError",
    "ProviderRegistry",
    "ProviderRouter",
    "LocalProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "build_default_registry",
    "register_default_providers",
]
