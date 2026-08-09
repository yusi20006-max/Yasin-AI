# Yasin-AI Architecture

## Overview

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

## Boundaries

- **Runtime** owns lifecycle and module orchestration.
- **Knowledge Platform** owns retrieval, embeddings, graph/reasoning primitives.
- **Memory Platform** owns durable long-term memory abstractions and storage.
- **Developer Platform** exposes stable extension contracts without forcing global registration.
- **API Service Layer** owns transport-neutral request dispatch and response/error contracts.
- **Observability** provides metrics primitives without coupling core code to a monitoring vendor.
- **Deployment** contains container/runtime configuration and persistent-volume policy.

## Dependency direction

Higher-level adapters may depend on lower-level contracts, but core modules must not import deployment-specific or vendor-specific code. Persistence and transport are replaceable boundaries.

## Security boundary

Secrets are runtime configuration, not source-controlled application state. Plugin execution is currently in-process; sandboxing and authorization must be added before accepting untrusted remote plugins.

## Persistence

SQLite is the default local persistence implementation for memory and semantic indexes. Storage paths are configurable. The application should interact with storage through interfaces/manager classes rather than hard-coding database details in business logic.

## API and deployment

The service layer is transport-neutral. HTTP or other network transports should adapt into the service layer rather than become part of core business logic. Production deployment is containerized with a read-only root filesystem and a dedicated writable data volume.

## Extension policy

New features should prefer narrow interfaces and adapters. Avoid adding framework dependencies to core packages unless the dependency provides a clear architectural benefit and has an explicit lifecycle/maintenance owner.
