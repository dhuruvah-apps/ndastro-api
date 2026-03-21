"""Extended tests for ndastro_api.core.security - additional branches."""

import asyncio
from datetime import timedelta

from ndastro_api.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

# ---------------------------------------------------------------------------
# TokenType enum
# ---------------------------------------------------------------------------


def test_token_type_access():
    assert TokenType.ACCESS == "access"


def test_token_type_refresh():
    assert TokenType.REFRESH == "refresh"


# ---------------------------------------------------------------------------
# create_access_token with explicit expires_delta (covers the 'if' branch)
# ---------------------------------------------------------------------------


def test_create_access_token_with_expires_delta():
    token = asyncio.run(create_access_token({"sub": "test_user"}, expires_delta=timedelta(minutes=30)))
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_access_token_with_short_expiry():
    token = asyncio.run(create_access_token({"sub": "user2"}, expires_delta=timedelta(seconds=5)))
    assert isinstance(token, str)


# ---------------------------------------------------------------------------
# create_refresh_token with explicit expires_delta
# ---------------------------------------------------------------------------


def test_create_refresh_token_with_expires_delta():
    token = asyncio.run(create_refresh_token({"sub": "test_user"}, expires_delta=timedelta(days=7)))
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_refresh_token_with_short_expiry():
    token = asyncio.run(create_refresh_token({"sub": "user3"}, expires_delta=timedelta(hours=1)))
    assert isinstance(token, str)


# ---------------------------------------------------------------------------
# verify_password — wrong password
# ---------------------------------------------------------------------------


def test_verify_password_wrong():
    hashed = get_password_hash("correct_password")
    result = asyncio.run(verify_password("wrong_password", hashed))
    assert result is False


def test_verify_password_correct():
    hashed = get_password_hash("test123")
    result = asyncio.run(verify_password("test123", hashed))
    assert result is True


# ---------------------------------------------------------------------------
# Token content verification
# ---------------------------------------------------------------------------


def test_access_token_different_data_different_token():
    token1 = asyncio.run(create_access_token({"sub": "user1"}))
    token2 = asyncio.run(create_access_token({"sub": "user2"}))
    assert token1 != token2


def test_refresh_token_different_from_access():
    access = asyncio.run(create_access_token({"sub": "user1"}))
    refresh = asyncio.run(create_refresh_token({"sub": "user1"}))
    assert access != refresh
