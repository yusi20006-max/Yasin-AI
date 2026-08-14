"""
RAG Capability Contract v1

Retrieval-Augmented Generation: retrieve context, optionally memory, then generate.
Orchestrated by yasinai.services.RagService.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from yasinai.contracts.base import (
    CapabilityMetadata,
    ContractViolationError,
    ObservabilityContext,
)
from yasinai.contracts.knowledge import KnowledgeEntry


@dataclass(frozen=True)
class RagRequest:
    """
    Input for a RAG pipeline run.

    Attributes:
        query:              User question / prompt (required)
        top_k:              Number of retrieval hits (default 5)
        include_memory:     Whether to append short-term memory to context
        memory_limit:       Max short-term memory entries when include_memory
        model:              Optional model hint for generation
        provider:           Optional preferred generation provider
        max_tokens:         Generation max tokens
        temperature:        Generation temperature
        system_prompt:      Optional system instruction (prepended)
        metadata:           Caller metadata
        context:            Observability context
    """

    query: str
    top_k: int = 5
    include_memory: bool = False
    memory_limit: int = 5
    model: Optional[str] = None
    provider: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ObservabilityContext] = None

    def __post_init__(self) -> None:
        if not self.query or not str(self.query).strip():
            raise ContractViolationError("RagRequest: 'query' must not be empty")
        if self.top_k < 1:
            raise ContractViolationError("RagRequest: 'top_k' must be >= 1")
        if self.memory_limit < 0:
            raise ContractViolationError("RagRequest: 'memory_limit' must be >= 0")


@dataclass(frozen=True)
class RagResult:
    """
    Output of a RAG pipeline run.

    Attributes:
        success:          True if generation completed
        answer:           Generated answer text
        sources:          Retrieved knowledge entries used as context
        model:            Model that produced the answer
        provider:         Generation provider name
        input_tokens:     Generation input tokens
        output_tokens:    Generation output tokens
        error:            Error message if success is False
        meta:             Capability metadata
    """

    success: bool
    answer: str = ""
    sources: List[KnowledgeEntry] = field(default_factory=list)
    model: Optional[str] = None
    provider: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="rag")
    )
