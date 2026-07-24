"""Long-term persistent storage."""

import json
import os
from typing import List, Dict, Any


class LongTermMemory:
    """Manages persistent key-value/document storage using local JSON files."""

    def __init__(self, storage_path: str = "long_term_memory.json"):
        """Initializes the long term memory.

        Args:
            storage_path: Path to the JSON file where memory is stored.
        """
        self.storage_path = storage_path
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Loads data from the storage file if it exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}
        else:
            self.data = {}

    def _save(self) -> None:
        """Saves current memory state to the storage file."""
        try:
            # Ensure containing directory exists
            dir_name = os.path.dirname(self.storage_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            # In-memory fallback if save fails
            pass

    def store(self, key: str, value: Any) -> None:
        """Stores a key-value pair in long-term memory.

        Args:
            key: The unique key identifier.
            value: The data to be stored.
        """
        self.data[key] = value
        self._save()

    def retrieve(self, key: str) -> Any:
        """Retrieves a value from long-term memory.

        Args:
            key: The identifier of the stored value.

        Returns:
            The stored value if found, otherwise None.
        """
        return self.data.get(key)

    def delete(self, key: str) -> bool:
        """Deletes a key-value pair from long-term memory.

        Args:
            key: The identifier to delete.

        Returns:
            True if the key was found and deleted, False otherwise.
        """
        if key in self.data:
            del self.data[key]
            self._save()
            return True
        return False

    def list_keys(self) -> List[str]:
        """Lists all keys in long-term memory.

        Returns:
            A list of keys.
        """
        return list(self.data.keys())

    def clear(self) -> None:
        """Clears all long-term memory and saves the empty state."""
        self.data = {}
        self._save()
