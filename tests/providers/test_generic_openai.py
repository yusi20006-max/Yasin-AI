from yasinai.providers.base import GenerationRequest
from yasinai.providers.generic_openai import GenericOpenAIProvider


def test_generic_provider_uses_runtime_name_url_model_and_transport():
    calls = {}

    def transport(url, headers, body):
        calls.update({"url": url, "headers": headers, "body": body})
        return {
            "id": "test-1",
            "model": "custom-model",
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1},
        }

    provider = GenericOpenAIProvider(
        name="my-gateway",
        base_url="https://gateway.example/v1/",
        api_key="secret-key",
        default_model="custom-model",
        transport=transport,
    )
    result = provider.generate(GenerationRequest(prompt="hello"))

    assert result.text == "ok"
    assert result.provider == "my-gateway"
    assert result.model == "custom-model"
    assert calls["url"] == "https://gateway.example/v1/chat/completions"
    assert calls["headers"]["Authorization"] == "Bearer secret-key"
    assert calls["body"]["model"] == "custom-model"


def test_generic_provider_info_contains_runtime_identity():
    provider = GenericOpenAIProvider(
        name="gateway",
        base_url="https://gateway.example/v1",
        api_key="secret",
        default_model="model-x",
    )
    assert provider.info.name == "gateway"
    assert provider.info.model_ids == ["model-x"]
    assert provider.info.metadata["protocol"] == "openai-chat-completions"
