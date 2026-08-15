"""
Yasin-Agent integration reference client.

Yasin-Agent owns planning and workflows. It must call Yasin-AI only via:
  - yasinai.contracts.*
  - yasinai.services.*

This module is a reference implementation / smoke harness for that boundary.
"""
from __future__ import annotations

from typing import Any

from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.contracts.knowledge import (
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.contracts.memory import MemoryRequest, MemoryResponse, MemoryType
from yasinai.contracts.rag import RagRequest, RagResult
from yasinai.services.generation_service import GenerationService
from yasinai.services.knowledge_service import KnowledgeService
from yasinai.services.rag_service import RagService


class YasinAgentClient:
    """
    Thin client surface intended for Yasin-Agent processes.

    Owns no provider credentials or internal platform imports.
    """

    def __init__(
        self,
        *,
        knowledge: KnowledgeService | None = None,
        generation: GenerationService | None = None,
        rag: RagService | None = None,
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

    # --- Memory (session / episodic) ---

    def remember(
        self,
        content: Any,
        *,
        key: str | None = None,
        long_term: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryResponse:
        mem_type = MemoryType.LONG_TERM if long_term else MemoryType.SHORT_TERM
        return self._knowledge.memory(
            MemoryRequest(
                operation="store",
                content=content,
                key=key,
                memory_type=mem_type,
                metadata=metadata or {},
            )
        )

    def recall(
        self,
        *,
        key: str | None = None,
        long_term: bool = False,
        limit: int | None = None,
    ) -> MemoryResponse:
        mem_type = MemoryType.LONG_TERM if long_term else MemoryType.SHORT_TERM
        return self._knowledge.memory(
            MemoryRequest(
                operation="retrieve",
                key=key,
                memory_type=mem_type,
                limit=limit,
            )
        )

    # --- Knowledge / retrieval ---

    def search(self, text: str, *, top_k: int = 5) -> KnowledgeResult:
        return self._knowledge.query(
            KnowledgeQuery(
                query_type=KnowledgeQueryType.SEMANTIC,
                text=text,
                top_k=top_k,
            )
        )

    def index_document(
        self, doc_id: str, text: str, metadata: dict[str, Any] | None = None
    ) -> None:
        self._knowledge.add_document(doc_id, text, metadata or {})

    # --- Generation ---

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> GenerationResult:
        return self._generation.generate(
            GenerationRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                provider=provider,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )

    # --- RAG (typical agent answer path) ---

    def answer(
        self,
        question: str,
        *,
        top_k: int = 5,
        include_memory: bool = True,
        model: str | None = None,
        provider: str | None = None,
    ) -> RagResult:
        return self._rag.run(
            RagRequest(
                query=question,
                top_k=top_k,
                include_memory=include_memory,
                model=model,
                provider=provider,
            )
        )

    def capabilities(self) -> list[str]:
        """Stable capability names Yasin-Agent may depend on."""
        return ["memory", "knowledge", "generation", "rag"]
