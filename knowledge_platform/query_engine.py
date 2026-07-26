"""
Query Engine for YasinAI Knowledge Graph.
"""

import logging
from typing import Any, List, Dict, Tuple, Optional
from knowledge_platform.triple_store import TripleStore

logger = logging.getLogger(__name__)


class QueryEngine:
    """
    Executes graph-based search, traversals, and queries.
    """

    def __init__(self, triple_store: TripleStore) -> None:
        self.triple_store: TripleStore = triple_store

    def find_neighbors(self, entity_name: str) -> List[Tuple[str, str]]:
        """
        Find direct neighbors of an entity.
        Returns a list of tuples containing (relation_name, target_entity_name).
        """
        logger.debug(f"QueryEngine: Finding direct neighbors of entity: '{entity_name}'")
        neighbors: List[Tuple[str, str]] = []

        # Outgoing triples
        outgoing = self.triple_store.query_triples(subject=entity_name)
        for _, p, o in outgoing:
            neighbors.append((p, o))

        # Incoming triples
        incoming = self.triple_store.query_triples(obj=entity_name)
        for s, p, _ in incoming:
            neighbors.append((f"inverse_{p}", s))

        return neighbors

    def find_path(self, start: str, end: str, max_depth: int = 3, visited: Optional[set] = None) -> Optional[List[Tuple[str, str]]]:
        """
        Find a path of relations and entities between start and end entity names.
        Returns a list of (relation, entity) showing the path, or None if not found.
        """
        logger.debug(f"QueryEngine: Pathfinding from '{start}' to '{end}' (max_depth={max_depth})...")
        if visited is None:
            visited = set()

        if start == end:
            return []

        if max_depth <= 0:
            return None

        visited.add(start)

        neighbors = self.find_neighbors(start)
        for rel, neighbor in neighbors:
            if neighbor in visited:
                continue
            path = self.find_path(neighbor, end, max_depth - 1, visited)
            if path is not None:
                return [(rel, neighbor)] + path

        visited.remove(start)
        return None
