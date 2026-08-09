"""Transport-neutral application service boundary.

HTTP/CLI adapters can depend on this layer without coupling the core to a web framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

from .errors import APIError, ValidationError
from .models import HealthResponse, ServiceResponse

Handler = Callable[[Mapping[str, Any]], Mapping[str, Any]]

@dataclass
class APIService:
    name: str = "yasinai"
    version: str = "0.1.0"
    _routes: Dict[str, Handler] | None = None

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

    def dispatch(self, method: str, path: str, payload: Optional[Mapping[str, Any]] = None) -> ServiceResponse:
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
        return ServiceResponse(200, result)

    @staticmethod
    def _normalize_path(path: str) -> str:
        path = "/" + str(path).strip().lstrip("/")
        if len(path) > 1:
            path = path.rstrip("/")
        return path

def create_service(name: str = "yasinai", version: str = "0.1.0") -> APIService:
    return APIService(name=name, version=version)
