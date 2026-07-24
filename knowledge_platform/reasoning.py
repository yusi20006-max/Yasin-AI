"""
Reasoning Engine subsystem for YasinAI Knowledge Platform.
Implements KnowledgeReasoner and RuleEngine.
"""

from typing import Any, Dict, List, Tuple, Callable
from knowledge_platform.graph import KnowledgeGraph


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
        self.rules.append((name, condition, action))

    def evaluate(self, facts: Any) -> List[Any]:
        """Evaluate all facts against rules, trigger actions and return results."""
        triggered_results = []
        for name, condition, action in self.rules:
            try:
                if condition(facts):
                    result = action(facts)
                    triggered_results.append({
                        "rule_name": name,
                        "result": result
                    })
            except Exception:
                pass
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
        connected = []
        queue = [start_entity]
        visited = {start_entity}

        while queue:
            current = queue.pop(0)
            triples = self.graph.query(subject=current, predicate=relation_name)
            for _, _, obj in triples:
                if obj not in visited:
                    visited.add(obj)
                    connected.append(obj)
                    queue.append(obj)
        return connected

    def deduce_symmetric_relations(self, relation_name: str, symmetric_relation_name: str) -> List[Tuple[str, str, str]]:
        """
        For a symmetric relationship (e.g., if A is_partner_of B, then B is_partner_of A),
        find all implied relationships that are missing.
        Returns a list of deduced triples (subject, predicate, obj).
        """
        deduced_triples = []
        all_triples = self.graph.query(predicate=relation_name)
        for s, p, o in all_triples:
            # Check if symmetric triple is already in graph
            symmetric_exists = len(self.graph.query(subject=o, predicate=symmetric_relation_name, obj=s)) > 0
            if not symmetric_exists:
                deduced_triples.append((o, symmetric_relation_name, s))
        return deduced_triples
