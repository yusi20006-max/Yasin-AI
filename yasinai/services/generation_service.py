"""
GenerationService — facade over ProviderRouter for text generation.

Phase 3.2: consumers call this (or contracts) instead of yasinai.providers.
"""
from __future__ import annotations

import logging
from typing import Optional

from yasinai.contracts.base import CapabilityMetadata
from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.providers.base import (
    GenerationRequest as ProviderGenerationRequest,
    ProviderCapability,
    ProviderError,
)
from yasinai.providers.factory import build_default_registry
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter, ProviderUnavailableError

logger = logging.getLogger(__name__)


class GenerationService:
    """
    Public generation facade.

    Routes GenerationRequest contracts through ProviderRouter to a concrete
    provider adapter. Never imports provider SDKs.
    """

    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        router: Optional[ProviderRouter] = None,
        *,
        default_capability: ProviderCapability = ProviderCapability.GENERATION,
    ) -> None:
        self._registry = registry or build_default_registry()
        self._router = router or ProviderRouter(self._registry)
        self._default_capability = default_capability

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Execute a generation request; always returns GenerationResult."""
        meta = CapabilityMetadata(capability="generation")
        try:
            provider = self._select_provider(request)
            internal = ProviderGenerationRequest(
                prompt=request.prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system_prompt=request.system_prompt,
                stop_sequences=list(request.stop_sequences or []),
                metadata=dict(request.metadata or {}),
            )
            response = provider.generate(internal)
            return GenerationResult(
                success=True,
                text=response.text,
                model=response.model,
                provider=response.provider,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                finish_reason=response.finish_reason,
                meta=CapabilityMetadata(
                    capability="generation",
                    provider=response.provider,
                ),
            )
        except ProviderUnavailableError as exc:
            logger.warning("Generation unavailable: %s", exc)
            return GenerationResult(
                success=False,
                error=str(exc),
                meta=meta,
            )
        except ProviderError as exc:
            logger.warning("Provider error: %s", exc)
            return GenerationResult(
                success=False,
                error=str(exc),
                provider=getattr(exc, "provider", None),
                meta=CapabilityMetadata(
                    capability="generation",
                    provider=getattr(exc, "provider", None),
                ),
            )
        except Exception as exc:  # noqa: BLE001 — facade must not leak
            logger.exception("GenerationService.generate failed")
            return GenerationResult(success=False, error=str(exc), meta=meta)

    def _select_provider(self, request: GenerationRequest):
        if request.provider:
            named = self._registry.get(request.provider)
            if named is None:
                raise ProviderUnavailableError(
                    self._default_capability, request.model
                )
            if not named.is_available():
                raise ProviderUnavailableError(
                    self._default_capability, request.model
                )
            return named
        return self._router.select(self._default_capability, model=request.model)

    @property
    def registry(self) -> ProviderRegistry:
        return self._registry
