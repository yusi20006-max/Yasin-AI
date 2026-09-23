from __future__ import annotations

from yasinai.contracts.generation import GenerationResult
from yasinai.gateway.http import YasinAIGateway


class FakeRegistry:
    def available_for_capability(self, capability):
        return []


class FakeGenerationService:
    registry = FakeRegistry()

    def __init__(self, result: GenerationResult):
        self.result = result
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return self.result


def test_health_is_stable():
    gateway = YasinAIGateway(FakeGenerationService(GenerationResult(success=True)))
    assert gateway.health() == {"status": "ok", "service": "yasin-ai"}


def test_models_returns_safe_metadata():
    gateway = YasinAIGateway(FakeGenerationService(GenerationResult(success=True)))
    assert gateway.models() == {"object": "list", "data": []}


def test_chat_completion_maps_request_and_result():
    service = FakeGenerationService(
        GenerationResult(
            success=True,
            text="hello",
            model="qwen-test",
            provider="local",
            input_tokens=2,
            output_tokens=1,
            finish_reason="stop",
        )
    )
    gateway = YasinAIGateway(service)
    status, body = gateway.chat_completions(
        {
            "model": "qwen-test",
            "messages": [
                {"role": "system", "content": "Be concise."},
                {"role": "user", "content": "Hello"},
            ],
            "max_tokens": 16,
            "temperature": 0.2,
        }
    )
    assert status == 200
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"] == "hello"
    assert body["usage"]["total_tokens"] == 3
    assert service.last_request.prompt == "Hello"
    assert service.last_request.system_prompt == "Be concise."


def test_invalid_messages_are_rejected():
    gateway = YasinAIGateway(FakeGenerationService(GenerationResult(success=True)))
    status, body = gateway.chat_completions({"messages": []})
    assert status == 400
    assert body["error"]["type"] == "invalid_request_error"


def test_generation_failure_maps_to_503():
    service = FakeGenerationService(GenerationResult(success=False, error="provider unavailable"))
    gateway = YasinAIGateway(service)
    status, body = gateway.chat_completions({"messages": [{"role": "user", "content": "Hello"}]})
    assert status == 503
    assert body["error"]["type"] == "provider_error"
    assert body["error"]["message"] == "provider unavailable"


def test_chat_completion_preserves_provider_and_model_pinning():
    service = FakeGenerationService(GenerationResult(success=True, text="ok", model="gemini-3.6-flash", provider="gemini"))
    gateway = YasinAIGateway(service)
    status, body = gateway.chat_completions({
        "provider": "gemini",
        "model": "gemini-3.6-flash",
        "messages": [{"role": "user", "content": "Hello"}],
    })
    assert status == 200
    assert body["model"] == "gemini-3.6-flash"
    assert service.last_request.provider == "gemini"
    assert service.last_request.model == "gemini-3.6-flash"


def test_chat_completion_keeps_unpinned_provider_none():
    service = FakeGenerationService(GenerationResult(success=True, text="ok", model="local", provider="local"))
    status, _ = YasinAIGateway(service).chat_completions({
        "messages": [{"role": "user", "content": "Hello"}],
    })
    assert status == 200
    assert service.last_request.provider is None
