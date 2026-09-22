from yasinai.providers.openai_provider import OpenAIProvider
from yasinai.providers.anthropic_provider import AnthropicProvider
from yasinai.providers.gemini_provider import GeminiProvider
from yasinai.providers.generic_openai import GenericOpenAIProvider

def ok_transport(url, headers, body):
    if "anthropic" in url: return {"id":"x","model":body["model"],"content":[{"type":"text","text":"ok"}],"usage":{}}
    if "generativelanguage" in url: return {"modelVersion":body.get("model","gemini"),"candidates":[{"content":{"parts":[{"text":"ok"}]},"finishReason":"STOP"}]}
    return {"id":"x","model":body["model"],"choices":[{"message":{"content":"ok"},"finish_reason":"stop"}],"usage":{}}

def fail_transport(url, headers, body):
    from yasinai.providers.base import ProviderError
    raise ProviderError("test", "request failed with HTTP 401", retryable=False)

def test_builtin_providers_validate_without_persisting_credentials():
    for provider in [OpenAIProvider(api_key="configured", transport=ok_transport), AnthropicProvider(api_key="configured", transport=ok_transport), GeminiProvider(api_key="configured", transport=ok_transport)]:
        result = provider.validate_credential("runtime-secret")
        assert result.authenticated is True
        assert result.reachable is True
        assert result.latency_ms is not None

def test_generic_openai_validation_reuses_existing_adapter():
    result = GenericOpenAIProvider(name="test", api_key="configured", base_url="https://example.test/v1", default_model="demo", transport=ok_transport).validate_credential("runtime-secret")
    assert result.authenticated is True

def test_validation_normalizes_auth_failure_without_secret():
    result = OpenAIProvider(api_key="configured", transport=fail_transport).validate_credential("runtime-secret")
    assert result.authenticated is False
    assert result.http_status == 401
    assert "runtime-secret" not in str(result)
