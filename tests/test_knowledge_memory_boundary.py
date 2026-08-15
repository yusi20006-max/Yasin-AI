"""#145 — Knowledge vs Memory contract boundary tests."""
from __future__ import annotations

import pytest

from yasinai.contracts.knowledge import KnowledgeQuery, KnowledgeQueryType
from yasinai.contracts.memory import MemoryRequest, MemoryType
from yasinai.services import KnowledgeService


@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vec.db"))
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.semantic_search import Retriever

    return KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "vec.db")),
    )


def test_memory_store_retrieve_short_term(svc):
    store = svc.memory(
        MemoryRequest(operation="store", memory_type=MemoryType.SHORT_TERM, content="session-turn-1")
    )
    assert store.success is True
    listed = svc.memory(MemoryRequest(operation="list", memory_type=MemoryType.SHORT_TERM))
    assert listed.success is True
    assert any("session-turn-1" in str(e.content) for e in listed.entries)


def test_memory_long_term_requires_key():
    from yasinai.contracts.base import ContractViolationError
    with pytest.raises(ContractViolationError):
        MemoryRequest(operation="store", memory_type=MemoryType.LONG_TERM, content="x")


def test_memory_long_term_roundtrip(svc):
    r = svc.memory(
        MemoryRequest(
            operation="store",
            memory_type=MemoryType.LONG_TERM,
            key="entity:user:1",
            content={"role": "operator"},
        )
    )
    assert r.success is True
    got = svc.memory(
        MemoryRequest(operation="retrieve", memory_type=MemoryType.LONG_TERM, key="entity:user:1")
    )
    assert got.success is True


def test_knowledge_semantic_does_not_expose_memory_entries(svc):
    svc.memory(
        MemoryRequest(operation="store", memory_type=MemoryType.SHORT_TERM, content="private-agent-state")
    )
    svc.add_document("doc-1", "World knowledge about Yasin ecosystem contracts.")
    result = svc.query(
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="ecosystem contracts", top_k=3)
    )
    assert result.success is True
    # Retrieved knowledge entries must not leak raw short-term memory payloads
    blob = " ".join(str(e) for e in result.entries)
    assert "private-agent-state" not in blob


def test_knowledge_graph_add_and_query(svc):
    svc.add_triple("Yasin-AI", "provides", "contracts")
    result = svc.query(
        KnowledgeQuery(query_type=KnowledgeQueryType.GRAPH, subject="Yasin-AI")
    )
    assert result.success is True
