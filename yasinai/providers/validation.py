"""Ephemeral credential validation contract for provider adapters."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ValidationResult:
    reachable: bool | None
    authenticated: bool | None
    http_status: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    latency_ms: int | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        return {"reachable": self.reachable, "authenticated": self.authenticated, "http_status": self.http_status, "error_code": self.error_code, "error_message": self.error_message, "latency_ms": self.latency_ms, "capabilities": dict(self.capabilities)}
