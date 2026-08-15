"""
Yasin-AI Public Capability Contracts v1

Stable, versioned contracts that define the boundary between
Yasin-AI and its consumers (Yasin-Agent, YasinHub, YasinCLI,
YasinRelay, YasinFeed, YasinPress).

Import from here, never from internal implementation modules.
"""

from yasinai.contracts.base import (
    CapabilityError,
    CapabilityMetadata,
    CapabilityUnavailableError,
    ContractViolationError,
    ObservabilityContext,
)
from yasinai.contracts.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
)
from yasinai.contracts.generation import (
    GenerationRequest,
    GenerationResult,
)
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
from yasinai.contracts.plugin import (
    PluginContract,
    PluginInvokeRequest,
    PluginInvokeResponse,
)
from yasinai.contracts.rag import (
    RagRequest,
    RagResult,
)

__all__ = [
    # base
    "CapabilityError",
    "CapabilityUnavailableError",
    "ContractViolationError",
    "ObservabilityContext",
    "CapabilityMetadata",
    # memory
    "MemoryRequest",
    "MemoryResponse",
    "MemoryEntry",
    "MemoryType",
    # knowledge
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeEntry",
    "KnowledgeQueryType",
    # embedding
    "EmbeddingRequest",
    "EmbeddingResponse",
    "EmbeddingVector",
    # plugin
    "PluginContract",
    "PluginInvokeRequest",
    "PluginInvokeResponse",
    # generation
    "GenerationRequest",
    "GenerationResult",
    # rag
    "RagRequest",
    "RagResult",
]

CONTRACT_VERSION = "v1"
