"""
Entity component for YasinAI Knowledge Graph.
"""

class Entity:
    """
    Represents a semantic concept or instance in the Knowledge Graph.
    """

    def __init__(self, name: str, entity_type: str = "Concept", properties: dict = None) -> None:
        self.name: str = name
        self.entity_type: str = entity_type
        self.properties: dict = properties or {}

    def get_property(self, key: str, default: any = None) -> any:
        """Get property by key."""
        return self.properties.get(key, default)

    def set_property(self, key: str, value: any) -> None:
        """Set property value."""
        self.properties[key] = value

    def __repr__(self) -> str:
        return f"Entity(name={self.name!r}, type={self.entity_type!r})"
