"""
Yasin-AI Public Capability Contracts v1

Stable, versioned contracts that define the boundary between
Yasin-AI and its consumers (Yasin-Agent, YasinHub, YasinCLI,
YasinRelay, YasinFeed, YasinPress).

Import from here, never from internal implementation modules.
"""

from yasinai.contracts.base import (
    CapabilityError,
    CapabilityUnavailableError,
    ContractViolationError,
    ObservabilityContext,
    CapabilityMetadata,
)
from yasinai.contracts.memory import (
    MemoryRequest,
    MemoryResponse,
    MemoryEntry,
    MemoryType,
)
from yasinai.contracts.knowledge import (
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeEntry,
    KnowledgeQueryType,
)
from yasinai.contracts.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingVector,
)
from yasinai.contracts.plugin import (
    PluginContract,
    PluginInvokeRequest,
    PluginInvokeResponse,
)
from yasinai.contracts.generation import (
    GenerationRequest,
    GenerationResult,
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
]

CONTRACT_VERSION = "v1"
