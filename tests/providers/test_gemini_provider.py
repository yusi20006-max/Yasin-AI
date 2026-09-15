from __future__ import annotations

from yasinai.providers.base import GenerationRequest, ProviderError
from yasinai.providers.gemini_provider import GeminiProvider


def test_gemini_generation_maps_request_and_response() -> None:
    captured = {}

    def transport(url, headers, body):
        captured.update(url=url, headers=headers, body=body)
        return {
            "modelVersion": "gemini-3.6-flash",
            "candidates": [{
                "content": {"parts": [{"text": "hello from gemini"}]},
                "finishReason": "STOP",
            }],
            "usageMetadata": {"promptTokenCount": 4, "candidatesTokenCount": 3},
        }

    provider = GeminiProvider(api_key="test-key", default_model="gemini-3.6-flash", transport=transport)
    response = provider.generate(GenerationRequest(
        prompt="hello",
        system_prompt="be concise",
        max_tokens=64,
        temperature=0.2,
        stop_sequences=["END"],
    ))

    assert response.text == "hello from gemini"
    assert response.provider == "gemini"
    assert response.input_tokens == 4
    assert response.output_tokens == 3
    assert captured["url"].endswith("/models/gemini-3.6-flash:generateContent")
    assert captured["headers"]["x-goog-api-key"] == "test-key"
    assert captured["body"]["systemInstruction"]["parts"][0]["text"] == "be concise"
    assert captured["body"]["generationConfig"]["maxOutputTokens"] == 64
    assert captured["body"]["generationConfig"]["stopSequences"] == ["END"]


def test_gemini_unconfigured_is_unavailable(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider()
    assert provider.is_available() is False
    try:
        provider.generate(GenerationRequest(prompt="hello"))
    except ProviderError as exc:
        assert exc.provider == "gemini"
        assert exc.retryable is False
    else:
        raise AssertionError("expected ProviderError")


def test_gemini_http_errors_have_bounded_retryability() -> None:
    def retryable_transport(url, headers, body):
        raise ProviderError("gemini", "Gemini request failed with HTTP 503", retryable=True)

    provider = GeminiProvider(api_key="test-key", transport=retryable_transport)
    try:
        provider.generate(GenerationRequest(prompt="hello"))
    except ProviderError as exc:
        assert exc.retryable is True
    else:
        raise AssertionError("expected ProviderError")


def test_gemini_malformed_response_is_not_retryable() -> None:
    provider = GeminiProvider(
        api_key="test-key",
        transport=lambda url, headers, body: {"candidates": []},
    )
    try:
        provider.generate(GenerationRequest(prompt="hello"))
    except ProviderError as exc:
        assert exc.retryable is False
    else:
        raise AssertionError("expected ProviderError")
