"""Builder to assemble consolidated prompt contexts."""

from typing import List, Dict, Any, Optional
from yasinai.knowledge_platform.manager import MemoryManager
from yasinai.knowledge_platform.graph import KnowledgeGraph
from yasinai.knowledge_platform.search import LocalSemanticRetriever
from yasinai.knowledge_platform.context import FormattedContext


class ContextBuilder:
    """Combines system context, conversation history, memories, and knowledge graph facts into unified prompts."""

    def __init__(self, memory_manager: MemoryManager, graph: KnowledgeGraph, retriever: LocalSemanticRetriever):
        """Initializes the ContextBuilder.

        Args:
            memory_manager: Active MemoryManager containing short and long term history.
            graph: KnowledgeGraph containing entities and connections.
            retriever: LocalSemanticRetriever for searching query-relevant information.
        """
        self.memory_manager = memory_manager
        self.graph = graph
        self.retriever = retriever
        self.system_context: str = ""

    def set_system_context(self, system_context: str) -> None:
        """Sets the default system-level context instruction.

        Args:
            system_context: Instruction context.
        """
        self.system_context = system_context

    def build_context(self, query: Optional[str] = None, memory_limit: int = 3, fact_limit: int = 5) -> FormattedContext:
        """Collects, ranks, and structures facts and memories relevant to a query.

        Args:
            query: The user input or search term used to pull semantic matches.
            memory_limit: Max memory fragments to retrieve.
            fact_limit: Max facts to retrieve from Knowledge Graph.

        Returns:
            A FormattedContext object containing compiled context records.
        """
        # 1. Retrieve short term conversation history
        history = self.memory_manager.get_conversation_history()

        # 2. Retrieve memories using semantic retrieval if a query is given
        retained_memories: List[str] = []
        if query:
            search_results = self.retriever.search(query, limit=memory_limit)
            for doc, _ in search_results:
                retained_memories.append(doc["text"])
        else:
            # Fallback to listing some keys or messages from long term if no query
            keys = self.memory_manager.long_term.list_keys()[:memory_limit]
            for key in keys:
                val = self.memory_manager.fetch_from_long_term(key)
                if isinstance(val, str):
                    retained_memories.append(val)
                else:
                    retained_memories.append(f"{key}: {val}")

        # 3. Retrieve relevant facts from Knowledge Graph
        # We can construct facts from graph triples. If query matches entity name or subject, prioritize them.
        facts: List[str] = []
        triples = self.graph.get_triples()

        if query:
            # Query-guided filtering of triples
            query_lower = query.lower()
            matching_triples = []
            other_triples = []
            for s, p, o in triples:
                # Basic lexical matching
                if query_lower in s.lower() or query_lower in p.lower() or query_lower in o.lower():
                    matching_triples.append((s, p, o))
                else:
                    other_triples.append((s, p, o))

            # Combine, keeping matching ones first
            ordered_triples = matching_triples + other_triples
        else:
            ordered_triples = triples

        for s, p, o in ordered_triples[:fact_limit]:
            # Format nicely as standard triple text: "Subject [Predicate] Object"
            facts.append(f"{s} --({p})--> {o}")

        return FormattedContext(
            system_context=self.system_context,
            history=history,
            memories=retained_memories,
            facts=facts
        )
