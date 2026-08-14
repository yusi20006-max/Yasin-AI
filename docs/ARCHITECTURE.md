# Yasin-AI Canonical Architecture Reference

Version: 1.0.0 (Metadata) / 1.1.0 (Release)
Status: Reconciled

## 1. Overview

Yasin-AI is organized as a layered Python platform. Core runtime behavior is kept independent from transports, persistence backends, observability exporters, and deployment tooling.

```text
                    Clients / Operators
                           |
                    API / CLI / SDK
                           |
                    API Service Layer
                           |
             +-------------+-------------+
             |                           |
          Runtime                  Developer Platform
             |                           |
      +------+-------+              Plugin SDK
      |              |
 Knowledge       Memory
 Platform        Platform
      |              |
 Retrieval       Persistence
      |
 Observability (cross-cutting)
      |
 Deployment / Infrastructure
```

---

## 2. Ecosystem Roles & Ownership Boundaries (YASIN-DOCS ADR-001)

Yasin-AI is defined as the **Canonical AI Platform** of the Yasin ecosystem according to YASIN-DOCS ADR-001. It must not be treated as an isolated or standalone project; instead, it provides shared AI capabilities while maintaining strict boundaries with other ecosystem repositories:

- **Yasin-Core**: Generic runtime and SDK foundation.
- **Yasin-Agent**: Agent planning, workflow, and execution semantics.
  *Boundary Note*: While Yasin-AI contains a local in-process `developer_platform/agent.py` implementation for library-level execution, the ecosystem-level agent planning and workflow orchestrator belongs strictly to **Yasin-Agent**.
- **YasinHub**: Ecosystem control, lifecycle, and observability.
- **YasinCLI**: Unified user-facing command surface.
  *Boundary Note*: The CLI commands in `yasinai/cli/` are local management helpers. The unified end-user command line is owned by **YasinCLI**.
- **Yasin-AI**: Canonical AI capability platform.
- **YasinRelay / YasinFeed / YasinPress**: Domain, content, and business pipelines.

### Shared AI Capabilities Owned by Yasin-AI
- Model/provider abstraction & provider routing
- Inference services
- Embeddings generation
- Semantic retrieval & Knowledge/RAG
- Durable AI memory contracts
- AI extension/plugin contracts
- AI observability hooks
- AI API/SDK contracts
- Provider reliability and fallback policies

---

## 3. Subsystem Breakdown & Key Classes

### A. Core Runtime (`yasinai/core/`)
The central execution layer orchestrating the system lifecycle.
- **`runtime.py`**: Orchestrates `Runtime` flow (Startup -> Bootstrap -> Initialization -> Module Registration -> Ready).
- **`system.py`**: Manages system state (`SystemInfo`) and service discovery (`ServiceRegistry`).
- **`bootstrap.py`**: Dynamically discovers and loads configured system modules via `Bootstrap`.
- **`config.py`**: Processes runtime settings, configuration options, and system defaults via `Config`.

### B. Developer Platform (`developer_platform/`)
Provides extension points and local SDK interfaces.
- **`agent.py`**: Houses the local `Agent` and `AgentSDK` (manages registration and lifecycles of local agents).
- **`app.py`**: Houses `AIApplication` (chains agents and plugins) and `AppSDK`.
- **`plugin.py`**: Implements the extensible `Plugin` and `PluginSDK`.
- **`debugger.py`**: Implements runtime tracing and logging via `Debugger`.
- **`profiler.py`**: Benchmarking utility `Profiler` for execution times.
- **`generator.py`**: Generates scaffolding for local plugins/agents.
- **`package_builder.py`**: Local package/plugin distribution helpers.

### C. CLI System (`yasinai/cli/`)
Local CLI management interface (command surface is `yasin`).
- **`main.py`**: Command routing, argument parsing, output formatters (including `--json`), and runtime binding.
- **Commands**:
  - `yasin status`: Runtime diagnostics.
  - `yasin agent create`: Local agent scaffolding.
  - `yasin memory search`: Local semantic search over Retriever.
  - `yasin security check`: Local security policy validation.
  - `yasin package build`: Deployment artifact generation.

### D. Security Platform (`security_platform/`)
Hardens the platform identity, credentials, and message validation.
- **`identity.py`**: Manages profile and RBAC schemas (`IdentityManager`).
- **`auth.py`**: Implements session state validation (`AuthManager`).
- **`authorization.py`**: Implements access policies (`PolicyEngine`, `PermissionManager`).
- **`encryption.py`**: Implements cryptographic functions (custom HMAC-SHA256 stream/XOR construction).
- **`monitoring.py`**: Audits runtime threats and events (`SecurityMonitor`).
- **`scanner.py`**: Performs local vulnerability scans (`SecurityScanner`).

### E. Knowledge Platform (`knowledge_platform/`)
Underpins local memory, knowledge retrieval, and rule execution.
- **`memory.py`**: Manages process memory (`MemoryManager`).
- **`triple_store.py`**: Indexes semantic relationships (`TripleStore`).
- **`graph.py`**: Coordinates concept linkages (`KnowledgeGraph`).
- **`query_engine.py`**: Runs structured queries over graphs (`QueryEngine`).
- **`semantic_search.py`**: Implements TF-IDF vector math and retrieval pipelines (`Retriever`, `EmbeddingEngine`, `VectorStore`).
- **`context.py`**: Dynamically assembles context for LLM execution (`ContextBuilder`).
- **`reasoning.py`**: Applies logical deductions on triples (`KnowledgeReasoner`, `RuleEngine`).

### F. Deployment System (`yasinai/deployment/`)
Generates deployment bundles and manages container smoke verifications.
- **`installer.py`**: Directs environment prerequisite checks and templates setup (`Installer`).
- **`docker_manager.py`**: Validates container compose files (`DockerManager`).
- **`package_builder.py`**: Bundles runtime source into deployable archives.
- **`health_check.py`**: Periodic diagnostics check (`HealthCheck`).

---

## 4. Capability Categorization & Project Boundaries

To maintain source-of-truth accuracy, capabilities are strictly categorized to avoid confusing working components with future contracts:

### IMPLEMENTED
- **Modular Runtime & Lifecycle**: Dynamic module bootstrapping and graceful state transitions.
- **Local SQLite Persistence**: SQLite-backed semantic vector storage for stable local memory retrieval.
- **In-process Plugin Extension**: Explicit registration and hot-toggling of trusted code in-process.
- **Local CLI Commands**: Diagnosis, status verification, and semantic search helpers.
- **API Service Layer**: Transport-neutral service interface and model definitions.
- **Metrics Observability**: Cross-cutting instrumentation timers and counters.

### CURRENT ARCHITECTURE
- Single-process focus with clear internal component layering.
- Configurable data directories and SQLite paths.
- Trusted plugin model (assumes running code is secure).

### PLANNED
- **Remote Plugin Sandboxing**: Isolated execution of untrusted external plugins.
- **Multi-provider Routing**: Automatic routing, retries, and fallback across cloud LLM providers.
- **Advanced Guardrails**: Dynamic safety policies run before model inference.

### FUTURE ECOSYSTEM CONTRACT
- **Ecosystem Observability**: Exposing metrics to `YasinHub`.
- **Ecosystem Agent Orchestration**: Delegating planning and workflow semantics to `Yasin-Agent`.
- **Unified Command Center**: Integrating local subcommands into `YasinCLI`.

---

## 5. Security Boundary & Limitations

- **Secrets Management**: Secrets are runtime configurations and must never be committed to source control.
- **In-process Trust**: The execution environment does not sandbox third-party plugin code. Only run trusted plugins.
- **No HA/Distribution**: The local SQLite storage is not designed as a highly available multi-node store.

---

## 6. Testing Architecture

Testing layers (implemented in `tests/`):
- `test_runtime.py`: Verifies configuration and bootstrap orchestration.
- `test_cli.py`: Verifies command options and JSON/text printing.
- `test_developer_platform.py`: Tests SDK plugin loading, generator, and debugger tracking.
- `test_security_platform.py`: Verifies encryption, identity management, and RBAC policies.
- `test_knowledge_platform.py`: Tests semantic search, knowledge graphs, and reasoning.
- `test_deployment.py`: Tests automated installers and docker configuration checks.
