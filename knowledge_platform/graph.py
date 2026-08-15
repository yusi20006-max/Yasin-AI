"""
Knowledge Graph coordinator for YasinAI Knowledge Platform.
"""
from __future__ import annotations

import logging

from knowledge_platform.entity import Entity
from knowledge_platform.query_engine import QueryEngine
from knowledge_platform.relation import Relation
from knowledge_platform.triple_store import TripleStore

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    Coordinating core component of the Knowledge Graph system.
    Integrates entities, relations, triple store, and query engine.
    """

    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.relations: dict[str, Relation] = {}
        self.triple_store: TripleStore = TripleStore()
        self.query_engine: QueryEngine = QueryEngine(self.triple_store)

    def add_entity(self, name: str, entity_type: str = "Concept", properties: dict | None = None) -> Entity:
        """Create and add an entity to the graph."""
        logger.debug(f"KnowledgeGraph: Adding entity '{name}' of type '{entity_type}'")
        if name in self.entities:
            # Update properties if already exists
            entity = self.entities[name]
            if properties:
                entity.properties.update(properties)
            return entity
        entity = Entity(name, entity_type, properties)
        self.entities[name] = entity
        return entity

    def get_entity(self, name: str) -> Entity | None:
        """Look up an entity by name."""
        return self.entities.get(name)

    def delete_entity(self, name: str) -> bool:
        """Delete an entity and remove all associated triples."""
        logger.info(f"KnowledgeGraph: Deleting entity '{name}'")
        if name in self.entities:
            del self.entities[name]
            # Clean up triple store
            associated_triples = self.triple_store.query_triples(subject=name)
            for s, p, o in associated_triples:
                self.triple_store.remove_triple(s, p, o)
            associated_triples = self.triple_store.query_triples(obj=name)
            for s, p, o in associated_triples:
                self.triple_store.remove_triple(s, p, o)
            logger.info(f"KnowledgeGraph: Successfully deleted entity '{name}' and associated relations.")
            return True
        logger.warning(f"KnowledgeGraph: Attempted to delete non-existent entity '{name}'")
        return False

    def add_relation(self, name: str, description: str = "", properties: dict | None = None) -> Relation:
        """Create and register a relation definition."""
        logger.debug(f"KnowledgeGraph: Registering relation '{name}'")
        if name in self.relations:
            relation = self.relations[name]
            relation.description = description
            if properties:
                relation.properties.update(properties)
            return relation
        relation = Relation(name, description, properties)
        self.relations[name] = relation
        return relation

    def get_relation(self, name: str) -> Relation | None:
        """Look up a relation definition."""
        return self.relations.get(name)

    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """Add a relationship triple to the graph, creating entities/relations if necessary."""
        logger.debug(f"KnowledgeGraph: Adding relationship triple ({subject}, {predicate}, {obj})")
        if subject not in self.entities:
            self.add_entity(subject)
        if predicate not in self.relations:
            self.add_relation(predicate)
        if obj not in self.entities:
            self.add_entity(obj)

        self.triple_store.add_triple(subject, predicate, obj)

    def query(self, subject: str | None = None, predicate: str | None = None, obj: str | None = None) -> list[tuple[str, str, str]]:
        """Query stored triples."""
        return self.triple_store.query_triples(subject, predicate, obj)

    def find_path(self, start: str, end: str, max_depth: int = 3) -> list[tuple[str, str]] | None:
        """Find a path between two entities."""
        return self.query_engine.find_path(start, end, max_depth)

    def clear(self) -> None:
        """Clear the complete graph."""
        logger.info("Clearing KnowledgeGraph components completely.")
        self.entities.clear()
        self.relations.clear()
        self.triple_store.clear()
