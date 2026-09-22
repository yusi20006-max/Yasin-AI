"""Gemini REST provider adapter for Yasin-AI."""
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

logger = logging.getLogger(__name__)

HttpTransport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.6-flash"


def _default_http_transport(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            exc.read()
        except Exception:
            pass
        retryable = exc.code == 429 or exc.code >= 500
        raise ProviderError("gemini", f"Gemini request failed with HTTP {exc.code}", retryable=retryable) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ProviderError("gemini", "Gemini network error", retryable=True) from exc


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


class GeminiProvider(ProviderBase):
    """Gemini generateContent adapter using the REST API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        default_model: str | None = None,
        transport: HttpTransport | None = None,
    ) -> None:
        self._api_key_override = api_key
        self._base_url = base_url.rstrip("/")
        self._default_model = default_model or os.environ.get("YASINAI_GEMINI_MODEL", DEFAULT_MODEL)
        self._transport = transport or _default_http_transport

    def _api_key(self) -> str | None:
        return self._api_key_override or os.environ.get("GEMINI_API_KEY")

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="gemini",
            version="1.0.0",
            capabilities=[ProviderCapability.GENERATION, ProviderCapability.CHAT],
            model_ids=[self._default_model],
            metadata={"env_key": "GEMINI_API_KEY", "base_url": self._base_url},
        )

    def is_available(self) -> bool:
        return bool(self._api_key())

    def validate_credential(self, credential: str, *, model: str | None = None):
        from time import perf_counter
        from yasinai.providers.validation import ValidationResult
        if not credential: return ValidationResult(None, False, error_code="INVALID_CREDENTIAL", error_message="credential is empty")
        started = perf_counter()
        try:
            probe = GeminiProvider(api_key=credential, base_url=self._base_url, default_model=model or self._default_model, transport=self._transport)
            probe._generate(GenerationRequest(prompt="health check", model=model or self._default_model, max_tokens=1, temperature=0.0))
            latency = round((perf_counter()-started)*1000)
            return ValidationResult(True, True, 200, None, None, latency, {"generation":"available"})
        except Exception as exc:
            return _validation_result_from_exception(exc, round((perf_counter()-started)*1000))

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        key = self._api_key()
        if not key:
            raise ProviderError("gemini", "GEMINI_API_KEY is not set", retryable=False)
        model = request.model or self._default_model
        contents = [{"role": "user", "parts": [{"text": request.prompt}]}]
        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
            },
        }
        if request.stop_sequences:
            body["generationConfig"]["stopSequences"] = request.stop_sequences
        if request.system_prompt:
            body["systemInstruction"] = {"parts": [{"text": request.system_prompt}]}

        url = f"{self._base_url}/models/{model}:generateContent"
        headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
        try:
            payload = self._transport(url, headers, body)
        except ProviderError:
            raise
        except Exception as exc:
            logger.error("Gemini transport error: %s", exc)
            raise ProviderError("gemini", "Gemini request failed", retryable=True) from exc

        try:
            candidate = payload["candidates"][0]
            parts = candidate["content"]["parts"]
            text = "".join(str(part["text"]) for part in parts if "text" in part)
            if not text:
                raise ValueError("empty response")
            usage = payload.get("usageMetadata") or {}
            finish = candidate.get("finishReason")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.error("Gemini unexpected response shape")
            raise ProviderError("gemini", "unexpected response format from provider", retryable=False) from exc

        return GenerationResponse(
            text=text,
            model=payload.get("modelVersion") or model,
            provider="gemini",
            input_tokens=int(usage.get("promptTokenCount") or 0),
            output_tokens=int(usage.get("candidatesTokenCount") or 0),
            finish_reason=finish,
        )
