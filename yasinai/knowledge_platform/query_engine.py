"""Query engine for triple pattern matching and graph traversal/search."""

from typing import List, Dict, Tuple, Set, Optional, Any
from yasinai.knowledge_platform.graph import KnowledgeGraph
from yasinai.knowledge_platform.entity import Entity
from yasinai.knowledge_platform.relation import Relation


class QueryEngine:
    """Executes search and pattern matching over a KnowledgeGraph."""

    def __init__(self, graph: KnowledgeGraph):
        """Initializes the QueryEngine.

        Args:
            graph: The KnowledgeGraph instance to query.
        """
        self.graph = graph

    def match_triple(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Matches triples in the graph based on wildcards.

        Args:
            subject: Source entity ID constraint, or None for wildcard.
            predicate: Relation type constraint, or None for wildcard.
            obj: Target entity ID constraint, or None for wildcard.

        Returns:
            A list of matching triples as (Subject, Predicate, Object) tuples.
        """
        matches = []
        for s, p, o in self.graph.get_triples():
            if subject is not None and s != subject:
                continue
            if predicate is not None and p != predicate:
                continue
            if obj is not None and o != obj:
                continue
            matches.append((s, p, o))
        return matches

    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """Finds a path of entity IDs connecting two entities using Breadth-First Search (BFS).

        Args:
            start_id: The starting entity ID.
            end_id: The destination entity ID.
            max_depth: Maximum path length to search.

        Returns:
            A list of entity IDs forming the shortest path, or None if no path exists.
        """
        if start_id not in self.graph.entities or end_id not in self.graph.entities:
            return None

        if start_id == end_id:
            return [start_id]

        queue: List[List[str]] = [[start_id]]
        visited: Set[str] = {start_id}

        while queue:
            path = queue.pop(0)
            if len(path) > max_depth:
                continue

            current_node = path[-1]
            if current_node == end_id:
                return path

            # Explore neighbors (outgoing relations)
            neighbors = self.graph.get_neighbors(current_node, direction="out")
            for neighbor_entity, _ in neighbors:
                if neighbor_entity.id not in visited:
                    visited.add(neighbor_entity.id)
                    new_path = list(path)
                    new_path.append(neighbor_entity.id)
                    queue.append(new_path)

        return None

    def search_by_property(self, key: str, value: Any) -> List[Entity]:
        """Searches for entities containing a specific property value.

        Args:
            key: The property attribute key.
            value: The property attribute value.

        Returns:
            A list of matching Entity objects.
        """
        matches = []
        for entity in self.graph.entities.values():
            if entity.get_property(key) == value:
                matches.append(entity)
        return matches
