"""Tests for ndastro_api.core.exceptions.http_exceptions."""

import pytest

from ndastro_api.core.exceptions.http_exceptions import (
    CustomAPIException,
    DuplicateResourceException,
    InvalidInputException,
    PermissionDeniedException,
    RateLimitExceededException,
    ResourceNotFoundException,
    UnauthorizedAccessException,
)


def test_resource_not_found_default_message():
    exc = ResourceNotFoundException()
    assert exc.message == "Requested resource not found."


def test_resource_not_found_custom_message():
    exc = ResourceNotFoundException("User not found")
    assert exc.message == "User not found"


def test_invalid_input_default_message():
    exc = InvalidInputException()
    assert exc.message == "Invalid input provided."


def test_invalid_input_custom_message():
    exc = InvalidInputException("Bad value for field 'date'")
    assert "Bad value" in exc.message


def test_permission_denied_default():
    exc = PermissionDeniedException()
    assert "Permission denied" in exc.message


def test_permission_denied_custom():
    exc = PermissionDeniedException("Admin only.")
    assert "Admin only" in exc.message


def test_rate_limit_exceeded_default():
    exc = RateLimitExceededException()
    assert "Rate limit" in exc.message


def test_rate_limit_exceeded_custom():
    exc = RateLimitExceededException("Too many requests: slow down.")
    assert "slow down" in exc.message


def test_duplicate_resource_default():
    exc = DuplicateResourceException()
    assert "already exists" in exc.message


def test_duplicate_resource_custom():
    exc = DuplicateResourceException("Email already registered.")
    assert "Email" in exc.message


def test_unauthorized_access_default():
    exc = UnauthorizedAccessException()
    assert "Unauthorized" in exc.message


def test_unauthorized_access_custom():
    exc = UnauthorizedAccessException("Token expired.")
    assert "Token" in exc.message


def test_custom_api_exception_default():
    exc = CustomAPIException()
    assert exc.message == "An error occurred in the ndastro_api application."


def test_custom_api_exception_custom():
    exc = CustomAPIException("Ephemeris data unavailable.")
    assert "Ephemeris" in exc.message


def test_all_exceptions_are_exceptions():
    for cls in (
        ResourceNotFoundException,
        InvalidInputException,
        PermissionDeniedException,
        RateLimitExceededException,
        DuplicateResourceException,
        UnauthorizedAccessException,
        CustomAPIException,
    ):
        exc = cls()
        assert isinstance(exc, Exception)


def test_resource_not_found_raises():
    with pytest.raises(ResourceNotFoundException):
        raise ResourceNotFoundException("Not found")


def test_invalid_input_raises():
    with pytest.raises(InvalidInputException):
        raise InvalidInputException()
