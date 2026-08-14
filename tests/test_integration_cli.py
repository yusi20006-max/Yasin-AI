"""Phase 4.3 — YasinCLI integration surface smoke tests."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from yasinai.integration import YasinCLIClient
from yasinai.providers import LocalProvider, ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService, RagService


@pytest.fixture
def cli(tmp_path, monkeypatch):
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
    return YasinCLIClient(knowledge=knowledge, generation=generation, rag=rag)


def test_cli_capabilities(cli):
    assert set(cli.capabilities()) >= {"memory_search", "generation", "rag"}


def test_cli_search_demo_corpus(cli):
    cli.seed_demo_documents()
    result = cli.search_memory("security", top_k=3)
    assert result.success is True
    rows = cli.format_search_results(result, threshold=0.5)
    assert any("Security platform" in r["content"] for r in rows)


def test_cli_generate(cli):
    result = cli.generate("hello cli", provider="local")
    assert result.success is True


def test_cli_client_forbidden_imports():
    path = (
        Path(__file__).resolve().parents[1]
        / "yasinai"
        / "integration"
        / "cli_client.py"
    )
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for forbidden in ("knowledge_platform", "developer_platform", "openai", "anthropic"):
        assert forbidden not in imported
