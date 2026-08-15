"""
Memory Capability Contract v1

Stable interface for short-term and long-term memory operations.
Backed by knowledge_platform.memory — consumers must not import that directly.
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


class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


@dataclass(frozen=True)
class MemoryRequest:
    """
    Input contract for a memory operation.

    Attributes:
        operation:  "store" | "retrieve" | "delete" | "list" | "clear"
        memory_type: SHORT_TERM or LONG_TERM
        key:        Required for long-term store/retrieve/delete
        content:    Required for store operations
        limit:      Optional; for short-term retrieve (top-N most recent)
        metadata:   Caller-supplied metadata attached to stored entries
        context:    Observability tracing context
    """

    operation: str
    memory_type: MemoryType = MemoryType.SHORT_TERM
    key: Optional[str] = None
    content: Optional[Any] = None
    limit: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[ObservabilityContext] = None

    LIMIT_LIMIT = 1000

    def __post_init__(self) -> None:
        valid_ops = {"store", "retrieve", "delete", "list", "clear"}
        if self.operation not in valid_ops:
            raise ContractViolationError(
                f"MemoryRequest.operation must be one of {valid_ops}, got '{self.operation}'"
            )
        if self.limit is not None:
            if self.limit < 0:
                raise ContractViolationError("MemoryRequest: 'limit' must be >= 0")
            if self.limit > self.LIMIT_LIMIT:
                raise ContractViolationError(
                    f"MemoryRequest: 'limit' must be <= {self.LIMIT_LIMIT}"
                )
        if self.operation == "store" and self.content is None:
            raise ContractViolationError("MemoryRequest: 'store' operation requires 'content'")
        if self.memory_type == MemoryType.LONG_TERM and self.operation in {"store", "retrieve", "delete"}:
            if not self.key:
                raise ContractViolationError(
                    f"MemoryRequest: long-term '{self.operation}' requires 'key'"
                )


@dataclass(frozen=True)
class MemoryEntry:
    """A single memory record returned in a MemoryResponse."""

    content: Any
    timestamp: float
    key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryResponse:
    """
    Output contract for a memory operation.

    Attributes:
        success:  True if the operation completed without error
        entries:  Populated for retrieve/list operations
        entry:    Populated for single-key retrieve
        deleted:  True if a delete operation removed the entry
        error:    Error message if success is False
        meta:     Capability metadata (version, provider, etc.)
    """

    success: bool
    entries: List[MemoryEntry] = field(default_factory=list)
    entry: Optional[MemoryEntry] = None
    deleted: bool = False
    error: Optional[str] = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="memory")
    )
