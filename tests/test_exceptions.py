import pytest

from enterprise_agent_platform.core.exceptions import NotFoundError, PlatformError


def test_platform_error() -> None:
    error = PlatformError("Something went wrong", code="CUSTOM")
    assert error.message == "Something went wrong"
    assert error.code == "CUSTOM"
    assert str(error) == "Something went wrong"


def test_not_found_error() -> None:
    error = NotFoundError("Agent", "abc-123")
    assert error.code == "NOT_FOUND"
    assert "Agent" in error.message
    assert error.details["id"] == "abc-123"


def test_validation_error() -> None:
    from enterprise_agent_platform.core.exceptions import ValidationError

    error = ValidationError("Invalid input", details={"field": "name"})
    assert error.code == "VALIDATION_ERROR"
