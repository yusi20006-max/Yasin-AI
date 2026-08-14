# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [1.1.1] - 2026-08-14

### Added
- Phase 2: capability catalog, contracts v1, provider architecture boundary, memory/knowledge service facade, CI coverage gate.
- Phase 3: OpenAI/Anthropic/Local providers, GenerationService, RagService and public contracts.
- Phase 4: ecosystem integration clients for Agent, Hub, CLI, Relay, Feed, Press.
- Phase 5: production profile static gates, plugin trust policy (trusted-only registry), production readiness tests.

### Security
- PluginRegistry rejects untrusted plugins by default (`PluginTrustError`).
- Production Dockerfile non-root + HEALTHCHECK; compose production hardening verified by tests.

### Changed
- `yasin memory search` routes through `YasinCLIClient` / services boundary.
- Platform version bumped to 1.1.1.

## [1.1.0] - 2026-08-12

### Added
- Standardized post-release maintenance policy (`MAINTENANCE.md`).
- Dependency vulnerability audit gate in the CI workflow.
- High-level system architecture and ecosystem boundaries documentation (`docs/ARCHITECTURE.md`).
- Unified metrics and instrumentation timer/counter checks in tests.
- Reconciled code version and package metadata to `1.1.0` across the codebase.
- Resolved and unified version contradiction across platform files.

## [1.0.0] - 2026-08-09

### Added
- Hardened modular runtime and deterministic lifecycle management.
- Persistent SQLite-backed long-term memory and semantic retrieval.
- Developer plugin SDK and deterministic plugin registry.
- Transport-neutral API/service layer.
- Dependency-free observability metrics.
- Hardened container deployment baseline.
- Security policy, dependency audit gate, and final security audit record.
- Release-candidate verification and production release documentation.

### Security
- Dependency auditing is enforced in CI.
- Secret-like files are rejected by CI checks.
- Production container uses a non-root runtime, read-only root filesystem, dropped capabilities, and `no-new-privileges`.

### Known limitations
- Plugins are trusted and execute in-process.
- Local SQLite persistence is not a distributed high-availability datastore.
- Production infrastructure security remains the responsibility of the deployment environment.
