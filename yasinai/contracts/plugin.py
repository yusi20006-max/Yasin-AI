"""
Plugin Capability Contract v1

Stable cross-repo interface for plugin invocation.
Backed by developer_platform.sdk — consumers must not import that directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasinai.contracts.base import (
    CapabilityMetadata,
    ContractViolationError,
    ObservabilityContext,
)


@dataclass(frozen=True)
class PluginContract:
    """Metadata describing a registered plugin at the public boundary."""

    name: str
    version: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PluginInvokeRequest:
    """
    Input contract for invoking a plugin.

    Attributes:
        name:     Registered plugin name
        args:     Positional arguments for the plugin handler
        kwargs:   Keyword arguments for the plugin handler
        context:  Observability tracing context
    """

    name: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    context: ObservabilityContext | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ContractViolationError(
                "PluginInvokeRequest: 'name' must not be empty"
            )


@dataclass(frozen=True)
class PluginInvokeResponse:
    """
    Output contract for a plugin invocation.

    Attributes:
        success:  True if the plugin completed without error
        result:   Return value from the plugin handler
        error:    Error message if success is False
        meta:     Capability metadata
    """

    success: bool
    result: Any = None
    error: str | None = None
    meta: CapabilityMetadata = field(
        default_factory=lambda: CapabilityMetadata(capability="plugin")
    )
