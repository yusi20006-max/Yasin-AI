"""
YasinRelay integration reference client.

YasinRelay owns message/event relay paths. It uses Yasin-AI for optional
enrichment (generation / RAG) without importing internal platforms.
"""
from __future__ import annotations

from typing import Optional

from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.contracts.rag import RagRequest, RagResult
from yasinai.services.generation_service import GenerationService
from yasinai.services.rag_service import RagService


class YasinRelayClient:
    """Relay-oriented enrichment: summarize/transform payloads via generation or RAG."""

    def __init__(
        self,
        *,
        generation: Optional[GenerationService] = None,
        rag: Optional[RagService] = None,
    ) -> None:
        self._generation = (
            generation if generation is not None else GenerationService()
        )
        self._rag = rag if rag is not None else RagService(generation=self._generation)

    def enrich(
        self,
        payload: str,
        *,
        instruction: str = "Summarize for relay delivery.",
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> GenerationResult:
        prompt = f"{instruction}\n\nPayload:\n{payload}"
        return self._generation.generate(
            GenerationRequest(
                prompt=prompt,
                provider=provider,
                model=model,
                system_prompt="You assist YasinRelay message enrichment.",
            )
        )

    def grounded_enrich(
        self,
        query: str,
        *,
        top_k: int = 3,
        provider: Optional[str] = None,
    ) -> RagResult:
        return self._rag.run(
            RagRequest(query=query, top_k=top_k, provider=provider, include_memory=False)
        )

    def capabilities(self) -> list:
        return ["enrich", "grounded_enrich"]
