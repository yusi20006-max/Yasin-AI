"""Persistence tests for the Knowledge Platform vector index."""

from knowledge_platform.semantic_search import Retriever
from knowledge_platform.vector_store import SQLiteVectorStore


def test_semantic_retriever_persists_across_instances(tmp_path):
    path = tmp_path / "vectors.db"

    first = Retriever(path=str(path))
    first.add_document("doc1", "YasinAI security configuration", {"topic": "security"})
    first.close()

    second = Retriever(path=str(path))
    results = second.retrieve("security configuration", limit=1)

    assert results
    assert results[0]["id"] == "doc1"
    assert results[0]["metadata"]["topic"] == "security"
    second.close()


def test_sqlite_vector_store_update_delete_and_clear(tmp_path):
    store = SQLiteVectorStore(tmp_path / "vectors.db")
    store.store_vector("a", [1.0, 0.0], {"text": "alpha"})
    store.store_vector("a", [0.0, 1.0], {"text": "updated"})

    records = store.get_all_records()
    assert len(records) == 1
    assert records[0]["vector"] == [0.0, 1.0]
    assert records[0]["metadata"]["text"] == "updated"

    assert store.delete("a") is True
    assert store.delete("missing") is False
    store.store_vector("b", [1.0], {"text": "beta"})
    store.clear()
    assert store.get_all_records() == []
    store.close()


def test_sqlite_vector_store_sets_wal_and_busy_timeout(tmp_path):
    store = SQLiteVectorStore(tmp_path / "vectors.db")
    journal_mode = store._connection.execute("PRAGMA journal_mode").fetchone()[0]
    busy_timeout = store._connection.execute("PRAGMA busy_timeout").fetchone()[0]
    assert journal_mode.lower() == "wal"
    assert busy_timeout == 5000
    store.close()


def test_sqlite_vector_store_in_memory_skips_wal_but_sets_busy_timeout():
    store = SQLiteVectorStore(":memory:")
    journal_mode = store._connection.execute("PRAGMA journal_mode").fetchone()[0]
    busy_timeout = store._connection.execute("PRAGMA busy_timeout").fetchone()[0]
    assert journal_mode.lower() != "wal"
    assert busy_timeout == 5000
    store.close()
