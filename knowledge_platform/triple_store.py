"""
Triple Store for YasinAI Knowledge Graph.
"""

import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class TripleStore:
    """
    Stores subject-predicate-object semantic triples.
    Also supports basic queries and matching.
    """

    def __init__(self) -> None:
        # Triples are stored as tuples of strings (subject_name, predicate_name, object_name)
        self._triples: List[Tuple[str, str, str]] = []

    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """Add a triple to the store if it does not already exist."""
        triple = (subject, predicate, obj)
        if triple not in self._triples:
            self._triples.append(triple)
            logger.debug(f"Added triple to store: {triple}")
        else:
            logger.debug(f"Triple already exists in store: {triple}")

    def remove_triple(self, subject: str, predicate: str, obj: str) -> bool:
        """Remove a triple from the store. Returns True if found and removed."""
        triple = (subject, predicate, obj)
        if triple in self._triples:
            self._triples.remove(triple)
            logger.info(f"Removed triple from store: {triple}")
            return True
        logger.warning(f"Attempted to remove non-existent triple: {triple}")
        return False

    def query_triples(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """
        Query the triple store using wildcards. None acts as a wildcard.
        """
        results: List[Tuple[str, str, str]] = []
        for s, p, o in self._triples:
            if subject is not None and s != subject:
                continue
            if predicate is not None and p != predicate:
                continue
            if obj is not None and o != obj:
                continue
            results.append((s, p, o))
        return results

    def list_all(self) -> List[Tuple[str, str, str]]:
        """List all stored triples."""
        return list(self._triples)

    def clear(self) -> None:
        """Clear all stored triples."""
        logger.info("Clearing TripleStore.")
        self._triples.clear()
