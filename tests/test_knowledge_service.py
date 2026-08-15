"""
Tests for KnowledgeService facade (Phase 2.7).

Covers memory operations and knowledge/retrieval/reasoning queries
through the public service layer without importing knowledge_platform
from the test consumer surface (tests may import internals for setup).
"""
from __future__ import annotations

import pytest

from yasinai.contracts.base import ContractViolationError
from yasinai.contracts.knowledge import (
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.contracts.memory import (
    MemoryRequest,
    MemoryType,
)
from yasinai.services import KnowledgeService
from yasinai.services.knowledge_service import KnowledgeService as KS

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc(tmp_path, monkeypatch):
    """Isolated service with temp long-term memory and vector paths."""
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vectors.db"))
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.semantic_search import Retriever

    return KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "vectors.db")),
    )


# ---------------------------------------------------------------------------
# Contract bounds validation
# ---------------------------------------------------------------------------

def test_knowledge_query_top_k_bounds():
    with pytest.raises(ContractViolationError, match="top_k"):
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="x", top_k=0)
    with pytest.raises(ContractViolationError, match="top_k"):
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="x", top_k=101)
    # boundary value accepted
    KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="x", top_k=100)


def test_memory_request_limit_bounds():
    with pytest.raises(ContractViolationError, match="limit"):
        MemoryRequest(operation="retrieve", limit=-1)
    with pytest.raises(ContractViolationError, match="limit"):
        MemoryRequest(operation="retrieve", limit=1001)
    # boundary value and None (no limit) are both accepted
    MemoryRequest(operation="retrieve", limit=1000)
    MemoryRequest(operation="retrieve", limit=None)


# ---------------------------------------------------------------------------
# Memory — short-term
# ---------------------------------------------------------------------------

def test_memory_store_short_term(svc):
    resp = svc.memory(
        MemoryRequest(operation="store", content="hello stm", memory_type=MemoryType.SHORT_TERM)
    )
    assert resp.success is True
    assert resp.entry is not None
    assert resp.entry.content == "hello stm"
    assert resp.meta.capability == "memory"


def test_memory_retrieve_short_term(svc):
    svc.memory(MemoryRequest(operation="store", content="a", memory_type=MemoryType.SHORT_TERM))
    svc.memory(MemoryRequest(operation="store", content="b", memory_type=MemoryType.SHORT_TERM))
    resp = svc.memory(
        MemoryRequest(operation="retrieve", memory_type=MemoryType.SHORT_TERM, limit=10)
    )
    assert resp.success is True
    assert len(resp.entries) == 2
    contents = {e.content for e in resp.entries}
    assert contents == {"a", "b"}


def test_memory_clear_short_term(svc):
    svc.memory(MemoryRequest(operation="store", content="x", memory_type=MemoryType.SHORT_TERM))
    resp = svc.memory(MemoryRequest(operation="clear", memory_type=MemoryType.SHORT_TERM))
    assert resp.success is True
    after = svc.memory(
        MemoryRequest(operation="retrieve", memory_type=MemoryType.SHORT_TERM)
    )
    assert after.entries == []


# ---------------------------------------------------------------------------
# Memory — long-term
# ---------------------------------------------------------------------------

def test_memory_store_and_retrieve_long_term(svc):
    store = svc.memory(
        MemoryRequest(
            operation="store",
            key="policy",
            content="encrypt keys",
            memory_type=MemoryType.LONG_TERM,
            metadata={"type": "rule"},
        )
    )
    assert store.success is True
    assert store.entry is not None
    assert store.entry.key == "policy"

    get = svc.memory(
        MemoryRequest(operation="retrieve", key="policy", memory_type=MemoryType.LONG_TERM)
    )
    assert get.success is True
    assert get.entry is not None
    assert get.entry.content == "encrypt keys"
    assert get.entry.metadata.get("type") == "rule"


def test_memory_delete_long_term(svc):
    svc.memory(
        MemoryRequest(
            operation="store",
            key="tmp",
            content="to-delete",
            memory_type=MemoryType.LONG_TERM,
        )
    )
    deleted = svc.memory(
        MemoryRequest(operation="delete", key="tmp", memory_type=MemoryType.LONG_TERM)
    )
    assert deleted.success is True
    assert deleted.deleted is True

    missing = svc.memory(
        MemoryRequest(operation="retrieve", key="tmp", memory_type=MemoryType.LONG_TERM)
    )
    assert missing.entry is None


def test_memory_list_long_term(svc):
    svc.memory(
        MemoryRequest(
            operation="store", key="k1", content="c1", memory_type=MemoryType.LONG_TERM
        )
    )
    svc.memory(
        MemoryRequest(
            operation="store", key="k2", content="c2", memory_type=MemoryType.LONG_TERM
        )
    )
    listed = svc.memory(MemoryRequest(operation="list", memory_type=MemoryType.LONG_TERM))
    assert listed.success is True
    assert len(listed.entries) >= 2
    keys = {e.key for e in listed.entries}
    assert "k1" in keys and "k2" in keys


def test_memory_short_term_delete_unsupported(svc):
    resp = svc.memory(
        MemoryRequest(operation="delete", key="x", memory_type=MemoryType.SHORT_TERM)
    )
    assert resp.success is False
    assert "clear" in (resp.error or "").lower()


# ---------------------------------------------------------------------------
# Knowledge — semantic retrieval
# ---------------------------------------------------------------------------

def test_query_semantic_empty_index(svc):
    result = svc.query(
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="anything", top_k=3)
    )
    assert isinstance(result, KnowledgeResult)
    assert result.success is True
    assert result.entries == []


def test_query_semantic_with_documents(svc):
    svc.add_document("d1", "The quick brown fox jumps over the lazy dog")
    svc.add_document("d2", "Yasin-AI provides memory and knowledge services")
    result = svc.query(
        KnowledgeQuery(
            query_type=KnowledgeQueryType.SEMANTIC,
            text="memory knowledge",
            top_k=5,
        )
    )
    assert result.success is True
    assert len(result.entries) >= 1
    # highest relevance should mention memory/knowledge
    top_content = str(result.entries[0].content).lower()
    assert "memory" in top_content or "knowledge" in top_content or "yasin" in top_content


# ---------------------------------------------------------------------------
# Knowledge — graph / triple
# ---------------------------------------------------------------------------

def test_query_graph_neighbors(svc):
    svc.add_triple("Alice", "knows", "Bob")
    svc.add_triple("Alice", "works_at", "Yasin")
    result = svc.query(
        KnowledgeQuery(query_type=KnowledgeQueryType.GRAPH, subject="Alice")
    )
    assert result.success is True
    assert len(result.entries) >= 2
    entities = {e.content.get("entity") for e in result.entries if isinstance(e.content, dict)}
    assert "Bob" in entities or "Yasin" in entities


def test_query_triple(svc):
    svc.add_triple("Python", "is_a", "language")
    result = svc.query(
        KnowledgeQuery(
            query_type=KnowledgeQueryType.TRIPLE,
            subject="Python",
            predicate="is_a",
        )
    )
    assert result.success is True
    assert len(result.entries) >= 1
    triple = result.entries[0].content
    assert triple["subject"] == "Python"
    assert triple["predicate"] == "is_a"
    assert triple["object"] == "language"


def test_query_reasoning(svc):
    svc.add_triple("A", "related_to", "B")
    svc.add_triple("B", "related_to", "C")
    result = svc.query(
        KnowledgeQuery(
            query_type=KnowledgeQueryType.REASONING,
            subject="A",
            relation="related_to",
        )
    )
    assert result.success is True
    # At minimum neighbors or deduced results; success path is what we assert
    assert isinstance(result.entries, list)


# ---------------------------------------------------------------------------
# Error / contract paths
# ---------------------------------------------------------------------------

def test_unsupported_memory_operation(svc):
    # Bypass contract validation by constructing a raw-like call via internal path
    # Contract forbids invalid ops, so we test the service defensive branch
    # by calling with a mocked request that somehow got through.
    class FakeReq:
        operation = "flush"
        memory_type = MemoryType.SHORT_TERM
        key = None
        content = None
        limit = None
        metadata = {}
        context = None

    resp = svc.memory(FakeReq())  # type: ignore[arg-type]
    assert resp.success is False
    assert "unsupported" in (resp.error or "").lower()


def test_service_import_surface():
    """Consumers import KnowledgeService from yasinai.services, not knowledge_platform."""
    assert KS is KnowledgeService
    from yasinai import services
    assert hasattr(services, "KnowledgeService")
