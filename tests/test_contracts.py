"""
Tests for Yasin-AI Public Capability Contracts v1
Phase 2.5
"""
import pytest

from yasinai.contracts import CONTRACT_VERSION
from yasinai.contracts.base import (
    CapabilityError,
    CapabilityMetadata,
    CapabilityUnavailableError,
    ContractViolationError,
    ObservabilityContext,
)
from yasinai.contracts.memory import MemoryEntry, MemoryRequest, MemoryResponse, MemoryType
from yasinai.contracts.knowledge import (
    KnowledgeEntry,
    KnowledgeQuery,
    KnowledgeQueryType,
    KnowledgeResult,
)
from yasinai.contracts.embedding import EmbeddingRequest, EmbeddingResponse, EmbeddingVector
from yasinai.contracts.plugin import (
    PluginContract,
    PluginInvokeRequest,
    PluginInvokeResponse,
)


# ---------------------------------------------------------------------------
# Contract version
# ---------------------------------------------------------------------------

def test_contract_version():
    assert CONTRACT_VERSION == "v1"


# ---------------------------------------------------------------------------
# Base types
# ---------------------------------------------------------------------------

def test_capability_error_has_code():
    err = CapabilityError("something failed", code="TEST_CODE")
    assert err.code == "TEST_CODE"
    assert err.as_dict() == {"error": "something failed", "code": "TEST_CODE"}


def test_capability_unavailable_error():
    err = CapabilityUnavailableError("generation")
    assert err.code == "CAPABILITY_UNAVAILABLE"
    assert "generation" in str(err)


def test_contract_violation_error():
    err = ContractViolationError("bad input")
    assert err.code == "CONTRACT_VIOLATION"


def test_observability_context_defaults():
    ctx = ObservabilityContext()
    assert ctx.trace_id is None
    assert ctx.caller is None
    assert ctx.metadata == {}


def test_capability_metadata_defaults():
    meta = CapabilityMetadata(capability="memory")
    assert meta.contract_version == "v1"
    assert meta.platform_version == "1.1.0"
    assert meta.provider is None


# ---------------------------------------------------------------------------
# Memory contract
# ---------------------------------------------------------------------------

def test_memory_request_short_term_store():
    req = MemoryRequest(operation="store", content="hello", memory_type=MemoryType.SHORT_TERM)
    assert req.operation == "store"
    assert req.content == "hello"


def test_memory_request_long_term_store_requires_key():
    with pytest.raises(ContractViolationError, match="key"):
        MemoryRequest(operation="store", content="x", memory_type=MemoryType.LONG_TERM)


def test_memory_request_long_term_store_with_key():
    req = MemoryRequest(
        operation="store",
        content="data",
        key="my-key",
        memory_type=MemoryType.LONG_TERM,
    )
    assert req.key == "my-key"


def test_memory_request_invalid_operation():
    with pytest.raises(ContractViolationError, match="operation"):
        MemoryRequest(operation="flush")


def test_memory_request_store_without_content():
    with pytest.raises(ContractViolationError, match="content"):
        MemoryRequest(operation="store")


def test_memory_response_success():
    entry = MemoryEntry(content="hello", timestamp=1.0, key="k1")
    resp = MemoryResponse(success=True, entry=entry)
    assert resp.success
    assert resp.entry.content == "hello"
    assert resp.meta.capability == "memory"


def test_memory_response_failure():
    resp = MemoryResponse(success=False, error="not found")
    assert not resp.success
    assert resp.error == "not found"


def test_memory_type_values():
    assert MemoryType.SHORT_TERM == "short_term"
    assert MemoryType.LONG_TERM == "long_term"


# ---------------------------------------------------------------------------
# Knowledge contract
# ---------------------------------------------------------------------------

def test_knowledge_query_semantic_requires_text():
    with pytest.raises(ContractViolationError, match="text"):
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC)


def test_knowledge_query_semantic_valid():
    q = KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="what is Yasin?", top_k=3)
    assert q.text == "what is Yasin?"
    assert q.top_k == 3


def test_knowledge_query_graph_requires_subject():
    with pytest.raises(ContractViolationError, match="subject"):
        KnowledgeQuery(query_type=KnowledgeQueryType.GRAPH)


def test_knowledge_query_graph_valid():
    q = KnowledgeQuery(query_type=KnowledgeQueryType.GRAPH, subject="Yasin-AI")
    assert q.subject == "Yasin-AI"


def test_knowledge_query_reasoning_requires_subject_and_relation():
    with pytest.raises(ContractViolationError):
        KnowledgeQuery(query_type=KnowledgeQueryType.REASONING, subject="A")


def test_knowledge_query_reasoning_valid():
    q = KnowledgeQuery(
        query_type=KnowledgeQueryType.REASONING,
        subject="A",
        relation="is_part_of",
    )
    assert q.relation == "is_part_of"


def test_knowledge_result_success():
    entry = KnowledgeEntry(content="Yasin-AI is the canonical AI platform", score=0.9)
    result = KnowledgeResult(success=True, entries=[entry])
    assert result.success
    assert len(result.entries) == 1
    assert result.entries[0].score == 0.9
    assert result.meta.capability == "knowledge"


def test_knowledge_result_failure():
    result = KnowledgeResult(success=False, error="index not found")
    assert not result.success


# ---------------------------------------------------------------------------
# Embedding contract
# ---------------------------------------------------------------------------

def test_embedding_request_requires_texts():
    with pytest.raises(ContractViolationError, match="texts"):
        EmbeddingRequest(texts=[])


def test_embedding_request_requires_string_texts():
    with pytest.raises(ContractViolationError, match="strings"):
        EmbeddingRequest(texts=["valid", 123])  # type: ignore


def test_embedding_request_valid():
    req = EmbeddingRequest(texts=["hello", "world"])
    assert len(req.texts) == 2


def test_embedding_response_success():
    vectors = [
        EmbeddingVector(text="hello", vector=[0.1, 0.2, 0.3]),
        EmbeddingVector(text="world", vector=[0.4, 0.5, 0.6]),
    ]
    resp = EmbeddingResponse(success=True, vectors=vectors)
    assert resp.success
    assert len(resp.vectors) == 2
    assert resp.meta.capability == "embedding"


def test_embedding_response_failure():
    resp = EmbeddingResponse(success=False, error="provider unavailable")
    assert not resp.success


# ---------------------------------------------------------------------------
# Plugin contract
# ---------------------------------------------------------------------------

def test_plugin_invoke_request_requires_name():
    with pytest.raises(ContractViolationError, match="name"):
        PluginInvokeRequest(name="")


def test_plugin_invoke_request_valid():
    req = PluginInvokeRequest(name="my-plugin", args=[1, 2], kwargs={"key": "val"})
    assert req.name == "my-plugin"
    assert req.args == [1, 2]


def test_plugin_invoke_response_success():
    resp = PluginInvokeResponse(success=True, result={"output": 42})
    assert resp.success
    assert resp.result["output"] == 42
    assert resp.meta.capability == "plugin"


def test_plugin_invoke_response_failure():
    resp = PluginInvokeResponse(success=False, error="plugin not found")
    assert not resp.success


def test_plugin_contract_metadata():
    pc = PluginContract(name="summarizer", version="1.0.0", description="Summarizes text")
    assert pc.name == "summarizer"
    assert pc.version == "1.0.0"


# ---------------------------------------------------------------------------
# Observability context flows through requests
# ---------------------------------------------------------------------------

def test_observability_context_in_memory_request():
    ctx = ObservabilityContext(trace_id="trace-123", caller="yasin-agent")
    req = MemoryRequest(operation="list", context=ctx)
    assert req.context.trace_id == "trace-123"
    assert req.context.caller == "yasin-agent"


def test_observability_context_in_knowledge_query():
    ctx = ObservabilityContext(trace_id="trace-456")
    q = KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="test", context=ctx)
    assert q.context.trace_id == "trace-456"
