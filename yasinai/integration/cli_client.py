"""
YasinCLI integration reference client.

YasinCLI owns the unified command-line UX. Capability work must go through
yasinai.contracts / yasinai.services (not knowledge_platform directly).
"""
from __future__ import annotations

from typing import Any

from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.contracts.knowledge import (
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.contracts.rag import RagRequest, RagResult
from yasinai.services.generation_service import GenerationService
from yasinai.services.knowledge_service import KnowledgeService
from yasinai.services.rag_service import RagService


class YasinCLIClient:
    """CLI-oriented capability client for status/memory/generate/rag bridges."""

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

    def search_memory(
        self, query: str, *, top_k: int = 5
    ) -> KnowledgeResult:
        return self._knowledge.query(
            KnowledgeQuery(
                query_type=KnowledgeQueryType.SEMANTIC,
                text=query or " ",
                top_k=top_k,
            )
        )

    def seed_demo_documents(self) -> None:
        """Deterministic demo corpus used by `yasin memory search` samples."""
        self._knowledge.add_document(
            "mem_001", "YasinAI configuration loading rules."
        )
        self._knowledge.add_document(
            "mem_002", "How to register custom modules in Core Runtime."
        )
        self._knowledge.add_document(
            "mem_003", "Security platform and identity management specs."
        )

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        return self._generation.generate(
            GenerationRequest(prompt=prompt, **kwargs)
        )

    def answer(self, question: str, **kwargs: Any) -> RagResult:
        return self._rag.run(RagRequest(query=question, **kwargs))

    def format_search_results(
        self, result: KnowledgeResult, *, threshold: float = 0.0
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for entry in result.entries or []:
            score = float(entry.score or 0.0)
            if score < threshold and threshold > 0:
                continue
            content = entry.content
            if isinstance(content, dict):
                text = content.get("text") or content.get("content") or str(content)
                doc_id = content.get("id") or entry.source or ""
            else:
                text = str(content)
                doc_id = entry.source or ""
            meta = entry.metadata or {}
            if "text" in meta:
                text = meta["text"]
            rows.append(
                {
                    "id": doc_id or meta.get("id", ""),
                    "content": text,
                    "score": round(score, 2),
                }
            )
        return rows

    def capabilities(self) -> list[str]:
        return ["memory_search", "generation", "rag"]
