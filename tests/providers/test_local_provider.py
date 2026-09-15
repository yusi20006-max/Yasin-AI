from __future__ import annotations

from typing import Any

import pytest

from yasinai.providers.base import GenerationRequest, ProviderError
from yasinai.providers.local_provider import LocalProvider


def fake_transport(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    assert url == "http://127.0.0.1:18765/chat/completions"
    assert headers["Authorization"] == "Bearer local"
    assert body["model"] == "qwen-test"
    assert body["messages"] == [
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "Hello"},
    ]
    return {
        "id": "chatcmpl-local-test",
        "model": "qwen-test",
        "choices": [
            {
                "message": {"content": "Hello from local Qwen."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 4, "completion_tokens": 5},
    }


def test_local_provider_generates_from_openai_compatible_endpoint() -> None:
    provider = LocalProvider(
        model_id="qwen-test",
        base_url="http://127.0.0.1:18765",
        transport=fake_transport,
    )

    result = provider.generate(
        GenerationRequest(
            prompt="Hello",
            system_prompt="Be concise.",
            model="qwen-test",
            max_tokens=32,
            temperature=0.2,
        )
    )

    assert result.text == "Hello from local Qwen."
    assert result.provider == "local"
    assert result.model == "qwen-test"
    assert result.input_tokens == 4
    assert result.output_tokens == 5
    assert result.finish_reason == "stop"


def test_local_provider_maps_http_failures_to_local_provider_error() -> None:
    def failing_transport(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        raise ProviderError("openai", "OpenAI network error", retryable=True)

    provider = LocalProvider(
        model_id="qwen-test",
        base_url="http://127.0.0.1:18765",
        transport=failing_transport,
    )

    with pytest.raises(ProviderError) as exc_info:
        provider.generate(GenerationRequest(prompt="Hello", model="qwen-test"))

    assert exc_info.value.provider == "local"
    assert exc_info.value.retryable is True


def test_local_provider_info_advertises_configured_model() -> None:
    provider = LocalProvider(model_id="qwen-test")

    assert provider.info.name == "local"
    assert provider.info.model_ids == ["qwen-test"]
    assert provider.info.metadata["protocol"] == "openai-chat-completions"
