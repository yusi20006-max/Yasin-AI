"""Transport-neutral application service boundary.

HTTP/CLI adapters can depend on this layer without coupling the core to a web framework.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable

from .errors import APIError, ValidationError
from .models import HealthResponse, ServiceResponse

logger = logging.getLogger(__name__)

Handler = Callable[[Mapping[str, Any]], Mapping[str, Any]]

@dataclass
class APIService:
    name: str = "yasinai"
    version: str = "1.1.3"
    _routes: dict[str, Handler] | None = None

    def __post_init__(self) -> None:
        self._routes = dict(self._routes or {})

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        method = method.upper().strip()
        path = self._normalize_path(path)
        if not method or not path:
            raise ValidationError("method and path are required")
        key = f"{method} {path}"
        if key in self._routes:
            raise ValidationError(f"route already registered: {key}")
        self._routes[key] = handler

    def health(self) -> HealthResponse:
        return HealthResponse("ok", self.name, self.version)

    def dispatch(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> ServiceResponse:
        key = f"{method.upper().strip()} {self._normalize_path(path)}"
        if key == "GET /health":
            return ServiceResponse(200, self.health().as_dict())
        handler = self._routes.get(key)
        if handler is None:
            return ServiceResponse(404, {"error": "route not found"})
        try:
            result = dict(handler(payload or {}))
        except APIError as exc:
            return ServiceResponse(exc.status_code, {"error": str(exc)})
        except Exception:
            # Any exception the handler doesn't raise as an APIError is a bug
            # in the handler, not a client error. Log full details internally
            # for debugging; never leak exception text or a traceback into
            # the response body — same "don't expose internals" principle
            # applied to provider error handling elsewhere in this codebase.
            logger.exception("Unhandled exception in handler for %s", key)
            return ServiceResponse(500, {"error": "internal server error"})
        return ServiceResponse(200, result)

    @staticmethod
    def _normalize_path(path: str) -> str:
        path = "/" + str(path).strip().lstrip("/")
        if len(path) > 1:
            path = path.rstrip("/")
        return path


def create_service(name: str = "yasinai", version: str = "1.1.3") -> APIService:
    return APIService(name=name, version=version)
