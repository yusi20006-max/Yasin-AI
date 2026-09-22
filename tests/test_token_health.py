from yasinai.providers.validation import ValidationResult
from yasinai.services.token_health import HealthState, TokenHealthEngine

def test_health_engine_maps_success_and_auth_failures():
    assert TokenHealthEngine(lambda _: ValidationResult(True, True, 200)).check("x").state is HealthState.HEALTHY
    r=TokenHealthEngine(lambda _: ValidationResult(True, False, 401, "UNAUTHORIZED", "rejected")).check("x")
    assert r.state is HealthState.QUARANTINED and r.quarantine

def test_health_engine_maps_transient_and_unknown_failures():
    r=TokenHealthEngine(lambda _: ValidationResult(True, None, 429, "RATE_LIMITED", "limited")).check("x")
    assert r.state is HealthState.COOLDOWN and r.retryable
    r=TokenHealthEngine(lambda _: ValidationResult(None, None, error_code="UNKNOWN", error_message="unknown")).check("x")
    assert r.state is HealthState.UNKNOWN
