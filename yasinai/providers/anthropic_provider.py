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
from typing import Any, Callable, Dict, Optional

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)

HttpTransport = Callable[[str, Dict[str, str], Dict[str, Any]], Dict[str, Any]]

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.anthropic.com"
DEFAULT_MODEL = "claude-3-5-haiku-latest"
ANTHROPIC_VERSION = "2023-06-01"


def _default_http_transport(
    url: str, headers: Dict[str, str], body: Dict[str, Any]
) -> Dict[str, Any]:
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


class AnthropicProvider(ProviderBase):
    """Anthropic Messages API adapter."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = DEFAULT_MODEL,
        transport: Optional[HttpTransport] = None,
    ) -> None:
        self._api_key_override = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._default_model = default_model
        self._transport = transport or _default_http_transport

    def _api_key(self) -> Optional[str]:
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

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        key = self._api_key()
        if not key:
            raise ProviderError(
                "anthropic",
                "ANTHROPIC_API_KEY is not set",
                retryable=False,
            )
        model = request.model or self._default_model
        body: Dict[str, Any] = {
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
