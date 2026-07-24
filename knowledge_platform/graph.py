"""
Knowledge Graph coordinator for YasinAI Knowledge Platform.
"""

from typing import Dict, List, Optional, Tuple

from knowledge_platform.entity import Entity
from knowledge_platform.relation import Relation
from knowledge_platform.triple_store import TripleStore
from knowledge_platform.query_engine import QueryEngine


class KnowledgeGraph:
    """
    Coordinating core component of the Knowledge Graph system.
    Integrates entities, relations, triple store, and query engine.
    """

    def __init__(self) -> None:
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.triple_store: TripleStore = TripleStore()
        self.query_engine: QueryEngine = QueryEngine(self.triple_store)

    def add_entity(self, name: str, entity_type: str = "Concept", properties: Optional[dict] = None) -> Entity:
        """Create and add an entity to the graph."""
        if name in self.entities:
            # Update properties if already exists
            entity = self.entities[name]
            if properties:
                entity.properties.update(properties)
            return entity
        entity = Entity(name, entity_type, properties)
        self.entities[name] = entity
        return entity

    def get_entity(self, name: str) -> Optional[Entity]:
        """Look up an entity by name."""
        return self.entities.get(name)

    def delete_entity(self, name: str) -> bool:
        """Delete an entity and remove all associated triples."""
        if name in self.entities:
            del self.entities[name]
            # Clean up triple store
            associated_triples = self.triple_store.query_triples(subject=name)
            for s, p, o in associated_triples:
                self.triple_store.remove_triple(s, p, o)
            associated_triples = self.triple_store.query_triples(obj=name)
            for s, p, o in associated_triples:
                self.triple_store.remove_triple(s, p, o)
            return True
        return False

    def add_relation(self, name: str, description: str = "", properties: Optional[dict] = None) -> Relation:
        """Create and register a relation definition."""
        if name in self.relations:
            relation = self.relations[name]
            relation.description = description
            if properties:
                relation.properties.update(properties)
            return relation
        relation = Relation(name, description, properties)
        self.relations[name] = relation
        return relation

    def get_relation(self, name: str) -> Optional[Relation]:
        """Look up a relation definition."""
        return self.relations.get(name)

    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """Add a relationship triple to the graph, creating entities/relations if necessary."""
        if subject not in self.entities:
            self.add_entity(subject)
        if predicate not in self.relations:
            self.add_relation(predicate)
        if obj not in self.entities:
            self.add_entity(obj)

        self.triple_store.add_triple(subject, predicate, obj)

    def query(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Query stored triples."""
        return self.triple_store.query_triples(subject, predicate, obj)

    def find_path(self, start: str, end: str, max_depth: int = 3) -> Optional[List[Tuple[str, str]]]:
        """Find a path between two entities."""
        return self.query_engine.find_path(start, end, max_depth)

    def clear(self) -> None:
        """Clear the complete graph."""
        self.entities.clear()
        self.relations.clear()
        self.triple_store.clear()
