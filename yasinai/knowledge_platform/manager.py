"""Memory manager to unify short and long term memory access."""

import os
from typing import List, Dict, Any, Optional
from yasinai.knowledge_platform.short_term_memory import ShortTermMemory
from yasinai.knowledge_platform.long_term_memory import LongTermMemory


class MemoryManager:
    """Unifies and manages access to ShortTermMemory and LongTermMemory."""

    def __init__(self, long_term_storage_path: str = "data/long_term_memory.json"):
        """Initializes the MemoryManager.

        Args:
            long_term_storage_path: Path to the persistent storage file.
        """
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_path=long_term_storage_path)

    def add_conversation_message(self, role: str, content: str) -> None:
        """Adds a message to the active short-term conversation memory.

        Args:
            role: Message sender role.
            content: Message body.
        """
        self.short_term.add_message(role, content)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retrieves short-term conversation messages.

        Returns:
            List of conversation messages.
        """
        return self.short_term.get_messages()

    def persist_to_long_term(self, key: str, value: Any) -> None:
        """Persists a key-value pair to long-term memory.

        Args:
            key: Target identifier.
            value: Data to store.
        """
        self.long_term.store(key, value)

    def fetch_from_long_term(self, key: str) -> Any:
        """Fetches a value from long-term memory.

        Args:
            key: Key to lookup.

        Returns:
            The stored data, or None.
        """
        return self.long_term.retrieve(key)

    def remove_from_long_term(self, key: str) -> bool:
        """Deletes a record from long-term memory.

        Args:
            key: Key to delete.

        Returns:
            True if deleted successfully, False otherwise.
        """
        return self.long_term.delete(key)

    def clear_all(self) -> None:
        """Clears both short-term and long-term memory."""
        self.short_term.clear()
        self.long_term.clear()
