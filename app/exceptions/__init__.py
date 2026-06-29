"""
Custom exception classes. Raised from services, caught once centrally
in main.py's exception handlers -- so every error response automatically
matches the {success, message, errors} envelope without each route
having to build that shape manually.
"""


class AppException(Exception):
    """Base class for all custom app exceptions."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource doesn't exist."""
    pass


class UnauthorizedException(AppException):
    """Raised when credentials are missing or invalid (HTTP 401)."""
    pass


class ForbiddenException(AppException):
    """Raised when the user is authenticated but not allowed to do this (HTTP 403)."""
    pass


class ValidationException(AppException):
    """Raised for business-rule validation failures not caught by Pydantic."""
    pass


class ConflictException(AppException):
    """Raised when an action conflicts with existing state (e.g. duplicate email)."""
    pass