"""Context representation for AI prompts."""

from typing import List, Dict, Any, Optional


class FormattedContext:
    """Contains formatted context string and structural data ready for AI ingestion."""

    def __init__(self, system_context: str, history: List[Dict[str, str]], memories: List[str], facts: List[str]):
        self.system_context = system_context
        self.history = history
        self.memories = memories
        self.facts = facts

    def to_prompt_string(self) -> str:
        """Assembles a structured prompt block from context details.

        Returns:
            A string prompt context.
        """
        blocks = []

        if self.system_context:
            blocks.append(f"### System Context\n{self.system_context}")

        if self.facts:
            facts_str = "\n".join([f"- {fact}" for fact in self.facts])
            blocks.append(f"### Knowledge Graph Facts\n{facts_str}")

        if self.memories:
            memories_str = "\n".join([f"- {mem}" for mem in self.memories])
            blocks.append(f"### Retained Memories\n{memories_str}")

        if self.history:
            history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])
            blocks.append(f"### Conversation History\n{history_str}")

        return "\n\n".join(blocks)

    def __repr__(self) -> str:
        return f"FormattedContext(history_len={len(self.history)}, memories_len={len(self.memories)}, facts_len={len(self.facts)})"
