"""
Provider Router — selects the best available provider for a capability.

Routing policy:
  1. If model hint is given, select the provider whose model_ids contain it.
  2. If model is given and no provider lists it: raise ProviderUnavailableError
     unless allow_fallback=True (opt-in best-effort).
  3. If no model hint, return the first available provider for the capability.
  4. If none available, raise ProviderUnavailableError.
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
        *,
        allow_fallback: bool = False,
    ) -> ProviderBase:
        """
        Select an available provider for ``capability``.

        Args:
            capability: Required provider capability.
            model: Optional model id hint. When set, only a provider that lists
                this id in ``info.model_ids`` is selected unless
                ``allow_fallback`` is True.
            allow_fallback: If True and ``model`` has no exact match, use the
                first available provider for the capability (best-effort).
                Default False — raise ``ProviderUnavailableError`` on mismatch.

        Raises:
            ProviderUnavailableError: No available provider, or model mismatch
                without ``allow_fallback``.
        """
        candidates = self._registry.available_for_capability(capability)

        if not candidates:
            raise ProviderUnavailableError(capability, model)

        if model:
            for provider in candidates:
                if model in provider.info.model_ids:
                    logger.debug(
                        "Router: selected '%s' for capability=%s model=%s",
                        provider.info.name, capability.value, model,
                    )
                    return provider
            if not allow_fallback:
                logger.debug(
                    "Router: no provider lists model '%s' for capability=%s",
                    model, capability.value,
                )
                raise ProviderUnavailableError(capability, model)
            logger.debug(
                "Router: no exact model match for '%s'; fallback to first available '%s'",
                model, candidates[0].info.name,
            )

        logger.debug(
            "Router: selected '%s' for capability=%s",
            candidates[0].info.name, capability.value,
        )
        return candidates[0]
