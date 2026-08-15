import pytest

from api_service.app import create_service
from api_service.errors import ValidationError


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


def test_unhandled_exception_returns_generic_500() -> None:
    service = create_service()
    service.add_route("GET", "/boom", lambda _: (_ for _ in ()).throw(RuntimeError("db exploded")))
    response = service.dispatch("GET", "/boom")
    assert response.status == 500
    assert response.data == {"error": "internal server error"}
    # The real exception message must never leak into the response body.
    assert "db exploded" not in str(response.data)


def test_unhandled_exception_response_shape_matches_api_error_shape() -> None:
    service = create_service()
    service.add_route("GET", "/api-error", lambda _: (_ for _ in ()).throw(ValidationError("bad input")))
    service.add_route("GET", "/bug", lambda _: (_ for _ in ()).throw(KeyError("missing")))

    api_error_response = service.dispatch("GET", "/api-error")
    unhandled_response = service.dispatch("GET", "/bug")

    assert set(api_error_response.data.keys()) == set(unhandled_response.data.keys()) == {"error"}


def test_unhandled_exception_is_logged_with_traceback(caplog) -> None:
    import logging

    service = create_service()
    service.add_route("GET", "/boom", lambda _: (_ for _ in ()).throw(RuntimeError("db exploded")))
    with caplog.at_level(logging.ERROR, logger="api_service.app"):
        service.dispatch("GET", "/boom")

    assert "Unhandled exception" in caplog.text
    assert "db exploded" in caplog.text
