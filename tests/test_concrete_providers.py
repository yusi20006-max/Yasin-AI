"""Tests for Phase 3.1 concrete provider adapters (mocked transport, no live API)."""
from __future__ import annotations

import pytest

from yasinai.providers import (
    AnthropicProvider,
    LocalProvider,
    OpenAIProvider,
    ProviderCapability,
    ProviderError,
    ProviderRegistry,
    ProviderRouter,
    build_default_registry,
)
from yasinai.providers.base import GenerationRequest
from yasinai.providers.router import ProviderUnavailableError

# ---------------------------------------------------------------------------
# LocalProvider
# ---------------------------------------------------------------------------

def test_local_always_available():
    p = LocalProvider()
    assert p.is_available() is True
    assert p.info.name == "local"
    assert ProviderCapability.GENERATION in p.info.capabilities


def test_local_generate_echo():
    p = LocalProvider()
    resp = p.generate(GenerationRequest(prompt="hello world", max_tokens=50))
    assert resp.provider == "local"
    assert "hello world" in resp.text
    assert resp.model == "local-echo-v1"
    assert resp.input_tokens >= 1
    assert resp.output_tokens >= 1


def test_local_system_prompt_and_stop():
    p = LocalProvider()
    resp = p.generate(
        GenerationRequest(
            prompt="abcSTOP more",
            system_prompt="sys",
            stop_sequences=["STOP"],
            max_tokens=100,
        )
    )
    assert "[system: sys]" in resp.text
    assert " more" not in resp.text
    assert "STOP" not in resp.text


# ---------------------------------------------------------------------------
# OpenAIProvider
# ---------------------------------------------------------------------------

def test_openai_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    p = OpenAIProvider()
    assert p.is_available() is False


def test_openai_available_with_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    p = OpenAIProvider()
    assert p.is_available() is True
    assert p.info.name == "openai"
    assert "gpt-4o" in p.info.model_ids


def test_openai_generate_with_mock_transport():
    def transport(url, headers, body):
        assert "chat/completions" in url
        assert headers["Authorization"].startswith("Bearer ")
        assert body["messages"][-1]["content"] == "ping"
        return {
            "id": "chatcmpl-1",
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "pong"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1},
        }

    p = OpenAIProvider(api_key="sk-test", transport=transport)
    resp = p.generate(GenerationRequest(prompt="ping", model="gpt-4o-mini"))
    assert resp.text == "pong"
    assert resp.provider == "openai"
    assert resp.input_tokens == 3
    assert resp.output_tokens == 1
    assert resp.finish_reason == "stop"


def test_openai_missing_key_raises():
    p = OpenAIProvider(api_key="")
    with pytest.raises(ProviderError, match="OPENAI_API_KEY"):
        p.generate(GenerationRequest(prompt="x"))


def test_openai_bad_response_shape():
    def transport(url, headers, body):
        return {"choices": []}

    p = OpenAIProvider(api_key="sk-test", transport=transport)
    with pytest.raises(ProviderError, match="unexpected response format") as ei:
        p.generate(GenerationRequest(prompt="x"))
    # must not leak payload dump
    assert "choices" not in str(ei.value)


def test_openai_http_error_message_redacted(monkeypatch):
    import urllib.error

    from yasinai.providers import openai_provider as mod

    class FakeHTTPError(urllib.error.HTTPError):
        def __init__(self):
            pass
        code = 400
        def read(self):
            return b'{"error":{"message":"secret-provider-detail","type":"invalid_request"}}'

    def boom(url, headers, body):
        raise FakeHTTPError()

    # Exercise default transport path by patching urlopen
    def fake_urlopen(req, timeout=60):
        raise FakeHTTPError()

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ProviderError) as ei:
        mod._default_http_transport("https://api.openai.com/v1/chat/completions", {}, {})
    msg = str(ei.value)
    assert "HTTP 400" in msg or "400" in msg
    assert "secret-provider-detail" not in msg
    assert ei.value.retryable is False


# ---------------------------------------------------------------------------
# AnthropicProvider
# ---------------------------------------------------------------------------

def test_anthropic_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    p = AnthropicProvider()
    assert p.is_available() is False


def test_anthropic_generate_with_mock_transport():
    def transport(url, headers, body):
        assert url.endswith("/v1/messages")
        assert "x-api-key" in headers
        assert body["messages"][0]["content"] == "hi"
        return {
            "id": "msg_1",
            "model": "claude-3-5-haiku-latest",
            "content": [{"type": "text", "text": "hello"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 2, "output_tokens": 1},
        }

    p = AnthropicProvider(api_key="ant-test", transport=transport)
    resp = p.generate(GenerationRequest(prompt="hi"))
    assert resp.text == "hello"
    assert resp.provider == "anthropic"
    assert resp.finish_reason == "end_turn"


def test_anthropic_missing_key_raises():
    p = AnthropicProvider(api_key="")
    with pytest.raises(ProviderError, match="ANTHROPIC_API_KEY"):
        p.generate(GenerationRequest(prompt="x"))


# ---------------------------------------------------------------------------
# Registry / Router integration
# ---------------------------------------------------------------------------

def test_build_default_registry_local_only(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    reg = build_default_registry()
    assert len(reg) == 3  # all registered
    available = reg.available_for_capability(ProviderCapability.GENERATION)
    names = {p.info.name for p in available}
    assert names == {"local"}


def test_router_selects_openai_when_key_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    reg = build_default_registry()
    router = ProviderRouter(reg)
    provider = router.select(ProviderCapability.GENERATION, model="gpt-4o")
    assert provider.info.name == "openai"


def test_router_falls_back_to_local(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    reg = ProviderRegistry()
    reg.register(LocalProvider())
    router = ProviderRouter(reg)
    provider = router.select(ProviderCapability.GENERATION)
    assert provider.info.name == "local"


def test_router_unavailable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    reg = ProviderRegistry()
    reg.register(OpenAIProvider())  # not available
    router = ProviderRouter(reg)
    with pytest.raises(ProviderUnavailableError):
        router.select(ProviderCapability.GENERATION)
