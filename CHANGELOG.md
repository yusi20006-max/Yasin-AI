# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [1.1.4] - 2026-08-15

### Fixed
- Final audit gaps: preserve requested model across provider fallback; redact internal exceptions from GenerationResult/RagResult errors; PackageBuilder path-traversal guard (#124)

## [1.1.3] - 2026-08-15

### Fixed
- ProviderRouter fails explicitly on unmatched model (#93)
- Provider HTTP bodies redacted from exception messages (#94)
- DockerManager cannot clobber production Docker files (#95)
- Legacy PluginSDK trust-boundary bypass closed (#96)
- RAG prompt trust boundary against indirect injection (#97)
- APIService maps unhandled exceptions to standard errors (#98)
- PackageBuilder produces a real deployment archive (#99)
- GenerationService bounded provider retry/fallback (#109)
- Upper bounds on unbounded numeric inputs (#111)
- SQLite WAL mode and busy_timeout in knowledge stores (#113)

### Changed
- Ruff lint backlog cleared; CI lint is blocking (#115, #116)
- GitHub Actions majors updated (checkout@v7, upload-artifact@v5) (#120)
- Docker CI deduplicated — docker-build.yml tag/manual only (#119)

## [1.1.2] - 2026-08-15

### Fixed
- Release tag/README version drift: official release now includes Docker hardening (#89), persistent memory/vector storage (#90), and Python version contract fix (#91).
- Installer default config no longer hardcodes `version = "1.0.0"`; reads package version dynamically.
- README current-release claims aligned with `pyproject.toml` (**v1.1.2**).

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
