from yasinai.providers.base import ProviderBase, ProviderInfo, ValidationResult

class DummyProvider(ProviderBase):
    @property
    def info(self): return ProviderInfo(name="dummy")
    def is_available(self): return True

def test_validation_result_is_secret_free_and_normalized():
    result = ValidationResult(reachable=True, authenticated=True, http_status=200, latency_ms=7, capabilities={"models":"available"})
    public = result.public_dict()
    assert public["authenticated"] is True
    assert public["http_status"] == 200
    assert public["latency_ms"] == 7
    assert "secret" not in str(public).lower()

def test_base_validation_fails_closed_without_persistence():
    result = DummyProvider().validate_credential("secret-token")
    assert result.error_code == "NOT_SUPPORTED"
    assert result.authenticated is None
    assert result.reachable is None
