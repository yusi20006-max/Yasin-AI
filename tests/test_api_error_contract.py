"""#147 — API error contract regression coverage."""
from __future__ import annotations

from pathlib import Path

from api_service.app import create_service
from api_service.errors import APIError, ValidationError

ROOT = Path(__file__).resolve().parents[1]


def test_error_contract_doc_exists():
    assert (ROOT / "docs" / "API_ERROR_CONTRACT.md").is_file()


def test_validation_error_shape_and_status():
    svc = create_service()
    svc.add_route("POST", "/v", lambda _: (_ for _ in ()).throw(ValidationError("field required")))
    res = svc.dispatch("POST", "/v", {})
    assert res.status == 400
    assert res.data == {"error": "field required"}


def test_custom_api_error_status():
    svc = create_service()
    svc.add_route("GET", "/deny", lambda _: (_ for _ in ()).throw(APIError("forbidden", status_code=403)))
    res = svc.dispatch("GET", "/deny")
    assert res.status == 403
    assert res.data == {"error": "forbidden"}


def test_provider_style_failure_mapped_generically():
    svc = create_service()

    def handler(_payload):
        raise APIError("upstream provider unavailable", status_code=503)

    svc.add_route("POST", "/generate", handler)
    res = svc.dispatch("POST", "/generate", {"prompt": "x"})
    assert res.status == 503
    assert res.data == {"error": "upstream provider unavailable"}
    assert "traceback" not in str(res.data).lower()


def test_internal_failure_never_leaks_exception_text():
    svc = create_service()
    marker = "SENSITIVE_MARKER_XYZ_999"
    svc.add_route("GET", "/x", lambda _: (_ for _ in ()).throw(RuntimeError(marker)))
    res = svc.dispatch("GET", "/x")
    assert res.status == 500
    assert res.data == {"error": "internal server error"}
    assert marker not in str(res.data)
