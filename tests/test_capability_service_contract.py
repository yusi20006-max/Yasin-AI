from __future__ import annotations

from yasinai.contracts import GenerationResult
from api_service import CAPABILITIES_PATH, CONTRACT_VERSION, GENERATION_PATH, create_capability_service


class FakeGenerationService:
    def __init__(self) -> None:
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return GenerationResult(
            success=True,
            text="generated",
            model=request.model or "fake-model",
            provider=request.provider or "fake",
            input_tokens=2,
            output_tokens=1,
            finish_reason="stop",
        )


def test_capabilities_are_versioned_and_public() -> None:
    service = create_capability_service(generation=FakeGenerationService())

    response = service.dispatch("GET", CAPABILITIES_PATH)

    assert response.status == 200
    assert response.data == {
        "contract_version": CONTRACT_VERSION,
        "service": "yasinai",
        "version": "1.1.4",
        "capabilities": ["generation"],
    }


def test_generation_contract_maps_to_generation_service() -> None:
    fake = FakeGenerationService()
    service = create_capability_service(generation=fake)

    response = service.dispatch(
        "POST",
        GENERATION_PATH,
        {
            "prompt": "hello",
            "model": "fake-model",
            "provider": "fake",
            "max_tokens": 64,
            "temperature": 0.2,
            "metadata": {"request_id": "test-1"},
        },
    )

    assert response.status == 200
    assert response.data["contract_version"] == "v1"
    assert response.data["success"] is True
    assert response.data["text"] == "generated"
    assert fake.requests[0].prompt == "hello"
    assert fake.requests[0].model == "fake-model"
    assert fake.requests[0].metadata == {"request_id": "test-1"}


def test_generation_rejects_invalid_payload_without_calling_service() -> None:
    fake = FakeGenerationService()
    service = create_capability_service(generation=fake)

    response = service.dispatch("POST", GENERATION_PATH, {"prompt": ""})

    assert response.status == 400
    assert "prompt" in response.data["error"]
    assert fake.requests == []


def test_generation_rejects_out_of_range_values() -> None:
    fake = FakeGenerationService()
    service = create_capability_service(generation=fake)

    response = service.dispatch(
        "POST",
        GENERATION_PATH,
        {"prompt": "hello", "temperature": 2.1},
    )

    assert response.status == 400
    assert "temperature" in response.data["error"]
    assert fake.requests == []


def test_health_remains_available_under_capability_service() -> None:
    service = create_capability_service(generation=FakeGenerationService())

    response = service.dispatch("GET", "/health")

    assert response.status == 200
    assert response.data == {
        "status": "ok",
        "service": "yasinai",
        "version": "1.1.4",
    }
