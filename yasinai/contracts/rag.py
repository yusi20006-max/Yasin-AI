"""
RAG Capability Contract v1

Retrieval-Augmented Generation: retrieve context, optionally memory, then generate.
Orchestrated by yasinai.services.RagService.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
    model: str | None = None
    provider: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7
    system_prompt: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    context: ObservabilityContext | None = None

    TOP_K_LIMIT = 100
    MEMORY_LIMIT_LIMIT = 1000
    MAX_TOKENS_LIMIT = 32000

    def __post_init__(self) -> None:
        if not self.query or not str(self.query).strip():
            raise ContractViolationError("RagRequest: 'query' must not be empty")
        if self.top_k < 1:
            raise ContractViolationError("RagRequest: 'top_k' must be >= 1")
        if self.top_k > self.TOP_K_LIMIT:
            raise ContractViolationError(f"RagRequest: 'top_k' must be <= {self.TOP_K_LIMIT}")
        if self.memory_limit < 0:
            raise ContractViolationError("RagRequest: 'memory_limit' must be >= 0")
        if self.memory_limit > self.MEMORY_LIMIT_LIMIT:
            raise ContractViolationError(
                f"RagRequest: 'memory_limit' must be <= {self.MEMORY_LIMIT_LIMIT}"
            )
        if self.max_tokens < 1:
            raise ContractViolationError("RagRequest: 'max_tokens' must be >= 1")
        if self.max_tokens > self.MAX_TOKENS_LIMIT:
            raise ContractViolationError(
                f"RagRequest: 'max_tokens' must be <= {self.MAX_TOKENS_LIMIT}"
            )


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
    sources: list[KnowledgeEntry] = field(default_factory=list)
    model: str | None = None
    provider: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="rag")
    )
