import pytest
from yasinai.gateway.token_validation import TokenValidationBridge

def test_bridge_requires_explicit_token():
    with pytest.raises(ValueError): TokenValidationBridge(bridge_token=None, allowed_origin="http://localhost")

def test_bridge_authorizes_exact_origin_and_token():
    bridge=TokenValidationBridge(bridge_token="bridge-secret", allowed_origin="http://localhost:8080")
    assert bridge.authorize({"X-YasinAI-Bridge-Token":"bridge-secret"}, "http://localhost:8080")
    assert not bridge.authorize({"X-YasinAI-Bridge-Token":"bridge-secret"}, "http://evil.example")
    assert not bridge.authorize({"X-YasinAI-Bridge-Token":"wrong"}, "http://localhost:8080")

def test_bridge_validation_output_does_not_echo_credential(monkeypatch):
    bridge=TokenValidationBridge(bridge_token="bridge-secret", allowed_origin="http://localhost")
    class Fake:
        def validate_credential(self, credential, model=None):
            from yasinai.providers.validation import ValidationResult
            return ValidationResult(True, True, 200)
    monkeypatch.setattr(bridge, "_provider", lambda name, credential: Fake())
    result=bridge.validate({"provider":"openai","credential":"runtime-secret"})
    assert "runtime-secret" not in str(result)
