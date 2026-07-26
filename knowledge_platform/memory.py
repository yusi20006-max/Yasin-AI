"""
Memory System for YasinAI Knowledge Platform.
Implements Short-Term Memory, Long-Term Memory, and MemoryManager.
"""

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Manages temporary, ephemeral conversation information.
    Typically stored in-memory with limit on quantity or TTL.
    """

    def __init__(self, capacity: int = 100) -> None:
        self.capacity: int = capacity
        self.memory: List[Dict[str, Any]] = []

    def store(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store a new piece of temporary info."""
        logger.debug(f"Storing short-term memory. Capacity={self.capacity}, Current count={len(self.memory)}")
        if len(self.memory) >= self.capacity:
            evicted = self.memory.pop(0)  # FIFO eviction
            logger.debug(f"Short-term memory capacity reached. Evicted oldest entry: {evicted.get('content')}")

        entry: Dict[str, Any] = {
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.memory.append(entry)
        return entry

    def retrieve(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve stored temporary information, sorted by timestamp descending."""
        logger.debug(f"Retrieving short-term memories with limit={limit}")
        sorted_mem = sorted(self.memory, key=lambda x: x["timestamp"], reverse=True)
        if limit is not None:
            return sorted_mem[:limit]
        return sorted_mem

    def clear(self) -> None:
        """Clear all short-term memories."""
        logger.info("Clearing short-term memory.")
        self.memory.clear()


class LongTermMemory:
    """
    Manages persistent, long-term information storage.
    """

    def __init__(self) -> None:
        self.memory: Dict[str, Dict[str, Any]] = {}

    def store(self, key: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Persist information under a specific identifier/key."""
        logger.debug(f"Storing long-term memory under key: '{key}'")
        entry: Dict[str, Any] = {
            "key": key,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.memory[key] = entry
        return entry

    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a persistent piece of information by key."""
        logger.debug(f"Retrieving long-term memory for key: '{key}'")
        return self.memory.get(key)

    def delete(self, key: str) -> bool:
        """Delete a piece of persistent memory. Returns True if found & deleted."""
        logger.debug(f"Deleting long-term memory for key: '{key}'")
        if key in self.memory:
            del self.memory[key]
            logger.info(f"Deleted long-term memory key '{key}' successfully.")
            return True
        logger.warning(f"Long-term memory key '{key}' not found for deletion.")
        return False

    def list_all(self) -> List[Dict[str, Any]]:
        """List all persistent memory entries."""
        logger.debug("Listing all long-term memory entries.")
        return list(self.memory.values())

    def clear(self) -> None:
        """Clear all long-term memories."""
        logger.info("Clearing long-term memory.")
        self.memory.clear()


class MemoryManager:
    """
    Orchestrates memory storage, routing between short term and long term memory subsystems.
    """

    def __init__(self, short_term: Optional[ShortTermMemory] = None, long_term: Optional[LongTermMemory] = None) -> None:
        self.short_term: ShortTermMemory = short_term or ShortTermMemory()
        self.long_term: LongTermMemory = long_term or LongTermMemory()

    def add_short_term(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save to short-term memory."""
        return self.short_term.store(content, metadata)

    def add_long_term(self, key: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save to long-term memory."""
        return self.long_term.store(key, content, metadata)

    def get_short_term(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve short term memories."""
        return self.short_term.retrieve(limit)

    def get_long_term(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve long term memory by key."""
        return self.long_term.retrieve(key)

    def delete_long_term(self, key: str) -> bool:
        """Remove long term memory by key."""
        return self.long_term.delete(key)

    def consolidate_short_to_long(self, key: str, index: int, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Consolidate a short-term memory entry into long-term persistent storage.
        """
        logger.info(f"Consolidating short-term memory at index {index} to long-term memory with key '{key}'")
        short_memories = self.short_term.retrieve()
        if 0 <= index < len(short_memories):
            entry = short_memories[index]
            meta = entry["metadata"].copy() if entry["metadata"] else {}
            if metadata:
                meta.update(metadata)
            meta["consolidated_at"] = time.time()
            return self.add_long_term(key, entry["content"], meta)
        logger.warning(f"Consolidation failed: Index {index} is out of bounds for short-term memories.")
        return None

    def clear_all(self) -> None:
        """Clear both short term and long term memories."""
        logger.info("Clearing all short-term and long-term memories.")
        self.short_term.clear()
        self.long_term.clear()
