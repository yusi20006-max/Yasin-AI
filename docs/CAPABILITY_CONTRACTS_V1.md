# Yasin-AI Capability Contracts v1

**Status:** Stable  
**Contract version:** v1  
**Platform version:** 1.1.0  
**Date:** 2026-08-14

---

## Purpose

These contracts define the **public integration boundary** between Yasin-AI
and all consumer projects (Yasin-Agent, YasinHub, YasinCLI, YasinRelay,
YasinFeed, YasinPress).

Consumers import from `yasinai.contracts`, never from internal modules such
as `knowledge_platform`, `developer_platform`, or `security_platform`.

---

## Package

```python
from yasinai.contracts import (
    # base
    CapabilityError,
    CapabilityUnavailableError,
    ContractViolationError,
    ObservabilityContext,
    CapabilityMetadata,
    # memory
    MemoryRequest, MemoryResponse, MemoryEntry, MemoryType,
    # knowledge
    KnowledgeQuery, KnowledgeResult, KnowledgeEntry, KnowledgeQueryType,
    # embedding
    EmbeddingRequest, EmbeddingResponse, EmbeddingVector,
    # plugin
    PluginContract, PluginInvokeRequest, PluginInvokeResponse,
)
```

---

## Contracts

### Memory (`yasinai.contracts.memory`)

Covers short-term (in-process) and long-term (SQLite-backed) memory operations.

| Type | Role |
|---|---|
| `MemoryRequest` | Input: operation, type, key, content, limit, metadata |
| `MemoryResponse` | Output: success, entry/entries, deleted, error, meta |
| `MemoryEntry` | A single stored record (content, timestamp, key, metadata) |
| `MemoryType` | Enum: `SHORT_TERM` / `LONG_TERM` |

Operations: `store` · `retrieve` · `delete` · `list` · `clear`

### Knowledge (`yasinai.contracts.knowledge`)

Covers knowledge graph queries, triple-store lookups, and transitive reasoning.

| Type | Role |
|---|---|
| `KnowledgeQuery` | Input: query_type, text, subject, predicate, relation, top_k |
| `KnowledgeResult` | Output: success, entries, error, meta |
| `KnowledgeEntry` | A single result (content, score, source, metadata) |
| `KnowledgeQueryType` | Enum: `SEMANTIC` / `GRAPH` / `TRIPLE` / `REASONING` |

### Embedding (`yasinai.contracts.embedding`)

Covers vector embedding for semantic search and RAG pipelines.
Currently backed by stdlib TF-IDF engine; contract is provider-neutral.

| Type | Role |
|---|---|
| `EmbeddingRequest` | Input: texts, model hint, metadata |
| `EmbeddingResponse` | Output: success, vectors, error, meta |
| `EmbeddingVector` | A single embedding (text, vector, model, metadata) |

### Plugin (`yasinai.contracts.plugin`)

Covers cross-repo plugin invocation.

| Type | Role |
|---|---|
| `PluginInvokeRequest` | Input: name, args, kwargs, context |
| `PluginInvokeResponse` | Output: success, result, error, meta |
| `PluginContract` | Metadata for a registered plugin |

---

## Base Types (shared by all contracts)

| Type | Purpose |
|---|---|
| `CapabilityError` | Base error; has `.code` and `.as_dict()` |
| `CapabilityUnavailableError` | Capability not configured / not implemented |
| `ContractViolationError` | Caller passed invalid input |
| `ObservabilityContext` | `trace_id`, `span_id`, `caller`, `metadata` — flows through every request |
| `CapabilityMetadata` | `capability`, `contract_version`, `platform_version`, `provider` — returned in every response |

---

## Versioning policy

- Contract version (`v1`) is **separate** from platform version (`1.1.0`).
- Backward-compatible additions (new optional fields) do not bump the contract version.
- Breaking changes require a new contract version (`v2`) and an ADR.
- `contract_version` is embedded in every `CapabilityMetadata` response so consumers can detect mismatches at runtime.

---

## What is NOT in v1

The following capability contracts are **PLANNED** and will be added in Phase 3
once the provider gateway exists:

- `GenerationRequest / GenerationResult` — **available** (Phase 3.2; via GenerationService)
- `ChatRequest / ChatResponse` (deferred; use GenerationRequest with system_prompt)
- `SummarizationRequest / SummarizationResponse`
- `ClassificationRequest / ClassificationResponse`
- `RAGRequest / RAGResponse` (requires unified pipeline)

Do not implement these until the provider abstraction (Phase 2.6 / Phase 3) is stable.

---

## Tests

`tests/test_contracts.py` — 34 tests covering all contract types,
validation rules, error codes, and observability context propagation.

---

*Related: `AI_CAPABILITY_CATALOG.md`, `VERSIONING_POLICY.md`, ADR-001, ADR-0007*
