"""
YasinFeed integration reference client.

YasinFeed owns feed/timeline aggregation. It uses Yasin-AI for ranking
hints and short summaries via contracts/services only.
"""
from __future__ import annotations

from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.contracts.knowledge import (
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.services.generation_service import GenerationService
from yasinai.services.knowledge_service import KnowledgeService


class YasinFeedClient:
    """Feed-oriented ranking/search + card summary generation."""

    def __init__(
        self,
        *,
        knowledge: KnowledgeService | None = None,
        generation: GenerationService | None = None,
    ) -> None:
        self._knowledge = knowledge if knowledge is not None else KnowledgeService()
        self._generation = (
            generation if generation is not None else GenerationService()
        )

    def rank(self, topic: str, *, top_k: int = 10) -> KnowledgeResult:
        return self._knowledge.query(
            KnowledgeQuery(
                query_type=KnowledgeQueryType.SEMANTIC,
                text=topic,
                top_k=top_k,
            )
        )

    def index_item(self, item_id: str, text: str) -> None:
        self._knowledge.add_document(item_id, text)

    def summarize_card(
        self,
        text: str,
        *,
        provider: str | None = None,
        max_tokens: int = 256,
    ) -> GenerationResult:
        return self._generation.generate(
            GenerationRequest(
                prompt=f"Write a short feed card summary:\n{text}",
                provider=provider,
                max_tokens=max_tokens,
                system_prompt="You write concise feed cards for YasinFeed.",
            )
        )

    def capabilities(self) -> list[str]:
        return ["rank", "index_item", "summarize_card"]
