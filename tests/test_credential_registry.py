from pathlib import Path

from yasinai.gateway.token_import import TokenImportBridge
from yasinai.gateway.token_validation import TokenValidationBridge
from yasinai.providers.validation import ValidationResult
from yasinai.services.credential_registry import CredentialRegistry


class StubBridge(TokenValidationBridge):
    def __init__(self, result):
        self.result = result
        self.allowed_origin = "http://localhost"
        self.bridge_token = "bridge"

    def validate(self, payload):
        return {"provider": payload["provider"], "health": self.result.public_dict()}


def test_healthy_import_is_persisted_and_redacted(tmp_path: Path):
    value = "credential-value-1"
    registry = CredentialRegistry(tmp_path / "credentials.json")
    bridge = TokenImportBridge(
        validation_bridge=StubBridge(ValidationResult(True, True, 200, None, None, 4, {"models": ["gpt-test"]})),
        registry=registry,
    )
    status, response = bridge.import_credential({"provider": "openai", "credential": value, "model": "gpt-test", "label": "primary"})
    assert status == 200
    assert response["imported"] is True
    assert value not in str(response)
    assert registry.get_credential(response["credential"]["id"]) == value
    assert registry.list_public() == [{
        "id": response["credential"]["id"],
        "provider": "openai",
        "model": "gpt-test",
        "label": "primary",
        "metadata": {},
    }]
    assert (tmp_path / "credentials.json").stat().st_mode & 0o777 == 0o600


def test_duplicate_import_is_idempotent(tmp_path: Path):
    registry = CredentialRegistry(tmp_path / "credentials.json")
    bridge = TokenImportBridge(
        validation_bridge=StubBridge(ValidationResult(True, True, 200)),
        registry=registry,
    )
    value = "credential-value-2"
    payload = {"provider": "openai", "credential": value}
    assert bridge.import_credential(payload)[1]["imported"] is True
    status, response = bridge.import_credential(payload)
    assert status == 200
    assert response["imported"] is False
    assert response["idempotent"] is True
    assert len(registry.list_public()) == 1


def test_unhealthy_credential_is_not_persisted(tmp_path: Path):
    registry = CredentialRegistry(tmp_path / "credentials.json")
    bridge = TokenImportBridge(
        validation_bridge=StubBridge(ValidationResult(True, False, 401, "UNAUTHORIZED", "rejected")),
        registry=registry,
    )
    value = "credential-value-3"
    status, response = bridge.import_credential({"provider": "openai", "credential": value})
    assert status == 422
    assert response["error"]["type"] == "credential_not_healthy"
    assert registry.list_public() == []


def test_import_rejects_validation_error_even_when_authenticated(tmp_path: Path):
    registry = CredentialRegistry(tmp_path / "credentials.json")
    bridge = TokenImportBridge(
        validation_bridge=StubBridge(ValidationResult(True, True, 200, "MODEL_NOT_FOUND", "missing")),
        registry=registry,
    )
    value = "credential-value-4"
    status, _ = bridge.import_credential({"provider": "openai", "credential": value})
    assert status == 422
    assert registry.list_public() == []


def test_secret_never_appears_in_public_record(tmp_path: Path):
    registry = CredentialRegistry(tmp_path / "credentials.json")
    value = "credential-value-5"
    record, _ = registry.import_credential(provider="openai", credential=value, metadata={"source": "token-manager"})
    assert "credential" not in record
    assert "credential-value-5" not in str(record)
