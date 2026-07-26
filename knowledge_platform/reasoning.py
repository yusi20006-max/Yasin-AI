"""
Reasoning Engine subsystem for YasinAI Knowledge Platform.
Implements KnowledgeReasoner and RuleEngine.
"""

import logging
from typing import Any, Dict, List, Tuple, Callable
from knowledge_platform.graph import KnowledgeGraph

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Manages custom logic or validation rules.
    Runs logic matches on objects or contexts.
    """

    def __init__(self) -> None:
        # Rules are tuples: (rule_name, condition_fn, action_fn)
        self.rules: List[Tuple[str, Callable[[Any], bool], Callable[[Any], Any]]] = []

    def add_rule(self, name: str, condition: Callable[[Any], bool], action: Callable[[Any], Any]) -> None:
        """Register a logical rule."""
        logger.debug(f"Registering logical rule in RuleEngine: '{name}'")
        self.rules.append((name, condition, action))

    def evaluate(self, facts: Any) -> List[Dict[str, Any]]:
        """Evaluate all facts against rules, trigger actions and return results."""
        logger.debug("Evaluating facts against registered rules...")
        triggered_results: List[Dict[str, Any]] = []
        for name, condition, action in self.rules:
            try:
                if condition(facts):
                    logger.debug(f"Rule '{name}' triggered successfully.")
                    result = action(facts)
                    triggered_results.append({
                        "rule_name": name,
                        "result": result
                    })
            except Exception as e:
                logger.error(f"Error evaluating rule '{name}': {e}", exc_info=True)
        return triggered_results


class KnowledgeReasoner:
    """
    Deduce new facts or validate existing relations inside a Knowledge Graph.
    Supports basic transitive deduction or constraint logic.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph: KnowledgeGraph = graph

    def deduce_transitive_relations(self, start_entity: str, relation_name: str) -> List[str]:
        """
        Deduce transitive connections for a relation (e.g. A is_part_of B, B is_part_of C -> A is_part_of C).
        Returns list of all directly or indirectly connected entities.
        """
        logger.info(f"Deducing transitive relations for '{start_entity}' over relation '{relation_name}'")
        connected: List[str] = []
        queue: List[str] = [start_entity]
        visited = {start_entity}

        while queue:
            current = queue.pop(0)
            triples = self.graph.query(subject=current, predicate=relation_name)
            for _, _, obj in triples:
                if obj not in visited:
                    visited.add(obj)
                    connected.append(obj)
                    queue.append(obj)
        logger.debug(f"Transitive deduction results for '{start_entity}': {connected}")
        return connected

    def deduce_symmetric_relations(self, relation_name: str, symmetric_relation_name: str) -> List[Tuple[str, str, str]]:
        """
        For a symmetric relationship (e.g., if A is_partner_of B, then B is_partner_of A),
        find all implied relationships that are missing.
        Returns a list of deduced triples (subject, predicate, obj).
        """
        logger.info(f"Deducing symmetric relations for '{relation_name}' as symmetric to '{symmetric_relation_name}'")
        deduced_triples: List[Tuple[str, str, str]] = []
        all_triples = self.graph.query(predicate=relation_name)
        for s, p, o in all_triples:
            # Check if symmetric triple is already in graph
            symmetric_exists = len(self.graph.query(subject=o, predicate=symmetric_relation_name, obj=s)) > 0
            if not symmetric_exists:
                deduced_triples.append((o, symmetric_relation_name, s))
        logger.debug(f"Symmetric deduction results: {deduced_triples}")
        return deduced_triples
