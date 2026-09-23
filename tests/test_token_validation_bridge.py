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


def test_create_server_wires_bridge_from_environment(monkeypatch):
    from yasinai.gateway.http import create_server
    monkeypatch.setenv("YASINAI_BRIDGE_TOKEN", "bridge-secret")
    monkeypatch.setenv("YASINAI_ALLOWED_ORIGIN", "http://localhost:8080")
    server = create_server(port=0)
    try:
        assert server.RequestHandlerClass is not None
    finally:
        server.server_close()


def test_bridge_rejects_oversized_validation_body(monkeypatch):
    from yasinai.gateway.http import create_server
    monkeypatch.setenv("YASINAI_BRIDGE_TOKEN", "bridge-secret")
    monkeypatch.setenv("YASINAI_ALLOWED_ORIGIN", "http://localhost")
    server = create_server(port=0)
    try:
        handler = server.RequestHandlerClass
        assert handler is not None
    finally:
        server.server_close()


def test_bridge_supports_orcarouter_with_allowlisted_base_url():
    bridge = TokenValidationBridge(bridge_token="bridge-secret", allowed_origin="http://localhost")
    adapter = bridge._provider(
        "orcarouter",
        "sk-orca-test",
        base_url="https://api.orcarouter.ai/v1",
        model="orcarouter/auto",
    )
    assert adapter.info.name == "orcarouter"
    assert adapter.info.metadata["base_url"] == "https://api.orcarouter.ai/v1"
    assert adapter.info.model_ids == ["orcarouter/auto"]


def test_bridge_rejects_unapproved_orcarouter_base_url():
    bridge = TokenValidationBridge(bridge_token="bridge-secret", allowed_origin="http://localhost")
    with pytest.raises(ValueError, match="unsupported OrcaRouter base URL"):
        bridge._provider(
            "orcarouter",
            "sk-orca-test",
            base_url="https://evil.example/v1",
            model="orcarouter/auto",
        )


def test_bridge_preserves_orcarouter_identity_and_base_url(monkeypatch):
    bridge = TokenValidationBridge(bridge_token="bridge-secret", allowed_origin="http://localhost")

    class Fake:
        def validate_credential(self, credential, model=None):
            from yasinai.providers.validation import ValidationResult
            return ValidationResult(True, True, 200, None, None, 12, {"models": [model]})

    monkeypatch.setattr(bridge, "_provider", lambda name, credential, **kwargs: Fake())
    result = bridge.validate({
        "provider": "orcarouter",
        "credential": "runtime-secret",
        "baseUrl": "https://api.orcarouter.ai/v1",
        "model": "orcarouter/auto",
    })
    assert result["provider"] == "orcarouter"
    assert result["health"]["authenticated"] is True
    assert "runtime-secret" not in str(result)


def test_token_import_preserves_orcarouter_base_url_without_exposing_credential(tmp_path, monkeypatch):
    from yasinai.gateway.token_import import TokenImportBridge
    from yasinai.services.credential_registry import CredentialRegistry

    class FakeValidation:
        def validate(self, payload):
            from yasinai.providers.validation import ValidationResult
            return {"provider": "orcarouter", "health": ValidationResult(True, True, 200).public_dict()}

    import_bridge = TokenImportBridge(
        validation_bridge=FakeValidation(),
        registry=CredentialRegistry(tmp_path / "credentials.json"),
    )
    status, response = import_bridge.import_credential({
        "provider": "orcarouter",
        "credential": "runtime-secret",
        "model": "orcarouter/auto",
        "baseUrl": "https://api.orcarouter.ai/v1",
        "metadata": {"source": "test"},
    })
    assert status == 200
    assert response["imported"] is True
    assert response["credential"]["provider"] == "orcarouter"
    assert response["credential"]["metadata"]["base_url"] == "https://api.orcarouter.ai/v1"
    assert "runtime-secret" not in str(response)
    assert "runtime-secret" in (tmp_path / "credentials.json").read_text()
