"""
Entity component for YasinAI Knowledge Graph.
"""
from __future__ import annotations

from typing import Any


class Entity:
    """
    Represents a semantic concept or instance in the Knowledge Graph.
    """

    def __init__(self, name: str, entity_type: str = "Concept", properties: dict[str, Any] | None = None) -> None:
        self.name: str = name
        self.entity_type: str = entity_type
        self.properties: dict[str, Any] = properties or {}

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get property by key."""
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        """Set property value."""
        self.properties[key] = value

    def __repr__(self) -> str:
        return f"Entity(name={self.name!r}, type={self.entity_type!r})"
