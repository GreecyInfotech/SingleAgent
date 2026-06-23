from typing import Any


class PlatformError(Exception):
    """Base exception for all platform errors."""

    def __init__(
        self, message: str, code: str = "PLATFORM_ERROR", details: dict[str, Any] | None = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(PlatformError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": identifier},
        )


class ValidationError(PlatformError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class AgentExecutionError(PlatformError):
    def __init__(self, message: str, agent_id: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            details={"agent_id": agent_id, **(details or {})},
        )


class AuthenticationError(PlatformError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(PlatformError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR")
