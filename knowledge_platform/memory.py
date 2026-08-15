"""Memory system for the YasinAI Knowledge Platform.

Short-term memory remains process-local; long-term memory is backed by a
pluggable durable store and defaults to SQLite for application use.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Protocol

from knowledge_platform.memory_store import SQLiteMemoryStore

logger = logging.getLogger(__name__)


class LongTermStore(Protocol):
    """Storage contract used by long-term memory."""

    def store(self, key: str, content: Any, timestamp: float, metadata: dict[str, Any]) -> dict[str, Any]: ...
    def retrieve(self, key: str) -> dict[str, Any] | None: ...
    def delete(self, key: str) -> bool: ...
    def list_all(self) -> list[dict[str, Any]]: ...
    def clear(self) -> None: ...


class ShortTermMemory:
    """Manages temporary, ephemeral conversation information."""

    def __init__(self, capacity: int = 100) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        self.capacity = capacity
        self.memory: list[dict[str, Any]] = []

    def store(self, content: Any, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)
        entry = {"content": content, "timestamp": time.time(), "metadata": metadata or {}}
        self.memory.append(entry)
        return entry

    def retrieve(self, limit: int | None = None) -> list[dict[str, Any]]:
        sorted_mem = sorted(self.memory, key=lambda x: x["timestamp"], reverse=True)
        return sorted_mem[:limit] if limit is not None else sorted_mem

    def clear(self) -> None:
        self.memory.clear()


class LongTermMemory:
    """Persistent long-term memory using a pluggable store (SQLite by default)."""

    def __init__(self, store: LongTermStore | None = None, path: str | None = None) -> None:
        default_path = os.environ.get("YASINAI_MEMORY_PATH", "~/.yasinai/memory.db")
        self._store: LongTermStore = store or SQLiteMemoryStore(path or default_path)

    def store(self, key: str, content: Any, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._store.store(key, content, time.time(), metadata or {})

    def retrieve(self, key: str) -> dict[str, Any] | None:
        return self._store.retrieve(key)

    def delete(self, key: str) -> bool:
        return self._store.delete(key)

    def list_all(self) -> list[dict[str, Any]]:
        return self._store.list_all()

    def clear(self) -> None:
        self._store.clear()

    def close(self) -> None:
        close = getattr(self._store, "close", None)
        if close:
            close()


class MemoryManager:
    """Orchestrates short-term and durable long-term memory."""

    def __init__(self, short_term: ShortTermMemory | None = None, long_term: LongTermMemory | None = None) -> None:
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term or LongTermMemory()

    def add_short_term(self, content: Any, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.short_term.store(content, metadata)

    def add_long_term(self, key: str, content: Any, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.long_term.store(key, content, metadata)

    def get_short_term(self, limit: int | None = None) -> list[dict[str, Any]]:
        return self.short_term.retrieve(limit)

    def get_long_term(self, key: str) -> dict[str, Any] | None:
        return self.long_term.retrieve(key)

    def delete_long_term(self, key: str) -> bool:
        return self.long_term.delete(key)

    def consolidate_short_to_long(self, key: str, index: int, metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
        short_memories = self.short_term.retrieve()
        if 0 <= index < len(short_memories):
            entry = short_memories[index]
            meta = dict(entry["metadata"] or {})
            if metadata:
                meta.update(metadata)
            meta["consolidated_at"] = time.time()
            return self.add_long_term(key, entry["content"], meta)
        return None

    def clear_all(self) -> None:
        self.short_term.clear()
        self.long_term.clear()
