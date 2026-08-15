"""
KnowledgeService — facade over knowledge_platform for Memory & Knowledge.

Phase 2.7: reconciles Memory / Knowledge / Retrieval boundaries.
Consumers import this (or contracts) instead of knowledge_platform.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from yasinai.contracts.base import CapabilityMetadata
from yasinai.contracts.knowledge import (
    KnowledgeEntry,
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.contracts.memory import (
    MemoryEntry,
    MemoryRequest,
    MemoryResponse,
    MemoryType,
)

logger = logging.getLogger(__name__)

# Internal imports — only allowed inside the service layer
from knowledge_platform.graph import KnowledgeGraph
from knowledge_platform.memory import MemoryManager
from knowledge_platform.reasoning import KnowledgeReasoner
from knowledge_platform.semantic_search import Retriever


class KnowledgeService:
    """
    Unified facade for memory operations and knowledge queries.

    Owns (or accepts) the internal MemoryManager, KnowledgeGraph, and Retriever.
    Translates public contracts to internal APIs and back.
    """

    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        retriever: Optional[Retriever] = None,
        reasoner: Optional[KnowledgeReasoner] = None,
    ) -> None:
        self._memory = memory_manager or MemoryManager()
        self._graph = knowledge_graph or KnowledgeGraph()
        self._retriever = retriever or Retriever()
        self._reasoner = reasoner  # lazy; created on first REASONING use if None

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def memory(self, request: MemoryRequest) -> MemoryResponse:
        """Execute a memory operation described by MemoryRequest."""
        meta = CapabilityMetadata(capability="memory")
        try:
            op = request.operation
            if op == "store":
                return self._memory_store(request, meta)
            if op == "retrieve":
                return self._memory_retrieve(request, meta)
            if op == "delete":
                return self._memory_delete(request, meta)
            if op == "list":
                return self._memory_list(request, meta)
            if op == "clear":
                return self._memory_clear(request, meta)
            return MemoryResponse(
                success=False,
                error=f"Unsupported memory operation: {op}",
                meta=meta,
            )
        except Exception as exc:
            logger.exception("KnowledgeService.memory failed")
            return MemoryResponse(success=False, error=str(exc), meta=meta)

    def _memory_store(self, request: MemoryRequest, meta: CapabilityMetadata) -> MemoryResponse:
        if request.memory_type == MemoryType.SHORT_TERM:
            raw = self._memory.add_short_term(request.content, request.metadata or None)
            entry = MemoryEntry(
                content=raw["content"],
                timestamp=raw["timestamp"],
                key=None,
                metadata=raw.get("metadata") or {},
            )
            return MemoryResponse(success=True, entry=entry, meta=meta)

        # LONG_TERM
        raw = self._memory.add_long_term(
            request.key,  # type: ignore[arg-type]
            request.content,
            request.metadata or None,
        )
        entry = MemoryEntry(
            content=raw["content"],
            timestamp=raw["timestamp"],
            key=raw.get("key") or request.key,
            metadata=raw.get("metadata") or {},
        )
        return MemoryResponse(success=True, entry=entry, meta=meta)

    def _memory_retrieve(self, request: MemoryRequest, meta: CapabilityMetadata) -> MemoryResponse:
        if request.memory_type == MemoryType.SHORT_TERM:
            raws = self._memory.get_short_term(limit=request.limit)
            entries = [
                MemoryEntry(
                    content=r["content"],
                    timestamp=r["timestamp"],
                    key=None,
                    metadata=r.get("metadata") or {},
                )
                for r in raws
            ]
            return MemoryResponse(success=True, entries=entries, meta=meta)

        raw = self._memory.get_long_term(request.key)  # type: ignore[arg-type]
        if raw is None:
            return MemoryResponse(success=True, entry=None, meta=meta)
        entry = MemoryEntry(
            content=raw["content"],
            timestamp=raw["timestamp"],
            key=raw.get("key") or request.key,
            metadata=raw.get("metadata") or {},
        )
        return MemoryResponse(success=True, entry=entry, meta=meta)

    def _memory_delete(self, request: MemoryRequest, meta: CapabilityMetadata) -> MemoryResponse:
        if request.memory_type == MemoryType.SHORT_TERM:
            # Short-term has no key-based delete in the underlying manager;
            # clear is the supported bulk operation.
            return MemoryResponse(
                success=False,
                error="Short-term memory does not support key-based delete; use clear",
                meta=meta,
            )
        deleted = self._memory.delete_long_term(request.key)  # type: ignore[arg-type]
        return MemoryResponse(success=True, deleted=bool(deleted), meta=meta)

    def _memory_list(self, request: MemoryRequest, meta: CapabilityMetadata) -> MemoryResponse:
        if request.memory_type == MemoryType.SHORT_TERM:
            raws = self._memory.get_short_term(limit=request.limit)
            entries = [
                MemoryEntry(
                    content=r["content"],
                    timestamp=r["timestamp"],
                    key=None,
                    metadata=r.get("metadata") or {},
                )
                for r in raws
            ]
            return MemoryResponse(success=True, entries=entries, meta=meta)

        # list all long-term via the underlying store
        raws = self._memory.long_term.list_all()
        entries = [
            MemoryEntry(
                content=r["content"],
                timestamp=r["timestamp"],
                key=r.get("key"),
                metadata=r.get("metadata") or {},
            )
            for r in raws
        ]
        if request.limit is not None:
            entries = entries[: request.limit]
        return MemoryResponse(success=True, entries=entries, meta=meta)

    def _memory_clear(self, request: MemoryRequest, meta: CapabilityMetadata) -> MemoryResponse:
        if request.memory_type == MemoryType.SHORT_TERM:
            self._memory.short_term.clear()
        elif request.memory_type == MemoryType.LONG_TERM:
            self._memory.long_term.clear()
        else:
            self._memory.clear_all()
        return MemoryResponse(success=True, meta=meta)

    # ------------------------------------------------------------------
    # Knowledge / Retrieval / Reasoning
    # ------------------------------------------------------------------

    def query(self, request: KnowledgeQuery) -> KnowledgeResult:
        """Execute a knowledge query described by KnowledgeQuery."""
        meta = CapabilityMetadata(capability="knowledge")
        try:
            qt = request.query_type
            if qt == KnowledgeQueryType.SEMANTIC:
                return self._query_semantic(request, meta)
            if qt == KnowledgeQueryType.GRAPH:
                return self._query_graph(request, meta)
            if qt == KnowledgeQueryType.TRIPLE:
                return self._query_triple(request, meta)
            if qt == KnowledgeQueryType.REASONING:
                return self._query_reasoning(request, meta)
            return KnowledgeResult(
                success=False,
                error=f"Unsupported query_type: {qt}",
                meta=meta,
            )
        except Exception as exc:
            logger.exception("KnowledgeService.query failed")
            return KnowledgeResult(success=False, error=str(exc), meta=meta)

    def _query_semantic(self, request: KnowledgeQuery, meta: CapabilityMetadata) -> KnowledgeResult:
        results = self._retriever.retrieve(request.text, limit=request.top_k)  # type: ignore[arg-type]
        entries: List[KnowledgeEntry] = []
        for item in results:
            # Retriever returns dicts or objects depending on implementation
            if isinstance(item, dict):
                content = item.get("content") or item.get("text") or item
                score = float(item.get("score", 1.0))
                source = item.get("source") or item.get("id")
                md = item.get("metadata") or {}
            else:
                content = getattr(item, "content", None) or getattr(item, "text", item)
                score = float(getattr(item, "score", 1.0))
                source = getattr(item, "source", None) or getattr(item, "id", None)
                md = getattr(item, "metadata", {}) or {}
            entries.append(
                KnowledgeEntry(content=content, score=score, source=source, metadata=md)
            )
        return KnowledgeResult(success=True, entries=entries, meta=meta)

    def _query_graph(self, request: KnowledgeQuery, meta: CapabilityMetadata) -> KnowledgeResult:
        neighbors = self._graph.query_engine.find_neighbors(request.subject)  # type: ignore[arg-type]
        entries = [
            KnowledgeEntry(
                content={"relation": rel, "entity": entity},
                score=1.0,
                source="graph",
                metadata={"subject": request.subject},
            )
            for rel, entity in neighbors
        ]
        return KnowledgeResult(success=True, entries=entries, meta=meta)

    def _query_triple(self, request: KnowledgeQuery, meta: CapabilityMetadata) -> KnowledgeResult:
        triples = self._graph.triple_store.query_triples(
            subject=request.subject,
            predicate=request.predicate,
        )
        entries = [
            KnowledgeEntry(
                content={"subject": s, "predicate": p, "object": o},
                score=1.0,
                source="triple_store",
            )
            for s, p, o in triples
        ]
        return KnowledgeResult(success=True, entries=entries, meta=meta)

    def _query_reasoning(self, request: KnowledgeQuery, meta: CapabilityMetadata) -> KnowledgeResult:
        if self._reasoner is None:
            self._reasoner = KnowledgeReasoner(self._graph)
        results: List[Any] = []
        # Prefer transitive deduction when a relation is supplied
        if request.relation and hasattr(self._reasoner, "deduce_transitive_relations"):
            try:
                results = self._reasoner.deduce_transitive_relations(
                    request.subject, request.relation  # type: ignore[arg-type]
                )
            except TypeError:
                # Signature may accept only the graph; fall back to neighbors
                results = []
        if not results:
            neighbors = self._graph.query_engine.find_neighbors(request.subject)  # type: ignore[arg-type]
            results = [
                {"relation": rel, "entity": ent}
                for rel, ent in neighbors
                if request.relation is None or rel == request.relation
            ]

        entries = [
            KnowledgeEntry(
                content=r if isinstance(r, dict) else {"value": r},
                score=1.0,
                source="reasoner",
                metadata={"subject": request.subject, "relation": request.relation},
            )
            for r in (results or [])
        ]
        return KnowledgeResult(success=True, entries=entries, meta=meta)

    # ------------------------------------------------------------------
    # Convenience helpers used by tests / internal callers
    # ------------------------------------------------------------------

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Index a document into the semantic retriever."""
        self._retriever.add_document(doc_id, text, metadata or {})

    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """Add a triple to the knowledge graph."""
        self._graph.add_triple(subject, predicate, obj)
