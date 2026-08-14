# Yasin-AI Versioning Policy and Compatibility Model

This document defines the canonical versioning policy, release lifecycle, and compatibility model for Yasin-AI.

---

## 1. Versioning Policy

Yasin-AI strictly follows [Semantic Versioning 2.0.0 (SemVer)](https://semver.org/) for its package versions.

### 1.1. Authoritative Package Version
- **Source of Truth**: The single authoritative source of truth for the platform version is defined in the `pyproject.toml` file under the `[project]` table:
  ```toml
  [project]
  version = "1.1.0"
  ```
- **Runtime Version Retrieval**: The runtime/module version is obtained programmatically by importing the package's `__version__` attribute:
  ```python
  import yasinai
  print(yasinai.__version__)  # Output: 1.1.0
  ```
  Alternatively, for installed packages, the standard library metadata can be used:
  ```python
  import importlib.metadata
  print(importlib.metadata.version("yasinai"))  # Output: 1.1.0
  ```

### 1.2. API & Capability Contract Versioning
- **Separation of Concerns**: The Yasin-AI package version and the **AI Capability Contract version** are decoupled and must remain independently versionable.
- **Contract Versioning**: The AI Capability Contract version (e.g., `v1`) represents the public request/response structures, stable endpoints, and in-process SDK integration points.
- **Mapping/Compatibility Rule**:
  - **Yasin-AI package (1.x.y)** implements **AI Capability Contract (v1)**.
  - A major version increment of the package does not automatically force a major increment of the AI Capability Contract unless breaking API wire contracts are introduced.

### 1.3. Release Tagging and Immutable Tags
- **Tag Format**: Releases are tagged using a standard Git tag prefixed with `v` (e.g., `v1.1.0`).
- **Tag Immutability**: Existing release tags are strictly **immutable**. Under no circumstances should an existing release tag be deleted or moved to a different commit. If a release contains a regression, a new patch release (e.g., `v1.1.1`) or hotfix must be cut.
- **Release Commits**: Tags must point at the exact commit on `main` that passed all CI quality, security, and test gates.

### 1.4. Unreleased & Pre-Release Representation
- **Unreleased / Development Changes**:
  - During active development on a release line, the development version is suffixed with `-dev` or `.dev0` (e.g., `1.1.1-dev` or `1.2.0-dev`).
  - This signifies that the code represents unreleased changes post the last stable release.
- **Pre-Releases / Release Candidates**:
  - Formal release previews are represented using standard SemVer suffixes:
    - Alpha: `1.2.0-alpha.1`
    - Beta: `1.2.0-beta.1`
    - Release Candidate: `1.2.0-rc.1` (or `1.2.0-rc1`)

### 1.5. CHANGELOG Structure
- **Standard Format**: The project's `CHANGELOG.md` adheres to the [Keep a Changelog](https://keepachangelog.com/) format.
- **Subheadings**: Every release section must categorize changes under:
  - `Added` for new features.
  - `Changed` for changes in existing functionality.
  - `Deprecated` for soon-to-be-removed features.
  - `Removed` for now-removed features.
  - `Fixed` for any bug fixes.
  - `Security` in case of vulnerabilities or security hardening.
- **Timestamps**: Release titles must include the version and release date in `YYYY-MM-DD` format (e.g., `## [1.1.0] - 2026-08-12`).

---

## 2. Compatibility Model

### 2.1. Python & Runtime Requirements
- **Prerequisite**: Yasin-AI is declared and guaranteed compatible with Python version **`>=3.8`**.
- **Installation Verifiers**: The environment installer verifies compatibility based on `sys.version_info` mapping major/minor requirements.

### 2.2. Package and SDK Compatibility
- **Backward Compatibility**: Patch (`1.1.x`) and minor (`1.x.0`) package releases must maintain absolute backward compatibility with existing developer plugin extensions and Agent SDK clients.
- **Breaking Changes**: Breaking package or API contract changes are restricted to new major version releases (e.g., `2.0.0`).

### 2.3. Provider Routing & Compatibility
- **Gateway Abstraction**: LLM providers and semantic/embedding drivers are accessed through transport-neutral wrappers.
- **No Heavy Coupling**: System capabilities do not tightly couple with specific third-party provider versions. Vendor-specific routing is managed via configurable parameter interfaces rather than hardcoded client dependencies.

### 2.4. Persistence & Schema Compatibility
- **Local SQLite Store**: Persistent memory and semantic retrieval rely on local SQLite files.
- **Schema Migrations**:
  - Minor and patch version upgrades must not break or invalidate existing SQLite databases or table schemas.
  - If a schema evolution is required, a backward-compatible migration plan or migration helper must be provided to migrate data from the old table format to the new structure without data loss.

---

## 3. Platform Release State Registry

This registry tracks the status and classification of known versions of Yasin-AI:

| Version | Release Date | State | Classification | Description |
|---|---|---|---|---|
| **`1.1.0`** | 2026-08-12 | **Released** | Maintenance Release | Current stable production baseline. Features automated dependency audit and unified architecture docs. |
| **`1.0.0`** | 2026-08-09 | **Released** | Major Release | Historical baseline launch. Hardened core runtime, persistent memory, and security platforms. |
| **`1.1.1-dev`** | — | **Development** | Unreleased / Active | Active development stage focusing on Phase 2.3+ features and version alignment. |
| **`1.2.0`** | Planned | **Planned** | Minor Release | Planned target featuring remote plugin sandboxing, provider gateways, and model registries. |
