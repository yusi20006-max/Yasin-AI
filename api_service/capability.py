"""Versioned Yasin-AI capability service contract.

This module is the transport-neutral public boundary used by adapters such as
HTTP, CLI, or in-process integration clients. Provider implementations remain
private to Yasin-AI.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from yasinai.contracts import GenerationRequest
from yasinai.services.generation_service import GenerationService

from .app import APIService
from .errors import ValidationError

CONTRACT_VERSION = "v1"
GENERATION_PATH = f"/{CONTRACT_VERSION}/generation"
CAPABILITIES_PATH = f"/{CONTRACT_VERSION}/capabilities"


def create_capability_service(
    *,
    generation: GenerationService | None = None,
    name: str = "yasinai",
    version: str = "1.1.4",
) -> APIService:
    """Create an API service exposing the stable v1 capability boundary."""
    generation_service = generation if generation is not None else GenerationService()
    service = APIService(name=name, version=version)

    def capabilities(_: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "contract_version": CONTRACT_VERSION,
            "service": name,
            "version": version,
            "capabilities": ["generation"],
        }

    def generate(payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValidationError("request body must be an object")

        request = GenerationRequest(
            prompt=_required_string(payload, "prompt"),
            model=_optional_string(payload, "model"),
            provider=_optional_string(payload, "provider"),
            system_prompt=_optional_string(payload, "system_prompt"),
            max_tokens=_bounded_int(payload, "max_tokens", 1, GenerationRequest.MAX_TOKENS_LIMIT, 1024),
            temperature=_bounded_float(payload, "temperature", 0.0, 2.0, 0.7),
            stop_sequences=_string_list(payload, "stop_sequences"),
            metadata=_metadata(payload.get("metadata")),
        )
        result = generation_service.generate(request)
        return {
            "contract_version": CONTRACT_VERSION,
            "success": result.success,
            "text": result.text,
            "model": result.model,
            "provider": result.provider,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "finish_reason": result.finish_reason,
            "error": result.error,
        }

    service.add_route("GET", CAPABILITIES_PATH, capabilities)
    service.add_route("POST", GENERATION_PATH, generate)
    return service


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{key}' must be a non-empty string")
    return value


def _optional_string(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{key}' must be a non-empty string when provided")
    return value


def _bounded_int(
    payload: Mapping[str, Any], key: str, minimum: int, maximum: int, default: int
) -> int:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValidationError(f"'{key}' must be an integer between {minimum} and {maximum}")
    return value


def _bounded_float(
    payload: Mapping[str, Any], key: str, minimum: float, maximum: float, default: float
) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= value <= maximum:
        raise ValidationError(f"'{key}' must be a number between {minimum} and {maximum}")
    return float(value)


def _string_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValidationError(f"'{key}' must be a list of strings")
    return list(value)


def _metadata(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValidationError("'metadata' must be an object")
    return dict(value)
