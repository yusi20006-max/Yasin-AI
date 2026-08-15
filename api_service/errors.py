"""Errors for the transport-neutral YasinAI service layer."""
from __future__ import annotations


class APIError(Exception):
    """Base service-layer error with HTTP status semantics."""

    status_code = 500

    def __init__(self, message: str = "", *, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class ValidationError(APIError):
    status_code = 400


class AuthenticationError(APIError):
    status_code = 401


class AuthorizationError(APIError):
    status_code = 403
