"""Secure Token Manager -> Yasin-AI credential import bridge."""
from __future__ import annotations

from typing import Any

from yasinai.gateway.token_validation import TokenValidationBridge
from yasinai.services.credential_registry import CredentialRegistry


class TokenImportBridge:
    def __init__(
        self,
        *,
        validation_bridge: TokenValidationBridge,
        registry: CredentialRegistry | None = None,
    ) -> None:
        self.validation_bridge = validation_bridge
        self.registry = registry or CredentialRegistry()

    def import_credential(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        provider = str(payload.get("provider") or "").strip().lower()
        credential = payload.get("credential")
        if not provider or not isinstance(credential, str) or not credential:
            return 400, {"error": {"message": "provider and credential are required", "type": "invalid_request_error"}}

        validation = self.validation_bridge.validate(payload)
        health = validation.get("health") if isinstance(validation, dict) else None
        if not isinstance(health, dict):
            return 502, {"error": {"message": "credential validation failed", "type": "provider_error"}}
        if health.get("authenticated") is not True or health.get("error_code") is not None:
            return 422, {
                "error": {
                    "message": "credential is not healthy and was not imported",
                    "type": "credential_not_healthy",
                    "health": health,
                }
            }

        metadata = payload.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            return 400, {"error": {"message": "metadata must be an object", "type": "invalid_request_error"}}
        metadata = dict(metadata or {})
        base_url = payload.get("baseUrl") or payload.get("base_url")
        if base_url:
            metadata["base_url"] = str(base_url).strip()

        public_record, created = self.registry.import_credential(
            provider=provider,
            credential=credential,
            model=payload.get("model"),
            label=payload.get("label"),
            metadata=metadata,
        )
        return 200, {
            "imported": created,
            "idempotent": not created,
            "credential": public_record,
            "health": health,
        }
