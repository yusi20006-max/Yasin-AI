"""
GenerationService — facade over ProviderRouter for text generation.

Phase 3.2: consumers call this (or contracts) instead of yasinai.providers.
"""
from __future__ import annotations

import logging
import time
from typing import List, Optional

from yasinai.contracts.base import CapabilityMetadata
from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.providers.base import (
    GenerationRequest as ProviderGenerationRequest,
)
from yasinai.providers.base import (
    ProviderBase,
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
        max_retries_per_provider: int = 1,
        retry_backoff_seconds: float = 0.1,
        max_provider_fallbacks: int = 2,
    ) -> None:
        self._registry = registry if registry is not None else build_default_registry()
        self._router = router if router is not None else ProviderRouter(self._registry)
        self._default_capability = default_capability
        self._max_retries_per_provider = max(0, max_retries_per_provider)
        self._retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self._max_provider_fallbacks = max(0, max_provider_fallbacks)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Execute a generation request; always returns GenerationResult.

        Retries the selected provider on retryable errors (bounded by
        max_retries_per_provider, with a short backoff between attempts).
        If a provider is exhausted and the caller did not pin a specific
        provider name, falls back to the next available candidate for the
        capability (bounded by max_provider_fallbacks). A caller-pinned
        provider (request.provider set) is only retried, never substituted.
        """
        meta = CapabilityMetadata(capability="generation")
        internal = ProviderGenerationRequest(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            stop_sequences=list(request.stop_sequences or []),
            metadata=dict(request.metadata or {}),
        )

        try:
            candidates = self._candidate_providers(request)
        except ProviderUnavailableError as exc:
            logger.warning("Generation unavailable: %s", exc)
            return GenerationResult(success=False, error=str(exc), meta=meta)

        pinned = bool(request.provider)
        fallbacks_used = 0
        last_error: Optional[ProviderError] = None

        for candidate in candidates:
            attempt = 0
            while True:
                try:
                    response = candidate.generate(internal)
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
                except ProviderError as exc:
                    last_error = exc
                    if exc.retryable and attempt < self._max_retries_per_provider:
                        attempt += 1
                        logger.warning(
                            "Provider '%s' failed (retryable), attempt %d/%d: %s",
                            candidate.info.name, attempt, self._max_retries_per_provider, exc,
                        )
                        if self._retry_backoff_seconds:
                            time.sleep(self._retry_backoff_seconds * attempt)
                        continue
                    logger.warning(
                        "Provider '%s' failed (retryable=%s), giving up on this provider: %s",
                        candidate.info.name, exc.retryable, exc,
                    )
                    break
                except Exception as exc:
                    logger.exception("GenerationService.generate failed")
                    return GenerationResult(success=False, error=str(exc), meta=meta)

            if pinned or fallbacks_used >= self._max_provider_fallbacks:
                break
            fallbacks_used += 1

        assert last_error is not None  # candidates is non-empty, loop always sets this on failure
        return GenerationResult(
            success=False,
            error=str(last_error),
            provider=getattr(last_error, "provider", None),
            meta=CapabilityMetadata(
                capability="generation",
                provider=getattr(last_error, "provider", None),
            ),
        )

    def _candidate_providers(self, request: GenerationRequest) -> List[ProviderBase]:
        """Return an ordered list of providers to try for this request.

        A caller-pinned request.provider yields exactly one candidate (no
        substitution). Otherwise, returns available providers for the
        capability ordered by the router's selection policy, so fallback
        tries alternates in the same order the router would prefer them.
        """
        if request.provider:
            named = self._registry.get(request.provider)
            if named is None or not named.is_available():
                raise ProviderUnavailableError(self._default_capability, request.model)
            return [named]

        # Prime the ordered candidate list via the router (respects model
        # hint matching), then include any other available providers for
        # this capability as further fallback candidates.
        primary = self._router.select(self._default_capability, model=request.model)
        rest = [
            p for p in self._registry.available_for_capability(self._default_capability)
            if p is not primary
        ]
        return [primary, *rest]

    @property
    def registry(self) -> ProviderRegistry:
        return self._registry
