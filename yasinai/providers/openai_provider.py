"""
OpenAIProvider — OpenAI Chat Completions adapter.

Credentials: OPENAI_API_KEY only (never hardcoded).
SDK libraries are imported inside call methods, not at module level.
HTTP transport is injectable for unit tests (no live API required).

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

logger = logging.getLogger(__name__)

from yasinai.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ProviderBase,
    ProviderCapability,
    ProviderError,
    ProviderInfo,
)

# Optional injectable transport: (url, headers, body_dict) -> response_dict
HttpTransport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


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
            "OpenAI HTTP %s error (raw body withheld from exception): %s",
            exc.code,
            detail,
        )
        raise ProviderError(
            "openai",
            f"OpenAI request failed with HTTP {exc.code}",
            retryable=exc.code >= 500,
        ) from exc
    except urllib.error.URLError as exc:
        logger.error("OpenAI network error: %s", exc)
        raise ProviderError(
            "openai",
            "OpenAI network error",
            retryable=True,
        ) from exc


class OpenAIProvider(ProviderBase):
    """OpenAI adapter using Chat Completions API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = DEFAULT_MODEL,
        transport: HttpTransport | None = None,
    ) -> None:
        # api_key arg is for tests only; production uses env
        self._api_key_override = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._default_model = default_model
        self._transport = transport or _default_http_transport

    def _api_key(self) -> str | None:
        return self._api_key_override or os.environ.get("OPENAI_API_KEY")

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openai",
            version="1.0.0",
            capabilities=[
                ProviderCapability.GENERATION,
                ProviderCapability.CHAT,
                ProviderCapability.EMBEDDING,
            ],
            model_ids=[
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
            metadata={"env_key": "OPENAI_API_KEY", "base_url": self._base_url},
        )

    def is_available(self) -> bool:
        return bool(self._api_key())

    def _generate(self, request: GenerationRequest) -> GenerationResponse:
        key = self._api_key()
        if not key:
            raise ProviderError(
                "openai",
                "OPENAI_API_KEY is not set",
                retryable=False,
            )
        model = request.model or self._default_model
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.stop_sequences:
            body["stop"] = request.stop_sequences

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/chat/completions"

        try:
            payload = self._transport(url, headers, body)
        except ProviderError:
            raise
        except Exception as exc:
            logger.error("OpenAI transport error: %s", exc)
            raise ProviderError(
                "openai",
                "OpenAI request failed",
                retryable=True,
            ) from exc

        try:
            choice = payload["choices"][0]
            text = choice["message"]["content"]
            usage = payload.get("usage") or {}
            finish = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            logger.error(
                "OpenAI unexpected response shape (payload withheld from exception): %r",
                payload,
            )
            raise ProviderError(
                "openai",
                "unexpected response format from provider",
                retryable=False,
            ) from exc

        return GenerationResponse(
            text=text or "",
            model=payload.get("model") or model,
            provider="openai",
            input_tokens=int(usage.get("prompt_tokens") or 0),
            output_tokens=int(usage.get("completion_tokens") or 0),
            finish_reason=finish,
            metadata={"id": payload.get("id")},
        )
