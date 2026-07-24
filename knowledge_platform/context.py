"""
Context Engine subsystem for YasinAI Knowledge Platform.
Implements ConversationMemory, ContextBuilder, and ReasoningEngine.
"""

from typing import Any, Dict, List, Optional


class ConversationMemory:
    """
    Manages active, multi-turn conversation memory history.
    """

    def __init__(self) -> None:
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a turn to conversation history."""
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        """Retrieve full message history."""
        return self.history

    def get_formatted_history(self) -> str:
        """Get formatted chat history as string."""
        formatted = []
        for msg in self.history:
            role_label = msg["role"].capitalize()
            formatted.append(f"{role_label}: {msg['content']}")
        return "\n".join(formatted)

    def clear(self) -> None:
        """Clear the history."""
        self.history.clear()


class ContextBuilder:
    """
    Builds structured AI prompts and context before response generation,
    weaving together user input, chat history, and retrieved knowledge blocks.
    """

    def __init__(self) -> None:
        pass

    def build_context(self, user_input: str, chat_history: List[Dict[str, str]], retrieved_knowledge: List[str]) -> str:
        """
        Synthesize the final structured context prompt.
        """
        sections = []

        # 1. System Prompt / Instructions
        sections.append("System Prompt: You are a helpful AI Assistant. Synthesize responses based on the provided context, rules, and conversation history.")

        # 2. Retrieved Knowledge Context
        if retrieved_knowledge:
            sections.append("--- RETRIEVED KNOWLEDGE ---")
            for i, info in enumerate(retrieved_knowledge, 1):
                sections.append(f"[{i}] {info}")

        # 3. Conversation History
        if chat_history:
            sections.append("--- CONVERSATION HISTORY ---")
            for msg in chat_history:
                sections.append(f"{msg['role'].capitalize()}: {msg['content']}")

        # 4. Active User Query
        sections.append("--- CURRENT USER INPUT ---")
        sections.append(f"User: {user_input}")

        return "\n".join(sections)


class ReasoningEngine:
    """
    Integrates with graph reasoning or rules to refine built contexts before passing to runtime/agent execution.
    """

    def __init__(self) -> None:
        pass

    def evaluate_and_refine(self, raw_context: str, rules_applied: List[str]) -> str:
        """
        Evaluate context against specific system rules and append compliance instructions.
        """
        if not rules_applied:
            return raw_context

        refinement_clause = "\n--- REASONING COMPLIANCE INSTRUCTIONS ---\nThis context must adhere strictly to the following verified facts/rules:\n"
        for rule in rules_applied:
            refinement_clause += f"- {rule}\n"

        return raw_context + refinement_clause
