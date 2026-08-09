"""Contract tests for the transport-neutral API service."""

import pytest

from .app import create_service
from .errors import ValidationError


def test_health_endpoint() -> None:
    service = create_service(version="1.2.3")
    response = service.dispatch("GET", "/health/")
    assert response.status == 200
    assert response.data == {"status": "ok", "service": "yasinai", "version": "1.2.3"}


def test_route_registration_and_dispatch() -> None:
    service = create_service()
    service.add_route("post", "/echo", lambda payload: {"echo": payload["value"]})
    response = service.dispatch("POST", "echo", {"value": "hello"})
    assert response.status == 200
    assert response.data == {"echo": "hello"}


def test_missing_route_is_404() -> None:
    assert create_service().dispatch("GET", "/missing").status == 404


def test_duplicate_route_is_rejected() -> None:
    service = create_service()
    service.add_route("GET", "/x", lambda _: {})
    with pytest.raises(ValidationError):
        service.add_route("get", "/x/", lambda _: {})
