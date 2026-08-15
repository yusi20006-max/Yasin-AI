"""
Base types shared across all Yasin-AI Capability Contracts v1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CapabilityError(Exception):
    """Base error for all Yasin-AI capability failures."""

    def __init__(self, message: str, code: str = "CAPABILITY_ERROR") -> None:
        super().__init__(message)
        self.code = code

    def as_dict(self) -> dict[str, str]:
        return {"error": str(self), "code": self.code}


class CapabilityUnavailableError(CapabilityError):
    """Raised when a capability is not yet implemented or not configured."""

    def __init__(self, capability: str) -> None:
        super().__init__(
            f"Capability '{capability}' is not available in this deployment.",
            code="CAPABILITY_UNAVAILABLE",
        )
        self.capability = capability


class ContractViolationError(CapabilityError):
    """Raised when a caller violates the contract (bad input, missing fields)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONTRACT_VIOLATION")


@dataclass(frozen=True)
class ObservabilityContext:
    """Opaque tracing/logging context passed through capability calls."""

    trace_id: str | None = None
    span_id: str | None = None
    caller: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityMetadata:
    """Describes the capability and its version at the response boundary."""

    capability: str
    contract_version: str = "v1"
    platform_version: str = "1.1.4"
    provider: str | None = None
