"""
AnthropicProvider — Anthropic Messages API adapter.

Credentials: ANTHROPIC_API_KEY only (never hardcoded).
SDK libraries are not required at import time; HTTP transport is injectable.

Exception messages must never contain raw provider HTTP bodies or full
response payloads. Log raw details at logger.error/debug only; raise a
safe generic ProviderError message for callers / GenerationResult.error.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Callable

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)

HttpTransport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.anthropic.com"
DEFAULT_MODEL = "claude-3-5-haiku-latest"
ANTHROPIC_VERSION = "2023-06-01"


def _default_http_transport(
    url: str, headers: dict[str, str], body: dict[str, Any]
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.error(
            "Anthropic HTTP %s error (raw body withheld from exception): %s",
            exc.code,
            detail,
        )
        raise ProviderError(
            "anthropic",
            f"Anthropic request failed with HTTP {exc.code}",
            retryable=exc.code >= 500,
        ) from exc
    except urllib.error.URLError as exc:
        logger.error("Anthropic network error: %s", exc)
        raise ProviderError(
            "anthropic",
            "Anthropic network error",
            retryable=True,
        ) from exc


def _validation_result_from_exception(exc: Exception, latency_ms: int):
    from yasinai.providers.validation import ValidationResult
    import re
    message = str(exc)
    match = re.search(r"HTTP (\d{3})", message)
    status = int(match.group(1)) if match else None
    if status in (401, 403): return ValidationResult(True, False, status, "UNAUTHORIZED" if status == 401 else "FORBIDDEN", "credential rejected by provider", latency_ms, {})
    if status == 429: return ValidationResult(True, None, status, "RATE_LIMITED", "provider rate limit", latency_ms, {})
    if status and status >= 500: return ValidationResult(True, None, status, "SERVER_ERROR", "provider server error", latency_ms, {})
    if getattr(exc, "retryable", False): return ValidationResult(False, None, status, "NETWORK_ERROR", "provider transport error", latency_ms, {})
    return ValidationResult(None, None, status, "UNKNOWN", "credential validation failed", latency_ms, {})


class AnthropicProvider(ProviderBase):
    """Anthropic Messages API adapter."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = DEFAULT_MODEL,
        transport: HttpTransport | None = None,
    ) -> None:
        self._api_key_override = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._default_model = default_model
        self._transport = transport or _default_http_transport

    def _api_key(self) -> str | None:
        return self._api_key_override or os.environ.get("ANTHROPIC_API_KEY")

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anthropic",
            version="1.0.0",
            capabilities=[
                ProviderCapability.GENERATION,
                ProviderCapability.CHAT,
            ],
            model_ids=[
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
                "claude-3-opus-latest",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
            metadata={"env_key": "ANTHROPIC_API_KEY", "base_url": self._base_url},
        )

    def is_available(self) -> bool:
        return bool(self._api_key())

    def validate_credential(self, credential: str, *, model: str | None = None):
        from time import perf_counter
        from yasinai.providers.validation import ValidationResult
        if not credential: return ValidationResult(None, False, error_code="INVALID_CREDENTIAL", error_message="credential is empty")
        started = perf_counter()
        try:
            probe = AnthropicProvider(api_key=credential, base_url=self._base_url, default_model=model or self._default_model, transport=self._transport)
            probe._generate(GenerationRequest(prompt="health check", model=model or self._default_model, max_tokens=1, temperature=0.0))
            latency = round((perf_counter()-started)*1000)
            return ValidationResult(True, True, 200, None, None, latency, {"generation":"available"})
        except Exception as exc:
            return _validation_result_from_exception(exc, round((perf_counter()-started)*1000))

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        key = self._api_key()
        if not key:
            raise ProviderError(
                "anthropic",
                "ANTHROPIC_API_KEY is not set",
                retryable=False,
            )
        model = request.model or self._default_model
        body: dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if request.system_prompt:
            body["system"] = request.system_prompt
        if request.stop_sequences:
            body["stop_sequences"] = request.stop_sequences

        headers = {
            "x-api-key": key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/v1/messages"

        try:
            payload = self._transport(url, headers, body)
        except ProviderError:
            raise
        except Exception as exc:
            logger.error("Anthropic transport error: %s", exc)
            raise ProviderError(
                "anthropic",
                "Anthropic request failed",
                retryable=True,
            ) from exc

        try:
            blocks = payload.get("content") or []
            text_parts = [
                b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text"
            ]
            text = "".join(text_parts)
            usage = payload.get("usage") or {}
            finish = payload.get("stop_reason")
        except (TypeError, AttributeError) as exc:
            logger.error(
                "Anthropic unexpected response shape (payload withheld from exception): %r",
                payload,
            )
            raise ProviderError(
                "anthropic",
                "unexpected response format from provider",
                retryable=False,
            ) from exc

        return GenerationResponse(
            text=text,
            model=payload.get("model") or model,
            provider="anthropic",
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            finish_reason=finish,
            metadata={"id": payload.get("id")},
        )
