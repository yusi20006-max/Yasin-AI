"""
Knowledge Capability Contract v1

Stable interface for knowledge graph queries and semantic retrieval.
Backed by knowledge_platform — consumers must not import that directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from yasinai.contracts.base import (
    CapabilityMetadata,
    ContractViolationError,
    ObservabilityContext,
)


class KnowledgeQueryType(str, Enum):
    SEMANTIC = "semantic"       # TF-IDF / vector similarity search
    GRAPH = "graph"             # Knowledge graph traversal
    TRIPLE = "triple"           # Subject / predicate / object lookup
    REASONING = "reasoning"     # Transitive deduction over graph


@dataclass(frozen=True)
class KnowledgeQuery:
    """
    Input contract for a knowledge retrieval operation.

    Attributes:
        query_type:  Type of retrieval to perform
        text:        Natural-language or keyword query (SEMANTIC)
        subject:     Entity name for GRAPH / TRIPLE queries
        predicate:   Relation name for TRIPLE queries
        relation:    Relation name for REASONING (transitive)
        top_k:       Max results for SEMANTIC queries (default 5)
        metadata:    Caller-supplied context
        context:     Observability tracing context
    """

    query_type: KnowledgeQueryType
    text: Optional[str] = None
    subject: Optional[str] = None
    predicate: Optional[str] = None
    relation: Optional[str] = None
    top_k: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ObservabilityContext] = None

    TOP_K_LIMIT = 100

    def __post_init__(self) -> None:
        if self.top_k < 1:
            raise ContractViolationError("KnowledgeQuery: 'top_k' must be >= 1")
        if self.top_k > self.TOP_K_LIMIT:
            raise ContractViolationError(
                f"KnowledgeQuery: 'top_k' must be <= {self.TOP_K_LIMIT}"
            )
        if self.query_type == KnowledgeQueryType.SEMANTIC and not self.text:
            raise ContractViolationError(
                "KnowledgeQuery: SEMANTIC query requires 'text'"
            )
        if self.query_type in {KnowledgeQueryType.GRAPH, KnowledgeQueryType.TRIPLE}:
            if not self.subject:
                raise ContractViolationError(
                    f"KnowledgeQuery: {self.query_type} query requires 'subject'"
                )
        if self.query_type == KnowledgeQueryType.REASONING:
            if not self.subject or not self.relation:
                raise ContractViolationError(
                    "KnowledgeQuery: REASONING query requires 'subject' and 'relation'"
                )


@dataclass(frozen=True)
class KnowledgeEntry:
    """A single result from a knowledge query."""

    content: Any
    score: float = 1.0
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeResult:
    """
    Output contract for a knowledge query.

    Attributes:
        success:  True if the query completed without error
        entries:  Ordered list of results (highest relevance first)
        error:    Error message if success is False
        meta:     Capability metadata
    """

    success: bool
    entries: List[KnowledgeEntry] = field(default_factory=list)
    error: Optional[str] = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="knowledge")
    )
