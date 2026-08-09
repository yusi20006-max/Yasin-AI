"""Stable developer-facing SDK primitives for YasinAI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional


class SDKError(Exception):
    """Base exception for developer SDK failures."""


class PluginError(SDKError):
    """Raised when a plugin cannot be registered or invoked."""


@dataclass(frozen=True)
class PluginSpec:
    """Metadata and callable contract for a YasinAI plugin."""

    name: str
    handler: Callable[..., Any]
    version: str = "1.0.0"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginRegistry:
    """Deterministic in-process registry for developer plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginSpec] = {}

    def register(self, plugin: PluginSpec) -> PluginSpec:
        if not plugin.name or not plugin.name.strip():
            raise PluginError("plugin name must not be empty")
        if plugin.name in self._plugins:
            raise PluginError(f"plugin already registered: {plugin.name}")
        self._plugins[plugin.name] = plugin
        return plugin

    def unregister(self, name: str) -> bool:
        return self._plugins.pop(name, None) is not None

    def get(self, name: str) -> Optional[PluginSpec]:
        return self._plugins.get(name)

    def list(self) -> Iterable[PluginSpec]:
        return tuple(self._plugins[name] for name in sorted(self._plugins))

    def invoke(self, name: str, *args: Any, **kwargs: Any) -> Any:
        plugin = self.get(name)
        if plugin is None:
            raise PluginError(f"plugin not found: {name}")
        return plugin.handler(*args, **kwargs)


def plugin(
    name: str,
    *,
    version: str = "1.0.0",
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Declare plugin metadata without coupling the handler to the registry."""

    def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
        setattr(
            handler,
            "__yasinai_plugin__",
            PluginSpec(name, handler, version, description, dict(metadata or {})),
        )
        return handler

    return decorator


__all__ = ["PluginError", "PluginRegistry", "PluginSpec", "SDKError", "plugin"]
