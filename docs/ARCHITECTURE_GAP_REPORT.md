# Yasin-AI Architecture Gap Report — Phase 2.2 Reconcilation

## 1. Current Architecture Overview

Yasin-AI is implemented as a single-process Python application composed of the following distinct packages/folders:
* **`yasinai/core/`**: Central execution orchestrator managing runtime lifecycle, settings configuration (`Config`), and bootstrap initialization (`Bootstrap`).
* **`api_service/`**: Transport-neutral service boundary mapping requests to immutable models. It is positioned as a top-level package outside `yasinai`.
* **`developer_platform/`**: Local Agent SDK (`Agent`), Plugin SDK, Application, debugger/profiler instrumentation, and local package bundling.
* **`knowledge_platform/`**: Groups diverse capabilities including memory managers (short/long-term memory), semantic search, TF-IDF vectorizers, context assembly engines, and reasoning engines.
* **`security_platform/`**: Encapsulates custom cryptography (custom HMAC-SHA256 XOR streams), authentication, role-based access controls, auditing, and vulnerability scanning. It is structured as a top-level package outside `yasinai`.
* **`yasinai/cli/`**: Diagnostic CLI wrapper mapping subcommands to underlying subsystem routines.
* **`yasinai/deployment/`**: Manages installer templates, docker configuration validations, and health-checks.
* **`observability/`**: Minimalist, dependency-free timer/counter instrumentation helpers.

---

## 2. Target Canonical Architecture Model

The target architecture defines a layered ecosystem contract. Each module is assigned a precise role in the request-handling, inference, or persistence pipeline:

```text
       ┌────────────────────────────────────────────────────────┐
       │                 API / SDK Contracts                    │
       └───────────────────────────┬────────────────────────────┘
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                     AI Runtime                         │
       │   (Request Lifecycle, Context, Service Orchestrator)   │
       └───────────────────────────┬────────────────────────────┘
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                    AI Services                         │
       │   (Generation, Structured Output, Classification,...)  │
       └───────────────────────────┬────────────────────────────┘
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                   Provider Gateway                     │
       │   (Routing, Retry, Fallback, Registry, Provider Health)│
       └─────┬───────────────────────────┬──────────────────────┘
             ▼                           ▼
 ┌──────────────────────┐    ┌──────────────────────┐
 │      Knowledge       │    │        Memory        │
 │ (Ingestion, RAG,...) │    │ (Storage, Lifecycle) │
 └──────────────────────┘    └──────────────────────┘
```

---

## 3. Identified Architectural Gaps

The following architectural gaps exist between the current codebase and the target canonical ecosystem model:

1. **Absence of Provider Gateway**: The platform lacks a formal gateway layer. It does not have a model registry, retry/fallback mechanisms, or provider health check logic. LLM calls are currently simulated/mocked directly inside separate modules without a centralized, intelligent vendor routing layer.
2. **Missing Central AI Services Layer**: There is no dedicated, unified services layer. Instead, capabilities like `EmbeddingEngine` are tightly coupled with semantic retrieval in `knowledge_platform`, and core text generation/summarization routines are missing or left as speculative developer platform features.
3. **Public/Private Boundary Confusion**: Top-level packages (`api_service/`, `security_platform/`, `observability/`, `developer_platform/`) are scattered outside of the main `yasinai/` Python package namespace. This introduces public API ambiguity, makes distribution complex, and pollutes the root import scope.
4. **Ecosystem Role & Boundaries Leakage**: The `developer_platform/agent.py` contains local agent and SDK execution concepts. This overlaps conceptually with the `Yasin-Agent` repository. These contracts must be reconciled so that Yasin-AI only maintains low-level, in-process capability hooks and delegators, rather than orchestrating complex multi-step planning workflows.

---

## 4. Responsibility Conflicts

* **Knowledge vs. Memory**: The `knowledge_platform/` groups both vector databases (semantic retrieval/indexing) and short/long-term agent memory storage (`MemoryManager`, `ConversationMemory`), which are functionally distinct. In the target model, vector retrieval is part of `Knowledge`, while conversational and episodic storage resides in `Memory`.
* **Ecosystem Control Plane vs. Local Diagnostics**: The `yasinai/cli/` has commands for agent generation and packaging. These commands leak developer toolchain capabilities and control plane responsibilities into a runtime module. Global observability and execution-flow control are strictly owned by `YasinHub` and `YasinCLI`, whereas Yasin-AI CLI must be limited to local module diagnostics.

---

## 5. Dependency Violations

* **Inward Private Module Coupling**: The CLI in `yasinai/cli/` bypasses runtime service orchestration boundaries and imports private platform packages (e.g., `from developer_platform.agent import AgentSDK` and `from knowledge_platform.semantic_search import Retriever`) directly. It should instead interact with the runtime's unified public API/SDK contracts.
* **Preferred Dependency Direction Violation**: The codebase currently exhibits an flat importing pattern:
  `Application/Agent` -> `Private Module Direct Import` -> `Low-level SQLite Implementation`
  The preferred dependency path is:
  `Application/Agent` -> `Stable Capability Contract` -> `AI Runtime / Gateway` -> `Provider/DB Abstraction` -> `Concrete Driver`

---

## 6. Modules Requiring Future Refactoring

To align the codebase perfectly with the target architectural layers, the following migrations are proposed for Phase 2.3+:

| Current Module | Target Directory | Description of Intended Migration |
|---|---|---|
| `api_service/` | `yasinai/api_service/` | Integrate as a sub-package. Refactor to expose versioned AI capability contracts. |
| `knowledge_platform/` | `yasinai/knowledge/` and `yasinai/memory/` | Split semantic retrieval/RAG into `knowledge/`, and conversational state persistence/SQL databases into `memory/`. |
| `developer_platform/` | `yasinai/extensions/` | Port plugin/tool execution boundaries to an extensions namespace. Completely isolate local agent execution from Yasin-Agent workflows. |
| `security_platform/` | `yasinai/security/` | Integrate security controls, policy engines, and custom encryption engines as an internal core sub-package. |
| `observability/` | `yasinai/observability/` | Refactor metrics and instrumentation to plug cleanly into `YasinHub` hooks rather than maintaining standalone metrics. |

---

## 7. Documentation Inconsistencies

1. **Discrepancy in Version Metadata**:
   * Codebase configs (e.g., `pyproject.toml`) and CLI output references declare version `1.0.0`.
   * High-level user documentation (`README.md`) and Git tags claim release version `1.1.0`.
   * This is a critical source-of-truth contradiction that must be aligned. This report recommends synchronizing codebase metadata and version files to represent **`1.1.0`** across all files to align with actual release tag states.

2. **Unclear SDK / Tool Boundaries**:
   * `DEVELOPER_SDK.md` presents a minimalist plugin registration example, but does not document any gateway or model registry abstractions required by the canonical ecosystem docs.

---

## 8. Recommended Migration Sequence

To prevent regressions and ensure seamless transition, the following multi-step migration sequence is recommended:

```text
Phase 2.2 (Current): Reconcile high-level architecture documents, align versions, and resolve tests.
   │
   ▼
Phase 2.3 (Next): Restructure Python package namespaces (move api_service, security, extensions under yasinai/).
   │
   ▼
Phase 2.4: Introduce Provider Gateway (routing, fallback policies, registry) and extract concrete providers.
   │
   ▼
Phase 2.5: Separate Knowledge (retrieval/ingestion) from Memory (conversational history, storage engines).
   │
   ▼
Phase 2.6: Integrate telemetry reporting interfaces for global ecosystem observability under YasinHub.
```
