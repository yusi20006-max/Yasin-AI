"""
YasinPress integration reference client.

YasinPress owns publishing/editorial workflows. It uses Yasin-AI for
draft assistance and grounded fact lookup via contracts/services only.
"""
from __future__ import annotations

from typing import List, Optional

from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.contracts.rag import RagRequest, RagResult
from yasinai.services.generation_service import GenerationService
from yasinai.services.knowledge_service import KnowledgeService
from yasinai.services.rag_service import RagService


class YasinPressClient:
    """Editorial helpers: draft, revise, grounded research."""

    def __init__(
        self,
        *,
        knowledge: Optional[KnowledgeService] = None,
        generation: Optional[GenerationService] = None,
        rag: Optional[RagService] = None,
    ) -> None:
        self._knowledge = knowledge if knowledge is not None else KnowledgeService()
        self._generation = (
            generation if generation is not None else GenerationService()
        )
        self._rag = (
            rag
            if rag is not None
            else RagService(knowledge=self._knowledge, generation=self._generation)
        )

    def draft(
        self,
        brief: str,
        *,
        provider: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> GenerationResult:
        return self._generation.generate(
            GenerationRequest(
                prompt=brief,
                provider=provider,
                max_tokens=max_tokens,
                system_prompt="You are an editorial assistant for YasinPress.",
            )
        )

    def research(
        self,
        question: str,
        *,
        top_k: int = 5,
        provider: Optional[str] = None,
    ) -> RagResult:
        return self._rag.run(
            RagRequest(
                query=question,
                top_k=top_k,
                provider=provider,
                include_memory=False,
                system_prompt="Answer for editorial fact-checking. Cite context.",
            )
        )

    def index_source(self, source_id: str, text: str) -> None:
        self._knowledge.add_document(source_id, text)

    def capabilities(self) -> List[str]:
        return ["draft", "research", "index_source"]
