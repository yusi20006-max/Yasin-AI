# Yasin-AI — Memory & Knowledge Architecture

**Phase:** 2.7  
**Status:** Boundary defined. Service facade: KnowledgeService.  
**Date:** 2026-08-14  
**Platform version:** 1.1.0

---

## Purpose

This document reconciles the **Memory**, **Knowledge**, **Retrieval**, and **RAG** boundaries
inside Yasin-AI. It defines which concerns live where, how consumers access them,
and the rules that keep internal modules (`knowledge_platform/`) hidden behind
stable public contracts and a thin service facade.

---

## Core Boundary Rule

| Layer | Location | Who may import |
|---|---|---|
| **Public contracts** | `yasinai.contracts` | Consumers (Yasin-Agent, YasinHub, …) and service layer |
| **Service facade** | `yasinai.services` | Consumers (preferred) and internal orchestration |
| **Internal implementation** | `knowledge_platform/` | **Only** `yasinai.services` and tests |

Consumers **must not** import `knowledge_platform` directly.
They import contracts and/or the `KnowledgeService` facade.

---

## Conceptual Separation

```
┌─────────────────────────────────────────────────────────────────┐
│  Consumer (Yasin-Agent, YasinHub, YasinCLI, …)                  │
│       import from yasinai.contracts  OR  yasinai.services       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  yasinai.services.KnowledgeService   (facade — Phase 2.7)       │
│  • translates contracts ↔ internal types                        │
│  • owns lifecycle of MemoryManager / KnowledgeGraph / Retriever │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
   │   Memory    │   │  Knowledge   │   │   Retrieval     │
   │  (STM/LTM)  │   │   Graph      │   │  (Semantic /    │
   │             │   │  + Reasoning │   │   TF-IDF RAG)   │
   └─────────────┘   └──────────────┘   └─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                  knowledge_platform/  (INTERNAL)
```

### 1. Memory

- **Short-term (STM):** process-local, capacity-bounded, FIFO eviction.
- **Long-term (LTM):** durable (SQLite by default via `YASINAI_MEMORY_PATH`).
- Contract: `MemoryRequest` / `MemoryResponse` / `MemoryEntry` / `MemoryType`.
- Operations: `store`, `retrieve`, `delete`, `list`, `clear`.

Memory is **not** a vector store. It stores opaque content + metadata keyed by
conversation or application keys. Semantic search over memory content is a
Retrieval concern, not a Memory concern.

### 2. Knowledge

- Entity–relation–triple graph (`KnowledgeGraph`, `TripleStore`, `QueryEngine`).
- Reasoning / transitive deduction (`KnowledgeReasoner`, `RuleEngine`).
- Contract: `KnowledgeQuery` / `KnowledgeResult` / `KnowledgeEntry` /
  `KnowledgeQueryType` (`SEMANTIC` | `GRAPH` | `TRIPLE` | `REASONING`).

Knowledge answers structured questions about entities and relations.
It does not own conversational history (that is Memory).

### 3. Retrieval

- TF-IDF / in-process vector similarity (`SemanticSearch`, `Retriever`,
  `EmbeddingEngine`, `VectorStore` / `SQLiteVectorStore`).
- Used for document ranking and lightweight RAG context assembly.
- Exposed to consumers via `KnowledgeQueryType.SEMANTIC` on the same
  knowledge contract surface (no separate retrieval contract in v1).

### 4. RAG (Retrieval-Augmented Generation)

- **Orchestration** lives in the future `yasinai.services.rag_service`
  (Phase 3). Phase 2.7 only defines the retrieval half and the memory /
  knowledge boundaries that RAG will compose.
- RAG will call:
  1. Retrieval (semantic) → context chunks
  2. optionally Memory (conversation history)
  3. Generation via ProviderRouter (Phase 3)

No generation SDKs are imported in the knowledge/memory path.

---

## Service Facade: KnowledgeService

```python
from yasinai.services import KnowledgeService
from yasinai.contracts import KnowledgeQuery, KnowledgeQueryType, MemoryRequest

svc = KnowledgeService()          # owns internal MemoryManager + graph + retriever
result = svc.query(KnowledgeQuery(query_type=KnowledgeQueryType.SEMANTIC, text="…"))
mem   = svc.memory(MemoryRequest(operation="store", content="…"))
```

Responsibilities:

- Construct and hold the internal `MemoryManager`, `KnowledgeGraph`, and
  `Retriever` (or accept injected instances for tests).
- Map contract types ↔ internal dicts / objects.
- Never leak `knowledge_platform` types to callers.
- Return contract-compliant responses even on internal errors
  (`success=False`, `error=…`).

---

## Explicit Non-Goals (Phase 2.7)

- No concrete LLM provider implementations (Phase 3).
- No full RAG orchestrator (Phase 3).
- No namespace move of `knowledge_platform/` under `yasinai/` (deferred).
- No change to the public contract shapes defined in Phase 2.5.

---

## Related Documents

| Document | Role |
|---|---|
| `docs/CAPABILITY_CONTRACTS_V1.md` | Public contract shapes |
| `docs/PROVIDER_ARCHITECTURE.md` | Provider boundary (Phase 2.6) |
| `docs/ARCHITECTURE.md` | Overall architecture |
| `AI_CAPABILITY_CATALOG.md` | Capability inventory |

---

## Change Log

| Date | Change |
|---|---|
| 2026-08-14 | Initial reconciliation (Phase 2.7). KnowledgeService facade added. |
