"""Unit tests for ndastro_api.core.security (password hashing and token creation)."""

import asyncio

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


def test_token_type_values():
    assert TokenType.ACCESS == "access"
    assert TokenType.REFRESH == "refresh"


# ---------------------------------------------------------------------------
# get_password_hash()
# ---------------------------------------------------------------------------


def test_password_hash_returns_string():
    hashed = get_password_hash("mypassword")
    assert isinstance(hashed, str)


def test_password_hash_different_from_plain():
    plain = "mysecret"
    assert get_password_hash(plain) != plain


def test_password_hash_salted_unique():
    """Two hashes of the same password should differ (bcrypt salt)."""
    h1 = get_password_hash("password")
    h2 = get_password_hash("password")
    assert h1 != h2


# ---------------------------------------------------------------------------
# verify_password() — async, wrapped with asyncio.run
# ---------------------------------------------------------------------------


def test_verify_password_correct():
    hashed = get_password_hash("correcthorse")
    assert asyncio.run(verify_password("correcthorse", hashed)) is True


def test_verify_password_wrong():
    hashed = get_password_hash("correcthorse")
    assert asyncio.run(verify_password("wrongpassword", hashed)) is False


# ---------------------------------------------------------------------------
# create_access_token()
# ---------------------------------------------------------------------------


def test_create_access_token_returns_string():
    token = asyncio.run(create_access_token(data={"sub": "testuser"}))
    assert isinstance(token, str)
    assert len(token) > 10


def test_create_access_token_different_subjects_differ():
    t1 = asyncio.run(create_access_token(data={"sub": "user1"}))
    t2 = asyncio.run(create_access_token(data={"sub": "user2"}))
    assert t1 != t2


def test_create_access_token_custom_expiry():
    from datetime import timedelta

    token = asyncio.run(create_access_token(data={"sub": "user"}, expires_delta=timedelta(minutes=5)))
    assert isinstance(token, str)


# ---------------------------------------------------------------------------
# create_refresh_token()
# ---------------------------------------------------------------------------


def test_create_refresh_token_returns_string():
    import asyncio

    token = asyncio.run(create_refresh_token(data={"sub": "testuser"}))
    assert isinstance(token, str)


def test_refresh_token_differs_from_access_token():
    import asyncio

    data = {"sub": "user"}
    access = asyncio.run(create_access_token(data=data))
    refresh = asyncio.run(create_refresh_token(data=data))
    assert access != refresh
