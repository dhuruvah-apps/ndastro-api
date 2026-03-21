"""Unit tests for ndastro_api.schemas (user and tier Pydantic schemas)."""

import datetime

import pytest
from pydantic import ValidationError

from ndastro_api.schemas.pagination import PaginatedListResponse
from ndastro_api.schemas.tier import TierCreate, TierRead
from ndastro_api.schemas.user import UserCreate

# ---------------------------------------------------------------------------
# TierCreate
# ---------------------------------------------------------------------------


def test_tier_create_valid():
    tier = TierCreate(name="free")
    assert tier.name == "free"


def test_tier_create_requires_name():
    with pytest.raises(ValidationError):
        TierCreate()  # type: ignore


# ---------------------------------------------------------------------------
# TierRead
# ---------------------------------------------------------------------------


def test_tier_read_has_id():
    tier = TierRead(id=1, name="pro", created_at=datetime.datetime.now())
    assert tier.name == "pro"


# ---------------------------------------------------------------------------
# UserCreate
# ---------------------------------------------------------------------------


def test_user_create_valid():
    user = UserCreate(
        name="Alice",
        username="alice123",
        email="alice@example.com",
        password="SecurePass1!",
    )
    assert user.username == "alice123"
    assert user.email == "alice@example.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Bob",
            username="bob",
            email="not-an-email",
            password="pass",
        )


# ---------------------------------------------------------------------------
# PaginatedListResponse
# ---------------------------------------------------------------------------


def test_paginated_list_response_empty():
    resp = PaginatedListResponse(items=[], total=0, page=1, items_per_page=10)
    assert resp.total == 0
    assert resp.items == []


def test_paginated_list_response_with_items():
    resp = PaginatedListResponse(items=["a", "b"], total=2, page=1, items_per_page=10)
    assert len(resp.items) == 2
    assert resp.next_page is None
