"""Short-term in-memory conversation storage."""

from typing import List, Dict


class ShortTermMemory:
    """Manages short-term, temporary conversational history."""

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to the conversation history.

        Args:
            role: The role of the message author (e.g., "user", "assistant").
            content: The content of the message.
        """
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Retrieves all conversation messages.

        Returns:
            A list of dictionaries containing message role and content.
        """
        return self.messages

    def clear(self) -> None:
        """Clears all short-term memory."""
        self.messages = []
