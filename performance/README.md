# Performance and reliability baseline

Phase 14 establishes a dependency-free performance contract.

## Reliability rules

- Keep startup and shutdown idempotent.
- Avoid network calls in constructors.
- Reuse durable resources and close them deterministically.
- Bound collections and queues that accept external input.
- Prefer lazy initialization for optional subsystems.
- Keep observability instrumentation thread-safe and low overhead.
- Every optimization that changes behavior must have a regression test.

## Measurement

`observability.metrics` provides lightweight counters and timers for service instrumentation without coupling the application to a monitoring vendor. Benchmarking belongs in CI/release validation rather than in production hot paths.

## Phase 14 acceptance criteria

- Concurrent metric updates do not lose increments.
- Timing instrumentation records both successful and failed calls.
- Decorated callables retain their name and docstring.
- No new runtime dependency is required for the performance layer.
