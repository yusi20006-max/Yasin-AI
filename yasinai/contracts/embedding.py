"""
Embedding Capability Contract v1

Stable interface for producing and comparing vector embeddings.
Currently backed by the stdlib TF-IDF engine in knowledge_platform.
Designed to accept external providers (OpenAI, etc.) in Phase 3
without changing this contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from yasinai.contracts.base import (
    CapabilityMetadata,
    ContractViolationError,
    ObservabilityContext,
)


@dataclass(frozen=True)
class EmbeddingRequest:
    """
    Input contract for an embedding operation.

    Attributes:
        texts:      One or more texts to embed
        model:      Optional provider model hint (ignored by stdlib engine)
        metadata:   Caller-supplied context
        context:    Observability tracing context
    """

    texts: List[str]
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ObservabilityContext] = None

    def __post_init__(self) -> None:
        if not self.texts:
            raise ContractViolationError(
                "EmbeddingRequest: 'texts' must contain at least one entry"
            )
        if any(not isinstance(t, str) for t in self.texts):
            raise ContractViolationError(
                "EmbeddingRequest: all entries in 'texts' must be strings"
            )


@dataclass(frozen=True)
class EmbeddingVector:
    """A single embedding result."""

    text: str
    vector: List[float]
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EmbeddingResponse:
    """
    Output contract for an embedding operation.

    Attributes:
        success:   True if all embeddings were produced
        vectors:   One EmbeddingVector per input text, same order
        error:     Error message if success is False
        meta:      Capability metadata
    """

    success: bool
    vectors: List[EmbeddingVector] = field(default_factory=list)
    error: Optional[str] = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="embedding")
    )
