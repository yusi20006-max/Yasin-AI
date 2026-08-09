"""Tests for durable long-term memory storage."""

from knowledge_platform.memory import LongTermMemory, MemoryManager
from knowledge_platform.memory_store import SQLiteMemoryStore


def test_sqlite_memory_store_round_trip_and_update(tmp_path):
    path = tmp_path / "memory.db"
    store = SQLiteMemoryStore(path)
    store.store("k1", {"value": 42}, 1.0, {"source": "test"})

    reopened = SQLiteMemoryStore(path)
    entry = reopened.retrieve("k1")
    assert entry is not None
    assert entry["content"] == {"value": 42}
    assert entry["metadata"] == {"source": "test"}

    reopened.store("k1", "updated", 2.0, {"source": "update"})
    assert reopened.retrieve("k1")["content"] == "updated"
    assert reopened.delete("k1") is True
    assert reopened.retrieve("k1") is None
    reopened.close()
    store.close()


def test_long_term_memory_defaults_to_durable_store(tmp_path):
    path = tmp_path / "memory.db"
    first = LongTermMemory(path=str(path))
    first.store("persisted", "survives restart")
    first.close()

    second = LongTermMemory(path=str(path))
    assert second.retrieve("persisted")["content"] == "survives restart"
    second.clear()
    second.close()


def test_memory_manager_accepts_durable_long_term_memory(tmp_path):
    manager = MemoryManager(long_term=LongTermMemory(path=str(tmp_path / "memory.db")))
    manager.add_long_term("concept", "durable concept", {"kind": "test"})
    assert manager.get_long_term("concept")["metadata"]["kind"] == "test"
    manager.clear_all()
    manager.long_term.close()
