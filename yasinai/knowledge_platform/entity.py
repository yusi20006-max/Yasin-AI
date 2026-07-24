"""Entity representation in the Knowledge Graph."""

from typing import Dict, Any, Optional


class Entity:
    """Represents a unique subject, concept, or object in the knowledge graph."""

    def __init__(self, id: str, name: str, type: Optional[str] = None, properties: Optional[Dict[str, Any]] = None):
        """Initializes an Entity.

        Args:
            id: Unique identifier for the entity.
            name: Human-readable name of the entity.
            type: Optional category/class of the entity.
            properties: Key-value attributes associated with the entity.
        """
        self.id = id
        self.name = name
        self.type = type or "Generic"
        self.properties = properties or {}

    def get_property(self, key: str) -> Any:
        """Retrieves a property value."""
        return self.properties.get(key)

    def set_property(self, key: str, value: Any) -> None:
        """Sets a property value."""
        self.properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Converts Entity to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Creates an Entity from a dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data.get("type"),
            properties=data.get("properties")
        )

    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', name='{self.name}', type='{self.type}')"
