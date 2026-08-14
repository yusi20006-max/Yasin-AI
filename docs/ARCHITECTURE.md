# Yasin-AI Canonical Architecture Reference

Version: 1.1.0
Status: Reconciled

## 1. Overview

Yasin-AI is structured as the Canonical AI Platform of the Yasin ecosystem. It is organized around clear layers to keep core runtime execution independent of specific transport endpoints, storage backends, telemetry exporters, and third-party AI models.

### Target Canonical Layered Architecture
```text
                    Clients / Operators
                           │
             ┌─────────────▼─────────────┐
             │     API / SDK Contracts   │  (External integration contracts)
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │         AI Runtime        │  (Request orchestration & lifecycle)
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │        AI Services        │  (Text generation, structured output)
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │     Provider Gateway      │  (Model registry, routing, fallback)
             └─────┬─────────────┬───────┘
                   ▼             ▼
             ┌───────────┐ ┌───────────┐
             │ Knowledge │ │  Memory   │  (Semantic store vs episodic memory)
             └───────────┘ └───────────┘
```

---

## 2. Ecosystem Roles & Ownership Boundaries (YASIN-DOCS ADR-001)

Yasin-AI provides shared, reusable AI capabilities for all other platforms in the Yasin ecosystem. It adheres to strict ownership boundaries:

- **Yasin-Core**: Standard runtime environment and general SDK foundations. Yasin-AI integrates with Yasin-Core during bootstrap, but does not duplicate general execution features.
- **Yasin-Agent**: Governs multi-step agent planning, reasoning-loop orchestration, and workflow semantics.
  *Boundary Note*: While Yasin-AI contains a local in-process `developer_platform/agent.py` to expose capability hook endpoints for libraries, all complex multi-step orchestrators belong strictly to **Yasin-Agent**.
- **YasinHub**: Governs global ecosystem control, runtime lifecycles, and cross-cutting telemetry.
  *Boundary Note*: Telemetry structures in `observability/` are local instrumentations. They will expose hooks to integrate directly with **YasinHub** in future phases.
- **YasinCLI**: Represents the unified, user-facing control CLI.
  *Boundary Note*: The local command runner `yasinai/cli/` is purely for local platform diagnostics; end-user commands will be ported into **YasinCLI**.

---

## 3. Preferred Dependency Direction

To maintain stability and enforce system boundaries, components must strictly adhere to the downward dependency direction:

```text
API / SDK Contracts
   │
   ▼
AI Runtime
   │
   ▼
AI Services
   │
   ▼
Provider / Knowledge / Memory Abstractions
   │
   ▼
Concrete Implementations (e.g., SQLite DB, specific LLM API clients)
```

### Prohibited Patterns
* **No Direct Implementation Leaks**: Applications or external agents must never import low-level driver or SQLite-specific logic directly. They must interact only with stable public contracts.
* **No Circular Imports**: Runtime engines must never depend on the CLI or specific adapters.

---

## 4. Current Subsystem Breakdown & Reconciled Boundaries

Currently, the platform's codebase is divided into several local capability packages:

### A. Core Runtime (`yasinai/core/`)
Manages startup, settings, and graceful system shutdowns.
* **`runtime.py`**: Manages runtime state transitions.
* **`bootstrap.py`**: Discovers and instantiates platform modules.
* **`config.py`**: Coordinates platform settings and defaults.

### B. API Service (`api_service/`)
Implements transport-neutral request-dispatch interfaces to prevent core modules from coupling with web or IPC frameworks.

### C. Developer Platform (`developer_platform/`)
Exposes integration surfaces and extension SDKs:
* **`agent.py` & `app.py`**: Local in-process wrapper APIs.
* **`plugin.py` & `extension.py`**: Hot-toggling and local execution of trusted user plugins.
* **`debugger.py` & `profiler.py`**: Performance analysis tools.

### D. Knowledge Platform (`knowledge_platform/`)
* **`semantic_search.py`**: Implements dependency-free TF-IDF vector math and retriever pipelines (`Retriever`, `EmbeddingEngine`).
* **`memory.py` & `memory_store.py`**: SQLite-backed conversational persistence and episodic managers.
* **`graph.py` & `triple_store.py`**: Constructs relational networks.
* **`reasoning.py`**: Simple logical deduction rules.

### E. Security Platform (`security_platform/`)
Hardens local platform identity, permissions, custom AES/HMAC encryption, and audit events.

### F. Observability (`observability/`)
Contains internal timer and counter telemetry.

---

## 5. Planned & Future Architecture Corrections (Deferred Refactoring)

As a result of the Phase 2.2 reconciliation, structural re-organizations are deferred to subsequent phases to maintain safe, incremental progress:

1. **Namespace Consolidation (Phase 2.3)**:
   * Move standalone directories (`api_service/`, `developer_platform/`, `security_platform/`, `observability/`) inside the main `yasinai/` package to resolve public/private boundary ambiguities.
2. **Provider Gateway Construction (Phase 2.4)**:
   * Introduce a centralized Provider Gateway layer containing a model registry, retry/fallback handling, and active provider health checks.
3. **Module Splitting (Phase 2.5)**:
   * Separate `knowledge_platform/` into distinct `knowledge/` (ingestion, RAG, triple store) and `memory/` (durable session histories, memory policies) packages.
