"""
YasinHub integration reference client.

YasinHub owns control-plane concerns and global observability. It consumes
Yasin-AI capabilities via contracts/services and may attach metrics for
Hub telemetry export.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from observability.metrics import MetricsRegistry

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


class YasinHubClient:
    """
    Hub-oriented surface: AI capability calls + metrics snapshot for control plane.
    """

    def __init__(
        self,
        *,
        knowledge: Optional[KnowledgeService] = None,
        generation: Optional[GenerationService] = None,
        rag: Optional[RagService] = None,
        metrics: Optional[MetricsRegistry] = None,
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
        self._metrics = metrics if metrics is not None else MetricsRegistry()

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> GenerationResult:
        self._metrics.counter("hub.generation.requests").inc()
        timer = self._metrics.timer("hub.generation.latency")
        from time import monotonic

        start = monotonic()
        result = self._generation.generate(
            GenerationRequest(
                prompt=prompt,
                model=model,
                provider=provider,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )
        timer.observe(monotonic() - start)
        if result.success:
            self._metrics.counter("hub.generation.success").inc()
        else:
            self._metrics.counter("hub.generation.errors").inc()
        return result

    def query_knowledge(
        self, text: str, *, top_k: int = 5
    ) -> KnowledgeResult:
        self._metrics.counter("hub.knowledge.requests").inc()
        result = self._knowledge.query(
            KnowledgeQuery(
                query_type=KnowledgeQueryType.SEMANTIC,
                text=text,
                top_k=top_k,
            )
        )
        if result.success:
            self._metrics.counter("hub.knowledge.success").inc()
        else:
            self._metrics.counter("hub.knowledge.errors").inc()
        return result

    def rag(
        self,
        query: str,
        *,
        top_k: int = 5,
        include_memory: bool = False,
        provider: Optional[str] = None,
    ) -> RagResult:
        self._metrics.counter("hub.rag.requests").inc()
        from time import monotonic

        start = monotonic()
        result = self._rag.run(
            RagRequest(
                query=query,
                top_k=top_k,
                include_memory=include_memory,
                provider=provider,
            )
        )
        self._metrics.timer("hub.rag.latency").observe(monotonic() - start)
        if result.success:
            self._metrics.counter("hub.rag.success").inc()
        else:
            self._metrics.counter("hub.rag.errors").inc()
        return result

    def metrics_snapshot(self) -> Dict[str, Any]:
        """Export counters/timers for YasinHub control-plane telemetry."""
        return self._metrics.snapshot()

    def capabilities(self) -> list:
        return ["generation", "knowledge", "rag", "metrics"]
