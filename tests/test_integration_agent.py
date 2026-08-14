"""Phase 4.1 — Yasin-Agent integration surface smoke tests."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from yasinai.integration import YasinAgentClient
from yasinai.providers import LocalProvider, ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService, RagService


FORBIDDEN_IMPORT_ROOTS = (
    "knowledge_platform",
    "developer_platform",
    "security_platform",
    "openai",
    "anthropic",
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vectors.db"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.semantic_search import Retriever

    knowledge = KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "vectors.db")),
    )
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    generation = GenerationService(registry=reg)
    rag = RagService(knowledge=knowledge, generation=generation)
    return YasinAgentClient(knowledge=knowledge, generation=generation, rag=rag)


def test_agent_client_capabilities(client):
    caps = client.capabilities()
    assert set(caps) >= {"memory", "knowledge", "generation", "rag"}


def test_agent_memory_roundtrip(client):
    stored = client.remember("session note", metadata={"src": "agent"})
    assert stored.success is True
    recalled = client.recall(limit=5)
    assert recalled.success is True
    assert any(e.content == "session note" for e in recalled.entries)


def test_agent_search_and_answer(client):
    client.index_document("a1", "Yasin-Agent orchestrates workflows on top of Yasin-AI.")
    search = client.search("workflows", top_k=3)
    assert search.success is True

    answer = client.answer("What does Yasin-Agent do?", include_memory=False, top_k=3)
    assert answer.success is True
    assert answer.provider == "local"
    assert answer.answer


def test_agent_generate(client):
    result = client.generate("ping", system_prompt="agent", provider="local")
    assert result.success is True
    assert result.provider == "local"


def test_agent_client_source_has_no_forbidden_imports():
    """Static boundary check: agent_client must not import internal packages."""
    path = Path(__file__).resolve().parents[1] / "yasinai" / "integration" / "agent_client.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for forbidden in FORBIDDEN_IMPORT_ROOTS:
        assert forbidden not in imported, f"forbidden import root: {forbidden}"
    assert "yasinai" in imported
