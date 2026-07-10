# core/exceptions.py
"""Custom exception classes for the application."""

class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status_code=503)