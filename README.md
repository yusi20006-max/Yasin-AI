# Yasin-AI

Canonical AI Platform of the Yasin Ecosystem.

Yasin-AI v1.1.4 provides shared AI capabilities while maintaining explicit boundaries with Yasin-Core, Yasin-Agent, YasinHub, YasinCLI and the Relay/Feed/Press domain platforms.

**Current code line: v1.1.4**

## Status

**Stable foundation / READY FOR CONTROLLED INTEGRATION.**

The current line includes runtime, provider abstraction and concrete adapters, bounded retry/fallback, generation and RAG service boundaries, persistent local memory/knowledge, security, observability, packaging, CI and production container hardening.

This is not a distributed HA platform and does not sandbox untrusted plugins.

## Current capabilities

### Runtime
- Modular lifecycle/bootstrap/configuration
- Service registration and controlled shutdown

### Providers and AI services
- Provider abstraction
- OpenAI, Anthropic and Local adapters
- Provider factory
- Bounded retry/fallback
- Explicit provider/model selection with model-constraint preservation
- GenerationService and public request/result contracts
- RagService and public RAG contracts

### Knowledge and Memory
- Semantic search and retrieval
- Knowledge graph/reasoning
- SQLite-backed vector and memory persistence
- WAL/busy-timeout concurrency hardening

**Contract distinction:** Knowledge is information/content about the world or corpus. Memory is state associated with an interaction, entity or agent.

### Security
- Authentication and authorization
- Encryption/key handling
- Repository security scanner
- Input/path safety limits
- Provider credential environment isolation
- Internal error redaction
- Trusted in-process plugin boundary
- Canonical scanner-backed `security check`

### Deployment and quality
- Production Docker hardening
- Non-root execution, reduced capabilities and read-only production profile where supported
- Python 3.9–3.12 CI matrix
- Ruff
- pip-audit
- Security gate
- Docker build/smoke validation

## Provider routing: implemented vs planned

**Implemented:** provider abstraction, provider selection, concrete adapters, bounded retry/fallback, explicit provider pinning and model-constraint preservation.

**Planned:** cost-aware routing, health-aware load balancing, policy-aware orchestration and automatic multi-node failover.

## Architecture boundaries

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
Concrete storage/provider implementations
```

Consumers must not depend on private implementation modules, SQLite internals, provider-specific clients or local CLI internals.

## Installation

```bash
git clone https://github.com/yusi20006-max/Yasin-AI.git
cd Yasin-AI
python -m pip install -e .
```

## Verification

```bash
python -m pytest -q
pip-audit
python -m build
```

Canonical security verification:

```bash
yasin security check
python -m yasinai.cli security check
```

Both paths use the same canonical `SecurityScanner` semantics.

## Persistence and availability

The default persistence model is local SQLite. Yasin-AI does not currently claim:

- Distributed/high-availability storage
- Automatic multi-node failover
- Sandboxed execution of untrusted plugins

These are explicit product boundaries, not hidden failures.

## Ecosystem integration

v1.1.4 is suitable for controlled integration. Before broad migration, consuming repositories must verify public capability contracts and architecture boundaries. The integration target is Yasin-AI's public contracts, not its private implementation tree.

## Planned

- Untrusted plugin sandboxing
- Advanced provider routing and load balancing
- Distributed/HA persistence
- Advanced inference guardrails
- Ecosystem observability adapters
- Unified command-center integration through YasinCLI

## Release history

- **v1.1.4** — Current code line; security/correctness/CI hardening
- **v1.1.3** — Provider, RAG, Docker, plugin, input, SQLite and CI hardening
- **v1.1.2** — Packaging, persistence and version-contract fixes
- **v1.1.1** — Capability contracts, providers/services and ecosystem integration clients
- **v1.1.0** — Architecture/documentation maintenance baseline
- **v1.0.0** — Initial production baseline

See `CHANGELOG.md`, `VERSIONING_POLICY.md`, `docs/ARCHITECTURE.md` and `AI_CAPABILITY_CATALOG.md` for canonical detail.

## Security

Report security issues according to `SECURITY.md`. Never commit credentials or secrets.

## License

MIT
