"""#131 — Yasin-Agent compatibility against Public API Contract v1."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from yasinai.contracts import (
    GenerationRequest,
    GenerationResult,
    KnowledgeQuery,
    KnowledgeQueryType,
    MemoryRequest,
    MemoryType,
)
from yasinai.integration import YasinAgentClient
from yasinai.providers import LocalProvider, ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ("knowledge_platform", "developer_platform", "security_platform")


@pytest.fixture
def agent(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vec.db"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.semantic_search import Retriever

    knowledge = KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "vec.db")),
    )
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    generation = GenerationService(registry=reg)
    return YasinAgentClient(knowledge=knowledge, generation=generation)


def test_agent_client_uses_public_imports_only():
    path = ROOT / "yasinai" / "integration" / "agent_client.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for pkg in PRIVATE:
        assert pkg not in imported


def test_agent_generate_via_public_contracts(agent):
    result = agent.generate("compat ping", provider="local")
    assert isinstance(result, GenerationResult)
    assert result.success is True


def test_agent_knowledge_query(agent):
    agent.index_document("a1", "Yasin-Agent consumes Yasin-AI contracts.")
    k = agent.search("contracts", top_k=2)
    assert k.success is True


def test_agent_memory_path_via_service(agent):
    resp = agent.remember("agent state")
    assert resp.success is True
