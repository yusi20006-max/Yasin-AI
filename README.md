# Yasin-AI

Production-ready AI platform focused on modular runtime services, persistent memory, knowledge retrieval, developer extensions, observability, and secure deployment.

**Current release: v1.1.0**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Status

Yasin-AI has completed its initial architecture and production-hardening cycle.

- Production release: **v1.1.0**
- Security audit: completed
- Release candidate verification: completed
- Performance/reliability baseline: completed
- Production deployment baseline: completed
- Post-release maintenance policy: established

See the [latest release](https://github.com/yusi20006-max/Yasin-AI/releases/tag/v1.1.0).

## Architecture

The project is organized around clear boundaries between:

- Runtime orchestration
- API/service layer
- Knowledge and retrieval
- Persistent memory
- Developer/plugin platform
- Observability
- Deployment and infrastructure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the current architecture and dependency boundaries.

## Core capabilities

### Runtime

- Modular runtime lifecycle
- CLI-oriented operation
- Explicit configuration and lifecycle management
- Dependency-light core components

### Memory and Knowledge

- Persistent local memory
- SQLite-backed storage
- Semantic/knowledge-oriented components
- Replaceable persistence boundaries

### Developer Platform

- Extension/plugin interfaces
- Narrow contracts for integrations
- Developer-facing service boundaries

### API and Services

- Transport-neutral service layer
- API-oriented request/response boundaries
- Centralized error handling

### Observability

- Dependency-free counters and timers
- Runtime instrumentation primitives
- Performance/reliability regression coverage

### Security

- Security policy and audit documentation
- Dependency security auditing
- Hardened production container baseline
- Non-root container execution
- Reduced Linux capabilities
- no-new-privileges
- Read-only root filesystem where supported

See [SECURITY.md](SECURITY.md) and [SECURITY_AUDIT_2026-08-09.md](SECURITY_AUDIT_2026-08-09.md).

## Installation

Clone the repository:

    git clone https://github.com/yusi20006-max/Yasin-AI.git
    cd Yasin-AI

For the current production version:

    git checkout v1.1.0

Install the project using the repository's supported Python packaging configuration.

## Verification

Before deploying a release, run:

    python -m pytest -q
    pip-audit
    python -m build

Container deployments should additionally verify the production compose profile and healthcheck in the target environment.

## Release history

- **v1.1.0** — Current production release
- **v1.0.0** — Previous production release

See the complete [release history](https://github.com/yusi20006-max/Yasin-AI/releases).

## Security

Security issues should be reported according to the project's security policy rather than through public issue disclosure.

See [SECURITY.md](SECURITY.md).

Important current security boundary:

> Plugin execution is trusted and in-process. Untrusted remote plugin execution is not currently supported and requires a future sandbox/authorization layer.

## Persistence and availability

The default persistence model is local SQLite-backed storage.

Yasin-AI does not currently claim:

- Distributed/high-availability storage
- Automatic multi-node failover
- Sandboxed execution of untrusted plugins

These limitations are intentional and documented rather than hidden.

## Production deployment

Production deployment guidance and hardening are documented in the repository deployment configuration and release documentation.

The release candidate and production baseline are documented in:

- [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md)
- [PRODUCTION_RELEASE.md](PRODUCTION_RELEASE.md)
- [MAINTENANCE.md](MAINTENANCE.md)

## Development

Create a feature branch before making changes:

    git checkout -b feat/my-change

Run the verification suite:

    python -m pytest -q
    pip-audit
    python -m build

Then submit changes through a pull request.

## Versioning

Yasin-AI follows semantic versioning for releases.

- Patch releases: backward-compatible fixes
- Minor releases: backward-compatible features
- Major releases: breaking changes

Existing release tags are immutable. A new release receives a new version tag rather than moving an existing tag.

## License

MIT
