"""Phase 4.2 — YasinHub integration surface smoke tests."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from observability.metrics import MetricsRegistry
from yasinai.integration import YasinHubClient
from yasinai.providers import LocalProvider, ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService, RagService


@pytest.fixture
def hub(tmp_path, monkeypatch):
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
    metrics = MetricsRegistry()
    return YasinHubClient(
        knowledge=knowledge, generation=generation, rag=rag, metrics=metrics
    )


def test_hub_capabilities(hub):
    assert set(hub.capabilities()) >= {"generation", "knowledge", "rag", "metrics"}


def test_hub_generate_and_metrics(hub):
    result = hub.generate("hub ping", provider="local")
    assert result.success is True
    snap = hub.metrics_snapshot()
    assert snap["counters"].get("hub.generation.requests") == 1
    assert snap["counters"].get("hub.generation.success") == 1
    assert "hub.generation.latency" in snap["timers"]


def test_hub_knowledge_and_rag(hub):
    # index via knowledge service on the client
    hub._knowledge.add_document("h1", "YasinHub aggregates control-plane telemetry.")
    k = hub.query_knowledge("telemetry", top_k=2)
    assert k.success is True
    r = hub.rag("What does YasinHub do?", top_k=2, provider="local")
    assert r.success is True
    snap = hub.metrics_snapshot()
    assert snap["counters"].get("hub.knowledge.requests") == 1
    assert snap["counters"].get("hub.rag.requests") == 1


def test_hub_client_forbidden_imports():
    path = (
        Path(__file__).resolve().parents[1]
        / "yasinai"
        / "integration"
        / "hub_client.py"
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
