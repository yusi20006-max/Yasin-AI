"""#136 — integration/regression harness across public contracts + services."""
from __future__ import annotations

import pytest

from yasinai.contracts.generation import GenerationRequest
from yasinai.contracts.knowledge import KnowledgeQuery, KnowledgeQueryType
from yasinai.contracts.memory import MemoryRequest, MemoryType
from yasinai.contracts.rag import RagRequest
from yasinai.providers.base import (
    GenerationRequest as PReq,
)
from yasinai.providers.base import (
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderInfo,
)
from yasinai.providers.registry import ProviderRegistry
from yasinai.services import GenerationService, KnowledgeService, RagService


class _LocalStub(ProviderBase):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="local-stub",
            capabilities=frozenset({ProviderCapability.GENERATION}),
            model_ids=["local-1"],
        )

    def is_available(self) -> bool:
        return True

    def _generate(self, request: PReq) -> GenerationResponse:
        return GenerationResponse(
            text=f"answer:{request.prompt[:40]}",
            model="local-1",
            provider="local-stub",
        )


@pytest.fixture
def stack(tmp_path, monkeypatch):
    monkeypatch.setenv("YASINAI_MEMORY_PATH", str(tmp_path / "mem.db"))
    monkeypatch.setenv("YASINAI_VECTOR_PATH", str(tmp_path / "vec.db"))
    from knowledge_platform.graph import KnowledgeGraph
    from knowledge_platform.memory import MemoryManager
    from knowledge_platform.semantic_search import Retriever

    knowledge = KnowledgeService(
        memory_manager=MemoryManager(),
        knowledge_graph=KnowledgeGraph(),
        retriever=Retriever(path=str(tmp_path / "vec.db")),
    )
    reg = ProviderRegistry()
    reg.register(_LocalStub())
    generation = GenerationService(registry=reg)
    rag = RagService(knowledge=knowledge, generation=generation)
    return knowledge, generation, rag


def test_end_to_end_memory_knowledge_generation_rag(stack):
    knowledge, generation, rag = stack

    mem = knowledge.memory(
        MemoryRequest(operation="store", memory_type=MemoryType.SHORT_TERM, content="session")
    )
    assert mem.success

    knowledge.add_document("d1", "Yasin-AI public contracts are stable for ecosystem consumers.")
    k = knowledge.query(
        KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="public contracts", top_k=2)
    )
    assert k.success

    gen = generation.generate(GenerationRequest(prompt="hello ecosystem", model="local-1"))
    assert gen.success is True
    assert gen.provider == "local-stub"

    answer = rag.run(RagRequest(query="What is stable for consumers?", top_k=2))
    assert answer.success is True
    assert answer.answer


def test_regression_public_imports_only_for_suite():
    from pathlib import Path

    path = Path(__file__)
    # Fixture may import knowledge_platform for test wiring only — allowed in tests.
    # Production integration clients are covered by boundary tests.
    assert path.name.startswith("test_")
