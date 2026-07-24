"""
Relation component for YasinAI Knowledge Graph.
"""

class Relation:
    """
    Represents a semantic connection or relationship between entities in the Knowledge Graph.
    """

    def __init__(self, name: str, description: str = "", properties: dict = None) -> None:
        self.name: str = name
        self.description: str = description
        self.properties: dict = properties or {}

    def __repr__(self) -> str:
        return f"Relation(name={self.name!r})"
