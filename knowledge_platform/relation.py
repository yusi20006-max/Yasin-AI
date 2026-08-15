"""
Relation component for YasinAI Knowledge Graph.
"""
from __future__ import annotations

from typing import Any


class Relation:
    """
    Represents a semantic connection or relationship between entities in the Knowledge Graph.
    """

    def __init__(self, name: str, description: str = "", properties: dict[str, Any] | None = None) -> None:
        self.name: str = name
        self.description: str = description
        self.properties: dict[str, Any] = properties or {}

    def __repr__(self) -> str:
        return f"Relation(name={self.name!r})"
