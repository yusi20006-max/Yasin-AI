# Yasin-AI Canonical Architecture Reference

**Version:** 1.1.4  
**Status:** Current / source-synchronized  
**Last reconciled:** 2026-08-16

## 1. Overview

Yasin-AI is the canonical AI capability platform of the Yasin ecosystem. v1.1.4 is a production baseline for controlled integration: it provides runtime, AI services, provider abstraction/adapters, bounded retry/fallback, knowledge/RAG services, persistent memory, security, observability, packaging and deployment foundations.

It is **not** currently a distributed HA platform and does **not** sandbox untrusted plugin code.

### Current layered architecture
```text
Clients / Ecosystem Integrations
              │
              ▼
       API / SDK Contracts
              │
              ▼
          AI Runtime
              │
              ▼
         AI Services
              │
              ▼
   Provider / Knowledge / Memory
        Abstractions
          │       │
          ▼       ▼
     Providers   SQLite stores
```

## 2. Ecosystem ownership boundaries

- **Yasin-Core:** generic runtime and SDK foundations.
- **Yasin-Agent:** multi-step agent planning, reasoning loops and workflow semantics.
- **YasinHub:** ecosystem control, lifecycle and cross-cutting observability.
- **YasinCLI:** unified user-facing command surface; the local CLI in this repository remains a diagnostic/platform helper.
- **YasinRelay / YasinFeed / YasinPress:** domain and business pipelines.

External consumers must use stable public contracts rather than private implementation modules.

## 3. Current capabilities

### Runtime
- lifecycle/bootstrap/configuration
- service registration and controlled shutdown

### Provider layer
- provider abstraction and concrete OpenAI/Anthropic/Local adapters
- provider factory
- bounded retry/fallback
- explicit provider/model pinning and model-constraint preservation

**Not implemented:** cost-aware routing, health-aware load balancing and automatic multi-node failover.

### Knowledge and memory
- semantic retrieval and TF-IDF baseline
- SQLite-backed vector/knowledge persistence
- knowledge graph and reasoning primitives
- memory manager and durable local persistence
- RAG service/orchestration boundary

**Contract rule:** Knowledge means information about content/world state; Memory means interaction/entity/agent-associated state.

### Security
- authentication/authorization
- encryption/key handling
- repository security scanner
- provider credential isolation via environment configuration
- input/path limits and internal-error redaction
- trusted-plugin boundary

### Observability
- counters/timers and local metrics snapshots

## 4. Dependency direction

```text
Public API / SDK Contracts
          │
          ▼
      AI Runtime
          │
          ▼
      AI Services
          │
          ▼
Provider / Knowledge / Memory abstractions
          │
          ▼
Concrete storage and provider implementations
```

Prohibited: circular imports, CLI dependencies from runtime engines, and external consumers importing low-level storage/provider implementation details.

## 5. Current repository structure

The repository still contains capability packages such as `api_service/`, `developer_platform/`, `security_platform/`, `knowledge_platform/`, `observability/`, and the main `yasinai/` package. A namespace rewrite is **not** a v1.1.4 prerequisite; existing boundaries are treated as stable until a compatibility-preserving migration is designed.

## 6. Planned architecture

The following are future work, not claims about v1.1.4:

1. **Advanced provider routing:** cost-aware, health-aware and policy-aware routing/load balancing.
2. **Untrusted plugin sandboxing:** isolated execution with explicit authorization and resource limits.
3. **Distributed/HA persistence:** remote/distributed storage and multi-node failover.
4. **Ecosystem observability contracts:** direct YasinHub integration.
5. **Advanced agent orchestration:** owned by Yasin-Agent.
6. **Unified command center:** owned by YasinCLI.

Old Phase 2.3/2.4/2.5 roadmap labels are historical planning artifacts and must not be interpreted as evidence that the corresponding work is still unimplemented.

## 7. Production boundary

v1.1.4 is **ready for controlled ecosystem integration**, subject to contract verification by each consuming repository. It must not be described as a complete distributed ecosystem AI platform.
