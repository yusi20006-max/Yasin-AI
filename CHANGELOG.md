# YasinAI Changelog

All notable changes to the YasinAI project will be documented in this file.

---

## [1.0.0] - 2026-07-25

### Added

#### Core Runtime
- Central orchestrator initialization and modular module loading lifecycle.
- Integrated system discovery and bootstrap configurations.

#### Knowledge Platform (Issue #4)
- **Memory System**: Implemented in-memory `ShortTermMemory` and persistent JSON-based `LongTermMemory` unified by `MemoryManager`.
- **Knowledge Graph**: Implemented `Entity`, `Relation`, and directed triple storage (`KnowledgeGraph`) with neighbor lookup and BFS-based pathfinding `QueryEngine`.
- **Semantic Search**: Developed localized `LocalSemanticRetriever` using custom TF-IDF calculations and Cosine Similarity.
- **Context Engine**: Added structured context compiling via `ContextBuilder` and `FormattedContext` for prompt assembly.
- **CLI Command**: Tied local semantic search capabilities to `yasin memory search <query>`.

#### Developer Platform (Issue #5)
- **Agent SDK**: Provided a flexible base `Agent` container with runtime state transitions and lifecycle hooks (`on_init`, `on_start`, `on_stop`).
- **Plugin SDK**: Implemented `Plugin` with loading/unloading hooks and generic dynamic action execution.
- **Application SDK**: Built unified application orchestration for registering, configuring, and executing multiple agents/plugins simultaneously.
- **Generator**: Scaffolded new custom developer agent packages.
- **Package Builder**: Added local zip bundle compression and structure validation routines.
- **CLI Commands**: Integrated `yasin agent create` and `yasin package build`.

#### Deployment System (Issue #6)
- **Installer**: Configured pre-requisite environment checks and automated `config.json` initialization.
- **Docker Manager**: Configured containerized environments detection and configuration helper generation.
- **Package Builder**: Handled full release workspace structure scanning and secure zip building.
- **Health Check**: Added end-to-end status reporting over Core, Knowledge, and Developer platforms.
- **Dockerization**: Provided a minimal, production-ready `Dockerfile` and `requirements.txt`.
- **CLI Commands**: Integrated `yasin health check` diagnostics report command.

### Testing Status
- Added comprehensive unit and integration tests under `tests/test_knowledge.py`, `tests/test_developer.py`, and `tests/test_deployment.py`.
- 100% test coverage over platform components, interface models, and CLI subcommands. All 29 tests pass successfully.
