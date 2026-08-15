# Yasin-AI Versioning Policy and Compatibility Model

This document is the canonical versioning policy for Yasin-AI.

## 1. Versioning Policy

Yasin-AI follows Semantic Versioning (SemVer).

### 1.1 Authoritative package version
The authoritative package version is the `[project] version` in `pyproject.toml`.

**Current stable version: `1.1.4`.**

Runtime consumers should use `yasinai.__version__` or `importlib.metadata.version("yasinai")` rather than duplicating a version constant in documentation.

### 1.2 API and capability contracts
The package version and public AI capability contract versions are independently versioned. A package patch/minor release does not imply a contract-major change. Breaking public contracts require an explicitly versioned compatibility transition.

### 1.3 Release tags
Release tags use the `vX.Y.Z` format and are immutable. A tag must point to the exact release commit that passed required CI, security and deployment gates. If a released tag is incorrect, do not move it; publish a new corrective release.

### 1.4 Development and pre-release versions
Unreleased development builds use a development/pre-release identifier such as `1.2.0.dev0` or `1.2.0-rc.1`. Documentation must never describe an unreleased development line as the current stable release.

### 1.5 Changelog
`CHANGELOG.md` follows Keep a Changelog. Each release records applicable Added, Changed, Deprecated, Removed, Fixed and Security changes with a release date.

## 2. Compatibility Model

### 2.1 Python
The v1.1.4 CI matrix verifies Python 3.9, 3.10, 3.11 and 3.12. The package metadata remains authoritative for installation constraints.

### 2.2 Package and SDK compatibility
Patch releases should preserve existing public behavior. Minor releases may add backward-compatible functionality. Breaking public API changes require a major release or an explicitly documented migration.

### 2.3 Provider compatibility
Yasin-AI currently provides provider abstraction, concrete provider adapters, bounded retry/fallback behavior, explicit provider/model selection and preservation of explicit model constraints. It does **not** claim cost-aware routing, health-aware load balancing or automatic multi-node provider orchestration.

### 2.4 Persistence
The default persistence model is local SQLite. WAL and busy-timeout settings improve concurrent local access, but this is not a distributed/HA datastore. Schema changes must include a backward-compatible migration strategy where required.

## 3. Release State Registry

| Version | State | Classification | Notes |
|---|---|---|---|
| `1.1.4` | Current code line | Stable | Current implementation baseline and audit/hardening line on `main`. |
| `1.1.3` | Historical | Patch release | Provider, RAG, Docker, plugin, input-limit, SQLite and CI hardening. |
| `1.1.2` | Historical | Patch release | Packaging, persistence, Docker and version-contract fixes. |
| `1.1.1` | Historical | Feature release | Capability contracts, providers/services, ecosystem clients and production gates. |
| `1.1.0` | Historical | Maintenance release | Architecture/documentation baseline. |
| `1.0.0` | Historical | Major release | Initial production baseline. |
| `1.2.x` | Planned | Future | Advanced routing, sandboxing and other capabilities only when implemented and verified. |

## 4. Release Truth Rule

Every release-related document must distinguish **implemented/current**, **historical**, **development**, and **planned** capabilities. Older roadmap phases are historical planning artifacts unless they still describe actual remaining work.

Existing release tags are immutable. A corrective release must receive a new tag rather than rewriting an existing tag.
