"""Tests for ndastro_api.core.exceptions.app_exceptions — all exception classes."""

import pytest

from ndastro_api.core.exceptions.app_exceptions import (
    EmailConfigurationError,
    PlanetNotFoundError,
    RedisClientNotInitializedError,
    RefreshTokenMissingInvalidException,
    UserIdNotSetError,
)

# ---------------------------------------------------------------------------
# RedisClientNotInitializedError (lines 13-14)
# ---------------------------------------------------------------------------


def test_redis_not_initialized_default_message():
    exc = RedisClientNotInitializedError()
    assert "Redis client is not initialized" in str(exc)
    assert exc.message == "Redis client is not initialized."


def test_redis_not_initialized_custom_message():
    exc = RedisClientNotInitializedError("Custom msg")
    assert exc.message == "Custom msg"
    assert str(exc) == "Custom msg"


def test_redis_not_initialized_is_exception():
    with pytest.raises(RedisClientNotInitializedError):
        raise RedisClientNotInitializedError()


# ---------------------------------------------------------------------------
# EmailConfigurationError (line 22)
# ---------------------------------------------------------------------------


def test_email_config_error_message():
    exc = EmailConfigurationError()
    assert "email" in str(exc).lower() or "configuration" in str(exc).lower()


def test_email_config_error_is_exception():
    with pytest.raises(EmailConfigurationError):
        raise EmailConfigurationError()


# ---------------------------------------------------------------------------
# UserIdNotSetError (line 30)
# ---------------------------------------------------------------------------


def test_user_id_not_set_error():
    exc = UserIdNotSetError("user-123")
    assert "user-123" in str(exc)


def test_user_id_not_set_is_exception():
    with pytest.raises(UserIdNotSetError):
        raise UserIdNotSetError("abc")


# ---------------------------------------------------------------------------
# RefreshTokenMissingInvalidException (line 38)
# ---------------------------------------------------------------------------


def test_refresh_token_exception():
    exc = RefreshTokenMissingInvalidException()
    assert exc.status_code == 401
    assert "refresh token" in exc.detail.lower()


def test_refresh_token_is_exception():
    with pytest.raises(RefreshTokenMissingInvalidException):
        raise RefreshTokenMissingInvalidException()


# ---------------------------------------------------------------------------
# PlanetNotFoundError (lines 46-47)
# ---------------------------------------------------------------------------


def test_planet_not_found_default():
    exc = PlanetNotFoundError()
    assert exc.message == "Planet not found in the data source."
    assert str(exc) == "Planet not found in the data source."


def test_planet_not_found_custom():
    exc = PlanetNotFoundError("Mars not found")
    assert exc.message == "Mars not found"


def test_planet_not_found_is_exception():
    with pytest.raises(PlanetNotFoundError):
        raise PlanetNotFoundError()
