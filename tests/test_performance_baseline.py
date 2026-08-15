"""#139 — performance baseline smoke (deterministic, no network)."""
from __future__ import annotations

import time

from yasinai.contracts.generation import GenerationRequest
from yasinai.contracts.knowledge import KnowledgeQuery, KnowledgeQueryType
from yasinai.contracts.memory import MemoryRequest, MemoryType
from yasinai.providers.base import (
    GenerationRequest as PReq,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderInfo,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.providers.router import ProviderRouter
from yasinai.services import GenerationService, KnowledgeService


class _Fast(ProviderBase):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="fast",
            capabilities=frozenset({ProviderCapability.GENERATION}),
            model_ids=["fast-1"],
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: PReq) -> GenerationResponse:
        return GenerationResponse(text="ok", model="fast-1", provider="fast")


def test_router_select_baseline():
    reg = ProviderRegistry()
    reg.register(_Fast())
    router = ProviderRouter(reg)
    t0 = time.perf_counter()
    for _ in range(100):
        router.select(ProviderCapability.GENERATION, model="fast-1")
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.5  # 100 selects << 5ms each budget with headroom


def test_local_generate_baseline():
    reg = ProviderRegistry()
    reg.register(_Fast())
    svc = GenerationService(registry=reg)
    t0 = time.perf_counter()
    for _ in range(20):
        assert svc.generate(GenerationRequest(prompt="x")).success
    assert time.perf_counter() - t0 < 1.0


def test_memory_and_knowledge_baseline(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "m.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "v.db"))
    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.semantic_search import Retriever

    svc = KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "v.db")),
    )
    t0 = time.perf_counter()
    for i in range(20):
        svc.memory(
            MemoryRequest(operation="store", memory_type=MemoryType.SHORT_TERM, content=f"e{i}")
        )
    svc.memory(MemoryRequest(operation="list", memory_type=MemoryType.SHORT_TERM))
    assert time.perf_counter() - t0 < 2.0

    for i in range(5):
        svc.add_document(f"d{i}", f"document body about topic {i} contracts")
    t1 = time.perf_counter()
    svc.query(KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="contracts", top_k=3))
    assert time.perf_counter() - t1 < 2.0
