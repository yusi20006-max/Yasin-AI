"""Errors for the transport-neutral YasinAI service layer."""

class APIError(Exception):
    """Base service-layer error."""

    status_code = 500

class ValidationError(APIError):
    status_code = 400

class AuthenticationError(APIError):
    status_code = 401

class AuthorizationError(APIError):
    status_code = 403
