"""
Relation component for YasinAI Knowledge Graph.
"""

from typing import Any, Dict, Optional


class Relation:
    """
    Represents a semantic connection or relationship between entities in the Knowledge Graph.
    """

    def __init__(self, name: str, description: str = "", properties: Optional[Dict[str, Any]] = None) -> None:
        self.name: str = name
        self.description: str = description
        self.properties: Dict[str, Any] = properties or {}

    def __repr__(self) -> str:
        return f"Relation(name={self.name!r})"
