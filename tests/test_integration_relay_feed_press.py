"""Phase 4.4 — YasinRelay / YasinFeed / YasinPress integration smoke tests."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from yasinai.integration import YasinFeedClient, YasinPressClient, YasinRelayClient
from yasinai.providers import LocalProvider, ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService, RagService


@pytest.fixture
def services(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vectors.db"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.memory import MemoryManager
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
    return knowledge, generation, rag


def test_relay_enrich(services):
    _, generation, rag = services
    client = YasinRelayClient(generation=generation, rag=rag)
    assert "enrich" in client.capabilities()
    result = client.enrich("hello relay", provider="local")
    assert result.success is True
    grounded = client.grounded_enrich("hello", provider="local")
    assert grounded.success is True


def test_feed_rank_and_summarize(services):
    knowledge, generation, _ = services
    client = YasinFeedClient(knowledge=knowledge, generation=generation)
    client.index_item("f1", "YasinFeed aggregates timeline posts for the ecosystem.")
    ranked = client.rank("timeline", top_k=3)
    assert ranked.success is True
    card = client.summarize_card("Long article text about releases.", provider="local")
    assert card.success is True


def test_press_draft_and_research(services):
    knowledge, generation, rag = services
    client = YasinPressClient(knowledge=knowledge, generation=generation, rag=rag)
    client.index_source("p1", "YasinPress publishes release notes for Yasin platforms.")
    draft = client.draft("Write a one-line blurb about YasinPress.", provider="local")
    assert draft.success is True
    research = client.research("release notes", provider="local", top_k=2)
    assert research.success is True


def _assert_no_forbidden(module_path: Path) -> None:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for forbidden in ("knowledge_platform", "developer_platform", "openai", "anthropic"):
        assert forbidden not in imported, f"{module_path.name}: {forbidden}"


def test_clients_forbidden_imports():
    root = Path(__file__).resolve().parents[1] / "yasinai" / "integration"
    for name in ("relay_client.py", "feed_client.py", "press_client.py"):
        _assert_no_forbidden(root / name)
