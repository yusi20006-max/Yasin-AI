"""
Yasin-AI Provider Abstraction Layer

This package defines the provider boundary for Yasin-AI.
It contains:
  - The public ProviderBase interface (all providers implement this)
  - The ProviderRegistry (single registry, per-Runtime instance)
  - The ProviderRouter (select provider by capability/model hint)
  - Provider-specific adapters (Phase 3 — not yet implemented)

STATUS: Phase 2.6 — boundary defined.
        Phase 3 will implement concrete providers (OpenAI, Anthropic, local).

Usage (Phase 3+):
    from yasinai.providers import ProviderRegistry, ProviderRouter
    from yasinai.providers.base import ProviderBase, GenerationRequest, GenerationResponse
"""

from yasinai.providers.base import (
    ProviderBase,
    ProviderCapability,
    ProviderInfo,
    GenerationRequest,
    GenerationResponse,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter

__all__ = [
    "ProviderBase",
    "ProviderCapability",
    "ProviderInfo",
    "GenerationRequest",
    "GenerationResponse",
    "ProviderRegistry",
    "ProviderRouter",
]
