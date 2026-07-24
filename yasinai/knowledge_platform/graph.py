"""Knowledge Graph module to store and manage entities and relations."""

from typing import Dict, List, Set, Tuple, Optional
from yasinai.knowledge_platform.entity import Entity
from yasinai.knowledge_platform.relation import Relation


class KnowledgeGraph:
    """Manages entities and relations (triples) in a directed graph structure."""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        # Mapping from source_id -> list of Relations
        self.out_relations: Dict[str, List[Relation]] = {}
        # Mapping from target_id -> list of Relations
        self.in_relations: Dict[str, List[Relation]] = {}

    def add_entity(self, entity: Entity) -> None:
        """Adds an entity to the graph.

        Args:
            entity: The Entity object to add.
        """
        self.entities[entity.id] = entity
        if entity.id not in self.out_relations:
            self.out_relations[entity.id] = []
        if entity.id not in self.in_relations:
            self.in_relations[entity.id] = []

    def remove_entity(self, entity_id: str) -> bool:
        """Removes an entity and all its associated relations from the graph.

        Args:
            entity_id: Unique ID of the entity to remove.

        Returns:
            True if the entity existed and was removed, False otherwise.
        """
        if entity_id not in self.entities:
            return False

        # Remove outgoing relations
        for rel in self.out_relations.get(entity_id, []):
            target = rel.target_id
            if target in self.in_relations:
                self.in_relations[target] = [r for r in self.in_relations[target] if r != rel]

        # Remove incoming relations
        for rel in self.in_relations.get(entity_id, []):
            source = rel.source_id
            if source in self.out_relations:
                self.out_relations[source] = [r for r in self.out_relations[source] if r != rel]

        del self.entities[entity_id]
        if entity_id in self.out_relations:
            del self.out_relations[entity_id]
        if entity_id in self.in_relations:
            del self.in_relations[entity_id]

        return True

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieves an Entity by its ID."""
        return self.entities.get(entity_id)

    def add_relation(self, relation: Relation) -> None:
        """Adds a relation (edge) between two entities in the graph.

        If either the source or target entity is not present, default generic
        entities are added automatically.

        Args:
            relation: The Relation object to add.
        """
        if relation.source_id not in self.entities:
            self.add_entity(Entity(id=relation.source_id, name=relation.source_id))
        if relation.target_id not in self.entities:
            self.add_entity(Entity(id=relation.target_id, name=relation.target_id))

        # Check for duplicates to prevent triple stacking
        for rel in self.out_relations[relation.source_id]:
            if rel.type == relation.type and rel.target_id == relation.target_id:
                # Update properties if needed, then return
                rel.properties.update(relation.properties)
                return

        self.out_relations[relation.source_id].append(relation)
        self.in_relations[relation.target_id].append(relation)

    def remove_relation(self, type: str, source_id: str, target_id: str) -> bool:
        """Removes a specific relation from the graph.

        Args:
            type: Relationship type.
            source_id: Source entity ID.
            target_id: Target entity ID.

        Returns:
            True if relation was found and removed, False otherwise.
        """
        removed = False
        if source_id in self.out_relations:
            original_len = len(self.out_relations[source_id])
            self.out_relations[source_id] = [
                r for r in self.out_relations[source_id]
                if not (r.type == type and r.source_id == source_id and r.target_id == target_id)
            ]
            if len(self.out_relations[source_id]) < original_len:
                removed = True

        if target_id in self.in_relations:
            self.in_relations[target_id] = [
                r for r in self.in_relations[target_id]
                if not (r.type == type and r.source_id == source_id and r.target_id == target_id)
            ]

        return removed

    def get_neighbors(self, entity_id: str, direction: str = "both") -> List[Tuple[Entity, Relation]]:
        """Retrieves neighboring entities and their connecting relations.

        Args:
            entity_id: The center entity ID.
            direction: Direction of relation. Can be "out", "in", or "both".

        Returns:
            A list of tuples, each containing (Neighbor Entity, Connecting Relation).
        """
        results = []
        if entity_id not in self.entities:
            return results

        if direction in ("out", "both"):
            for rel in self.out_relations.get(entity_id, []):
                target_entity = self.entities.get(rel.target_id)
                if target_entity:
                    results.append((target_entity, rel))

        if direction in ("in", "both"):
            for rel in self.in_relations.get(entity_id, []):
                source_entity = self.entities.get(rel.source_id)
                if source_entity:
                    results.append((source_entity, rel))

        return results

    def get_triples(self) -> List[Tuple[str, str, str]]:
        """Retrieves all triples in the graph in (Subject, Predicate, Object) format."""
        triples = []
        for source_id, relations in self.out_relations.items():
            for rel in relations:
                triples.append((source_id, rel.type, rel.target_id))
        return triples
