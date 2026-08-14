"""
Provider Router — selects the best available provider for a capability.

Routing policy (Phase 2.6):
  1. If model hint is given, prefer the provider whose model_ids contain it.
  2. Otherwise, return the first available provider for the capability.
  3. If none available, raise ProviderUnavailableError.

Phase 3 will extend this with priority weights, cost routing, and
fallback chains defined in configuration.
"""
from __future__ import annotations

import logging
from typing import Optional

from yasinai.providers.base import ProviderBase, ProviderCapability, ProviderError
from yasinai.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class ProviderUnavailableError(ProviderError):
    """Raised when no provider is available for the requested capability."""
    def __init__(self, capability: ProviderCapability, model: Optional[str] = None) -> None:
        msg = f"No available provider for capability '{capability.value}'"
        if model:
            msg += f" with model hint '{model}'"
        super().__init__(provider="router", message=msg, retryable=False)
        self.capability = capability
        self.model = model


class ProviderRouter:
    """
    Selects a provider for a given capability + optional model hint.

    Usage:
        router = ProviderRouter(registry)
        provider = router.select(ProviderCapability.GENERATION, model="gpt-4o")
        response = provider.generate(request)
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def select(
        self,
        capability: ProviderCapability,
        model: Optional[str] = None,
    ) -> ProviderBase:
        candidates = self._registry.available_for_capability(capability)

        if not candidates:
            raise ProviderUnavailableError(capability, model)

        if model:
            # Prefer a provider that explicitly lists this model_id
            for provider in candidates:
                if model in provider.info.model_ids:
                    logger.debug(
                        "Router: selected '%s' for capability=%s model=%s",
                        provider.info.name, capability.value, model,
                    )
                    return provider
            # Fall through: use first available if no exact model match
            logger.debug(
                "Router: no exact model match for '%s'; using first available provider '%s'",
                model, candidates[0].info.name,
            )

        logger.debug(
            "Router: selected '%s' for capability=%s",
            candidates[0].info.name, capability.value,
        )
        return candidates[0]
