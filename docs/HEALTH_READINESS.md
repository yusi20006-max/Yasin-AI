# Health, Readiness, and Graceful Shutdown

**Platform:** Yasin-AI 1.1.4

## Runtime probes

| Probe | API | Meaning |
|---|---|---|
| Liveness / readiness | `Runtime.is_ready()` | `True` only in `READY` state |
| Structured readiness | `Runtime.readiness()` | state, version, services, last_error |
| Graceful shutdown | `Runtime.shutdown()` | Idempotent; unregisters services |

## Deployment health

`yasinai.deployment.health_check.HealthCheck.run_all_checks()` aggregates runtime/CLI/security/knowledge checks and reports `HEALTHY` or `DEGRADED`.

## API

`APIService.health()` → `{"status":"ok","service":"yasinai","version":...}`

## Verification

`tests/test_health_readiness_shutdown.py`
