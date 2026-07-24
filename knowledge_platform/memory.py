"""
Memory System for YasinAI Knowledge Platform.
Implements Short-Term Memory, Long-Term Memory, and MemoryManager.
"""

import time
from typing import Any, Dict, List, Optional


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
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)  # FIFO eviction

        entry = {
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.memory.append(entry)
        return entry

    def retrieve(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve stored temporary information, sorted by timestamp descending."""
        sorted_mem = sorted(self.memory, key=lambda x: x["timestamp"], reverse=True)
        if limit is not None:
            return sorted_mem[:limit]
        return sorted_mem

    def clear(self) -> None:
        """Clear all short-term memories."""
        self.memory.clear()


class LongTermMemory:
    """
    Manages persistent, long-term information storage.
    """

    def __init__(self) -> None:
        self.memory: Dict[str, Dict[str, Any]] = {}

    def store(self, key: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Persist information under a specific identifier/key."""
        entry = {
            "key": key,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.memory[key] = entry
        return entry

    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a persistent piece of information by key."""
        return self.memory.get(key)

    def delete(self, key: str) -> bool:
        """Delete a piece of persistent memory. Returns True if found & deleted."""
        if key in self.memory:
            del self.memory[key]
            return True
        return False

    def list_all(self) -> List[Dict[str, Any]]:
        """List all persistent memory entries."""
        return list(self.memory.values())

    def clear(self) -> None:
        """Clear all long-term memories."""
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
        short_memories = self.short_term.retrieve()
        if 0 <= index < len(short_memories):
            entry = short_memories[index]
            meta = entry["metadata"].copy() if entry["metadata"] else {}
            if metadata:
                meta.update(metadata)
            meta["consolidated_at"] = time.time()
            return self.add_long_term(key, entry["content"], meta)
        return None

    def clear_all(self) -> None:
        """Clear both short term and long term memories."""
        self.short_term.clear()
        self.long_term.clear()
