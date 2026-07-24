"""Relation representation in the Knowledge Graph."""

from typing import Dict, Any, Optional


class Relation:
    """Represents a labeled, directed link/edge between two entities in the knowledge graph."""

    def __init__(self, type: str, source_id: str, target_id: str, properties: Optional[Dict[str, Any]] = None):
        """Initializes a Relation.

        Args:
            type: The relationship type/label (predicate).
            source_id: The ID of the source entity (subject).
            target_id: The ID of the target entity (object).
            properties: Key-value attributes associated with the relationship.
        """
        self.type = type
        self.source_id = source_id
        self.target_id = target_id
        self.properties = properties or {}

    def get_property(self, key: str) -> Any:
        """Retrieves a property value."""
        return self.properties.get(key)

    def set_property(self, key: str, value: Any) -> None:
        """Sets a property value."""
        self.properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Converts Relation to dictionary representation."""
        return {
            "type": self.type,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relation':
        """Creates a Relation from a dictionary representation."""
        return cls(
            type=data["type"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            properties=data.get("properties")
        )

    def __repr__(self) -> str:
        return f"Relation(type='{self.type}', source_id='{self.source_id}', target_id='{self.target_id}')"
