# Performance baseline

Phase 14 establishes a lightweight, dependency-free performance contract. Runtime code must avoid unbounded in-memory caches, repeated initialization, and unnecessary work on hot paths. Performance measurements belong outside core business logic.

The existing `observability.metrics` primitives provide counters/timers for future benchmarks without forcing a monitoring vendor into the application.

## Reliability rules

- Bound collections and queues when accepting external input.
- Reuse durable storage connections where appropriate; close them deterministically.
- Keep startup idempotent.
- Avoid network calls in constructors.
- Prefer lazy work for optional subsystems.
- Add regression tests for every performance optimization that changes behavior.
